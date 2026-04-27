"""
Configuration module for FastAPI Gateway.
Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # FastAPI Configuration
    app_name: str = "Nexus FastAPI Gateway"
    debug: bool = False
    log_level: str = "INFO"

    # gRPC Configuration
    grpc_host: str = "localhost"
    grpc_port: int = 50051
    grpc_timeout: int = 30

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_url: str = ""
    redis_cache_ttl: int = 604800  # 7 days in seconds

    # Pinecone Configuration
    pinecone_api_key: str = ""
    pinecone_index_name: str = "nexus-copilot"

    # Groq Configuration
    groq_api_key: str = ""
    groq_model: str = "mixtral-8x7b-32768"
    groq_temperature: float = 0.7

    # Embedding Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # Cache Configuration
    similarity_threshold: float = 0.95
    top_k_retrieval: int = 5

    # File Upload Configuration
    upload_directory: str = "./data/uploads"
    max_upload_size: int = 104857600  # 100MB in bytes
    allowed_file_types: list[str] = ["pdf", "docx", "txt"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        json_schema_extra = {
            "allowed_file_types": '["pdf","docx","txt"]'
        }

    @property
    def grpc_url(self) -> str:
        """Construct gRPC service URL."""
        return f"{self.grpc_host}:{self.grpc_port}"

    @property
    def redis_connection_url(self) -> str:
        """Construct Redis connection URL."""
        if self.redis_url:
            return self.redis_url
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def ensure_upload_directory(self) -> Path:
        """Ensure upload directory exists and return Path object."""
        upload_path = Path(self.upload_directory)
        upload_path.mkdir(parents=True, exist_ok=True)
        return upload_path


# Create global settings instance
settings = Settings()
