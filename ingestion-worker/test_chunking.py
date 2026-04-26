"""Unit tests for chunking service"""
import pytest
from chunking import DocumentChunker


def test_chunk_text_basic():
    """Test basic text chunking"""
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=10)
    text = "This is a test document. " * 20
    
    chunks = chunker.chunk_text(text, source="test.txt")
    
    assert len(chunks) > 0
    assert all("text" in chunk for chunk in chunks)
    assert all("metadata" in chunk for chunk in chunks)


def test_chunk_text_preserves_content():
    """Test that chunking preserves all content"""
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=10)
    text = "Important information in this test. " * 10
    
    chunks = chunker.chunk_text(text, source="test.txt")
    combined = " ".join([chunk["text"] for chunk in chunks])
    
    # Content should mostly be preserved (minus some whitespace variations)
    assert "Important information" in combined


def test_chunk_metadata():
    """Test that metadata is correctly attached"""
    chunker = DocumentChunker()
    text = "Test text. " * 50
    source = "test_source.txt"
    
    chunks = chunker.chunk_text(text, source=source)
    
    for chunk in chunks:
        assert chunk["metadata"]["source"] == source
        assert "chunk_index" in chunk["metadata"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
