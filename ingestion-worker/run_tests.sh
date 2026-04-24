#!/bin/bash
# Ingestion Worker Test Runner Script for Git Bash/Unix

echo "======================================================================"
echo "Testing Nexus-Copilot Ingestion Worker"
echo "======================================================================"

# Set Python path to include local pb package
export PYTHONPATH="."

echo ""
echo "[1/5] Testing Chunking Service..."
python -m pytest test_chunking.py -v --tb=short
if [ $? -ne 0 ]; then
    echo "✗ Chunking tests failed"
    exit 1
fi
echo "✓ Chunking tests passed"

echo ""
echo "[2/5] Testing Embedding Service..."
python -m pytest test_embedding.py -v --tb=short
if [ $? -ne 0 ]; then
    echo "✗ Embedding tests failed"
    exit 1
fi
echo "✓ Embedding tests passed"

echo ""
echo "[3/5] Testing Integration Pipeline..."
python -m pytest test_integration.py -v --tb=short
if [ $? -ne 0 ]; then
    echo "✗ Integration tests failed"
    exit 1
fi
echo "✓ Integration tests passed"

echo ""
echo "[4/5] Testing gRPC Server Startup..."
# Start server in background
python main.py > /tmp/server.log 2>&1 &
SERVER_PID=$!

# Wait for startup
sleep 3

# Check if server is listening on port 50051
if netstat -tuln 2>/dev/null | grep -q 50051 || lsof -i :50051 2>/dev/null | grep -q LISTEN; then
    echo "✓ gRPC server listening on port 50051"
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
else
    echo "✗ gRPC server failed to start"
    cat /tmp/server.log
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo ""
echo "[5/5] Validating Imports..."
python -c "from ingestion_service import IngestionServicer; from config import settings; from chunking import DocumentChunker; from embedding import EmbeddingService; print('✓ All imports successful')"
if [ $? -ne 0 ]; then
    echo "✗ Import validation failed"
    exit 1
fi

echo ""
echo "======================================================================"
echo "✓ All tests passed successfully!"
echo "======================================================================"
exit 0
