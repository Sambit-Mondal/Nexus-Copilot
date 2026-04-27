"""
Query endpoint for RAG-based Q&A.
Implements Server-Sent Events (SSE) streaming for token-by-token responses.
"""

import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.models import QueryRequest, ErrorResponse
from app.rag_pipeline import get_rag_pipeline
from app.logger import get_logger
from app.exceptions import NexusException

logger = get_logger(__name__)

router = APIRouter()


@router.post("/api/v1/query", tags=["RAG"])
async def query_endpoint(request: QueryRequest):
    """
    RAG Query Endpoint - Processes user queries with semantic caching and streaming.

    This endpoint:
    1. Generates an embedding for the query
    2. Checks Redis semantic cache (>0.95 similarity)
    3. If cache hit: returns cached response immediately (<10ms)
    4. If cache miss: retrieves context from Pinecone
    5. Streams LLM response token-by-token via Server-Sent Events
    6. Caches query and response for future hits

    Request:
    {
        "query": "What is the risk exposure in tech sector?",
        "session_id": "session-uuid-5678",
        "include_citations": true
    }

    Response (200 OK - SSE Stream):
    event: start
    data: {"cached": false, "session_id": "session-uuid-5678"}

    event: chunk
    data: "The risk exposure"

    event: chunk
    data: " in the tech sector"

    event: citations
    data: {"sources": [{"document": "Q3-2024-Report.pdf", "page": 12, "score": 0.95}]}

    event: done
    data: {}

    Args:
        request: QueryRequest with query, session_id, and include_citations

    Returns:
        StreamingResponse with SSE events

    Raises:
        HTTPException: If query processing fails
    """
    try:
        logger.info(
            f"Query endpoint called (session: {request.session_id}, query: {request.query[:100]}...)"
        )

        # Get RAG pipeline
        rag_pipeline = get_rag_pipeline()

        async def event_stream():
            """Generate SSE events from RAG pipeline."""
            try:
                async for response in rag_pipeline.process_query(
                    query=request.query,
                    session_id=request.session_id,
                    include_citations=request.include_citations,
                ):
                    response_type = response.get("type")

                    if response_type == "start":
                        # Send start event
                        yield f"event: start\n"
                        yield f'data: {json.dumps({"cached": response.get("cached"), "session_id": response.get("session_id")})}\n\n'

                    elif response_type == "chunk":
                        # Send content chunk
                        yield f"event: chunk\n"
                        yield f'data: {json.dumps(response.get("content"))}\n\n'

                    elif response_type == "citations":
                        # Send citations
                        yield f"event: citations\n"
                        yield f'data: {json.dumps({"sources": response.get("sources")})}\n\n'

                    elif response_type == "done":
                        # Send completion event
                        yield f"event: done\n"
                        yield f'data: {{}}\n\n'

                    elif response_type == "error":
                        # Send error event
                        yield f"event: error\n"
                        yield f'data: {json.dumps({"error": response.get("error"), "code": response.get("code")})}\n\n'
                        break

            except NexusException as e:
                logger.error(f"Nexus error in query stream: {str(e)}")
                yield f"event: error\n"
                yield f'data: {json.dumps({"error": e.message, "code": e.code})}\n\n'
            except Exception as e:
                logger.error(f"Unexpected error in query stream: {str(e)}")
                yield f"event: error\n"
                yield f'data: {json.dumps({"error": "Internal server error", "code": "INTERNAL_ERROR"})}\n\n'

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        logger.error(f"Query endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to process query", "code": "INTERNAL_ERROR"},
        )


@router.options("/api/v1/query", tags=["RAG"])
async def query_options():
    """Handle CORS preflight for query endpoint."""
    return {}
