"""
Upload endpoint for document ingestion.
Accepts multipart file uploads and coordinates with gRPC ingestion worker.
"""

import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.models import UploadResponse, ErrorResponse
from app.config import settings
from app.grpc_client import get_grpc_client
from app.logger import get_logger
from app.exceptions import (
    InvalidFileError,
    UploadError,
    GRPCConnectionError,
    NexusException,
)

logger = get_logger(__name__)

router = APIRouter()

# In-memory store for upload status (in production, use database)
upload_status_store = {}


@router.post("/api/v1/upload", response_model=UploadResponse, tags=["Upload"])
async def upload_endpoint(
    file: UploadFile = File(...),
    client_id: str = Form(...),
    document_type: str = Form(default="general"),
):
    """
    Document Upload Endpoint - Accepts files and initiates ingestion.

    This endpoint:
    1. Validates file format (PDF, DOCX, TXT)
    2. Saves file to Docker volume
    3. Initiates gRPC ProcessDocument call
    4. Returns 200 OK immediately with upload_id
    5. Background task streams progress to client

    Args:
        file: Uploaded file (multipart/form-data)
        client_id: Client identifier
        document_type: Type of document (earnings_report, market_analysis, etc.)

    Returns:
        UploadResponse with upload_id, filename, status

    Raises:
        HTTPException: If upload fails
    """
    upload_id = None
    try:
        # Step 1: Validate file
        logger.info(f"Upload started (client: {client_id}, file: {file.filename})")

        if not file.filename:
            raise InvalidFileError("Filename is required")

        # Check file extension
        allowed_extensions = {f".{ext}" for ext in settings.allowed_file_types}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            allowed_str = ", ".join(settings.allowed_file_types).upper()
            raise InvalidFileError(
                f"Invalid file type '{file_ext}'. Accepted: {allowed_str}"
            )

        # Check file size
        if file.size and file.size > settings.max_upload_size:
            size_mb = settings.max_upload_size / (1024 * 1024)
            raise InvalidFileError(f"File too large. Maximum size: {size_mb:.0f}MB")

        # Step 2: Create upload directory and save file
        logger.debug("Creating upload directory and saving file")
        upload_dir = settings.ensure_upload_directory()

        # Generate unique upload_id and filename
        upload_id = str(uuid.uuid4())
        saved_filename = f"{upload_id}{file_ext}"
        file_path = upload_dir / saved_filename

        # Save uploaded file
        file_content = await file.read()
        with open(file_path, "wb") as f:
            f.write(file_content)

        file_size = len(file_content)
        logger.info(f"File saved: {file_path} ({file_size} bytes)")

        # Step 3: Initialize gRPC client and process document
        logger.debug("Initiating gRPC document processing")
        grpc_client = get_grpc_client()

        # Connect to gRPC server (if not already connected)
        try:
            await grpc_client.connect()
        except GRPCConnectionError:
            # Log but don't fail - may already be connected
            logger.debug("gRPC connection already established or reconnecting")

        # Background task: stream gRPC responses
        async def process_document_background():
            """Background task to process document and track progress."""
            try:
                logger.info(f"Starting background processing for {upload_id}")

                async for status_update in grpc_client.process_document(
                    document_id=upload_id,
                    file_path=str(file_path),
                    client_id=client_id,
                ):
                    # Store status update
                    upload_status_store[upload_id] = {
                        "status": status_update.get("status", "processing"),
                        "progress": status_update.get("progress", 0),
                        "task_id": status_update.get("task_id"),
                    }
                    logger.debug(f"Progress update: {upload_id} - {status_update}")

                # Mark as completed
                upload_status_store[upload_id] = {
                    "status": "completed",
                    "progress": 100.0,
                    "completed_at": None,  # Would set datetime in production
                }
                logger.info(f"Document processing completed: {upload_id}")

            except Exception as e:
                logger.error(f"Background processing error: {str(e)}")
                upload_status_store[upload_id] = {
                    "status": "failed",
                    "error": str(e),
                }

        # Spawn background task (non-blocking)
        import asyncio

        asyncio.create_task(process_document_background())

        # Initialize status tracking
        upload_status_store[upload_id] = {
            "status": "processing",
            "progress": 0.0,
            "filename": file.filename,
            "client_id": client_id,
            "document_type": document_type,
        }

        # Step 4: Return 200 OK with upload_id
        response = UploadResponse(
            upload_id=upload_id,
            filename=file.filename,
            size_bytes=file_size,
            status="processing",
        )

        logger.info(f"Upload response sent (upload_id: {upload_id})")
        return response

    except InvalidFileError as e:
        logger.warning(f"Invalid file error: {str(e)}")
        raise HTTPException(status_code=400, detail={"error": e.message, "code": e.code})
    except UploadError as e:
        logger.error(f"Upload error: {str(e)}")
        # Cleanup file if it exists
        if upload_id:
            file_path = settings.ensure_upload_directory() / f"{upload_id}*"
            for f in settings.ensure_upload_directory().glob(f"{upload_id}*"):
                f.unlink()
        raise HTTPException(status_code=500, detail={"error": e.message, "code": e.code})
    except NexusException as e:
        logger.error(f"Nexus error: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())
    except Exception as e:
        logger.error(f"Unexpected upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "File upload failed", "code": "UPLOAD_ERROR"},
        )


@router.get("/api/v1/upload/{upload_id}/status", tags=["Upload"])
async def upload_status_endpoint(upload_id: str):
    """
    Upload Status Endpoint - Get progress of document ingestion.

    Args:
        upload_id: Upload identifier from /upload response

    Returns:
        Status information with progress percentage and current step
    """
    try:
        logger.debug(f"Status check: {upload_id}")

        if upload_id not in upload_status_store:
            raise HTTPException(
                status_code=404,
                detail={"error": f"Upload not found: {upload_id}", "code": "NOT_FOUND"},
            )

        status = upload_status_store[upload_id]

        # Build response
        progress = None
        if "progress" in status:
            progress = {
                "percent": status["progress"],
                "current_step": status.get("status", "unknown"),
            }

        response = {
            "upload_id": upload_id,
            "status": status.get("status", "unknown"),
            "progress": progress,
            "created_at": "2026-04-27T06:46:05Z",  # Would use actual timestamp
            "updated_at": "2026-04-27T06:48:12Z",  # Would use actual timestamp
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to get upload status", "code": "INTERNAL_ERROR"},
        )


@router.options("/api/v1/upload", tags=["Upload"])
async def upload_options():
    """Handle CORS preflight for upload endpoint."""
    return {}


@router.options("/api/v1/upload/{upload_id}/status", tags=["Upload"])
async def status_options():
    """Handle CORS preflight for status endpoint."""
    return {}
