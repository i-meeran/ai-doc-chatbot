"""
Vector Store Service
Handles: text chunking, HuggingFace embeddings, FAISS indexing & search
"""

import os
import json
import pickle
import uuid
from pathlib import Path
from typing import Optional
from loguru import logger

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

from config import settings


class VectorStoreService:
    def __init__(self):
        self.embeddings = None
        self.vector_store: Optional[FAISS] = None
        self.file_registry: dict = {}  # file_id -> file metadata
        self.registry_path = Path(settings.faiss_index_path) / "registry.json"
        self.index_path = Path(settings.faiss_index_path)

        self._load_embeddings()
        self._load_index()

    # ── Init ─────────────────────────────────────────────────
    def _load_embeddings(self):
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("Embeddings model loaded")

    def _load_index(self):
        """Load existing FAISS index from disk if available."""
        index_file = self.index_path / "index.faiss"
        if index_file.exists():
            try:
                self.vector_store = FAISS.load_local(
                    str(self.index_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
                logger.info("Loaded existing FAISS index from disk")
            except Exception as e:
                logger.warning(f"Could not load FAISS index: {e}. Starting fresh.")

        if self.registry_path.exists():
            with open(self.registry_path, "r") as f:
                self.file_registry = json.load(f)
            logger.info(f"Loaded file registry: {len(self.file_registry)} files")

    def _save_index(self):
        """Persist FAISS index and registry to disk."""
        if self.vector_store:
            self.vector_store.save_local(str(self.index_path))
        with open(self.registry_path, "w") as f:
            json.dump(self.file_registry, f, indent=2, default=str)

    # ── Ingest ───────────────────────────────────────────────
    def ingest_document(
        self,
        text: str,
        filename: str,
        file_type: str,
        metadata: dict,
        file_id: Optional[str] = None,
    ) -> dict:
        """
        Chunk text, embed it, and store in FAISS.
        Returns: { file_id, chunk_count }
        """
        if not text.strip():
            raise ValueError("No text content extracted from file.")

        file_id = file_id or str(uuid.uuid4())

        # Smart chunking — respects paragraphs, sentences, words
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_text(text)
        logger.info(f"Split '{filename}' into {len(chunks)} chunks")

        # Build LangChain Document objects with rich metadata
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "file_id": file_id,
                    "filename": filename,
                    "file_type": file_type,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    **metadata,
                },
            )
            documents.append(doc)

        # Add to FAISS (create or merge)
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vector_store.add_documents(documents)

        # Register file
        self.file_registry[file_id] = {
            "file_id": file_id,
            "filename": filename,
            "file_type": file_type,
            "chunks": len(chunks),
            "metadata": metadata,
        }

        self._save_index()
        logger.info(f"Ingested '{filename}' with {len(chunks)} chunks (id: {file_id})")
        return {"file_id": file_id, "chunk_count": len(chunks)}

    # ── Search ───────────────────────────────────────────────
    def search(
        self,
        query: str,
        top_k: int = 5,
        file_ids: Optional[list[str]] = None,
    ) -> list[Document]:
        """
        Semantic search over FAISS index.
        Optionally filter by specific file_ids.
        """
        if self.vector_store is None:
            return []

        # Fetch more results if filtering, to ensure top_k after filter
        fetch_k = top_k * 4 if file_ids else top_k

        results = self.vector_store.similarity_search(query, k=fetch_k)

        if file_ids:
            results = [r for r in results if r.metadata.get("file_id") in file_ids]

        return results[:top_k]

    # ── Delete ───────────────────────────────────────────────
    def delete_file(self, file_id: str) -> bool:
        """Remove all chunks for a file from the index."""
        if file_id not in self.file_registry:
            return False

        # FAISS doesn't support partial deletion — rebuild without that file
        if self.vector_store:
            all_docs = []
            docstore = self.vector_store.docstore._dict
            index_to_id = self.vector_store.index_to_docstore_id

            for idx, doc_id in index_to_id.items():
                doc = docstore.get(doc_id)
                if doc and doc.metadata.get("file_id") != file_id:
                    all_docs.append(doc)

            if all_docs:
                self.vector_store = FAISS.from_documents(all_docs, self.embeddings)
            else:
                self.vector_store = None

        del self.file_registry[file_id]
        self._save_index()
        logger.info(f"Deleted file {file_id} from vector store")
        return True

    # ── Helpers ──────────────────────────────────────────────
    def get_index_size(self) -> int:
        if self.vector_store is None:
            return 0
        return self.vector_store.index.ntotal

    def get_all_files(self) -> list[dict]:
        return list(self.file_registry.values())

    def file_exists(self, file_id: str) -> bool:
        return file_id in self.file_registry


# Singleton instance shared across the app
vector_store_service = VectorStoreService()
