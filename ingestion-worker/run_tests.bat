@echo off
REM Ingestion Worker Test Runner Script

echo ======================================================================
echo Testing Nexus-Copilot Ingestion Worker
echo ======================================================================

REM Set Python path to include local pb package
set PYTHONPATH=%cd%

echo.
echo [1/5] Testing Chunking Service...
python -m pytest test_chunking.py -v --tb=short
if errorlevel 1 (
    echo ✗ Chunking tests failed
    goto error
)
echo ✓ Chunking tests passed

echo.
echo [2/5] Testing Embedding Service...
python -m pytest test_embedding.py -v --tb=short
if errorlevel 1 (
    echo ✗ Embedding tests failed
    goto error
)
echo ✓ Embedding tests passed

echo.
echo [3/5] Testing Integration Pipeline...
python -m pytest test_integration.py -v --tb=short
if errorlevel 1 (
    echo ✗ Integration tests failed
    goto error
)
echo ✓ Integration tests passed

echo.
echo [4/5] Testing gRPC Server Startup...
timeout /t 2 >nul
python main.py >nul 2>&1 &
set SERVER_PID=%ERRORLEVEL%
timeout /t 3 >nul

REM Check if server is running
netstat -ano | find "50051" >nul
if %ERRORLEVEL% equ 0 (
    echo ✓ gRPC server listening on port 50051
    taskkill /PID %SERVER_PID% /F >nul 2>&1
) else (
    echo ✗ gRPC server failed to start
    goto error
)

echo.
echo [5/5] Validating Imports...
python -c "from ingestion_service import IngestionServicer; from config import settings; from chunking import DocumentChunker; from embedding import EmbeddingService; print('✓ All imports successful')"
if errorlevel 1 (
    echo ✗ Import validation failed
    goto error
)

echo.
echo ======================================================================
echo ✓ All tests passed successfully!
echo ======================================================================
exit /b 0

:error
echo.
echo ======================================================================
echo ✗ Tests failed
echo ======================================================================
exit /b 1
