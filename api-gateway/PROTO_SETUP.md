# API Gateway - FastAPI Application Structure

## Running Protobuf Compilation

Before using this module, generate the protobuf stubs by running from the project root:

```bash
cd protocol
python compile.py          # All platforms
# or
./compile.sh              # Unix/Linux/macOS
# or
compile.bat               # Windows
```

This will populate the `app/pb/` directory with:
- `document_service_pb2.py`
- `document_service_pb2_grpc.py`
- `__init__.py`