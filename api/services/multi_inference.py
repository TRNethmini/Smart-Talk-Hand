import logging
import pickle
from collections import deque
from pathlib import Path
from typing import Deque, List, Tuple, Dict, Iterable

import numpy as np
from tensorflow import keras

from landmark_extractor import LandmarkExtractor
from config import PROJECT_ROOT, API_DIR, NUM_LANDMARKS, COORDS_PER_LM

logger = logging.getLogger("uvicorn.error")

MODELS_DIR = API_DIR / "models"

class ModelContext:
    def __init__(self, model, scaler, label_encoder, seq_len: int, max_num_hands: int):
        self.model = model
        self.scaler = scaler
        self.label_encoder = label_encoder
        self.seq_len = seq_len
        self.max_num_hands = max_num_hands
        self.n_feats = max_num_hands * NUM_LANDMARKS * COORDS_PER_LM
        self.frame_buffer = deque(maxlen=seq_len)

models_registry: Dict[str, ModelContext] = {}
landmark_extractor: LandmarkExtractor | None = None

def load_all_models() -> None:
    global landmark_extractor
    
    if not MODELS_DIR.exists():
        logger.warning(f"Models directory not found: {MODELS_DIR}")
        return
        
    for d in MODELS_DIR.iterdir():
        if not d.is_dir():
            continue
            
        # The legacy alphabet directory uses 'ssl_alphabet' prefix for its files
        model_name = "ssl_alphabet" if d.name == "alphabet" else d.name
        
        model_path = d / f"{model_name}_lstm.keras"
        scaler_path = d / f"{model_name}_lstm_scaler.pkl"
        meta_path = d / f"{model_name}_sequences.pkl"
        
        if not (model_path.exists() and scaler_path.exists() and meta_path.exists()):
            continue
            
        try:
            logger.info(f"Loading multi-model: {model_name}")
            model = keras.models.load_model(model_path)
            
            with open(scaler_path, "rb") as f:
                scaler = pickle.load(f)
                
            with open(meta_path, "rb") as f:
                meta = pickle.load(f)
                
            label_encoder = meta["label_encoder"]
            seq_len = int(meta.get("seq_len", 30))
            max_num_hands = int(meta.get("max_num_hands", 2))
            
            ctx = ModelContext(model, scaler, label_encoder, seq_len, max_num_hands)
            models_registry[model_name] = ctx
            logger.info(f"Successfully loaded {model_name} (hands={max_num_hands}, seq={seq_len})")
        except Exception as e:
            logger.error(f"Failed to load {model_name}: {e}")

    try:
        if landmark_extractor is None:
            landmark_extractor = LandmarkExtractor()
            logger.info("LandmarkExtractor initialized for multi-model webcam frames.")
    except Exception as exc:
        logger.error("Failed to initialize LandmarkExtractor: %s", exc)

def get_classes(model_name: str) -> List[str]:
    if model_name not in models_registry:
        raise ValueError(f"Model '{model_name}' not loaded.")
    return [str(c) for c in models_registry[model_name].label_encoder.classes_]

def predict_topk_from_sequences(
    model_name: str, sequences: np.ndarray, topk: int
) -> Tuple[str, List[Tuple[str, float]]]:
    if model_name not in models_registry:
        raise ValueError(f"Model '{model_name}' not loaded.")
        
    ctx = models_registry[model_name]
    if sequences.ndim != 3:
        raise ValueError("sequences must be 3D: [num_seq][SEQ_LEN][N_FEATS]")

    n_samples, n_steps, n_feats = sequences.shape
    if n_steps != ctx.seq_len or n_feats != ctx.n_feats:
        raise ValueError(
            f"Expected shape (num_seq, {ctx.seq_len}, {ctx.n_feats}), got {tuple(sequences.shape)}"
        )

    flat = sequences.reshape(-1, n_feats)
    flat_s = ctx.scaler.transform(flat)
    seqs_s = flat_s.reshape(n_samples, n_steps, n_feats)

    probs = ctx.model.predict(seqs_s, verbose=0)
    if n_samples > 1:
        avg = probs.mean(axis=0)
    else:
        avg = probs[0]

    k = min(topk, avg.shape[0])
    topk_idx = np.argsort(avg)[::-1][:k]
    labels = ctx.label_encoder.inverse_transform(topk_idx)

    predicted_label = str(labels[0])
    topk_items = [(str(lbl), float(avg[i])) for lbl, i in zip(labels, topk_idx)]
    return predicted_label, topk_items

def landmarks_to_frame_vec(landmarks: List[List[float]] | None, max_num_hands: int) -> np.ndarray:
    n_feats = max_num_hands * NUM_LANDMARKS * COORDS_PER_LM
    vec = np.zeros((n_feats,), dtype=np.float32)

    if not landmarks:
        return vec

    arr = np.array(landmarks[:max_num_hands * NUM_LANDMARKS], dtype=np.float32).reshape(-1)
    count = min(arr.size, n_feats)
    vec[:count] = arr[:count]

    for h in range(max_num_hands):
        offset = h * NUM_LANDMARKS * COORDS_PER_LM
        wrist = vec[offset : offset + COORDS_PER_LM].copy()
        if np.any(wrist != 0):
            for lm in range(NUM_LANDMARKS):
                base = offset + lm * COORDS_PER_LM
                vec[base : base + COORDS_PER_LM] -= wrist

    return vec

def frames_to_sequence(frame_vecs: Iterable[np.ndarray], seq_len: int) -> np.ndarray:
    frame_list = [np.asarray(v, dtype=np.float32) for v in frame_vecs]
    if not frame_list:
        raise ValueError("frame_vecs must not be empty")

    frames_arr = np.stack(frame_list, axis=0)
    n_frames, n_feats = frames_arr.shape

    if n_frames >= seq_len:
        seq = frames_arr[:seq_len]
    else:
        seq = np.zeros((seq_len, n_feats), dtype=np.float32)
        seq[:n_frames] = frames_arr

    return seq[np.newaxis, ...]
