import logging
import pickle
from collections import deque
from typing import Deque, List, Tuple

import numpy as np
from tensorflow import keras

from config import (
    COORDS_PER_LM,
    DEFAULT_SEQ_LEN,
    META_PATH,
    MODEL_PATH,
    N_FEATS,
    NUM_LANDMARKS,
    SCALER_PATH,
)
from landmark_extractor import LandmarkExtractor


logger = logging.getLogger("uvicorn.error")


model = None
scaler = None
label_encoder = None
SEQ_LEN: int = DEFAULT_SEQ_LEN
FRAME_BUFFER: Deque[List[float]] = deque()
landmark_extractor: LandmarkExtractor | None = None


def load_artifacts() -> None:
    """Load model, scaler, label encoder and initialize webcam helpers."""
    global model, scaler, label_encoder, SEQ_LEN, FRAME_BUFFER, landmark_extractor

    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model not found at {MODEL_PATH}")

    logger.info("Loading model from %s", MODEL_PATH)
    model = keras.models.load_model(MODEL_PATH)

    if not SCALER_PATH.exists():
        raise RuntimeError(f"Scaler not found at {SCALER_PATH}")

    with open(SCALER_PATH, "rb") as f:
        scaler_loaded = pickle.load(f)

    scaler_type = type(scaler_loaded).__name__
    logger.info("Loaded scaler of type %s", scaler_type)
    scaler = scaler_loaded

    if not META_PATH.exists():
        raise RuntimeError(f"Metadata file not found at {META_PATH}")

    with open(META_PATH, "rb") as f:
        meta = pickle.load(f)

    label_encoder = meta["label_encoder"]
    SEQ_LEN = int(meta.get("seq_len", DEFAULT_SEQ_LEN))
    FRAME_BUFFER = deque(maxlen=SEQ_LEN)

    logger.info(
        "Artifacts loaded: SEQ_LEN=%s, num_classes=%s",
        SEQ_LEN,
        len(label_encoder.classes_),
    )

    # Initialize landmark extractor for webcam base64 images.
    try:
        landmark_extractor = LandmarkExtractor()
        logger.info("LandmarkExtractor initialized for webcam frames.")
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Failed to initialize LandmarkExtractor: %s", exc)
        landmark_extractor = None


def get_classes() -> List[str]:
    if label_encoder is None:
        raise RuntimeError("Label encoder not loaded")
    return [str(c) for c in label_encoder.classes_]


def predict_topk_from_sequences(
    sequences: np.ndarray, topk: int
) -> Tuple[str, List[Tuple[str, float]]]:
    """Core prediction pipeline shared by /predict and webcam endpoints.

    sequences: array of shape (num_seq, SEQ_LEN, N_FEATS)
    """
    if model is None or scaler is None or label_encoder is None:
        raise RuntimeError("Model or scaler not loaded")

    if sequences.ndim != 3:
        raise ValueError("sequences must be 3D: [num_seq][SEQ_LEN][N_FEATS]")

    n_samples, n_steps, n_feats = sequences.shape
    if n_steps != SEQ_LEN or n_feats != N_FEATS:
        raise ValueError(
            f"Expected shape (num_seq, {SEQ_LEN}, {N_FEATS}), got {tuple(sequences.shape)}"
        )

    flat = sequences.reshape(-1, n_feats)
    flat_s = scaler.transform(flat)
    seqs_s = flat_s.reshape(n_samples, n_steps, n_feats)

    probs = model.predict(seqs_s, verbose=0)
    if n_samples > 1:
        avg = probs.mean(axis=0)
    else:
        avg = probs[0]

    k = min(topk, avg.shape[0])
    topk_idx = np.argsort(avg)[::-1][:k]
    labels = label_encoder.inverse_transform(topk_idx)

    predicted_label = str(labels[0])
    topk_items = [(str(lbl), float(avg[i])) for lbl, i in zip(labels, topk_idx)]
    return predicted_label, topk_items


def landmarks_to_frame_vec(landmarks: List[List[float]] | None) -> np.ndarray:
    """Convert single-hand landmarks into a feature vector matching training.

    Mirrors the training representation:
    - 1 hand × 21 landmarks × 3 coords = 63 features
    - Hand is wrist-normalized (wrist at origin)
    """
    vec = np.zeros((N_FEATS,), dtype=np.float32)

    if not landmarks:
        return vec

    arr = np.array(landmarks[:NUM_LANDMARKS], dtype=np.float32).reshape(-1)
    max_first_hand = NUM_LANDMARKS * COORDS_PER_LM
    count = min(arr.size, max_first_hand)
    vec[:count] = arr[:count]

    wrist = vec[:COORDS_PER_LM].copy()
    if np.any(wrist != 0):
        for lm in range(NUM_LANDMARKS):
            base = lm * COORDS_PER_LM
            vec[base : base + COORDS_PER_LM] -= wrist

    return vec

