@echo off
REM Protocol Buffer Compilation Script for Windows
REM This script generates Python and Go stubs from the proto files

setlocal enabledelayedexpansion

set PROTO_DIR=%~dp0
set API_GATEWAY_OUTPUT=%PROTO_DIR%..\api-gateway\app\pb
set INGESTION_WORKER_OUTPUT=%PROTO_DIR%..\ingestion-worker\pb

REM Create output directories
echo Creating output directories...
if not exist "%API_GATEWAY_OUTPUT%" mkdir "%API_GATEWAY_OUTPUT%"
if not exist "%INGESTION_WORKER_OUTPUT%" mkdir "%INGESTION_WORKER_OUTPUT%"

REM Check if grpcio-tools is installed for Python
echo.
echo Checking for grpcio-tools...
python -c "import grpc_tools" >nul 2>&1
if errorlevel 1 (
    echo Installing grpcio-tools...
    pip install grpcio-tools
)

REM Generate Python stubs
echo.
echo Generating Python protobuf stubs...
python -m grpc_tools.protoc ^
    -I"%PROTO_DIR%" ^
    --python_out="%API_GATEWAY_OUTPUT%" ^
    --grpc_python_out="%API_GATEWAY_OUTPUT%" ^
    "%PROTO_DIR%document_service.proto"

if errorlevel 1 (
    echo [ERROR] Failed to generate Python stubs
    exit /b 1
)

REM Create __init__.py for Python package
echo. > "%API_GATEWAY_OUTPUT%\__init__.py"
echo [SUCCESS] Python stubs generated in %API_GATEWAY_OUTPUT%

REM Check if protoc is installed for Go
echo.
echo Checking for protoc compiler...
where protoc >nul 2>&1
if errorlevel 1 (
    echo [WARNING] protoc not found. Go stubs generation skipped.
    echo [INFO] Install protoc from: https://github.com/protocolbuffers/protobuf/releases
    goto end
)

REM Generate Go stubs
echo.
echo Generating Go protobuf stubs...
protoc ^
    -I="%PROTO_DIR%" ^
    --go_out="%INGESTION_WORKER_OUTPUT%" ^
    --go-grpc_out="%INGESTION_WORKER_OUTPUT%" ^
    "%PROTO_DIR%document_service.proto"

if errorlevel 1 (
    echo [ERROR] Failed to generate Go stubs
    exit /b 1
)

echo [SUCCESS] Go stubs generated in %INGESTION_WORKER_OUTPUT%

:end
echo.
echo [COMPLETE] Protocol buffer compilation finished!
endlocal
