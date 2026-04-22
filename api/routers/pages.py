from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from config import LETTERS_HTML_PATH, WEBCAM_HTML_PATH, MULTI_WEBCAM_HTML_PATH, MULTI_CLASSES_HTML_PATH


router = APIRouter()


@router.get("/api/webcam")
async def webcam_page() -> FileResponse:
    """Serve the webcam testing HTML page."""
    if not WEBCAM_HTML_PATH.exists():
        raise HTTPException(status_code=404, detail="webcam.html not found")
    return FileResponse(WEBCAM_HTML_PATH)


@router.get("/api/letters")
async def letters_page() -> FileResponse:
    """Serve the letter selection HTML page."""
    if not LETTERS_HTML_PATH.exists():
        raise HTTPException(status_code=404, detail="letters.html not found")
    return FileResponse(LETTERS_HTML_PATH)


@router.get("/api/multi-webcam")
async def multi_webcam_page() -> FileResponse:
    """Serve the multi-model webcam testing HTML page."""
    if not MULTI_WEBCAM_HTML_PATH.exists():
        raise HTTPException(status_code=404, detail="multi_webcam.html not found")
    return FileResponse(MULTI_WEBCAM_HTML_PATH)


@router.get("/api/multi-classes")
async def multi_classes_page() -> FileResponse:
    """Serve the multi-model class selection HTML page."""
    if not MULTI_CLASSES_HTML_PATH.exists():
        raise HTTPException(status_code=404, detail="multi_classes.html not found")
    return FileResponse(MULTI_CLASSES_HTML_PATH)

