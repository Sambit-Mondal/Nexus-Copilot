"""gRPC Ingestion Worker Server Entry Point"""
import logging
import signal
import sys
import os
from concurrent import futures

import grpc

from ingestion_service import IngestionServicer
from pb.document_service_pb2_grpc import add_DocumentIngesterServicer_to_server
from config import settings

# Configure logging
logging.basicConfig(
    level=settings.log_level.upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def serve():
    """Start gRPC server"""
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_concurrent_streams", 100),
            ("grpc.max_send_message_length", -1),
            ("grpc.max_receive_message_length", -1),
        ]
    )
    
    add_DocumentIngesterServicer_to_server(
        IngestionServicer(),
        server
    )
    
    bind_address = f"{settings.grpc_host}:{settings.grpc_port}"
    server.add_insecure_port(bind_address)
    
    logger.info(f"Starting gRPC Ingestion Worker on {bind_address}")
    server.start()
    logger.info("Server started and ready to serve")
    
    def handle_signal(signum, frame):
        logger.info("Received shutdown signal, gracefully stopping...")
        server.stop(grace_period=5)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down...")
        server.stop(grace_period=5)


if __name__ == '__main__':
    serve()
