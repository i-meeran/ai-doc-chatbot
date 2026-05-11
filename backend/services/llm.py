"""
Gemini LLM Service with API Key Rotation
Automatically switches to next key when one expires/fails
"""

import google.generativeai as genai
from langchain.schema import Document
from loguru import logger
from config import settings


class LLMService:
    def __init__(self):
        # Add multiple API keys here — when one expires, it uses the next
        self.api_keys = [
            settings.gemini_api_key,           # Primary key from .env
            settings.gemini_api_key_2 or None, # Backup key 1
            settings.gemini_api_key_3 or None, # Backup key 2
        ]
        # Remove empty keys
        self.api_keys = [k for k in self.api_keys if k]
        self.current_key_index = 0
        self.model_name = "gemini-2.0-flash-lite"  # Best free limits
        self.model = None
        self._init_model()
        logger.info(f"LLM service initialized with {len(self.api_keys)} API key(s)")

    def _init_model(self):
        """Initialize model with current API key."""
        key = self.api_keys[self.current_key_index]
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"Using API key #{self.current_key_index + 1}")

    def _rotate_key(self):
        """Switch to next available API key."""
        self.current_key_index += 1
        if self.current_key_index >= len(self.api_keys):
            self.current_key_index = 0
            raise Exception("All API keys have been exhausted. Please add new keys to .env")
        logger.warning(f"Rotating to API key #{self.current_key_index + 1}")
        self._init_model()

    def generate_answer(self, question: str, context_docs: list[Document]) -> dict:
        if not context_docs:
            return {
                "answer": "I couldn't find relevant information in the uploaded documents.",
                "model": self.model_name,
                "tokens_used": 0,
            }

        # Build context
        context_parts = []
        for i, doc in enumerate(context_docs, start=1):
            fname = doc.metadata.get("filename", "unknown")
            context_parts.append(f"[Source {i} — {fname}]\n{doc.page_content}")
        context = "\n\n---\n\n".join(context_parts)

        prompt = f"""You are an expert document assistant. Answer ONLY from the context below.
If the answer is not in the context, say: "I don't have enough information in the uploaded documents."
Always mention which source/file you used.
Be concise but complete. Use bullet points when helpful.

Context:
{context}

Question: {question}

Answer:"""

        # Try with key rotation on failure
        max_attempts = len(self.api_keys)
        for attempt in range(max_attempts):
            try:
                logger.info(f"Sending query to Gemini (attempt {attempt + 1})")
                response = self.model.generate_content(prompt)
                return {
                    "answer": response.text,
                    "model": self.model_name,
                    "tokens_used": None,
                }
            except Exception as e:
                error_msg = str(e).lower()
                if any(word in error_msg for word in ["expired", "invalid", "quota", "exhausted", "resource_exhausted", "429"]):
                    logger.warning(f"API key #{self.current_key_index + 1} failed: {e}")
                    if self.current_key_index + 1 < len(self.api_keys):
                        try:
                            self._rotate_key()
                        except Exception as rotation_err:
                            raise Exception(str(rotation_err))
                    else:
                        raise Exception(
                            "All API keys have hit their quota. "
                            "Please wait until tomorrow or add new keys to .env"
                        )
                else:
                    raise e

        raise Exception("All API keys failed. Please renew your Gemini API keys.")

    def is_connected(self) -> bool:
        try:
            self.model.generate_content("ping")
            return True
        except Exception:
            return False


# Singleton instance
llm_service = LLMService()