from typing import List

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Request body for /api/v1/predict.

    sequences: list of sequences, each of shape (SEQ_LEN, N_FEATS)
    """

    sequences: List[List[List[float]]] = Field(
        ..., description="List of sequences [num_seq][SEQ_LEN][N_FEATS]"
    )
    topk: int = Field(
        5,
        ge=1,
        description="Number of top probabilities to return",
    )


class TopKItem(BaseModel):
    label: str
    prob: float


class PredictResponse(BaseModel):
    predicted_label: str
    topk: List[TopKItem]
    seq_len: int
    num_sequences: int


class WebcamFrameRequest(BaseModel):
    """Request body for /api/v1/webcam-frame.

    image: base64-encoded image (data URL or raw base64 string).
    """

    image: str
    mirror: bool = False


class WebcamSequenceRequest(BaseModel):
    """Request body for /api/v1/webcam-sequence.

    frames: list of base64-encoded image strings (data URLs or raw base64).
    """

    frames: List[str]
    mirror: bool = False

