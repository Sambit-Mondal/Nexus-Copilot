# Ingestion Worker - Golang gRPC Service Structure

## Running Protobuf Compilation

Before using this module, generate the protobuf stubs by running from the project root:

```bash
cd protocol
python compile.py          # All platforms (requires Python)
# or
./compile.sh              # Unix/Linux/macOS
# or
compile.bat               # Windows
```

This will populate the `pb/` directory with:
- `document_service.pb.go`
- `document_service_grpc.pb.go`

## Prerequisites for Go Compilation

```bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
```

Ensure `protoc` is installed:
- **macOS**: `brew install protobuf`
- **Ubuntu/Debian**: `sudo apt-get install protobuf-compiler`
- **Windows**: Download from https://github.com/protocolbuffers/protobuf/releases
