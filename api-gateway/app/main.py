"""
FastAPI Gateway - Main entry point for the Nexus API.
Coordinates uploads, queries, caching, and RAG-based response generation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.logger import get_logger
from app.exceptions import NexusException
from app.health_route import router as health_router
from app.query_route import router as query_router
from app.upload_route import router as upload_router

logger = get_logger(__name__, log_level=settings.log_level)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Distributed Enterprise RAG Copilot for Financial Advisory",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler for NexusException
@app.exception_handler(NexusException)
async def nexus_exception_handler(request, exc: NexusException):
    """Handle custom Nexus exceptions."""
    logger.error(f"Nexus exception: {exc.message} (code: {exc.code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "code": exc.code},
    )


# Include routers
app.include_router(health_router)
app.include_router(query_router)
app.include_router(upload_router)


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/api/v1/upload",
            "query": "/api/v1/query",
            "docs": "/docs",
        },
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on app startup."""
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app_name}")
    logger.info("=" * 60)
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"gRPC target: {settings.grpc_url}")
    logger.info(f"Redis: {settings.redis_host}:{settings.redis_port}")
    logger.info(f"Pinecone index: {settings.pinecone_index_name}")
    logger.info(f"LLM model: {settings.openai_model}")
    logger.info(f"Embedding model: {settings.embedding_model}")
    logger.info(f"Cache TTL: {settings.redis_cache_ttl}s")
    logger.info(f"Similarity threshold: {settings.similarity_threshold}")
    logger.info("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown."""
    logger.info("Shutting down FastAPI Gateway")
    try:
        from app.grpc_client import get_grpc_client

        grpc_client = get_grpc_client()
        await grpc_client.disconnect()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower(),
    )
