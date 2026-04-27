"""
Custom exception classes for the FastAPI Gateway.
"""

from fastapi import HTTPException
from typing import Any, Optional


class NexusException(Exception):
    """Base exception class for all Nexus errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary response."""
        return {
            "error": self.message,
            "code": self.code,
            "status_code": self.status_code,
        }


class InvalidFileError(NexusException):
    """Raised when uploaded file is invalid."""

    def __init__(self, message: str = "Invalid file format"):
        super().__init__(message, code="INVALID_FILE", status_code=400)


class UploadError(NexusException):
    """Raised when file upload fails."""

    def __init__(self, message: str = "File upload failed"):
        super().__init__(message, code="UPLOAD_ERROR", status_code=500)


class GRPCConnectionError(NexusException):
    """Raised when gRPC connection fails."""

    def __init__(self, message: str = "Failed to connect to ingestion worker"):
        super().__init__(message, code="GRPC_CONNECTION_ERROR", status_code=503)


class GRPCProcessingError(NexusException):
    """Raised when gRPC processing fails."""

    def __init__(self, message: str = "Document processing failed"):
        super().__init__(message, code="GRPC_PROCESSING_ERROR", status_code=500)


class EmbeddingError(NexusException):
    """Raised when embedding generation fails."""

    def __init__(self, message: str = "Failed to generate embedding"):
        super().__init__(message, code="EMBEDDING_ERROR", status_code=500)


class CacheError(NexusException):
    """Raised when Redis cache operation fails."""

    def __init__(self, message: str = "Redis cache operation failed"):
        super().__init__(message, code="CACHE_ERROR", status_code=500)


class RetrieverError(NexusException):
    """Raised when Pinecone retrieval fails."""

    def __init__(self, message: str = "Failed to retrieve documents from vector DB"):
        super().__init__(message, code="RETRIEVER_ERROR", status_code=500)


class LLMError(NexusException):
    """Raised when LLM generation fails."""

    def __init__(self, message: str = "LLM generation failed"):
        super().__init__(message, code="LLM_ERROR", status_code=500)


class QueryValidationError(NexusException):
    """Raised when query validation fails."""

    def __init__(self, message: str = "Invalid query"):
        super().__init__(message, code="QUERY_VALIDATION_ERROR", status_code=400)


def nexus_exception_handler(exc: NexusException) -> dict:
    """Convert NexusException to HTTP response."""
    return {
        "error": exc.message,
        "code": exc.code,
    }
