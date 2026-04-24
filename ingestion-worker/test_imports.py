#!/usr/bin/env python
"""Quick import validation test"""
import sys
import traceback

def test_imports():
    """Test all imports work correctly"""
    errors = []
    
    try:
        print("Testing pb.document_service_pb2 import...")
        from pb import document_service_pb2
        print("  ✓ pb.document_service_pb2 imported successfully")
    except Exception as e:
        errors.append(f"pb.document_service_pb2: {e}")
        traceback.print_exc()
    
    try:
        print("Testing pb.document_service_pb2_grpc import...")
        from pb import document_service_pb2_grpc
        print("  ✓ pb.document_service_pb2_grpc imported successfully")
    except Exception as e:
        errors.append(f"pb.document_service_pb2_grpc: {e}")
        traceback.print_exc()
    
    try:
        print("Testing config import...")
        from config import settings
        print(f"  ✓ config.settings imported successfully")
        print(f"    - gRPC host: {settings.grpc_host}")
        print(f"    - gRPC port: {settings.grpc_port}")
    except Exception as e:
        errors.append(f"config: {e}")
        traceback.print_exc()
    
    try:
        print("Testing chunking import...")
        from chunking import DocumentChunker
        print("  ✓ chunking.DocumentChunker imported successfully")
    except Exception as e:
        errors.append(f"chunking: {e}")
        traceback.print_exc()
    
    try:
        print("Testing embedding import...")
        from embedding import EmbeddingService
        print("  ✓ embedding.EmbeddingService imported successfully")
    except Exception as e:
        errors.append(f"embedding: {e}")
        traceback.print_exc()
    
    try:
        print("Testing pinecone_client import...")
        from pinecone_client import PineconeClient
        print("  ✓ pinecone_client.PineconeClient imported successfully")
    except Exception as e:
        errors.append(f"pinecone_client: {e}")
        traceback.print_exc()
    
    try:
        print("Testing ingestion_service import...")
        from ingestion_service import IngestionServicer
        print("  ✓ ingestion_service.IngestionServicer imported successfully")
    except Exception as e:
        errors.append(f"ingestion_service: {e}")
        traceback.print_exc()
    
    try:
        print("Testing main import...")
        import main
        print("  ✓ main module imported successfully")
    except Exception as e:
        errors.append(f"main: {e}")
        traceback.print_exc()
    
    if errors:
        print("\n❌ Import validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("\n✅ All imports successful!")
        return True

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
