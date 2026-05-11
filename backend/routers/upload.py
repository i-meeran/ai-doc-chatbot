"""
Upload Router
POST /api/upload       — upload one or multiple files
GET  /api/files        — list all uploaded files
DELETE /api/files/{id} — delete a file
"""

import uuid
import aiofiles
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from loguru import logger

from config import settings
from services.file_parser import parse_file, is_supported, get_file_type
from services.vector_store import vector_store_service
from models.schemas import (
    UploadResponse, UploadError, FilesListResponse, FileInfo, DeleteResponse
)

router = APIRouter(prefix="/api", tags=["files"])


@router.post("/upload", response_model=list[UploadResponse | UploadError])
async def upload_files(files: list[UploadFile] = File(...)):
    """
    Upload one or more files of any supported type.
    Returns per-file results so partial failures are visible.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    results = []

    for upload in files:
        filename = upload.filename or "unknown"
        logger.info(f"Received upload: {filename}")

        # ── Validation ──────────────────────────────────────
        if not is_supported(filename):
            results.append(UploadError(
                filename=filename,
                error=f"Unsupported file type '{get_file_type(filename)}'. "
                      f"Supported: pdf, docx, pptx, xlsx, csv, txt, md, json, xml, html, png, jpg, jpeg"
            ))
            continue

        file_bytes = await upload.read()

        if len(file_bytes) > settings.max_file_size_bytes:
            results.append(UploadError(
                filename=filename,
                error=f"File too large ({len(file_bytes) // 1024 // 1024}MB). Max is {settings.max_file_size_mb}MB."
            ))
            continue

        # ── Parse ────────────────────────────────────────────
        parsed = parse_file(file_bytes, filename)

        if parsed["error"]:
            results.append(UploadError(
                filename=filename,
                error=f"Parsing failed: {parsed['error']}"
            ))
            continue

        if not parsed["text"].strip():
            results.append(UploadError(
                filename=filename,
                error="No text could be extracted from this file."
            ))
            continue

        # ── Save file to disk ────────────────────────────────
        file_id = str(uuid.uuid4())
        save_path = Path(settings.upload_dir) / f"{file_id}_{filename}"
        async with aiofiles.open(save_path, "wb") as f:
            await f.write(file_bytes)

        # ── Ingest into vector store ─────────────────────────
        try:
            ingest_result = vector_store_service.ingest_document(
                text=parsed["text"],
                filename=filename,
                file_type=parsed["file_type"],
                metadata={
                    **parsed["metadata"],
                    "size_bytes": len(file_bytes),
                    "uploaded_at": datetime.utcnow().isoformat(),
                    "file_path": str(save_path),
                },
                file_id=file_id,
            )
        except Exception as e:
            logger.error(f"Ingestion failed for {filename}: {e}")
            results.append(UploadError(filename=filename, error=f"Indexing failed: {e}"))
            continue

        results.append(UploadResponse(
            success=True,
            file_id=file_id,
            filename=filename,
            file_type=parsed["file_type"],
            chunks_created=ingest_result["chunk_count"],
            message=f"Successfully processed '{filename}' into {ingest_result['chunk_count']} searchable chunks."
        ))

    return results


@router.get("/files", response_model=FilesListResponse)
async def list_files():
    """Return all uploaded and indexed files."""
    files_raw = vector_store_service.get_all_files()
    files = []
    for f in files_raw:
        meta = f.get("metadata", {})
        files.append(FileInfo(
            file_id=f["file_id"],
            filename=f["filename"],
            file_type=f["file_type"],
            size_bytes=meta.get("size_bytes", 0),
            chunks=f["chunks"],
            uploaded_at=datetime.fromisoformat(meta.get("uploaded_at", datetime.utcnow().isoformat())),
            status="ready",
        ))
    return FilesListResponse(files=files, total=len(files))


@router.delete("/files/{file_id}", response_model=DeleteResponse)
async def delete_file(file_id: str):
    """Delete a file and remove it from the vector index."""
    if not vector_store_service.file_exists(file_id):
        raise HTTPException(status_code=404, detail=f"File '{file_id}' not found.")

    # Remove physical file
    upload_dir = Path(settings.upload_dir)
    for path in upload_dir.glob(f"{file_id}_*"):
        path.unlink(missing_ok=True)

    success = vector_store_service.delete_file(file_id)
    return DeleteResponse(
        success=success,
        file_id=file_id,
        message="File deleted and removed from search index."
    )
