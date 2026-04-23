#!/usr/bin/env python3
"""
Protocol Buffer Compilation Script for Windows/Linux/macOS
Generates Python and Go stubs from proto definitions
Handles spaces in paths correctly with protobuf version compatibility
"""

import os
import sys
import subprocess
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def log_info(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def log_warn(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

def log_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def fix_protobuf_version():
    """Install and manage protobuf version compatibility"""
    print("\n📦 Checking protobuf installation...")
    try:
        import protobuf
        version = protobuf.__version__
        major = int(version.split('.')[0])
        
        if major >= 6:
            log_warn(f"Protobuf {version} is incompatible with downstream packages.")
            print("   Installing compatible protobuf version (5.26.1+)...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", 
                 "protobuf>=5.26.1,<6.0.0"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                log_info("Protobuf downgraded to compatible version")
                return True
            else:
                log_error("Failed to downgrade protobuf")
                if result.stderr:
                    print(result.stderr)
                return False
        else:
            log_info(f"Protobuf {version} is compatible")
            return True
    except ImportError:
        log_warn("Protobuf not installed. Installing now...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "protobuf>=5.26.1,<6.0.0"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            log_info("Protobuf installed successfully")
            return True
        else:
            log_error("Failed to install protobuf")
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        log_warn(f"Could not verify protobuf version: {e}")
        print("   Attempting to install protobuf...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "protobuf>=5.26.1,<6.0.0"],
            capture_output=True, text=True
        )
        return result.returncode == 0

def main():
    # Get script directory
    script_dir = Path(__file__).parent.absolute()
    proto_dir = str(script_dir)
    api_gateway_output = str(script_dir.parent / "api-gateway" / "app" / "pb")
    ingestion_worker_output = str(script_dir.parent / "ingestion-worker" / "pb")
    
    print("=" * 70)
    print("🔄 Protocol Buffer Compilation Script")
    print("=" * 70)
    
    # Fix protobuf version first
    if not fix_protobuf_version():
        return False
    
    # Create output directories
    print("\n📁 Creating output directories...")
    Path(api_gateway_output).mkdir(parents=True, exist_ok=True)
    Path(ingestion_worker_output).mkdir(parents=True, exist_ok=True)
    log_info("Output directories ready")
    
    # Check Python prerequisites
    print("\n🐍 Checking Python prerequisites...")
    try:
        import grpc_tools
        log_info("grpcio-tools is installed")
    except ImportError:
        log_warn("grpcio-tools not found. Installing...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "grpcio-tools"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            log_error("Failed to install grpcio-tools")
            print(result.stderr)
            return False
        log_info("grpcio-tools installed successfully")
    
    # Generate Python stubs - use list format for proper path handling (no shell=True!)
    print("\n🔧 Generating Python protobuf stubs...")
    proto_file = os.path.join(proto_dir, "document_service.proto")
    
    python_cmd = [
        sys.executable,
        "-m", "grpc_tools.protoc",
        f"-I{proto_dir}",
        f"--python_out={api_gateway_output}",
        f"--grpc_python_out={api_gateway_output}",
        proto_file
    ]
    
    try:
        result = subprocess.run(python_cmd, check=True, capture_output=True, text=True)
        # Create __init__.py
        init_file = Path(api_gateway_output) / "__init__.py"
        init_file.touch()
        log_info(f"Python stubs generated in {api_gateway_output}")
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to generate Python stubs")
        print(f"\nCommand: {' '.join(python_cmd)}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        log_error(f"Error during Python compilation: {e}")
        return False
    
    # Check for protoc (Go)
    print("\n🔍 Checking for protoc compiler...")
    try:
        result = subprocess.run(
            ["protoc", "--version"],
            capture_output=True, text=True, check=True
        )
        log_info(f"protoc found: {result.stdout.strip()}")
        
        # Generate Go stubs
        print("\n🔧 Generating Go protobuf stubs...")
        go_cmd = [
            "protoc",
            f"-I={proto_dir}",
            f"--go_out={ingestion_worker_output}",
            f"--go-grpc_out={ingestion_worker_output}",
            proto_file
        ]
        
        try:
            result = subprocess.run(go_cmd, check=True, capture_output=True, text=True)
            log_info(f"Go stubs generated in {ingestion_worker_output}")
        except subprocess.CalledProcessError as e:
            log_warn("Go stubs generation failed (skipping - this is optional)")
            print(f"\nCommand attempted: {' '.join(go_cmd)}")
            if e.stderr and "protoc-gen-go" in e.stderr:
                print("\n⚠️  Missing Go plugins for protoc")
                print("   Go stubs are optional. Install plugins with:")
                print("   • go install github.com/protocolbuffers/protobuf-go/cmd/protoc-gen-go@latest")
                print("   • go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest")
                print("   Then ensure $GOPATH/bin is in your PATH")
                print("\n   Or use: go get -u google.golang.org/grpc/cmd/protoc-gen-go-grpc")
            elif e.stderr:
                print(f"Error: {e.stderr}")
    
    except FileNotFoundError:
        log_warn("protoc compiler not found. Skipping Go stub generation.")
        print("   Install from: https://github.com/protocolbuffers/protobuf/releases")
        print("   Or use: brew install protobuf (macOS)")
        print("   Or use: apt-get install protobuf-compiler (Linux)")
    except subprocess.CalledProcessError:
        log_warn("protoc not working properly. Skipping Go stub generation.")
    
    print("\n" + "=" * 70)
    log_info("✅ Protocol buffer compilation complete!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
