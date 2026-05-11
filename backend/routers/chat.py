"""
Chat Router
POST /api/chat  — ask a question over uploaded documents
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from services.vector_store import vector_store_service
from services.llm import llm_service
from models.schemas import ChatRequest, ChatResponse, SourceChunk

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask a question. Retrieves relevant chunks from FAISS,
    then sends them to Groq LLM for a context-aware answer.
    """
    logger.info(f"Chat request: '{request.question[:80]}...'")

    # ── Guard: index must have documents ────────────────────
    if vector_store_service.get_index_size() == 0:
        raise HTTPException(
            status_code=400,
            detail="No documents have been uploaded yet. Please upload files first."
        )

    # ── Validate requested file IDs ──────────────────────────
    if request.file_ids:
        for fid in request.file_ids:
            if not vector_store_service.file_exists(fid):
                raise HTTPException(
                    status_code=404,
                    detail=f"File ID '{fid}' not found."
                )

    # ── Semantic search ──────────────────────────────────────
    relevant_docs = vector_store_service.search(
        query=request.question,
        top_k=request.top_k,
        file_ids=request.file_ids,
    )

    if not relevant_docs:
        return ChatResponse(
            answer="I couldn't find relevant content in the uploaded documents for your question.",
            sources=[],
            question=request.question,
            model_used=llm_service.model,
        )

    # ── Generate answer via Groq ─────────────────────────────
    llm_result = llm_service.generate_answer(
        question=request.question,
        context_docs=relevant_docs,
    )

    # ── Build source references ──────────────────────────────
    seen = set()
    sources = []
    for doc in relevant_docs:
        meta = doc.metadata
        key = (meta.get("file_id"), meta.get("chunk_index"))
        if key in seen:
            continue
        seen.add(key)
        sources.append(SourceChunk(
            file_id=meta.get("file_id", ""),
            filename=meta.get("filename", "unknown"),
            file_type=meta.get("file_type", ""),
            page=meta.get("page_count"),
            content_preview=doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
        ))

    return ChatResponse(
        answer=llm_result["answer"],
        sources=sources,
        question=request.question,
        model_used=llm_result["model"],
        tokens_used=llm_result["tokens_used"],
    )
