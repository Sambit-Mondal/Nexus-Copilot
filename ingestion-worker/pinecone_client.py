"""Pinecone vector database integration"""
from typing import List, Dict, Any
from pinecone import Pinecone
from config import settings


class PineconeClient:
    """Handles upserting vectors to Pinecone"""
    
    def __init__(self, api_key: str = None, index_name: str = None):
        self.api_key = api_key or settings.pinecone_api_key
        self.index_name = index_name or settings.pinecone_index_name
        
        if not self.api_key:
            raise ValueError("Pinecone API key not configured")
        
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(self.index_name)
    
    def upsert_vectors(
        self,
        vectors: List[tuple],
        batch_size: int = None
    ) -> Dict[str, Any]:
        """
        Upsert vectors to Pinecone in batches
        
        Args:
            vectors: List of (id, embedding, metadata) tuples
            batch_size: Number of vectors per batch
        
        Returns:
            Status dict with upserted count
        """
        batch_size = batch_size or settings.batch_size
        total_upserted = 0
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            upsert_response = self.index.upsert(vectors=batch)
            total_upserted += len(batch)
        
        return {
            "status": "success",
            "upserted_count": total_upserted,
            "index": self.index_name
        }
    
    def query_similar(
        self,
        embedding: List[float],
        top_k: int = 5,
        filter_dict: Dict = None
    ) -> List[Dict]:
        """Query similar vectors"""
        results = self.index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        
        return results.get("matches", [])
    
    def delete_vectors(self, vector_ids: List[str]) -> Dict[str, Any]:
        """Delete vectors by ID"""
        self.index.delete(ids=vector_ids)
        return {
            "status": "success",
            "deleted_count": len(vector_ids)
        }
