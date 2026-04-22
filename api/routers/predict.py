from typing import List

import numpy as np
from fastapi import APIRouter, HTTPException, WebSocket

from models.schemas import (
    PredictRequest,
    PredictResponse,
    TopKItem,
    WebcamFrameRequest,
    WebcamSequenceRequest,
)
from services import inference, preprocessing


router = APIRouter()


@router.post("/api/v1/predict", response_model=PredictResponse)
async def predict(req: PredictRequest) -> PredictResponse:
    """Predict Sinhala alphabet letter(s) from landmark sequences.

    Expects sequences shaped [num_seq][SEQ_LEN][N_FEATS].
    """
    try:
        seqs = np.array(req.sequences, dtype="float32")
        predicted_label, topk_items = inference.predict_topk_from_sequences(
            seqs, req.topk
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    topk_models = [
        TopKItem(label=lbl, prob=prob) for lbl, prob in topk_items
    ]

    return PredictResponse(
        predicted_label=predicted_label,
        topk=topk_models,
        seq_len=inference.SEQ_LEN,
        num_sequences=int(seqs.shape[0]),
    )


@router.post("/api/v1/webcam-frame")
async def webcam_frame(req: WebcamFrameRequest) -> dict:
    """Accept a single webcam frame as base64 image and predict using the main LSTM model.

    We:
    - Extract hand landmarks from the image.
    - Flatten/pad to N_FEATS features for the current frame.
    - Maintain a sliding window of SEQ_LEN frames in FRAME_BUFFER.
    - Once the buffer is full, reuse the /api/v1/predict pipeline on a single sequence.
    """
    if (
        inference.model is None
        or inference.scaler is None
        or inference.label_encoder is None
    ):
        raise HTTPException(status_code=503, detail="Model not loaded")
    if inference.landmark_extractor is None:
        raise HTTPException(status_code=503, detail="Landmark extractor not initialized")

    if inference.SEQ_LEN <= 0:
        raise HTTPException(status_code=500, detail="Invalid SEQ_LEN")

    landmarks = inference.landmark_extractor.extract(req.image)
    if landmarks is None:
        return {
            "status": "error",
            "message": "No hand detected",
            "frames": len(inference.FRAME_BUFFER),
            "landmarks": [],
        }

    frame_vec = inference.landmarks_to_frame_vec(landmarks)
    inference.FRAME_BUFFER.append(frame_vec.tolist())
    frames = len(inference.FRAME_BUFFER)

    if frames < inference.SEQ_LEN:
        return {
            "status": "buffering",
            "frames": frames,
            "landmarks": landmarks,
        }

    seq = np.array(inference.FRAME_BUFFER, dtype="float32")
    seq = seq[-inference.SEQ_LEN :]

    flat_seq = seq.reshape(-1, seq.shape[-1])
    flat_s = inference.scaler.transform(flat_seq)
    seq_s = flat_s.reshape(1, inference.SEQ_LEN, seq.shape[-1])

    probs = inference.model.predict(seq_s, verbose=0)[0]
    top_idx = int(np.argmax(probs))
    confidence = float(probs[top_idx])
    label = str(inference.label_encoder.inverse_transform([top_idx])[0])

    return {
        "status": "prediction",
        "label": label,
        "confidence": confidence,
        "frames": frames,
        "landmarks": landmarks,
    }


@router.post("/api/v1/webcam-sequence", response_model=PredictResponse)
async def webcam_sequence(req: WebcamSequenceRequest) -> PredictResponse:
    """Accept a batch of webcam frames and run a single sequence prediction."""
    if (
        inference.model is None
        or inference.scaler is None
        or inference.label_encoder is None
    ):
        raise HTTPException(status_code=503, detail="Model not loaded")
    if inference.landmark_extractor is None:
        raise HTTPException(status_code=503, detail="Landmark extractor not initialized")
    if not req.frames:
        raise HTTPException(status_code=400, detail="frames must not be empty")

    frame_vecs: List[np.ndarray] = []
    for frame_str in req.frames:
        lms = inference.landmark_extractor.extract(frame_str)
        vec = inference.landmarks_to_frame_vec(lms or [])
        frame_vecs.append(vec)

    seq = preprocessing.frames_to_sequence(frame_vecs)

    try:
        predicted_label, topk_items = inference.predict_topk_from_sequences(seq, 5)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    topk_models = [
        TopKItem(label=lbl, prob=prob) for lbl, prob in topk_items
    ]

    return PredictResponse(
        predicted_label=predicted_label,
        topk=topk_models,
        seq_len=inference.SEQ_LEN,
        num_sequences=1,
    )


@router.post("/api/v1/webcam-reset")
async def webcam_reset() -> dict:
    """Reset the sliding-frame buffer used for webcam predictions."""
    inference.FRAME_BUFFER.clear()
    return {"status": "reset", "frames": 0}


@router.websocket("/ws/predict")
async def ws_predict(websocket: WebSocket) -> None:
    """WebSocket endpoint placeholder.

    Realtime WS streaming is disabled because there is no separate realtime model.
    Use the HTTP /api/v1/webcam-frame endpoint instead.
    """
    await websocket.accept()
    await websocket.send_json(
        {
            "error": "Realtime WebSocket streaming is disabled (no realtime model configured). "
            "Use /api/v1/webcam-frame for webcam predictions."
        }
    )
    await websocket.close()

