@echo off
REM Ingestion Worker Test Runner - Simplified and Robust
REM This version focuses on clear diagnostics

setlocal enabledelayedexpansion

echo ======================================================================
echo Nexus-Copilot Ingestion Worker - Comprehensive Test Suite
echo ======================================================================

REM Set Python path
set PYTHONPATH=%cd%

REM Count test phases
set TEST_PASSED=0
set TEST_FAILED=0

REM ======================================================================
REM [1/5] Chunking Tests
REM ======================================================================
echo.
echo [1/5] Testing Chunking Service...
python -m pytest test_chunking.py -v --tb=short 2>&1
if errorlevel 1 (
    echo ✗ Chunking tests FAILED
    set TEST_FAILED=1
    goto errors
) else (
    echo ✓ Chunking tests PASSED
    set /a TEST_PASSED+=1
)

REM ======================================================================
REM [2/5] Embedding Tests
REM ======================================================================
echo.
echo [2/5] Testing Embedding Service...
python -m pytest test_embedding.py -v --tb=short 2>&1
if errorlevel 1 (
    echo ✗ Embedding tests FAILED
    set TEST_FAILED=1
    goto errors
) else (
    echo ✓ Embedding tests PASSED
    set /a TEST_PASSED+=1
)

REM ======================================================================
REM [3/5] Integration Tests
REM ======================================================================
echo.
echo [3/5] Testing Integration Pipeline...
python -m pytest test_integration.py -v --tb=short 2>&1
if errorlevel 1 (
    echo ✗ Integration tests FAILED
    set TEST_FAILED=1
    goto errors
) else (
    echo ✓ Integration tests PASSED
    set /a TEST_PASSED+=1
)

REM ======================================================================
REM [4/5] gRPC Server Startup Test
REM ======================================================================
echo.
echo [4/5] Testing gRPC Server Startup...

REM First verify that basic imports work
echo Checking imports...
python -c "from main import serve; print('OK')" >nul 2>&1
if errorlevel 1 (
    echo ✗ Import check failed
    echo Running detailed diagnostic...
    python simple_test.py
    set TEST_FAILED=1
    goto errors
)

echo Starting server in background...
setlocal enabledelayedexpansion
set SERVER_LOG=%TEMP%\nexus_server_%RANDOM%.log

start "" /B python main.py > "%SERVER_LOG%" 2>&1

REM Wait for server to start
timeout /t 5 >nul

REM Check if server is listening on port 50051
echo Checking if server is listening on port 50051...
netstat -ano 2>nul | find "50051" >nul

if errorlevel 1 (
    echo ✗ Server startup failed (port not listening)
    echo.
    echo Server log output:
    echo ======================================================================
    type "%SERVER_LOG%"
    echo ======================================================================
    echo.
    echo Running diagnostic...
    python minimal_test.py
    if exist "%SERVER_LOG%" del "%SERVER_LOG%"
    set TEST_FAILED=1
    goto errors
) else (
    echo ✓ Server is listening on port 50051
    
    REM Give server a moment to stabilize
    timeout /t 1 >nul
    
    REM Kill all python processes (cleanup)
    taskkill /F /IM python.exe >nul 2>&1
    timeout /t 1 >nul
    
    if exist "%SERVER_LOG%" del "%SERVER_LOG%"
    set /a TEST_PASSED+=1
)

REM ======================================================================
REM [5/5] Import Validation
REM ======================================================================
echo.
echo [5/5] Validating All Imports...
python -c "from ingestion_service import IngestionServicer; from config import settings; from chunking import DocumentChunker; from embedding import EmbeddingService; print('✓ All imports successful')" 2>&1
if errorlevel 1 (
    echo ✗ Import validation failed
    set TEST_FAILED=1
    goto errors
) else (
    set /a TEST_PASSED+=1
)

REM ======================================================================
REM Success!
REM ======================================================================
echo.
echo ======================================================================
echo ✓ ALL TESTS PASSED! (!TEST_PASSED!/5)
echo ======================================================================
exit /b 0

REM ======================================================================
REM Error handling
REM ======================================================================
:errors
echo.
echo ======================================================================
echo ✗ TESTS FAILED (!TEST_FAILED! failure)
echo ======================================================================
echo.
echo Diagnostics:
echo 1. Check Python version: python --version
echo 2. Check pip packages: pip list ^| find "grpcio"
echo 3. Run imports test: python test_proto_imports.py
echo 4. Run minimal test: python minimal_test.py
echo 5. Run simple test: python simple_test.py
echo.
echo ======================================================================
exit /b 1
