import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import pickle
import mediapipe as mp
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
import json

try:
    import requests
except ImportError:  # pragma: no cover - optional dependency
    requests = None

from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision


BaseOptions = mp_python.BaseOptions
HandLandmarker = mp_vision.HandLandmarker
HandLandmarkerOptions = mp_vision.HandLandmarkerOptions
VisionRunningMode = mp_vision.RunningMode


# Project root (scripts/ is one level below)
ROOT_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = ROOT_DIR / "models" / "ssl_alphabet_lstm.keras"
SEQUENCE_META_PATH = ROOT_DIR / "dataset" / "processed" / "ssl-alphabet-converted" / "ssl_alphabet_sequences.pkl"
MODEL_FILE = ROOT_DIR / "notebooks" / "hand_landmarker.task"

MAX_NUM_HANDS = 2
NUM_LANDMARKS = 21
COORDS_PER_LM = 3


def result_to_flat_landmarks(result):
    """Convert a HandLandmarkerResult to a flat numpy array.

    Returns (flat_array, detected). flat_array has shape
    (MAX_NUM_HANDS * 21 * 3,); undetected hands are zero-padded.
    """
    landmarks = np.zeros(MAX_NUM_HANDS * NUM_LANDMARKS * COORDS_PER_LM, dtype=np.float32)
    detected = bool(result.hand_landmarks)

    if detected:
        for hand_idx, hand_lms in enumerate(result.hand_landmarks):
            if hand_idx >= MAX_NUM_HANDS:
                break
            offset = hand_idx * NUM_LANDMARKS * COORDS_PER_LM
            for lm_idx, lm in enumerate(hand_lms):
                base = offset + lm_idx * COORDS_PER_LM
                landmarks[base] = lm.x
                landmarks[base + 1] = lm.y
                landmarks[base + 2] = lm.z

    return landmarks, detected


def normalise_landmarks(landmarks_flat):
    """Translate each hand so that the wrist (landmark 0) is at the origin."""
    normed = landmarks_flat.copy()
    for h in range(MAX_NUM_HANDS):
        offset = h * NUM_LANDMARKS * COORDS_PER_LM
        wrist = normed[offset : offset + COORDS_PER_LM].copy()
        if np.any(wrist != 0):
            for lm in range(NUM_LANDMARKS):
                base = offset + lm * COORDS_PER_LM
                normed[base : base + COORDS_PER_LM] -= wrist
    return normed


def load_hand_landmarker():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(f"MediaPipe model file not found: {MODEL_FILE}")

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL_FILE)),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=MAX_NUM_HANDS,
        min_hand_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return HandLandmarker.create_from_options(options)


def extract_landmarks_from_video(video_path: Path) -> np.ndarray:
    """Run MediaPipe Hands over a video and return per-frame landmark vectors."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames = []

    with load_hand_landmarker() as detector:
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            timestamp_ms = int(frame_idx * 1000 / fps)

            result = detector.detect_for_video(mp_image, timestamp_ms)
            lm_flat, detected = result_to_flat_landmarks(result)

            if detected:
                normed = normalise_landmarks(lm_flat)
                frames.append(normed)

            frame_idx += 1

    cap.release()

    if not frames:
        return np.empty((0, MAX_NUM_HANDS * NUM_LANDMARKS * COORDS_PER_LM), dtype=np.float32)

    return np.stack(frames, axis=0)


def build_sequences(frames: np.ndarray, seq_len: int, stride: int) -> np.ndarray:
    """Convert per-frame landmarks to fixed-length sequences."""
    if len(frames) == 0:
        return np.empty((0, seq_len, frames.shape[1] if frames.ndim == 2 else MAX_NUM_HANDS * NUM_LANDMARKS * COORDS_PER_LM), dtype=np.float32)

    all_sequences = []
    if len(frames) < seq_len:
        padded = np.zeros((seq_len, frames.shape[1]), dtype=np.float32)
        padded[: len(frames)] = frames
        all_sequences.append(padded)
    else:
        for start in range(0, len(frames) - seq_len + 1, stride):
            all_sequences.append(frames[start : start + seq_len])

    return np.stack(all_sequences, axis=0)


def scale_sequences(X_seq: np.ndarray, scaler) -> np.ndarray:
    """Apply StandardScaler (fitted on training data) to sequences."""
    n_samples, n_steps, n_feats = X_seq.shape
    flat = X_seq.reshape(-1, n_feats)
    flat_s = scaler.transform(flat)
    return flat_s.reshape(n_samples, n_steps, n_feats)


def load_label_encoder_and_meta():
    """Load label encoder, training data, and sequence metadata from the training pickle."""
    if not SEQUENCE_META_PATH.exists():
        raise FileNotFoundError(f"Sequence metadata file not found: {SEQUENCE_META_PATH}")

    with open(SEQUENCE_META_PATH, "rb") as f:
        data = pickle.load(f)

    le = data["label_encoder"]
    X_train = data["X_train"]
    seq_len = int(data.get("seq_len", 30))
    stride = int(data.get("stride", 5))
    return le, X_train, seq_len, stride


def infer_video_local(video_path: Path, topk: int = 5):
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"LSTM model not found at {MODEL_PATH}")

    print(f"Loading model from {MODEL_PATH}")
    model = keras.models.load_model(MODEL_PATH)

    # Recreate scaler from training data to avoid pickle version issues
    le, X_train, seq_len_meta, stride_meta = load_label_encoder_and_meta()
    n_train, n_steps, n_feats = X_train.shape
    scaler = StandardScaler()
    scaler.fit(X_train.reshape(-1, n_feats))

    print(f"SEQ_LEN from metadata: {seq_len_meta}, STRIDE: {stride_meta}")

    print(f"Processing video: {video_path}")
    frames = extract_landmarks_from_video(video_path)
    print(f"Detected frames with hands: {len(frames)}")

    if len(frames) == 0:
        print("No hand landmarks detected in this video. Cannot run inference.")
        return

    X_seq = build_sequences(frames, seq_len=seq_len_meta, stride=stride_meta)
    print(f"Built {X_seq.shape[0]} sequences of shape {X_seq.shape[1:]}\\n")

    X_seq_s = scale_sequences(X_seq, scaler)

    probs = model.predict(X_seq_s, verbose=0)  # (num_seq, num_classes)
    avg_probs = probs.mean(axis=0)

    pred_idx = int(np.argmax(avg_probs))
    pred_label = le.inverse_transform([pred_idx])[0]

    print("=== Inference Result ===")
    print(f"Predicted letter: {pred_label}")

    # Top-k breakdown
    k = min(topk, avg_probs.shape[0])
    top_indices = np.argsort(avg_probs)[::-1][:k]
    print("\\nTop-k probabilities:")
    for rank, idx in enumerate(top_indices, start=1):
        label = le.inverse_transform([idx])[0]
        score = float(avg_probs[idx])
        print(f"{rank:>2}. {label} : {score:.4f}")


def infer_video_via_api(video_path: Path, api_url: str, topk: int = 5) -> None:
    if requests is None:
        raise RuntimeError(
            "The 'requests' library is required for --api-url. "
            "Install it with: pip install requests"
        )

    # Load metadata to get SEQ_LEN / STRIDE
    le, _X_train, seq_len_meta, stride_meta = load_label_encoder_and_meta()
    print(f"Using SEQ_LEN={seq_len_meta}, STRIDE={stride_meta} from metadata")

    print(f"Processing video: {video_path}")
    frames = extract_landmarks_from_video(video_path)
    print(f"Detected frames with hands: {len(frames)}")

    if len(frames) == 0:
        print("No hand landmarks detected in this video. Cannot run inference.")
        return

    X_seq = build_sequences(frames, seq_len=seq_len_meta, stride=stride_meta)
    print(f"Built {X_seq.shape[0]} sequences of shape {X_seq.shape[1:]}\\n")

    payload = {
        "sequences": X_seq.tolist(),  # [num_seq][SEQ_LEN][126]
        "topk": topk,
    }

    print(f"Calling API at {api_url} ...")
    resp = requests.post(api_url, json=payload, timeout=30)
    if resp.status_code != 200:
        print(f"API error {resp.status_code}: {resp.text}", file=sys.stderr)
        return

    data = resp.json()
    pred_label = data.get("predicted_label")
    topk_items = data.get("topk", [])

    print("=== Inference Result (API) ===")
    print(f"Predicted letter: {pred_label}")

    if topk_items:
        print("\\nTop-k probabilities:")
        for i, item in enumerate(topk_items, start=1):
            print(f"{i:>2}. {item['label']} : {item['prob']:.4f}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Infer a Sinhala sign alphabet letter from a video using the LSTM sequence model."
    )
    parser.add_argument("video_path", type=str, help="Path to the input video file (.mp4, .mov, etc.)")
    parser.add_argument(
        "--topk",
        type=int,
        default=5,
        help="Number of top probabilities to display (default: 5)",
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default=None,
        help="Optional FastAPI /predict endpoint URL; if provided, use API instead of local model",
    )

    args = parser.parse_args(argv)

    video_path = Path(args.video_path)
    if not video_path.exists():
        print(f"Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.api_url:
            infer_video_via_api(video_path, api_url=args.api_url, topk=args.topk)
        else:
            infer_video_local(video_path, topk=args.topk)
    except Exception as e:
        print(f"Error during inference: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

