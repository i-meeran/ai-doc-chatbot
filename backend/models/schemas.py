from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Upload Response ─────────────────────────────────────────
class UploadResponse(BaseModel):
    success: bool
    file_id: str
    filename: str
    file_type: str
    chunks_created: int
    message: str


class UploadError(BaseModel):
    success: bool = False
    error: str
    filename: str


# ── Chat Request / Response ─────────────────────────────────
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    file_ids: Optional[list[str]] = Field(
        default=None,
        description="Specific file IDs to search. If None, searches all files."
    )
    top_k: int = Field(default=5, ge=1, le=20)


class SourceChunk(BaseModel):
    file_id: str
    filename: str
    file_type: str
    page: Optional[int] = None
    content_preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    question: str
    model_used: str
    tokens_used: Optional[int] = None


# ── File Info ───────────────────────────────────────────────
class FileInfo(BaseModel):
    file_id: str
    filename: str
    file_type: str
    size_bytes: int
    chunks: int
    uploaded_at: datetime
    status: str  # "ready" | "processing" | "error"


class FilesListResponse(BaseModel):
    files: list[FileInfo]
    total: int


# ── Delete Response ─────────────────────────────────────────
class DeleteResponse(BaseModel):
    success: bool
    file_id: str
    message: str


# ── Health Check ────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    version: str
    groq_connected: bool
    faiss_index_size: int
    total_files: int
