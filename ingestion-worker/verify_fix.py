#!/usr/bin/env python
"""Comprehensive fix verification for proto import issue"""
import os
import sys

print("=" * 70)
print("NEXUS-COPILOT INGESTION WORKER - PROTO IMPORT FIX VERIFICATION")
print("=" * 70)

# Check file structure
print("\n[1] Checking directory structure...")
required_files = {
    'pb/__init__.py': 'Proto package marker',
    'pb/document_service_pb2.py': 'Generated proto message definitions',
    'pb/document_service_pb2_grpc.py': 'Generated gRPC service stubs',
    'ingestion_service.py': 'Core ingestion service implementation',
    'main.py': 'gRPC server entry point',
    'config.py': 'Configuration management',
    'chunking.py': 'Document chunking service',
    'embedding.py': 'Embedding service',
    'pinecone_client.py': 'Pinecone integration',
    'test_chunking.py': 'Chunking unit tests',
    'test_embedding.py': 'Embedding unit tests',
    'test_integration.py': 'Integration tests',
    'test_imports.py': 'Import validation test',
}

all_exist = True
for filepath, description in required_files.items():
    full_path = os.path.join(os.getcwd(), filepath)
    exists = os.path.isfile(full_path)
    status = "✓" if exists else "✗"
    print(f"  {status} {filepath:<40} ({description})")
    if not exists:
        all_exist = False

if not all_exist:
    print("\n❌ Some required files are missing!")
    sys.exit(1)

# Check pb/__init__.py imports
print("\n[2] Checking pb/__init__.py exports...")
with open('pb/__init__.py', 'r') as f:
    pb_init = f.read()
    has_pb2 = 'document_service_pb2' in pb_init
    has_grpc = 'document_service_pb2_grpc' in pb_init
    print(f"  {'✓' if has_pb2 else '✗'} Exports document_service_pb2")
    print(f"  {'✓' if has_grpc else '✗'} Exports document_service_pb2_grpc")

# Check document_service_pb2_grpc.py for relative imports
print("\n[3] Checking pb/document_service_pb2_grpc.py import style...")
with open('pb/document_service_pb2_grpc.py', 'r') as f:
    grpc_content = f.read()
    has_relative_import = 'from . import document_service_pb2' in grpc_content
    has_absolute_import = 'import document_service_pb2 as' in grpc_content and 'from . import' not in grpc_content
    
    if has_relative_import:
        print("  ✓ Uses relative import: from . import document_service_pb2")
    elif has_absolute_import:
        print("  ✗ Uses absolute import (should be relative)")
    else:
        print("  ⚠ Import pattern unclear")

# Check ingestion_service.py imports
print("\n[4] Checking ingestion_service.py imports...")
with open('ingestion_service.py', 'r') as f:
    service_content = f.read()
    checks = {
        'from pb.document_service_pb2 import': 'Direct import from pb.document_service_pb2',
        'from pb.document_service_pb2_grpc import': 'Direct import from pb.document_service_pb2_grpc',
        'class IngestionServicer(DocumentIngesterServicer):': 'Extends DocumentIngesterServicer',
        'yield ProcessingStatus(': 'Uses ProcessingStatus directly'
    }
    for check, description in checks.items():
        found = check in service_content
        print(f"  {'✓' if found else '✗'} {description}")

# Check main.py imports
print("\n[5] Checking main.py imports...")
with open('main.py', 'r') as f:
    main_content = f.read()
    checks = {
        'from pb.document_service_pb2_grpc import add_DocumentIngesterServicer_to_server': 'Imports add function',
        'from ingestion_service import IngestionServicer': 'Imports IngestionServicer',
        'add_DocumentIngesterServicer_to_server(': 'Uses add function directly'
    }
    for check, description in checks.items():
        found = check in main_content
        print(f"  {'✓' if found else '✗'} {description}")

# Check test_imports.py exists and is valid
print("\n[6] Checking test_imports.py...")
if os.path.isfile('test_imports.py'):
    with open('test_imports.py', 'r') as f:
        test_content = f.read()
        has_pb2 = 'from pb import document_service_pb2' in test_content
        has_grpc = 'from pb import document_service_pb2_grpc' in test_content
        has_ingestion = 'from ingestion_service import IngestionServicer' in test_content
        print(f"  ✓ test_imports.py exists")
        print(f"  {'✓' if has_pb2 else '✗'} Tests pb.document_service_pb2 import")
        print(f"  {'✓' if has_grpc else '✗'} Tests pb.document_service_pb2_grpc import")
        print(f"  {'✓' if has_ingestion else '✗'} Tests ingestion_service import")
else:
    print("  ✗ test_imports.py not found")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
The following changes have been made to fix the proto import issue:

1. Updated pb/__init__.py to explicitly export proto modules
2. Verified pb/document_service_pb2_grpc.py uses relative imports
3. Updated ingestion_service.py to import directly from pb modules
4. Updated main.py to import proto functions from pb module
5. Updated run_tests.bat to use PYTHONPATH=%cd% only
6. Updated run_tests.sh to use export PYTHONPATH="."
7. Created test_imports.py for comprehensive import validation

Key fix: Removed sys.path manipulation and PYTHONPATH references to api-gateway/app.
This ensures all proto imports resolve to the local pb/ package only.

Next steps:
1. Run: python test_imports.py
2. Run: run_tests.bat (Windows) or bash run_tests.sh (Unix)
3. Verify all tests pass
4. Commit changes
""")
print("=" * 70)
