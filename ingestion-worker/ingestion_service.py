"""Ingestion service implementation with gRPC streaming"""
import os
import uuid
import logging
from typing import Generator
import grpc

# Import proto stubs from local pb package
from pb.document_service_pb2 import DocumentRequest, ProcessingStatus
from pb.document_service_pb2_grpc import DocumentIngesterServicer

from chunking import DocumentChunker
from embedding import EmbeddingService
from pinecone_client import PineconeClient
from config import settings

logger = logging.getLogger(__name__)


class IngestionServicer(DocumentIngesterServicer):
    """Implements DocumentIngester service"""
    
    def __init__(self):
        self.chunker = DocumentChunker()
        self.embedder = EmbeddingService()
        self.pinecone = None
        try:
            self.pinecone = PineconeClient()
        except ValueError as e:
            logger.warning(f"Pinecone not configured: {e}")
    
    def ProcessDocument(
        self,
        request: DocumentRequest,
        context: grpc.ServicerContext
    ) -> Generator[ProcessingStatus, None, None]:
        """
        Process document: chunk, embed, and upsert to Pinecone
        Streams status updates back to the client
        """
        task_id = str(uuid.uuid4())
        file_path = request.file_path
        document_id = request.document_id
        client_id = request.client_id
        
        try:
            # Step 1: Load and chunk document
            yield ProcessingStatus(
                task_id=task_id,
                status="CHUNKING",
                progress_percentage=10.0,
                message=f"Starting to chunk document: {document_id}"
            )
            
            chunks = self._load_and_chunk(file_path)
            chunk_count = len(chunks)
            logger.info(f"Task {task_id}: Created {chunk_count} chunks from {file_path}")
            
            yield ProcessingStatus(
                task_id=task_id,
                status="CHUNKING",
                progress_percentage=35.0,
                message=f"Successfully chunked into {chunk_count} segments"
            )
            
            # Step 2: Generate embeddings
            yield ProcessingStatus(
                task_id=task_id,
                status="EMBEDDING",
                progress_percentage=40.0,
                message="Generating embeddings for chunks"
            )
            
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedder.batch_embed(texts)
            
            yield ProcessingStatus(
                task_id=task_id,
                status="EMBEDDING",
                progress_percentage=70.0,
                message=f"Generated {len(embeddings)} embeddings"
            )
            
            # Step 3: Prepare vectors for upsert
            vectors = self._prepare_vectors(
                chunks, embeddings, document_id, client_id
            )
            
            # Step 4: Upsert to Pinecone
            yield ProcessingStatus(
                task_id=task_id,
                status="INDEXING",
                progress_percentage=75.0,
                message="Upserting vectors to Pinecone"
            )
            
            if self.pinecone:
                result = self.pinecone.upsert_vectors(vectors)
                upserted = result["upserted_count"]
                logger.info(f"Task {task_id}: Upserted {upserted} vectors to Pinecone")
                
                yield ProcessingStatus(
                    task_id=task_id,
                    status="INDEXING",
                    progress_percentage=95.0,
                    message=f"Upserted {upserted} vectors"
                )
            else:
                logger.warning(f"Task {task_id}: Pinecone not available, skipping upsert")
                yield ProcessingStatus(
                    task_id=task_id,
                    status="INDEXING",
                    progress_percentage=95.0,
                    message="Pinecone not configured, vectors prepared but not upserted"
                )
            
            # Step 5: Completion
            yield ProcessingStatus(
                task_id=task_id,
                status="COMPLETED",
                progress_percentage=100.0,
                message=f"Successfully processed document {document_id}"
            )
            
            logger.info(f"Task {task_id}: Document processing completed")
            
        except Exception as e:
            error_msg = f"Error processing document: {str(e)}"
            logger.error(f"Task {task_id}: {error_msg}", exc_info=True)
            
            yield ProcessingStatus(
                task_id=task_id,
                status="FAILED",
                progress_percentage=0.0,
                error_message=error_msg
            )
            
            context.abort(grpc.StatusCode.INTERNAL, error_msg)
    
    def _load_and_chunk(self, file_path: str) -> list:
        """Load PDF and chunk it"""
        if file_path.lower().endswith('.pdf'):
            chunks = self.chunker.load_pdf(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            chunks = self.chunker.chunk_text(text, source=file_path)
        
        return chunks
    
    def _prepare_vectors(
        self,
        chunks: list,
        embeddings: list,
        document_id: str,
        client_id: str
    ) -> list:
        """Prepare vectors in (id, embedding, metadata) format for Pinecone"""
        vectors = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_id = f"{document_id}_{i}"
            metadata = {
                "document_id": document_id,
                "client_id": client_id,
                "chunk_index": i,
                "text": chunk["text"],
                **chunk.get("metadata", {})
            }
            
            vectors.append((vector_id, embedding, metadata))
        
        return vectors
