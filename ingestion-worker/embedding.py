"""Embedding service using sentence-transformers for semantic embeddings"""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from config import settings


class EmbeddingService:
    """Generates semantic embeddings for text chunks using Sentence Transformers"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        # Load sentence-transformer model for semantic embeddings
        self.model = SentenceTransformer(self.model_name)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query (for similarity search)"""
        embedding = self.model.encode([query], convert_to_numpy=True)[0]
        return embedding.tolist()
    
    def batch_embed(self, texts: List[str], batch_size: int = None) -> List[List[float]]:
        """Embed texts in batches to manage memory"""
        batch_size = batch_size or settings.embedding_batch_size
        embeddings = self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
        return embeddings.tolist()
