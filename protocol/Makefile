.PHONY: generate-python generate-go generate-all clean help

# Directories
PROTO_DIR := .
PYTHON_OUTPUT_DIR := python_pb
GO_OUTPUT_DIR := go_pb
API_GATEWAY_OUTPUT := ../api-gateway/app/pb
INGESTION_WORKER_OUTPUT := ../ingestion-worker/pb

help:
	@echo "Protocol Buffer Compilation"
	@echo "============================"
	@echo "make generate-python     - Generate Python stubs for api-gateway"
	@echo "make generate-go         - Generate Go stubs for ingestion-worker"
	@echo "make generate-all        - Generate all stubs (Python and Go)"
	@echo "make clean               - Remove generated files"

generate-python:
	@echo "Generating Python protobuf stubs..."
	@mkdir -p $(API_GATEWAY_OUTPUT)
	python -m grpc_tools.protoc \
		-I$(PROTO_DIR) \
		--python_out=$(API_GATEWAY_OUTPUT) \
		--grpc_python_out=$(API_GATEWAY_OUTPUT) \
		$(PROTO_DIR)/document_service.proto
	@echo "✓ Python stubs generated in $(API_GATEWAY_OUTPUT)"
	@touch $(API_GATEWAY_OUTPUT)/__init__.py

generate-go:
	@echo "Generating Go protobuf stubs..."
	@mkdir -p $(INGESTION_WORKER_OUTPUT)
	protoc \
		-I=$(PROTO_DIR) \
		--go_out=$(INGESTION_WORKER_OUTPUT) \
		--go-grpc_out=$(INGESTION_WORKER_OUTPUT) \
		$(PROTO_DIR)/document_service.proto
	@echo "✓ Go stubs generated in $(INGESTION_WORKER_OUTPUT)"

generate-all: generate-python generate-go
	@echo "✓ All protocol buffer stubs generated successfully!"

clean:
	@echo "Cleaning generated files..."
	@rm -rf $(API_GATEWAY_OUTPUT) $(INGESTION_WORKER_OUTPUT)
	@echo "✓ Cleanup complete"
