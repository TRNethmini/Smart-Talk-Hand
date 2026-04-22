import base64
import time
from typing import List

import numpy as np
import glob
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from config import API_DIR
from models.schemas import (
    PredictRequest,
    PredictResponse,
    TopKItem,
    WebcamFrameRequest,
    WebcamSequenceRequest,
)
from services import multi_inference

router = APIRouter()

@router.get("/api/v1/models")
async def list_models():
    """List all available multi-models loaded in the system."""
    return {
        "models": list(multi_inference.models_registry.keys())
    }

@router.get("/api/v1/models/{model_name}/classes")
async def list_classes(model_name: str):
    """List all training classes available in a loaded multi-model."""
    if model_name not in multi_inference.models_registry:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    classes = multi_inference.get_classes(model_name)
    return {"classes": classes}

@router.get("/api/v1/models/{model_name}/classes/{class_name}/video")
async def get_class_video(model_name: str, class_name: str):
    """Return a raw .mp4 sample video for the specified class from the dataset."""
    if model_name not in multi_inference.models_registry:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")

    # The dataset directory uses hyphens instead of underscores (e.g. ssl-alphabet vs ssl_alphabet)
    dataset_model = model_name.replace("_", "-")
    # Base dataset dir is at the root of the project (one level above API_DIR)
    dataset_dir = API_DIR.parent / "dataset" / dataset_model / class_name

    if not dataset_dir.exists() or not dataset_dir.is_dir():
        raise HTTPException(status_code=404, detail="No video dataset found for this class")

    # Find the first mp4 video in the folder
    videos = list(dataset_dir.glob("*.mp4"))
    if not videos:
        raise HTTPException(status_code=404, detail="No MP4 video found in the dataset for this class")

    return FileResponse(path=videos[0], media_type="video/mp4")

@router.post("/api/v1/models/{model_name}/predict", response_model=PredictResponse)
async def predict_multi(model_name: str, req: PredictRequest) -> PredictResponse:
    if model_name not in multi_inference.models_registry:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        
    try:
        seqs = np.array(req.sequences, dtype="float32")
        predicted_label, topk_items = multi_inference.predict_topk_from_sequences(
            model_name, seqs, req.topk
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
        seq_len=multi_inference.models_registry[model_name].seq_len,
        num_sequences=int(seqs.shape[0]),
    )

@router.post("/api/v1/models/{model_name}/webcam-frame")
async def webcam_frame_multi(model_name: str, req: WebcamFrameRequest) -> dict:
    if model_name not in multi_inference.models_registry:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        
    ctx = multi_inference.models_registry[model_name]
    
    if multi_inference.landmark_extractor is None:
        raise HTTPException(status_code=503, detail="Landmark extractor not initialized")

    landmarks = multi_inference.landmark_extractor.extract(req.image, mirror=req.mirror)
    if landmarks is None:
        return {
            "status": "error",
            "message": "No hand detected",
            "frames": len(ctx.frame_buffer),
            "landmarks": [],
        }

    frame_vec = multi_inference.landmarks_to_frame_vec(landmarks, ctx.max_num_hands)
    ctx.frame_buffer.append(frame_vec.tolist())
    frames = len(ctx.frame_buffer)

    if frames < ctx.seq_len:
        return {
            "status": "buffering",
            "frames": frames,
            "landmarks": landmarks,
        }

    seq = np.array(ctx.frame_buffer, dtype="float32")
    seq = seq[-ctx.seq_len :]

    flat_seq = seq.reshape(-1, seq.shape[-1])
    flat_s = ctx.scaler.transform(flat_seq)
    seq_s = flat_s.reshape(1, ctx.seq_len, seq.shape[-1])

    probs = ctx.model.predict(seq_s, verbose=0)[0]
    top_idx = int(np.argmax(probs))
    confidence = float(probs[top_idx])
    label = str(ctx.label_encoder.inverse_transform([top_idx])[0])

    return {
        "status": "prediction",
        "label": label,
        "confidence": confidence,
        "frames": frames,
        "landmarks": landmarks,
    }

@router.post("/api/v1/models/{model_name}/webcam-sequence", response_model=PredictResponse)
async def webcam_sequence_multi(model_name: str, req: WebcamSequenceRequest) -> PredictResponse:
    if model_name not in multi_inference.models_registry:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        
    ctx = multi_inference.models_registry[model_name]

    if multi_inference.landmark_extractor is None:
        raise HTTPException(status_code=503, detail="Landmark extractor not initialized")
    if not req.frames:
        raise HTTPException(status_code=400, detail="frames must not be empty")

    # debug_dir = API_DIR / "debug_frames" / f"seq_{model_name}_{int(time.time())}"
    # debug_dir.mkdir(parents=True, exist_ok=True)

    frame_vecs: List[np.ndarray] = []
    for i, frame_str in enumerate(req.frames):
        # try:
        #     encoded = frame_str.split(",", 1)[1] if "," in frame_str else frame_str
        #     with open(debug_dir / f"frame_{i:03d}.jpg", "wb") as f:
        #         f.write(base64.b64decode(encoded))
        # except Exception as e:
        #     print(f"Failed to save debug frame: {e}")

        lms = multi_inference.landmark_extractor.extract(frame_str, mirror=req.mirror)
        vec = multi_inference.landmarks_to_frame_vec(lms or [], ctx.max_num_hands)
        frame_vecs.append(vec)

    seq = multi_inference.frames_to_sequence(frame_vecs, ctx.seq_len)

    try:
        predicted_label, topk_items = multi_inference.predict_topk_from_sequences(model_name, seq, 5)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    topk_models = [TopKItem(label=lbl, prob=prob) for lbl, prob in topk_items]

    return PredictResponse(
        predicted_label=predicted_label,
        topk=topk_models,
        seq_len=ctx.seq_len,
        num_sequences=1,
    )

@router.post("/api/v1/models/{model_name}/webcam-reset")
async def webcam_reset_multi(model_name: str) -> dict:
    if model_name not in multi_inference.models_registry:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        
    multi_inference.models_registry[model_name].frame_buffer.clear()
    return {"status": "reset", "frames": 0}
