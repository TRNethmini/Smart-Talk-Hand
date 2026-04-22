from fastapi import APIRouter

from services import inference


router = APIRouter()


@router.get("/")
async def root() -> dict:
    return {
        "message": "SSL Alphabet LSTM API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


@router.get("/api/v1/health")
async def health() -> dict:
    """Simple health check endpoint."""
    # Touch inference module so startup errors surface early if needed
    _ = inference.SEQ_LEN
    return {"status": "ok"}

