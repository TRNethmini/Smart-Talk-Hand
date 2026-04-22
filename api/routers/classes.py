from fastapi import APIRouter, HTTPException

from services import inference


router = APIRouter()


@router.get("/api/v1/classes")
async def get_classes() -> dict:
    """Return the list of class labels known to the model."""
    try:
        classes = inference.get_classes()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"classes": classes}

