#!/usr/bin/env python3
"""
PrismWeave RAG API Server Launcher
Automatically sets up environment and starts the RAG server
"""

import subprocess
import sys
import os
from pathlib import Path

def check_uv_available():
    """Check if uv is available"""
    try:
        subprocess.run(['uv', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_dependencies():
    """Install API server dependencies using uv"""
    print("🔧 Installing API server dependencies...")
    
    if check_uv_available():
        cmd = ['uv', 'pip', 'install', '-r', 'requirements-api.txt']
        print(f"Running: {' '.join(cmd)}")
    else:
        print("⚠️  uv not found, falling back to pip")
        cmd = ['pip', 'install', '-r', 'requirements-api.txt']
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_ollama_running():
    """Check if Ollama is running"""
    import httpx
    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
            return True
    except:
        pass
    
    print("⚠️  Ollama is not running. Please start Ollama first:")
    print("   ollama serve")
    return False

def check_vector_db():
    """Check if vector database exists"""
    vector_db_path = Path("src/vector_db")
    if vector_db_path.exists():
        print("✅ Vector database found")
        return True
    else:
        print("⚠️  Vector database not found. You may need to process documents first:")
        print("   python cli/prismweave.py process /path/to/docs --add-to-vector")
        return True  # Not critical for startup

def start_server(host="127.0.0.1", port=8000, log_level="info"):
    """Start the RAG API server"""
    print(f"🚀 Starting PrismWeave RAG API Server on {host}:{port}")
    
    cmd = [
        'python', '-m', 'src.api.rag_server',
        '--host', host,
        '--port', str(port),
        '--log-level', log_level
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🎯 PrismWeave RAG Server Launcher")
    print("=" * 40)
    
    # Change to ai-processing directory
    script_dir = Path(__file__).parent
    ai_processing_dir = script_dir.parent / "ai-processing"
    
    if ai_processing_dir.exists():
        os.chdir(ai_processing_dir)
        print(f"📁 Working directory: {ai_processing_dir}")
    else:
        print(f"❌ ai-processing directory not found: {ai_processing_dir}")
        sys.exit(1)
    
    # Check prerequisites
    print("\n🔍 Checking prerequisites...")
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check Ollama
    if not check_ollama_running():
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Check vector database
    check_vector_db()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Start PrismWeave RAG API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"])
    parser.add_argument("--install-langchain", action="store_true", help="Install LangChain dependencies")
    
    args = parser.parse_args()
    
    # Install LangChain if requested
    if args.install_langchain:
        print("\n🔧 Installing LangChain dependencies...")
        if check_uv_available():
            cmd = ['uv', 'pip', 'install', 'langchain', 'langchain-community', 'langchain-chroma', 'langchain-ollama']
        else:
            cmd = ['pip', 'install', 'langchain', 'langchain-community', 'langchain-chroma', 'langchain-ollama']
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ LangChain dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to install LangChain: {e}")
    
    # Start the server
    print(f"\n🚀 Starting server...")
    print(f"   OpenAI API: http://{args.host}:{args.port}/v1/chat/completions")
    print(f"   RAG Status: http://{args.host}:{args.port}/rag/status")
    print(f"   Health: http://{args.host}:{args.port}/health")
    print("\n   Press Ctrl+C to stop\n")
    
    start_server(args.host, args.port, args.log_level)

if __name__ == "__main__":
    main()
