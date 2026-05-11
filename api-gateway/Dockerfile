# api-gateway/Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY api-gateway/requirements.txt .
RUN pip install -r requirements.txt

# --- gRPC Compilation ---
# 1. Copy the shared proto files
COPY protocol ./protocol

# 2. Copy the API application code
COPY api-gateway/app ./app

# 3. Create the pb directory and __init__.py
RUN mkdir -p ./app/pb && touch ./app/pb/__init__.py

# 4. Generate the gRPC python files
RUN python -m grpc_tools.protoc \
    -I./protocol \
    --python_out=./app/pb \
    --grpc_python_out=./app/pb \
    ./protocol/document_service.proto

# 5. Patch the generated file to use relative imports
RUN sed -i 's/import document_service_pb2 as document__service__pb2/from . import document_service_pb2 as document__service__pb2/g' ./app/pb/document_service_pb2_grpc.py
# ------------------------

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=15s --timeout=5s --retries=5 --start-period=10s \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]