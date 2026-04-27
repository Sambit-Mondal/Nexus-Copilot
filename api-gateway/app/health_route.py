"""
Health check endpoint for system diagnostics.
Verifies all dependencies are available and healthy.
"""

from fastapi import APIRouter, HTTPException
from app.models import HealthResponse
from app.config import settings
from app.logger import get_logger
from app.embedding import get_embedding_service
from app.cache import get_semantic_cache
from app.retriever import get_pinecone_retriever
from app.grpc_client import get_grpc_client
from app.rag_pipeline import get_rag_pipeline
import asyncio

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health Check Endpoint - Verifies all system dependencies.

    Checks:
    - Redis cache connectivity
    - gRPC worker connectivity
    - Pinecone index accessibility
    - Embedding model availability

    Returns:
        HealthResponse with status of each component

    Raises:
        HTTPException: If critical dependency fails
    """
    try:
        logger.info("Health check initiated")

        # Check Redis
        redis_status = "connected"
        try:
            cache = get_semantic_cache()
            if not cache.health_check():
                redis_status = "error"
        except Exception as e:
            logger.warning(f"Redis health check failed: {str(e)}")
            redis_status = "disconnected"

        # Check gRPC
        grpc_status = "ready"
        try:
            grpc_client = get_grpc_client()
            if not await grpc_client.health_check():
                grpc_status = "error"
        except Exception as e:
            logger.warning(f"gRPC health check failed: {str(e)}")
            grpc_status = "disconnected"

        # Check Pinecone
        pinecone_status = "connected"
        try:
            retriever = get_pinecone_retriever()
            if not retriever.health_check():
                pinecone_status = "error"
        except Exception as e:
            logger.warning(f"Pinecone health check failed: {str(e)}")
            pinecone_status = "disconnected"

        # Check Embedding Model
        embedding_status = "ready"
        try:
            embedding = get_embedding_service()
            # Model is already loaded in __init__, so if we got here, it's ready
        except Exception as e:
            logger.warning(f"Embedding model health check failed: {str(e)}")
            embedding_status = "error"

        # Determine overall status
        overall_status = "healthy"
        if redis_status != "connected" or grpc_status != "ready" or pinecone_status != "connected":
            overall_status = "degraded"

        if redis_status == "disconnected" and pinecone_status == "disconnected":
            overall_status = "unhealthy"

        logger.info(
            f"Health check complete: {overall_status} "
            f"(Redis: {redis_status}, gRPC: {grpc_status}, "
            f"Pinecone: {pinecone_status}, Embedding: {embedding_status})"
        )

        return HealthResponse(
            status=overall_status,
            redis=redis_status,
            grpc=grpc_status,
            pinecone=pinecone_status,
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={"error": "Service unavailable", "code": "SERVICE_UNAVAILABLE"},
        )


@router.get("/api/v1/health", response_model=HealthResponse, tags=["System"])
async def api_health_check():
    """Alias for /health endpoint (API v1 version)."""
    return await health_check()


@router.options("/health", tags=["System"])
async def health_options():
    """Handle CORS preflight for health endpoint."""
    return {}
