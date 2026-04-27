"""
RAG Pipeline orchestrator.
Coordinates the entire query-to-response workflow.
"""

from typing import AsyncGenerator, Dict, Any, Optional, List
from app.embedding import get_embedding_service
from app.cache import get_semantic_cache
from app.retriever import get_pinecone_retriever
from app.llm import get_llm_service
from app.logger import get_logger
from app.exceptions import (
    EmbeddingError,
    RetrieverError,
    LLMError,
    QueryValidationError,
)

logger = get_logger(__name__)


class RAGPipeline:
    """Orchestrates the complete RAG (Retrieval-Augmented Generation) workflow."""

    def __init__(self):
        """Initialize RAG pipeline with all required services."""
        self.embedding_service = get_embedding_service()
        self.cache_service = get_semantic_cache()
        self.retriever = get_pinecone_retriever()
        self.llm_service = get_llm_service()

        logger.info("RAG pipeline initialized with all services")

    async def process_query(
        self,
        query: str,
        session_id: str,
        include_citations: bool = True,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a user query through the complete RAG pipeline.

        Flow:
        1. Validate query
        2. Generate embedding
        3. Check semantic cache (>0.95 similarity)
        4. If cache hit: return cached response
        5. If cache miss: retrieve from Pinecone
        6. Build prompt with context
        7. Stream LLM response
        8. Cache response for future queries
        9. Yield citations (optional)

        Args:
            query: User's question
            session_id: Session identifier
            include_citations: Whether to include source citations

        Yields:
            Response chunks and metadata as streaming JSON-like dicts

        Raises:
            QueryValidationError: If query is invalid
            EmbeddingError: If embedding generation fails
            RetrieverError: If retrieval fails
            LLMError: If LLM generation fails
        """
        try:
            # Step 1: Validate query
            if not query or not query.strip():
                raise QueryValidationError("Query cannot be empty")

            query = query.strip()
            logger.info(f"Processing query (session: {session_id}): {query[:100]}...")

            # Step 2: Generate query embedding
            logger.debug("Generating query embedding")
            query_embedding = self.embedding_service.embed_text(query)

            # Step 3: Check semantic cache
            logger.debug("Checking semantic cache")
            cached_response = self.cache_service.search_similar(query_embedding)

            if cached_response:
                logger.info(f"Cache hit for query (session: {session_id})")
                yield {
                    "type": "start",
                    "cached": True,
                    "session_id": session_id,
                }

                # Yield cached response in chunks
                for chunk in cached_response.split(" "):
                    yield {
                        "type": "chunk",
                        "content": chunk + " ",
                    }

                yield {
                    "type": "done",
                    "cached": True,
                }
                return

            # Cache miss - proceed with full RAG
            logger.info(f"Cache miss - performing full RAG (session: {session_id})")
            yield {
                "type": "start",
                "cached": False,
                "session_id": session_id,
            }

            # Step 4: Retrieve from Pinecone
            logger.debug("Retrieving context from Pinecone")
            chunks = self.retriever.retrieve(query_embedding)

            if not chunks:
                logger.warning(f"No context retrieved for query: {query}")
                yield {
                    "type": "chunk",
                    "content": "I don't have any relevant documents to answer this query. ",
                }
                yield {
                    "type": "done",
                    "cached": False,
                }
                return

            logger.info(f"Retrieved {len(chunks)} context chunks")

            # Step 5: Build prompt
            context = self.llm_service.format_context(chunks)
            prompt = self.llm_service.build_rag_prompt(context, query)

            # Step 6: Stream LLM response
            logger.debug("Starting LLM response streaming")
            full_response = ""

            async for token in self.llm_service.stream_response(prompt):
                yield {
                    "type": "chunk",
                    "content": token,
                }
                full_response += token

            # Step 7: Cache the response
            logger.debug("Caching response for future queries")
            try:
                self.cache_service.cache_response(
                    query=query,
                    embedding=query_embedding,
                    response=full_response,
                    metadata={
                        "session_id": session_id,
                        "num_chunks": len(chunks),
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to cache response: {str(e)}")
                # Don't fail the entire query for cache failures

            # Step 8: Yield citations if requested
            if include_citations:
                citations = self.llm_service.extract_citations(chunks)
                yield {
                    "type": "citations",
                    "sources": citations,
                }

            logger.info(f"Query processing completed (session: {session_id})")
            yield {
                "type": "done",
                "cached": False,
            }

        except QueryValidationError as e:
            logger.error(f"Query validation error: {str(e)}")
            yield {
                "type": "error",
                "error": str(e),
                "code": "QUERY_VALIDATION_ERROR",
            }
        except EmbeddingError as e:
            logger.error(f"Embedding error: {str(e)}")
            yield {
                "type": "error",
                "error": "Failed to process query embedding",
                "code": "EMBEDDING_ERROR",
            }
        except RetrieverError as e:
            logger.error(f"Retrieval error: {str(e)}")
            yield {
                "type": "error",
                "error": "Failed to retrieve context documents",
                "code": "RETRIEVAL_ERROR",
            }
        except LLMError as e:
            logger.error(f"LLM error: {str(e)}")
            yield {
                "type": "error",
                "error": "Failed to generate response",
                "code": "LLM_ERROR",
            }
        except Exception as e:
            logger.error(f"Unexpected error in RAG pipeline: {str(e)}")
            yield {
                "type": "error",
                "error": "An unexpected error occurred",
                "code": "INTERNAL_ERROR",
            }

    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get health status of all RAG pipeline components.

        Returns:
            Dictionary with status of each component
        """
        return {
            "embedding": "healthy",  # Already initialized in __init__
            "cache": self.cache_service.health_check(),
            "retriever": self.retriever.health_check(),
            "llm": "healthy",  # Already initialized in __init__
        }


# Global RAG pipeline instance
_rag_pipeline: RAGPipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """
    Get or create the global RAG pipeline instance.

    Returns:
        RAGPipeline instance (singleton)
    """
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
