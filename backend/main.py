"""
Universal Document AI Chatbot — Backend
FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from config import settings
from routers import upload, chat
from services.vector_store import vector_store_service
from services.llm import llm_service
from models.schemas import HealthResponse


# ── App Setup ────────────────────────────────────────────────
app = FastAPI(
    title="Universal Document AI Chatbot",
    description="Chat with any file type using RAG — PDF, DOCX, XLSX, PPTX, CSV, TXT, images & more",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────
app.include_router(upload.router)
app.include_router(chat.router)


# ── Health Check ─────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check():
    return HealthResponse(
        status="ok",
        version="1.0.0",
        groq_connected=llm_service.is_connected(),
        faiss_index_size=vector_store_service.get_index_size(),
        total_files=len(vector_store_service.get_all_files()),
    )


@app.get("/", tags=["system"])
async def root():
    return {
        "message": "Universal Document AI Chatbot API",
        "docs": "/docs",
        "health": "/health",
    }


# ── Startup ──────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("Starting Universal Document AI Chatbot API...")
    logger.info(f"FAISS index size: {vector_store_service.get_index_size()} vectors")
    logger.info(f"Files indexed: {len(vector_store_service.get_all_files())}")
    logger.info("API ready!")


# ── Run ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level="info",
    )
