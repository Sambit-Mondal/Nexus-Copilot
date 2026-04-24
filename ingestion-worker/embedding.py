"""Embedding service using scikit-learn TfidfVectorizer"""
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from config import settings


class EmbeddingService:
    """Generates embeddings for text chunks using TF-IDF"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        # TF-IDF vectorizer for lightweight embeddings
        self.vectorizer = TfidfVectorizer(
            max_features=384,  # Match MiniLM dimensions
            lowercase=True,
            stop_words='english'
        )
        self.is_fitted = False
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if not self.is_fitted:
            embeddings = self.vectorizer.fit_transform(texts).toarray()
            self.is_fitted = True
        else:
            embeddings = self.vectorizer.transform(texts).toarray()
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query (for similarity search)"""
        if not self.is_fitted:
            embedding = self.vectorizer.fit_transform([query]).toarray()[0]
            self.is_fitted = True
        else:
            embedding = self.vectorizer.transform([query]).toarray()[0]
        return embedding.tolist()
    
    def batch_embed(self, texts: List[str], batch_size: int = None) -> List[List[float]]:
        """Embed texts in batches to manage memory"""
        batch_size = batch_size or settings.embedding_batch_size
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embed_texts(batch)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
