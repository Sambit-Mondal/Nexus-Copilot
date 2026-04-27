"""
Embedding service for query/document vectorization.
Uses HuggingFace sentence-transformers for fast, accurate embeddings.
"""

import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.logger import get_logger
from app.exceptions import EmbeddingError

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating embeddings using HuggingFace models."""

    def __init__(self):
        """Initialize the embedding model."""
        try:
            logger.info(f"Loading embedding model: {settings.embedding_model_name}")
            self.model = SentenceTransformer(settings.embedding_model_name)
            self.dimension = settings.embedding_dimension
            logger.info(
                f"Embedding model loaded successfully (dimension: {self.dimension})"
            )
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise EmbeddingError(f"Failed to load embedding model: {str(e)}")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Numpy array of shape (384,)

        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")

            embedding = self.model.encode(text, convert_to_numpy=True)

            if embedding.shape[0] != self.dimension:
                raise ValueError(
                    f"Expected embedding dimension {self.dimension}, got {embedding.shape[0]}"
                )

            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise EmbeddingError(f"Failed to generate embedding: {str(e)}")

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts (batch).

        Args:
            texts: List of texts to embed

        Returns:
            Numpy array of shape (n, 384)

        Raises:
            EmbeddingError: If batch embedding generation fails
        """
        try:
            if not texts:
                raise ValueError("Text list cannot be empty")

            # Filter out empty texts
            texts = [t.strip() for t in texts if t and t.strip()]

            if not texts:
                raise ValueError("All texts are empty")

            embeddings = self.model.encode(texts, convert_to_numpy=True)

            if embeddings.shape[1] != self.dimension:
                raise ValueError(
                    f"Expected embedding dimension {self.dimension}, got {embeddings.shape[1]}"
                )

            return embeddings
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {str(e)}")
            raise EmbeddingError(f"Failed to generate batch embeddings: {str(e)}")

    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.

        Args:
            vec1: First vector (numpy array)
            vec2: Second vector (numpy array)

        Returns:
            Cosine similarity score between -1 and 1

        Raises:
            EmbeddingError: If vectors have incompatible dimensions
        """
        try:
            if vec1.shape != vec2.shape:
                raise ValueError(
                    f"Vector shape mismatch: {vec1.shape} vs {vec2.shape}"
                )

            # Normalize vectors
            vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-8)
            vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-8)

            # Compute cosine similarity
            similarity = float(np.dot(vec1_norm, vec2_norm))

            return similarity
        except Exception as e:
            logger.error(f"Cosine similarity computation failed: {str(e)}")
            raise EmbeddingError(f"Failed to compute cosine similarity: {str(e)}")

    @staticmethod
    def cosine_similarities(vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        """
        Compute cosine similarities between one vector and multiple vectors.

        Args:
            vec: Single vector (shape: (384,))
            matrix: Matrix of vectors (shape: (n, 384))

        Returns:
            Array of similarity scores (shape: (n,))

        Raises:
            EmbeddingError: If dimensions are incompatible
        """
        try:
            if vec.ndim != 1:
                raise ValueError(f"Expected 1D vector, got shape {vec.shape}")
            if matrix.ndim != 2:
                raise ValueError(f"Expected 2D matrix, got shape {matrix.shape}")

            # Normalize
            vec_norm = vec / (np.linalg.norm(vec) + 1e-8)
            matrix_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-8)

            # Compute similarities
            similarities = np.dot(matrix_norm, vec_norm)

            return similarities
        except Exception as e:
            logger.error(f"Batch similarity computation failed: {str(e)}")
            raise EmbeddingError(f"Failed to compute batch similarities: {str(e)}")


# Global embedding service instance
_embedding_service: EmbeddingService = None


def get_embedding_service() -> EmbeddingService:
    """
    Get or create the global embedding service instance.

    Returns:
        EmbeddingService instance (singleton)
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
