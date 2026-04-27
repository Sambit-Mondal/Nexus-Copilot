"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid


class UploadRequest(BaseModel):
    """Request model for file upload endpoint."""

    client_id: str = Field(..., description="Client identifier")
    document_type: Optional[str] = Field(
        None, description="Document type (e.g., earnings_report, market_analysis)"
    )


class UploadResponse(BaseModel):
    """Response model for file upload endpoint."""

    upload_id: str = Field(..., description="Unique upload identifier")
    filename: str = Field(..., description="Original filename")
    size_bytes: int = Field(..., description="File size in bytes")
    status: str = Field(default="processing", description="Upload status")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "upload_id": "upload-550e8400-e29b-41d4-a716-446655440000",
                "filename": "Q3-2024-Report.pdf",
                "size_bytes": 5242880,
                "status": "processing",
                "created_at": "2026-04-27T06:46:05Z",
            }
        }


class UploadStatusResponse(BaseModel):
    """Response model for upload status endpoint."""

    upload_id: str
    status: str
    progress: Optional[dict] = Field(
        None,
        description="Progress information (current_step, chunks_processed, total_chunks, percent)",
    )
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "upload_id": "upload-550e8400-e29b-41d4-a716-446655440000",
                "status": "processing",
                "progress": {
                    "current_step": "embedding",
                    "chunks_processed": 45,
                    "total_chunks": 120,
                    "percent": 37.5,
                },
                "created_at": "2026-04-27T06:46:05Z",
                "updated_at": "2026-04-27T06:48:12Z",
            }
        }


class QueryRequest(BaseModel):
    """Request model for query endpoint."""

    query: str = Field(..., min_length=1, max_length=2000, description="User query")
    session_id: str = Field(..., description="Session identifier")
    include_citations: bool = Field(
        default=True, description="Include source citations in response"
    )

    @validator("query")
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the risk exposure in the tech sector?",
                "session_id": "session-550e8400-e29b-41d4-a716-446655440000",
                "include_citations": True,
            }
        }


class Citation(BaseModel):
    """Citation/source information."""

    document: str = Field(..., description="Document name/filename")
    page: Optional[int] = Field(None, description="Page number")
    score: Optional[float] = Field(None, description="Relevance score")


class QueryResponse(BaseModel):
    """Response model for query endpoint (streaming)."""

    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cached: bool = Field(default=False, description="Whether response was from cache")
    sources: Optional[List[Citation]] = Field(None, description="Source citations")

    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "query-550e8400-e29b-41d4-a716-446655440000",
                "cached": False,
                "sources": [
                    {"document": "Q3-2024-Report.pdf", "page": 12, "score": 0.95},
                    {"document": "Tech-Analysis-2024.pdf", "page": 5, "score": 0.91},
                ],
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Overall health status")
    redis: str = Field(..., description="Redis connection status")
    grpc: str = Field(..., description="gRPC worker connection status")
    pinecone: str = Field(..., description="Pinecone connection status")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "redis": "connected",
                "grpc": "ready",
                "pinecone": "connected",
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid file type. Accepted: PDF, DOCX, TXT",
                "code": "INVALID_FILE",
            }
        }
