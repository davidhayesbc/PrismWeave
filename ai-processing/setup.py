#!/usr/bin/env python3
"""
PrismWeave AI Processing Setup Script
Automated setup for the AI processing pipeline using UV
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(command, description="Running command"):
    """Run a command and handle errors"""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        print(f"   Output: {e.stdout}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_uv_installation():
    """Check if UV is installed and install if not"""
    print("🔧 Checking UV installation...")
    
    if shutil.which("uv"):
        # Check UV version
        try:
            result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
            print(f"   ✅ UV {result.stdout.strip()} found")
            return True
        except:
            print("   ⚠️  UV found but version check failed")
            return True
    
    print("📥 Installing UV...")
    if platform.system() == "Windows":
        # Install UV on Windows using PowerShell
        install_cmd = 'powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"'
    else:
        # Install UV on Unix systems
        install_cmd = 'curl -LsSf https://astral.sh/uv/install.sh | sh'
    
    if run_command(install_cmd, "Installing UV"):
        print("   ✅ UV installed successfully")
        # Add UV to PATH for this session if on Unix
        if platform.system() != "Windows":
            home = os.path.expanduser("~")
            uv_path = f"{home}/.cargo/bin"
            if uv_path not in os.environ.get("PATH", ""):
                os.environ["PATH"] = f"{uv_path}:{os.environ.get('PATH', '')}"
        return True
    else:
        print("   ❌ Failed to install UV")
        print("   💡 Please install UV manually: https://docs.astral.sh/uv/getting-started/installation/")
        return False

def setup_uv_project():
    """Initialize UV project and install dependencies"""
    print("🔧 Setting up UV project...")
    
    # Check if pyproject.toml exists
    if not Path("pyproject.toml").exists():
        print("   ❌ pyproject.toml not found")
        return False
    
    # Initialize UV project if .venv doesn't exist
    if not Path(".venv").exists():
        print("   📦 Creating virtual environment with UV...")
        if not run_command("uv venv", "Creating UV virtual environment"):
            return False
    
    # Install dependencies
    print("   📦 Installing dependencies with UV...")
    if not run_command("uv sync", "Installing dependencies"):
        return False
    
    print("   ✅ UV project setup complete")
    return True

def install_dev_dependencies():
    """Install development dependencies"""
    print("�️ Installing development dependencies...")
    
    if run_command("uv sync --extra dev", "Installing dev dependencies"):
        print("   ✅ Development dependencies installed")
        return True
    else:
        print("   ⚠️  Dev dependencies installation failed (continuing)")
        return True  # Don't fail the whole setup for dev deps

def check_ollama():
    """Check if Ollama is installed and running"""
    print("🤖 Checking Ollama installation...")
    
    # Check if ollama command exists
    try:
        result = subprocess.run("ollama --version", shell=True, capture_output=True, text=True)
        print(f"   ✅ Ollama version: {result.stdout.strip()}")
    except:
        print("   ❌ Ollama not found in PATH")
        print("   📥 Please install Ollama from: https://ollama.ai/")
        return False
    
    # Check if Ollama server is running
    try:
        result = subprocess.run("ollama list", shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ Ollama server is running")
            models = [line.strip() for line in result.stdout.split('\n') if line.strip() and not line.startswith('NAME')]
            if models:
                print(f"   📋 Available models: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
            else:
                print("   ⚠️  No models installed")
            return True
        else:
            print("   ❌ Ollama server not responding")
            return False
    except subprocess.TimeoutExpired:
        print("   ❌ Ollama server timeout")
        return False
    except Exception as e:
        print(f"   ❌ Error checking Ollama: {e}")
        return False

def download_recommended_models():
    """Download recommended models for PrismWeave"""
    print("📥 Downloading recommended AI models...")
    
    models = [
        ("phi3:mini", "Small model for fast tagging and classification"),
        ("nomic-embed-text", "Embedding model for semantic search"),
    ]
    
    for model, description in models:
        print(f"   📥 Downloading {model} ({description})...")
        if run_command(f"ollama pull {model}", f"Downloading {model}"):
            print(f"   ✅ {model} downloaded successfully")
        else:
            print(f"   ⚠️  Failed to download {model}")

def create_directory_structure():
    """Create necessary directory structure"""
    print("📁 Creating directory structure...")
    
    directories = [
        ".prismweave",
        ".prismweave/chroma_db",
        ".prismweave/summaries",
        ".prismweave/metadata",
        "logs"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   📁 Created {directory}")
    
    return True

def test_installation():
    """Test the installation"""
    print("🧪 Testing installation...")
    
    # Test Python imports
    print("   📋 Testing Python imports...")
    test_script = """
import sys
sys.path.insert(0, 'src')

try:
    from src.utils.config import get_config
    from src.models.ollama_client import OllamaClient
    print("✅ Core imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test configuration loading
try:
    config = get_config()
    print("✅ Configuration loaded")
except Exception as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)
"""
    
    with open("test_setup.py", "w") as f:
        f.write(test_script)
    
    # Use UV to run the test
    success = run_command("uv run python test_setup.py", "Testing Python setup")
    
    # Clean up test file
    Path("test_setup.py").unlink(missing_ok=True)
    
    return success

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Activate the UV environment:")
    print("   uv shell")
    print("   # or")
    print("   source .venv/bin/activate  # Unix")
    print("   .venv\\Scripts\\activate     # Windows")
    
    print("\n2. Process your existing documents:")
    print("   uv run python cli/prismweave.py process")
    
    print("\n3. Search your documents:")
    print("   uv run python cli/prismweave.py search \"your query here\"")
    
    print("\n4. Check system status:")
    print("   uv run python cli/prismweave.py status")
    
    print("\n📚 Your document collection:")
    config_path = Path("config.yaml")
    if config_path.exists():
        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
            docs_path = config.get('integration', {}).get('documents_path', '../PrismWeaveDocs/documents')
            print(f"   📁 {docs_path}")
        except:
            print("   📁 ../PrismWeaveDocs/documents (default)")
    
    print("\n🔧 Configuration file: config.yaml")
    print("🔍 Logs will be saved to: logs/")
    print("\n🚀 Happy documenting with PrismWeave!")

def main():
    """Main setup function"""
    print("🌟 PrismWeave AI Processing Setup (UV Edition)")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check and install UV
    if not check_uv_installation():
        sys.exit(1)
    
    # Setup UV project
    if not setup_uv_project():
        print("❌ Failed to set up UV project")
        sys.exit(1)
    
    # Install dev dependencies (optional)
    install_dev_dependencies()
    
    # Check Ollama
    ollama_available = check_ollama()
    if not ollama_available:
        print("⚠️  Ollama not available. Some features will be limited.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Download models if Ollama is available
    if ollama_available:
        response = input("Download recommended AI models? This may take several minutes. (Y/n): ")
        if response.lower() != 'n':
            download_recommended_models()
    
    # Create directories
    if not create_directory_structure():
        print("❌ Failed to create directory structure")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
