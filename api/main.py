import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import classes, health, pages, predict, multi_predict, auth, community, chat, rag
from services import inference, multi_inference, rag_service
from database import init_db


app = FastAPI(title="SSL Alphabet LSTM API", version="1.0.0")
logger = logging.getLogger("uvicorn.error")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    """Load ML artifacts and initialize helpers."""
    inference.load_artifacts()
    multi_inference.load_all_models()
    await init_db()
    
    # We load RAG in the background or await it 
    # Warning: Embedding a PDF on startup natively blocks slightly but secures memory
    import asyncio
    asyncio.create_task(rag_service.init_rag())


app.include_router(health.router)
app.include_router(classes.router)
app.include_router(predict.router)
app.include_router(multi_predict.router)
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(community.router)
app.include_router(chat.router)
app.include_router(rag.router)

