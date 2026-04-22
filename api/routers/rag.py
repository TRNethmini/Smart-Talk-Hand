from fastapi import APIRouter
from pydantic import BaseModel
from services.rag_service import get_feedback

router = APIRouter()

class RAGFeedbackRequest(BaseModel):
    expected: str
    predicted: str

class RAGFeedbackResponse(BaseModel):
    feedback: str

@router.post("/api/v1/rag/feedback", response_model=RAGFeedbackResponse)
async def fetch_llm_feedback(req: RAGFeedbackRequest):
    # Offload the FAISS search and Ollama inference to the async loop
    correction = await get_feedback(
        expected_sign=req.expected,
        predicted_sign=req.predicted
    )
    return RAGFeedbackResponse(feedback=correction)
