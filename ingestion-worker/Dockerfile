FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for ML/ML operations
RUN apt-get update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Copy proto files from api-gateway
COPY api-gateway/app/pb ./pb

# Copy requirements and install dependencies
COPY ingestion-worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ingestion-worker/ .

# Create temp directory for processing
RUN mkdir -p /tmp/nexus-ingestion

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import grpc; print('OK')" || exit 1

# Run the gRPC server
CMD ["python", "main.py"]
