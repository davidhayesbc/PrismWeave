@echo off
echo 🚀 Setting up PrismWeave RAG Integration
echo.

REM Check if we're in the right directory
if not exist "config.yaml" (
    echo ❌ Error: Please run this script from the ai-processing directory
    echo    Expected to find config.yaml in current directory
    pause
    exit /b 1
)

echo ✅ Found config.yaml - correct directory confirmed
echo.

echo 📦 Installing API server dependencies...
pip install -r requirements-api.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully
echo.

echo 🔍 Checking Ollama connection...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Ollama not responding on localhost:11434
    echo    Please ensure Ollama is running before starting the RAG server
) else (
    echo ✅ Ollama is running and accessible
)
echo.

echo 🗃️ Checking vector database...
python cli\prismweave.py vector-stats
echo.

echo 🏁 Setup complete! Next steps:
echo.
echo 1. Start the RAG server:
echo    python scripts\start_rag_server.py
echo.
echo 2. Test the server:
echo    Open: http://localhost:8000/health
echo.
echo 3. Use with Open WebUI:
echo    cd docker
echo    docker-compose -f docker-compose.open-webui.yml up -d
echo    Open: http://localhost:3000
echo.
echo 4. See full setup guide:
echo    RAG_INTEGRATION_GUIDE.md
echo.
pause
