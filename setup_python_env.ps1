#!/usr/bin/env pwsh
# Setup script for PrismWeave AI Processing environment

Write-Host "🔧 Setting up PrismWeave AI Processing environment..." -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "ai-processing")) {
    Write-Host "❌ Error: Please run this script from the PrismWeave root directory" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "ai-processing\.venv\Scripts\python.exe")) {
    Write-Host "❌ Error: Virtual environment not found at ai-processing\.venv" -ForegroundColor Red
    Write-Host "💡 Tip: Run 'cd ai-processing && uv sync' to create the environment" -ForegroundColor Yellow
    exit 1
}

# Get Python version from virtual environment
$pythonVersion = & "ai-processing\.venv\Scripts\python.exe" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
Write-Host "✅ Python version: $pythonVersion" -ForegroundColor Green

# Check if pytest is installed
$pytestVersion = & "ai-processing\.venv\Scripts\python.exe" -m pytest --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Pytest version: $pytestVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Pytest not found in virtual environment" -ForegroundColor Red
    exit 1
}

# Test pytest discovery
Write-Host "🔍 Testing pytest discovery..." -ForegroundColor Cyan
$testDiscovery = & "ai-processing\.venv\Scripts\python.exe" -m pytest --collect-only "ai-processing\tests" -q 2>&1
if ($LASTEXITCODE -eq 0) {
    $testCount = ($testDiscovery | Select-String "collected").Line -replace ".* (\d+) .*", '$1'
    Write-Host "✅ Discovered $testCount tests successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Pytest discovery failed:" -ForegroundColor Red
    Write-Host $testDiscovery -ForegroundColor Red
    exit 1
}

# Show the exact Python path that VS Code should use
$fullPythonPath = Resolve-Path "ai-processing\.venv\Scripts\python.exe"
Write-Host "" -ForegroundColor White
Write-Host "🎯 VS Code Python Interpreter Path:" -ForegroundColor Cyan
Write-Host "   $fullPythonPath" -ForegroundColor Yellow
Write-Host "" -ForegroundColor White
Write-Host "📋 To configure VS Code:" -ForegroundColor Cyan
Write-Host "   1. Press Ctrl+Shift+P" -ForegroundColor White
Write-Host "   2. Type 'Python: Select Interpreter'" -ForegroundColor White
Write-Host "   3. Select or enter the path above" -ForegroundColor White
Write-Host "   4. Run 'Test: Reset and Reload All Test Data'" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "✅ Environment setup verification complete!" -ForegroundColor Green
