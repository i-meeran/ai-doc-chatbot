from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional
 
 
class Settings(BaseSettings):
    # Gemini API Keys — add multiple for rotation
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    gemini_api_key_2: Optional[str] = Field(None, env="GEMINI_API_KEY_2")
    gemini_api_key_3: Optional[str] = Field(None, env="GEMINI_API_KEY_3")
    gemini_model: str = Field("gemini-2.5-flash", env="GEMINI_MODEL")
 
    # Embeddings (local HuggingFace)
    embedding_model: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL"
    )
 
    # Storage paths
    faiss_index_path: str = Field("./storage/faiss_index", env="FAISS_INDEX_PATH")
    upload_dir: str = Field("./storage/uploads", env="UPLOAD_DIR")
 
    # File constraints
    max_file_size_mb: int = Field(50, env="MAX_FILE_SIZE_MB")
 
    # Chunking
    chunk_size: int = Field(500, env="CHUNK_SIZE")
    chunk_overlap: int = Field(50, env="CHUNK_OVERLAP")
 
    # Server
    app_host: str = Field("0.0.0.0", env="APP_HOST")
    app_port: int = Field(8000, env="APP_PORT")
    debug: bool = Field(True, env="DEBUG")
    cors_origins: str = Field("http://localhost:3000", env="CORS_ORIGINS")
 
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]
 
    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024
 
    def create_dirs(self):
        Path(self.faiss_index_path).mkdir(parents=True, exist_ok=True)
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
 
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
 
 
settings = Settings()
settings.create_dirs()