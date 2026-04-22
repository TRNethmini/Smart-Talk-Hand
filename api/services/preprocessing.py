from typing import Iterable, List

import numpy as np

from services import inference


def frames_to_sequence(
    frame_vecs: Iterable[np.ndarray],
) -> np.ndarray:
    """Build a single (1, SEQ_LEN, N_FEATS) sequence from per-frame vectors.

    Pads with zeros or truncates to match the configured SEQ_LEN.
    """
    frame_list: List[np.ndarray] = [np.asarray(v, dtype=np.float32) for v in frame_vecs]
    if not frame_list:
        raise ValueError("frame_vecs must not be empty")

    frames_arr = np.stack(frame_list, axis=0)
    n_frames, n_feats = frames_arr.shape

    seq_len = inference.SEQ_LEN
    if n_frames >= seq_len:
        seq = frames_arr[:seq_len]
    else:
        seq = np.zeros((seq_len, n_feats), dtype=np.float32)
        seq[:n_frames] = frames_arr

    return seq[np.newaxis, ...]  # (1, SEQ_LEN, N_FEATS)

