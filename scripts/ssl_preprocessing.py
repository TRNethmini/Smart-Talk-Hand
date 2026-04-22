"""SSL video preprocessing with MediaPipe. Standalone script — no api imports."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import cv2
import mediapipe as mp
import numpy as np
import pickle
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from sklearn.model_selection import train_test_split

# Project root: parent of the directory containing this file (e.g. c:\Redmi)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

MP_BASE_OPTIONS = mp_python.BaseOptions
MP_HAND_LANDMARKER = mp_vision.HandLandmarker
MP_HAND_LANDMARKER_OPTS = mp_vision.HandLandmarkerOptions
MP_RUNNING_MODE = mp_vision.RunningMode

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)


@dataclass
class PreprocessConfig:
    ssl_name: str
    max_num_hands: int = 2
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    num_landmarks: int = 21
    coords_per_landmark: int = 3
    seq_len: int = 30
    stride: int = 5


def _project_paths(ssl_name: str) -> Tuple[Path, Path, str]:
    dataset_dir = PROJECT_ROOT / "dataset" / ssl_name
    processed_root = PROJECT_ROOT / "dataset" / "processed" / ssl_name
    processed_root.mkdir(parents=True, exist_ok=True)
    base_name = ssl_name.replace("-", "_")
    return dataset_dir, processed_root, base_name


def _model_path() -> Path:
    return PROJECT_ROOT / "models" / "hand_landmarker.task"


def ensure_hand_landmarker_model() -> Path:
    model_path = _model_path()
    model_path.parent.mkdir(parents=True, exist_ok=True)

    if model_path.exists():
        print(f"MediaPipe hand_landmarker exists at {model_path}")
        return model_path

    import urllib.request

    print("Downloading MediaPipe hand_landmarker.task …")
    urllib.request.urlretrieve(MODEL_URL, model_path)
    size_mb = model_path.stat().st_size / 1e6
    print(f"Saved to {model_path} ({size_mb:.1f} MB)")
    return model_path


def scan_videos(dataset_dir: Path) -> List[Tuple[Path, str]]:
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    exts = {".MOV", ".MP4", ".AVI"}
    video_files: List[Tuple[Path, str]] = []

    for letter_dir in sorted(dataset_dir.iterdir()):
        if not letter_dir.is_dir():
            continue
        label = letter_dir.name
        vids = [
            v
            for v in sorted(letter_dir.iterdir())
            if v.suffix.upper() in exts
        ]
        if not vids:
            continue
        for v in vids:
            video_files.append((v, label))

    print(f"Found {len(video_files)} videos in {dataset_dir}")
    return video_files


def _result_to_flat_landmarks(
    result,
    max_num_hands: int,
    num_landmarks: int,
    coords_per_lm: int,
) -> Tuple[np.ndarray, bool]:
    size = max_num_hands * num_landmarks * coords_per_lm
    landmarks = np.zeros(size, dtype=np.float32)
    detected = bool(result.hand_landmarks)

    if detected:
        for hand_idx, hand_lms in enumerate(result.hand_landmarks):
            if hand_idx >= max_num_hands:
                break
            offset = hand_idx * num_landmarks * coords_per_lm
            for lm_idx, lm in enumerate(hand_lms):
                base = offset + lm_idx * coords_per_lm
                landmarks[base] = lm.x
                landmarks[base + 1] = lm.y
                landmarks[base + 2] = lm.z

    return landmarks, detected


def _normalise_landmarks(
    landmarks_flat: np.ndarray,
    max_num_hands: int,
    num_landmarks: int,
    coords_per_lm: int,
) -> np.ndarray:
    normed = landmarks_flat.copy()
    for h in range(max_num_hands):
        offset = h * num_landmarks * coords_per_lm
        wrist = normed[offset : offset + coords_per_lm].copy()
        if np.any(wrist != 0):
            for lm in range(num_landmarks):
                base = offset + lm * coords_per_lm
                normed[base : base + coords_per_lm] -= wrist
    return normed


def extract_video_sequences(
    video_files: Sequence[Tuple[Path, str]],
    cfg: PreprocessConfig,
    model_path: Path,
) -> Dict[str, List[np.ndarray]]:
    video_sequences: Dict[str, List[np.ndarray]] = {}
    skipped_frames: Dict[str, int] = {}
    processed_frames: Dict[str, int] = {}

    options = MP_HAND_LANDMARKER_OPTS(
        base_options=MP_BASE_OPTIONS(model_asset_path=str(model_path)),
        running_mode=MP_RUNNING_MODE.VIDEO,
        num_hands=cfg.max_num_hands,
        min_hand_detection_confidence=cfg.min_detection_confidence,
        min_tracking_confidence=cfg.min_tracking_confidence,
    )

    for vid_path, label in video_files:
        cap = cv2.VideoCapture(str(vid_path))
        if not cap.isOpened():
            print(f"  [ERROR] Cannot open {vid_path}")
            continue

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frames_for_video: List[np.ndarray] = []

        with MP_HAND_LANDMARKER.create_from_options(options) as detector:
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=frame_rgb,
                )
                timestamp_ms = int(frame_idx * 1000 / fps)

                result = detector.detect_for_video(mp_image, timestamp_ms)
                lm_flat, detected = _result_to_flat_landmarks(
                    result,
                    cfg.max_num_hands,
                    cfg.num_landmarks,
                    cfg.coords_per_landmark,
                )

                if detected:
                    normed = _normalise_landmarks(
                        lm_flat,
                        cfg.max_num_hands,
                        cfg.num_landmarks,
                        cfg.coords_per_landmark,
                    )
                    frames_for_video.append(normed)
                    processed_frames[label] = processed_frames.get(label, 0) + 1
                else:
                    skipped_frames[label] = skipped_frames.get(label, 0) + 1

                frame_idx += 1

        cap.release()

        if frames_for_video:
            video_sequences.setdefault(label, []).append(
                np.array(frames_for_video, dtype=np.float32)
            )

        total = processed_frames.get(label, 0) + skipped_frames.get(label, 0)
        det_rate = (
            processed_frames.get(label, 0) / total * 100 if total else 0.0
        )
        print(
            f"  {label} : {processed_frames.get(label, 0):4d} detected / "
            f"{total:4d} total frames  ({det_rate:.1f}%)"
        )

    total_frames = sum(processed_frames.values())
    total_videos = sum(len(v) for v in video_sequences.values())
    print(f"\nTotal frames with detections: {total_frames}")
    print(f"Total videos: {total_videos}")
    print(f"Unique labels: {len(video_sequences)}")
    return video_sequences


def build_sequences(
    video_sequences: Dict[str, List[np.ndarray]],
    seq_len: int,
    stride: int,
) -> Tuple[np.ndarray, np.ndarray]:
    all_sequences: List[np.ndarray] = []
    all_labels: List[str] = []

    for label, videos in video_sequences.items():
        for frames in videos:
            n_frames = len(frames)
            if n_frames < seq_len:
                padded = np.zeros(
                    (seq_len, frames.shape[1]), dtype=np.float32
                )
                padded[:n_frames] = frames
                all_sequences.append(padded)
                all_labels.append(label)
            else:
                for start in range(0, n_frames - seq_len + 1, stride):
                    all_sequences.append(frames[start : start + seq_len])
                    all_labels.append(label)

    X = np.array(all_sequences, dtype=np.float32)
    y = np.array(all_labels)

    print(
        f"Sequence matrix X : {X.shape}  (sequences, timesteps, features)\n"
        f"Label array y     : {y.shape}\n"
        f"SEQ_LEN={seq_len}, STRIDE={stride}\n"
        f"Features per timestep: {X.shape[2]}"
    )
    return X, y


def split_sequences(
    X: np.ndarray,
    y: np.ndarray,
    random_state: int = 42,
) -> Tuple[np.ndarray, ...]:
    from sklearn.preprocessing import LabelEncoder

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # Stratification requires ≥2 samples per class (train and temp each get some)
    min_class_count = np.bincount(y_encoded.astype(int)).min()
    stratify_train = min_class_count >= 2

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y_encoded,
        test_size=0.3,
        random_state=random_state,
        stratify=y_encoded if stratify_train else None,
    )

    min_class_temp = np.bincount(y_temp.astype(int)).min()
    stratify_val_test = min_class_temp >= 2

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.5,
        random_state=random_state,
        stratify=y_temp if stratify_val_test else None,
    )

    if not stratify_train:
        print(
            "⚠ At least one class has only 1 sample; train/temp split is NOT stratified."
        )
    if not stratify_val_test:
        print(
            "⚠ Some classes had < 2 samples in temp set; "
            "val/test split is NOT stratified."
        )

    print(f"Train : {X_train.shape[0]:6d} samples")
    print(f"Val   : {X_val.shape[0]:6d} samples")
    print(f"Test  : {X_test.shape[0]:6d} samples")

    num_classes = len(le.classes_)
    print(f"Classes: {num_classes}")
    return X_train, X_val, X_test, y_train, y_val, y_test, le, num_classes


def build_dataset_dict(
    cfg: PreprocessConfig,
    X_train: np.ndarray,
    X_val: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_val: np.ndarray,
    y_test: np.ndarray,
    le,
    num_classes: int,
) -> dict:
    return {
        "X_train": X_train,
        "X_val": X_val,
        "X_test": X_test,
        "y_train": y_train,
        "y_val": y_val,
        "y_test": y_test,
        "label_encoder": le,
        "num_classes": num_classes,
        "max_num_hands": cfg.max_num_hands,
        "num_landmarks": cfg.num_landmarks,
        "coords_per_landmark": cfg.coords_per_landmark,
        "seq_len": cfg.seq_len,
        "stride": cfg.stride,
    }


def save_dataset(
    dataset: dict,
    processed_root: Path,
    base_name: str,
) -> Path:
    output_path = processed_root / f"{base_name}_sequences.pkl"
    with open(output_path, "wb") as f:
        pickle.dump(dataset, f)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Saved sequence dataset to {output_path}")
    print(f"File size: {size_mb:.2f} MB")
    return output_path


def run_for_dataset(
    ssl_name: str,
    max_num_hands: int = 2,
    seq_len: int = 30,
    stride: int = 5,
) -> Path:
    dataset_dir, processed_root, base_name = _project_paths(ssl_name)
    print(f"=== Preprocessing dataset '{ssl_name}' ===")
    print(f"Dataset dir   : {dataset_dir}")
    print(f"Processed dir : {processed_root}")

    cfg = PreprocessConfig(
        ssl_name=ssl_name,
        max_num_hands=max_num_hands,
        seq_len=seq_len,
        stride=stride,
    )

    model_path = ensure_hand_landmarker_model()
    video_files = scan_videos(dataset_dir)

    if not video_files:
        raise RuntimeError(f"No videos found under {dataset_dir}")

    video_sequences = extract_video_sequences(video_files, cfg, model_path)
    X, y = build_sequences(video_sequences, cfg.seq_len, cfg.stride)
    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
        le,
        num_classes,
    ) = split_sequences(X, y)

    dataset = build_dataset_dict(
        cfg,
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
        le,
        num_classes,
    )
    return save_dataset(dataset, processed_root, base_name)


__all__ = [
    "PreprocessConfig",
    "ensure_hand_landmarker_model",
    "scan_videos",
    "extract_video_sequences",
    "build_sequences",
    "split_sequences",
    "build_dataset_dict",
    "save_dataset",
    "run_for_dataset",
]
