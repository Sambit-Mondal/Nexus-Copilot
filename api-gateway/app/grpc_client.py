"""
gRPC client for communication with the Ingestion Worker service.
Handles document processing requests and status streaming.
"""

import asyncio
from typing import AsyncGenerator, Optional
from pathlib import Path
from app.config import settings
from app.logger import get_logger
from app.exceptions import GRPCConnectionError, GRPCProcessingError

logger = get_logger(__name__)


class GRPCClient:
    """Client for communicating with Ingestion Worker via gRPC."""

    def __init__(self):
        """Initialize gRPC client (lazy connection)."""
        self.grpc_url = settings.grpc_url
        self.timeout = settings.grpc_timeout
        self._channel = None
        self._stub = None

        logger.info(f"gRPC client initialized (target: {self.grpc_url})")

    async def connect(self) -> None:
        """
        Establish connection to gRPC server.

        Raises:
            GRPCConnectionError: If connection fails
        """
        try:
            import grpc

            logger.info(f"Connecting to gRPC server: {self.grpc_url}")

            # Create channel with reasonable options
            self._channel = grpc.aio.secure_channel(
                self.grpc_url,
                grpc.ssl_channel_credentials(),
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            ) if "ssl" in self.grpc_url else grpc.aio.insecure_channel(
                self.grpc_url,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )

            # Import proto stubs
            from app.pb.document_service_pb2_grpc import DocumentIngesterServicer
            from app.pb import document_service_pb2_grpc

            self._stub = document_service_pb2_grpc.DocumentIngesterStub(self._channel)

            # Test connection with timeout
            await asyncio.wait_for(
                self._test_connection(),
                timeout=self.timeout,
            )

            logger.info("gRPC connection established successfully")

        except asyncio.TimeoutError:
            logger.error(f"gRPC connection timeout ({self.timeout}s)")
            raise GRPCConnectionError(f"Connection timeout to {self.grpc_url}")
        except Exception as e:
            logger.error(f"gRPC connection failed: {str(e)}")
            raise GRPCConnectionError(f"Failed to connect to {self.grpc_url}: {str(e)}")

    async def _test_connection(self) -> None:
        """Test gRPC connection by making a simple call."""
        try:
            # Try to call a health check or similar
            # For now, just verify channel is ready
            await self._channel.ready()
        except Exception as e:
            raise e

    async def disconnect(self) -> None:
        """Disconnect from gRPC server."""
        try:
            if self._channel:
                await self._channel.close()
                logger.info("gRPC connection closed")
        except Exception as e:
            logger.error(f"Error closing gRPC connection: {str(e)}")

    async def process_document(
        self,
        document_id: str,
        file_path: str,
        client_id: Optional[str] = None,
    ) -> AsyncGenerator[dict, None]:
        """
        Send document to ingestion worker for processing.
        Streams status updates back.

        Args:
            document_id: Unique document identifier
            file_path: Path to file to process
            client_id: Optional client identifier

        Yields:
            Status update dictionaries with progress information

        Raises:
            GRPCProcessingError: If processing fails
        """
        try:
            if not self._stub:
                await self.connect()

            # Verify file exists
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            logger.info(f"Starting document processing via gRPC: {document_id}")

            # Import proto message types
            from app.pb.document_service_pb2 import IngestRequest

            # Create request
            request = IngestRequest(
                document_id=document_id,
                s3_url=file_path,
                client_id=client_id or "unknown",
            )

            # Stream responses from gRPC server
            try:
                async for response in self._stub.IngestDocument(
                    request,
                    timeout=self.timeout * 10,  # Longer timeout for processing
                ):
                    yield {
                        "task_id": response.task_id,
                        "status": response.status,
                        "progress": float(response.progress),
                    }

                logger.info(f"Document processing completed: {document_id}")

            except asyncio.TimeoutError:
                logger.error(f"gRPC processing timeout: {document_id}")
                raise GRPCProcessingError("Document processing timeout")

        except FileNotFoundError as e:
            logger.error(f"File not found for processing: {str(e)}")
            raise GRPCProcessingError(f"File not found: {str(e)}")
        except Exception as e:
            logger.error(f"gRPC document processing failed: {str(e)}")
            raise GRPCProcessingError(f"Document processing failed: {str(e)}")

    async def health_check(self) -> bool:
        """
        Check if gRPC server is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            if not self._stub:
                await self.connect()

            # Try a lightweight operation
            logger.debug("Performing gRPC health check")
            # Add actual health check call if available in proto
            return True

        except Exception as e:
            logger.error(f"gRPC health check failed: {str(e)}")
            return False


# Global gRPC client instance
_grpc_client: GRPCClient = None


def get_grpc_client() -> GRPCClient:
    """
    Get or create the global gRPC client instance.

    Returns:
        GRPCClient instance (singleton)
    """
    global _grpc_client
    if _grpc_client is None:
        _grpc_client = GRPCClient()
    return _grpc_client
