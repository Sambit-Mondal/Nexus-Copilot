"""Ingestion Worker Configuration"""
import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Service configuration from environment variables"""
    
    model_config = ConfigDict(env_file=".env", case_sensitive=False)
    
    # gRPC Server
    grpc_host: str = "127.0.0.1"
    grpc_port: int = 50051
    
    # Pinecone
    pinecone_api_key: str = ""
    pinecone_index_name: str = "nexus-documents"
    pinecone_region: str = "us-east-1"
    
    # Embeddings
    embedding_model: str = "tfidf"
    embedding_batch_size: int = 32
    
    # Document Processing
    chunk_size: int = 500
    chunk_overlap: int = 50
    batch_size: int = 100
    
    # Storage
    temp_dir: str = "/tmp/nexus-ingestion"
    s3_bucket: str = ""
    s3_region: str = "us-east-1"
    
    # Logging
    log_level: str = "INFO"


settings = Settings()
