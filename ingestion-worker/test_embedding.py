"""Unit tests for embedding service"""
import pytest
from embedding import EmbeddingService


def test_embedding_initialization():
    """Test EmbeddingService initializes correctly"""
    service = EmbeddingService()
    assert service is not None
    assert service.vectorizer is not None


def test_embed_query():
    """Test single query embedding"""
    service = EmbeddingService()
    query = "What is financial risk?"
    
    embedding = service.embed_query(query)
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)


def test_embed_texts():
    """Test batch text embedding"""
    service = EmbeddingService()
    texts = [
        "Financial risk assessment",
        "Portfolio management",
        "Market analysis"
    ]
    
    embeddings = service.embed_texts(texts)
    
    assert len(embeddings) == len(texts)
    assert all(isinstance(emb, list) for emb in embeddings)
    assert all(len(emb) > 0 for emb in embeddings)


def test_embedding_dimensions():
    """Test that embeddings have consistent dimensions"""
    service = EmbeddingService()
    texts = ["Text one", "Text two", "Text three"]
    
    embeddings = service.embed_texts(texts)
    dimensions = [len(emb) for emb in embeddings]
    
    # All embeddings should have same dimension
    assert len(set(dimensions)) == 1


def test_batch_embed():
    """Test batch embedding with smaller batch size"""
    service = EmbeddingService()
    texts = ["Text " + str(i) for i in range(100)]
    
    embeddings = service.batch_embed(texts, batch_size=10)
    
    assert len(embeddings) == len(texts)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
