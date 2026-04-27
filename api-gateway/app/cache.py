"""
Redis semantic cache service for query caching.
Implements similarity-based lookups with configurable threshold.
"""

import json
import numpy as np
from typing import Optional, Dict, Any, List
import redis
from app.config import settings
from app.logger import get_logger
from app.exceptions import CacheError
from app.embedding import get_embedding_service

logger = get_logger(__name__)


class SemanticCache:
    """Redis-based semantic cache with similarity search."""

    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(settings.redis_connection_url)
            # Test connection
            self.redis_client.ping()
            logger.info(f"Redis cache connected: {settings.redis_connection_url}")
            self.similarity_threshold = settings.similarity_threshold
            self.cache_ttl = settings.redis_cache_ttl
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise CacheError(f"Redis connection failed: {str(e)}")

    def get_cache_key(self, prefix: str, key: str) -> str:
        """Generate cache key with prefix."""
        return f"{prefix}:{key}"

    def cache_response(
        self, query: str, embedding: np.ndarray, response: str, metadata: Dict[str, Any] = None
    ) -> None:
        """
        Cache a query response with its embedding.

        Args:
            query: Original query text
            embedding: Query embedding (numpy array)
            response: Generated response text
            metadata: Optional metadata (session_id, client_id, etc.)

        Raises:
            CacheError: If caching fails
        """
        try:
            # Convert embedding to list for JSON serialization
            embedding_list = embedding.tolist()

            # Create cache entry
            cache_entry = {
                "query": query,
                "embedding": embedding_list,
                "response": response,
                "metadata": metadata or {},
            }

            # Generate unique key based on query hash
            import hashlib

            query_hash = hashlib.md5(query.encode()).hexdigest()
            cache_key = self.get_cache_key("query", query_hash)

            # Store in Redis with TTL
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(cache_entry),
            )

            logger.info(f"Cached query response: {cache_key} (TTL: {self.cache_ttl}s)")
        except Exception as e:
            logger.error(f"Cache write failed: {str(e)}")
            # Don't raise here - cache failures shouldn't break the query flow
            pass

    def search_similar(self, query_embedding: np.ndarray) -> Optional[str]:
        """
        Search for a similar cached query and return response if similarity > threshold.

        Args:
            query_embedding: Query embedding to search for

        Returns:
            Cached response if similar query found, None otherwise

        Raises:
            CacheError: If cache search fails
        """
        try:
            # Get all cache keys
            pattern = self.get_cache_key("query", "*")
            keys = self.redis_client.keys(pattern)

            if not keys:
                logger.debug("No cached queries found")
                return None

            best_match = None
            best_similarity = 0.0

            # Search through all cached queries
            for key in keys:
                cache_data = self.redis_client.get(key)
                if not cache_data:
                    continue

                try:
                    cache_entry = json.loads(cache_data)
                    cached_embedding = np.array(cache_entry["embedding"])

                    # Compute similarity
                    similarity = self._cosine_similarity(query_embedding, cached_embedding)

                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = cache_entry

                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse cache entry {key}: {str(e)}")
                    continue

            # Return cached response if similarity exceeds threshold
            if best_similarity > self.similarity_threshold and best_match:
                logger.info(
                    f"Cache hit! Similarity: {best_similarity:.4f} (threshold: {self.similarity_threshold})"
                )
                return best_match["response"]

            logger.debug(
                f"No similar query found (best: {best_similarity:.4f}, threshold: {self.similarity_threshold})"
            )
            return None

        except Exception as e:
            logger.error(f"Cache search failed: {str(e)}")
            # Don't raise - cache misses shouldn't break the query flow
            return None

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-8)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-8)
        return float(np.dot(vec1_norm, vec2_norm))

    def clear_old_entries(self, days: int = 7) -> int:
        """
        Clear cache entries older than specified days.
        Note: Redis TTL is already handled, this is for manual cleanup.

        Args:
            days: Number of days to keep

        Returns:
            Number of entries cleared
        """
        try:
            pattern = self.get_cache_key("query", "*")
            keys = self.redis_client.keys(pattern)
            cleared = 0

            for key in keys:
                # Redis handles TTL automatically, just log
                ttl = self.redis_client.ttl(key)
                if ttl == -1:
                    # No expiration set, delete it
                    self.redis_client.delete(key)
                    cleared += 1

            logger.info(f"Cleared {cleared} expired cache entries")
            return cleared

        except Exception as e:
            logger.error(f"Cache cleanup failed: {str(e)}")
            return 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            pattern = self.get_cache_key("query", "*")
            keys = self.redis_client.keys(pattern)

            info = self.redis_client.info("memory")

            return {
                "total_entries": len(keys),
                "memory_used_mb": info.get("used_memory_human", "N/A"),
                "ttl_seconds": self.cache_ttl,
                "similarity_threshold": self.similarity_threshold,
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {str(e)}")
            return {}

    def clear_all(self) -> None:
        """Clear all cache entries (use with caution)."""
        try:
            pattern = self.get_cache_key("query", "*")
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            logger.info(f"Cleared {len(keys)} cache entries")
        except Exception as e:
            logger.error(f"Cache clear failed: {str(e)}")

    def health_check(self) -> bool:
        """Check if Redis is healthy."""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return False


# Global cache instance
_semantic_cache: SemanticCache = None


def get_semantic_cache() -> SemanticCache:
    """
    Get or create the global semantic cache instance.

    Returns:
        SemanticCache instance (singleton)
    """
    global _semantic_cache
    if _semantic_cache is None:
        _semantic_cache = SemanticCache()
    return _semantic_cache
