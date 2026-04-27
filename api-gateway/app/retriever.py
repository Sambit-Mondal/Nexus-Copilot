"""
Pinecone vector database retrieval service.
Handles similarity search and chunk retrieval from the vector index.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from pinecone import Pinecone
from app.config import settings
from app.logger import get_logger
from app.exceptions import RetrieverError

logger = get_logger(__name__)


class Chunk:
    """Represents a retrieved document chunk."""

    def __init__(
        self,
        text: str,
        source: str,
        page: Optional[int] = None,
        score: float = 0.0,
        chunk_id: Optional[str] = None,
    ):
        self.text = text
        self.source = source
        self.page = page
        self.score = score
        self.chunk_id = chunk_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary."""
        return {
            "text": self.text,
            "source": self.source,
            "page": self.page,
            "score": self.score,
            "chunk_id": self.chunk_id,
        }


class PineconeRetriever:
    """Service for retrieving documents from Pinecone vector database."""

    def __init__(self):
        """Initialize Pinecone client and index."""
        try:
            if not settings.pinecone_api_key:
                raise ValueError("PINECONE_API_KEY not set")

            logger.info(
                f"Initializing Pinecone (index: {settings.pinecone_index_name})"
            )

            # Initialize Pinecone client
            self.pc = Pinecone(api_key=settings.pinecone_api_key)

            # Get index
            self.index = self.pc.Index(settings.pinecone_index_name)

            # Verify index is accessible
            index_stats = self.index.describe_index_stats()
            logger.info(
                f"Pinecone index connected: {index_stats.total_vector_count} vectors"
            )

            self.top_k = settings.top_k_retrieval

        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise RetrieverError(f"Pinecone initialization failed: {str(e)}")

    def retrieve(self, query_embedding: np.ndarray, top_k: Optional[int] = None) -> List[Chunk]:
        """
        Retrieve top-k most similar chunks from Pinecone.

        Args:
            query_embedding: Query embedding (numpy array)
            top_k: Number of results to retrieve (defaults to settings.top_k_retrieval)

        Returns:
            List of Chunk objects sorted by relevance

        Raises:
            RetrieverError: If retrieval fails
        """
        try:
            if top_k is None:
                top_k = self.top_k

            # Convert numpy array to list
            query_vector = query_embedding.tolist()

            # Query Pinecone
            logger.debug(f"Querying Pinecone with top_k={top_k}")
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                include_values=False,
            )

            # Parse results into Chunk objects
            chunks = []
            for match in results.matches:
                metadata = match.metadata or {}

                chunk = Chunk(
                    text=metadata.get("text", ""),
                    source=metadata.get("source", "unknown"),
                    page=metadata.get("page", None),
                    score=float(match.score),
                    chunk_id=match.id,
                )

                chunks.append(chunk)

            logger.info(f"Retrieved {len(chunks)} chunks from Pinecone")
            return chunks

        except Exception as e:
            logger.error(f"Pinecone retrieval failed: {str(e)}")
            raise RetrieverError(f"Failed to retrieve chunks: {str(e)}")

    def retrieve_with_filter(
        self,
        query_embedding: np.ndarray,
        filter_dict: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None,
    ) -> List[Chunk]:
        """
        Retrieve chunks with optional metadata filtering.

        Args:
            query_embedding: Query embedding
            filter_dict: Metadata filter (e.g., {"source": "Q3-Report.pdf"})
            top_k: Number of results

        Returns:
            List of Chunk objects

        Raises:
            RetrieverError: If retrieval fails
        """
        try:
            if top_k is None:
                top_k = self.top_k

            query_vector = query_embedding.tolist()

            logger.debug(f"Querying Pinecone with filter: {filter_dict}")
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict,
            )

            chunks = []
            for match in results.matches:
                metadata = match.metadata or {}
                chunk = Chunk(
                    text=metadata.get("text", ""),
                    source=metadata.get("source", "unknown"),
                    page=metadata.get("page", None),
                    score=float(match.score),
                    chunk_id=match.id,
                )
                chunks.append(chunk)

            logger.info(f"Retrieved {len(chunks)} filtered chunks from Pinecone")
            return chunks

        except Exception as e:
            logger.error(f"Filtered retrieval failed: {str(e)}")
            raise RetrieverError(f"Failed to retrieve filtered chunks: {str(e)}")

    def health_check(self) -> bool:
        """Check if Pinecone is healthy."""
        try:
            self.index.describe_index_stats()
            return True
        except Exception as e:
            logger.error(f"Pinecone health check failed: {str(e)}")
            return False


# Global retriever instance
_pinecone_retriever: PineconeRetriever = None


def get_pinecone_retriever() -> PineconeRetriever:
    """
    Get or create the global Pinecone retriever instance.

    Returns:
        PineconeRetriever instance (singleton)
    """
    global _pinecone_retriever
    if _pinecone_retriever is None:
        _pinecone_retriever = PineconeRetriever()
    return _pinecone_retriever
