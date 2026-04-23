#!/bin/bash

# Protocol Buffer Compilation Script for Unix-like systems
# This script generates Python and Go stubs from the proto files

set -e

PROTO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_GATEWAY_OUTPUT="$PROTO_DIR/../api-gateway/app/pb"
INGESTION_WORKER_OUTPUT="$PROTO_DIR/../ingestion-worker/pb"

echo "Protocol Buffer Compilation"
echo "============================"
echo ""

# Create output directories
echo "Creating output directories..."
mkdir -p "$API_GATEWAY_OUTPUT"
mkdir -p "$INGESTION_WORKER_OUTPUT"

# Check if grpcio-tools is installed for Python
echo ""
echo "Checking for grpcio-tools..."
if ! python3 -c "import grpc_tools" 2>/dev/null; then
    echo "Installing grpcio-tools..."
    pip install grpcio-tools
fi

# Generate Python stubs
echo ""
echo "Generating Python protobuf stubs..."
python3 -m grpc_tools.protoc \
    -I"$PROTO_DIR" \
    --python_out="$API_GATEWAY_OUTPUT" \
    --grpc_python_out="$API_GATEWAY_OUTPUT" \
    "$PROTO_DIR/document_service.proto"

# Create __init__.py for Python package
touch "$API_GATEWAY_OUTPUT/__init__.py"
echo "✓ Python stubs generated in $API_GATEWAY_OUTPUT"

# Check if protoc is installed for Go
echo ""
echo "Checking for protoc compiler..."
if ! command -v protoc &> /dev/null; then
    echo "[WARNING] protoc not found. Go stubs generation skipped."
    echo "[INFO] Install protoc from: https://github.com/protocolbuffers/protobuf/releases"
    exit 0
fi

# Check if Go protoc plugins are installed
echo "Checking for Go protoc plugins..."
if ! go list -m github.com/grpc-ecosystem/grpc-gateway/v2 >/dev/null 2>&1; then
    echo "Installing Go protoc plugins..."
    go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
fi

# Generate Go stubs
echo ""
echo "Generating Go protobuf stubs..."
protoc \
    -I="$PROTO_DIR" \
    --go_out="$INGESTION_WORKER_OUTPUT" \
    --go-grpc_out="$INGESTION_WORKER_OUTPUT" \
    "$PROTO_DIR/document_service.proto"

echo "✓ Go stubs generated in $INGESTION_WORKER_OUTPUT"

echo ""
echo "✓ All protocol buffer stubs generated successfully!"
