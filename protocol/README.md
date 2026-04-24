# Protocol Buffers - Nexus Copilot gRPC Contract

This directory contains the Protocol Buffer definitions for gRPC communication between the FastAPI gateway and the Golang ingestion worker.

## Directory Structure

```
protocol/
├── document_service.proto    # Main gRPC service definition
├── compile.bat              # Windows compilation script
├── compile.sh               # Unix/Linux/macOS compilation script
├── Makefile                 # Make-based build automation (Unix)
└── README.md                # This file
```

## Proto Definitions

### `document_service.proto`

Defines the gRPC contract with:

- **DocumentRequest**: Message for ingestion requests
  - `file_path` (string): Local or S3 path to document
  - `document_id` (string): Unique document identifier
  - `client_id` (string): Client identifier for data segmentation

- **ProcessingStatus**: Streaming status updates
  - `task_id` (string): Unique task identifier
  - `status` (string): Current status (CHUNKING, EMBEDDING, INDEXING, COMPLETED, ERROR)
  - `progress_percentage` (float): Progress 0.0-100.0
  - `message` (string): Optional status message
  - `error_message` (string): Optional error details

- **DocumentIngester Service**: Main service
  - `rpc ProcessDocument(DocumentRequest) returns (stream ProcessingStatus)`

## Compilation Instructions

### Prerequisites

#### For Python (api-gateway)
```bash
pip install grpcio grpcio-tools
```

#### For Go (ingestion-worker)
```bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
```

Install `protoc` compiler:
- **macOS**: `brew install protobuf`
- **Ubuntu/Debian**: `apt-get install protobuf-compiler`
- **Windows**: Download from [protobuf releases](https://github.com/protocolbuffers/protobuf/releases)

### Compilation Methods

#### Method 1: Automated Scripts (Recommended)

**Windows:**
```cmd
cd protocol
compile.bat
```

**Unix/Linux/macOS:**
```bash
cd protocol
chmod +x compile.sh
./compile.sh
```

#### Method 2: Using Make (Unix/Linux/macOS)

```bash
cd protocol
make generate-all      # Generate both Python and Go
make generate-python   # Python only
make generate-go       # Go only
make clean            # Remove generated files
```

#### Method 3: Manual Compilation

**Python:**
```bash
python -m grpc_tools.protoc \
  -I./protocol \
  --python_out=./api-gateway/app/pb \
  --grpc_python_out=./api-gateway/app/pb \
  ./protocol/document_service.proto
```

**Go:**
```bash
protoc \
  -I=./protocol \
  --go_out=./ingestion-worker/pb \
  --go-grpc_out=./ingestion-worker/pb \
  ./protocol/document_service.proto
```

## Generated Files

After compilation, the following files are created:

### Python (in `api-gateway/app/pb/`)
- `document_service_pb2.py` - Protocol buffer message definitions
- `document_service_pb2_grpc.py` - gRPC service stubs
- `__init__.py` - Python package marker

### Go (in `ingestion-worker/pb/`)
- `document_service.pb.go` - Protocol buffer message definitions
- `document_service_grpc.pb.go` - gRPC service stubs

## Usage

### In API Gateway (Python)
```python
from app.pb import document_service_pb2_grpc, document_service_pb2

# Create gRPC client
channel = grpc.aio.secure_channel('localhost:50051', credentials)
stub = document_service_pb2_grpc.DocumentIngesterStub(channel)

# Make request
request = document_service_pb2.DocumentRequest(
    file_path="s3://bucket/doc.pdf",
    document_id="doc-123",
    client_id="client-456"
)

# Stream responses
async for status in stub.ProcessDocument(request):
    print(f"Status: {status.status}, Progress: {status.progress_percentage}%")
```

### In Ingestion Worker (Go)
```go
import (
    pb "github.com/sambit-mondal/nexus-copilot/pb/document_service"
)

type DocumentIngesterServer struct {
    pb.UnimplementedDocumentIngesterServer
}

func (s *DocumentIngesterServer) ProcessDocument(
    req *pb.DocumentRequest,
    stream pb.DocumentIngester_ProcessDocumentServer,
) error {
    // Implementation
}
```

## Best Practices

1. **Always regenerate stubs** after modifying `.proto` files
2. **Version control**: Commit both `.proto` files and generated stubs
3. **API Stability**: Treat the proto contract as your public API - breaking changes require versioning
4. **Backward Compatibility**: Use field numbers carefully; never reuse deprecated numbers
5. **Documentation**: Comment proto messages for IDE intellisense

## Troubleshooting

### Python: ModuleNotFoundError: No module named 'grpc_tools'
```bash
pip install --upgrade grpcio-tools
```

### Go: Cannot find protoc-gen-go
Ensure `$GOPATH/bin` is in your `$PATH`:
```bash
export PATH="$PATH:$(go env GOPATH)/bin"
```

### Proto compilation errors
- Check proto file syntax with: `protoc --version`
- Verify paths are correct and relative to script location
- Ensure output directories exist and are writable

## Resources

- [Protocol Buffers Documentation](https://developers.google.com/protocol-buffers)
- [gRPC Documentation](https://grpc.io/docs)
- [Python gRPC Guide](https://grpc.io/docs/languages/python)
- [Go gRPC Guide](https://grpc.io/docs/languages/go)