"""Integration test for ingestion pipeline"""
import pytest
import os
from ingestion_service import IngestionServicer


@pytest.fixture
def servicer():
    """Create a test servicer instance"""
    return IngestionServicer()


def test_prepare_vectors(servicer):
    """Test vector preparation for Pinecone"""
    chunks = [
        {"text": "Chunk 1", "metadata": {"page": 0}},
        {"text": "Chunk 2", "metadata": {"page": 1}},
        {"text": "Chunk 3", "metadata": {"page": 2}},
    ]
    embeddings = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
        [0.7, 0.8, 0.9],
    ]
    
    document_id = "doc_123"
    client_id = "client_456"
    
    vectors = servicer._prepare_vectors(chunks, embeddings, document_id, client_id)
    
    assert len(vectors) == 3
    for i, (vec_id, embedding, metadata) in enumerate(vectors):
        assert vec_id == f"{document_id}_{i}"
        assert embedding == embeddings[i]
        assert metadata["document_id"] == document_id
        assert metadata["client_id"] == client_id
        assert metadata["text"] == chunks[i]["text"]


def test_chunking_flow(servicer):
    """Test document chunking flow"""
    # Create a simple test file
    test_file = "/tmp/test_document.txt"
    test_content = "Sample document content. " * 50
    
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    try:
        chunks = servicer._load_and_chunk(test_file)
        
        assert len(chunks) > 0
        assert all("text" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
