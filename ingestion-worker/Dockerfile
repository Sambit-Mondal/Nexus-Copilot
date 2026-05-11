# ingestion-worker/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies, ML tools, and grpcurl
RUN apt-get update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    curl \
    && curl -sSL https://github.com/fullstorydev/grpcurl/releases/download/v1.8.7/grpcurl_1.8.7_linux_x86_64.tar.gz | tar -xz -C /usr/local/bin grpcurl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY ingestion-worker/requirements.txt .
RUN pip install -r requirements.txt

# --- gRPC Compilation ---
# 1. Copy the shared proto files
COPY protocol ./protocol

# 2. Copy the worker application code
COPY ingestion-worker/ ./

# 3. Create pb directory and compile
RUN mkdir -p ./pb && touch ./pb/__init__.py
RUN python -m grpc_tools.protoc \
    -I./protocol \
    --python_out=./pb \
    --grpc_python_out=./pb \
    ./protocol/document_service.proto

# 4. Patch the generated file to use relative imports
RUN sed -i 's/import document_service_pb2 as document__service__pb2/from . import document_service_pb2 as document__service__pb2/g' ./pb/document_service_pb2_grpc.py
# ------------------------

# Create temp directory for document processing
RUN mkdir -p /tmp/nexus-ingestion

# Run the gRPC server
CMD ["python", "main.py"]