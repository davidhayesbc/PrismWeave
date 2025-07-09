#!/usr/bin/env python3
"""
PrismWeave RAG Server Launcher
Easy startup script for the RAG-enabled API server
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

# Change to the correct directory
script_dir = Path(__file__).parent
ai_processing_dir = script_dir.parent
os.chdir(ai_processing_dir)

# Add the src directory to Python path
src_dir = ai_processing_dir / "src"
sys.path.insert(0, str(src_dir))

def main():
    """Launch the RAG server"""
    print("🚀 Starting PrismWeave RAG API Server...")
    print("📁 Working directory:", ai_processing_dir)
    print("🔧 Configuration: config.yaml")
    print()
    
    # Check if required packages are installed
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn found")
    except ImportError:
        print("❌ Missing dependencies. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn[standard]"])
    
    # Start the server
    try:
        from src.api.rag_server import main as start_server
        start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
