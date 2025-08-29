# PrismWeave Local Bookmarklet Development Server
# This script starts a local HTTP server for testing bookmarklets

param(
    [Parameter(HelpMessage="Port number to use (default: 8080)")]
    [int]$Port = 8080,
    
    [Parameter(HelpMessage="Auto-open browser (default: true)")]
    [bool]$OpenBrowser = $true
)

Write-Host "🌟 PrismWeave Local Bookmarklet Development Server" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# Check if we're in the correct directory
$currentDir = Get-Location
$expectedPath = "*\PrismWeave\browser-extension"

if ($currentDir -notlike $expectedPath -and $currentDir -notlike "*\PrismWeave") {
    Write-Host "⚠️  Warning: You might not be in the correct directory." -ForegroundColor Yellow
    Write-Host "   Expected: PrismWeave\browser-extension or PrismWeave root" -ForegroundColor Yellow
    Write-Host "   Current:  $currentDir" -ForegroundColor Yellow
    Write-Host ""
}

# Find the local generator file
$generatorPath = ""
$searchPaths = @(
    ".\dev-tools\local-bookmarklet-generator.html",
    ".\browser-extension\dev-tools\local-bookmarklet-generator.html",
    ".\local-bookmarklet-generator.html"
)

foreach ($path in $searchPaths) {
    if (Test-Path $path) {
        $generatorPath = Resolve-Path $path
        break
    }
}

if (-not $generatorPath) {
    Write-Host "❌ Error: Could not find local-bookmarklet-generator.html" -ForegroundColor Red
    Write-Host "   Please run this script from the PrismWeave directory or browser-extension directory" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Found generator: $generatorPath" -ForegroundColor Green

# Check if port is available
try {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $Port)
    $listener.Start()
    $listener.Stop()
    Write-Host "🔌 Port $Port is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Port $Port is already in use. Trying another port..." -ForegroundColor Yellow
    $Port = $Port + 1
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $Port)
        $listener.Start()
        $listener.Stop()
        Write-Host "🔌 Using port $Port instead" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error: Could not find an available port" -ForegroundColor Red
        exit 1
    }
}

$url = "http://localhost:$Port"
$generatorUrl = "$url/local-bookmarklet-generator.html"

# Check if Python is available
$pythonCmd = $null
$pythonCommands = @("python", "python3", "py")

foreach ($cmd in $pythonCommands) {
    try {
        $version = & $cmd --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Host "🐍 Found Python: $version" -ForegroundColor Green
            break
        }
    } catch {
        # Command not found, continue
    }
}

if (-not $pythonCmd) {
    Write-Host "❌ Error: Python not found in PATH" -ForegroundColor Red
    Write-Host "   Please install Python or ensure it's in your PATH" -ForegroundColor Red
    Write-Host "   Download from: https://python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Determine the directory to serve from
$serverDir = Split-Path $generatorPath -Parent
if (-not $serverDir) {
    $serverDir = "."
}

Write-Host "🚀 Starting local development server..." -ForegroundColor Cyan
Write-Host "   Directory: $serverDir" -ForegroundColor Gray
Write-Host "   Port:      $Port" -ForegroundColor Gray
Write-Host "   URL:       $generatorUrl" -ForegroundColor Gray
Write-Host ""

# Create a simple index.html if it doesn't exist
$indexPath = Join-Path $serverDir "index.html"
if (-not (Test-Path $indexPath)) {
    $indexContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>PrismWeave Development Server</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; padding: 2rem; }
        .container { max-width: 600px; margin: 0 auto; }
        .link { display: inline-block; background: #007bff; color: white; padding: 1rem 2rem; text-decoration: none; border-radius: 6px; margin: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌟 PrismWeave Development Server</h1>
        <p>Local development tools for PrismWeave bookmarklets</p>
        <a href="local-bookmarklet-generator.html" class="link">📚 Bookmarklet Generator</a>
        <p><small>Server running on port $Port</small></p>
    </div>
</body>
</html>
"@
    Set-Content -Path $indexPath -Value $indexContent -Encoding UTF8
    Write-Host "📄 Created index.html" -ForegroundColor Green
}

# Open browser if requested
if ($OpenBrowser) {
    Write-Host "🌐 Opening browser..." -ForegroundColor Green
    Start-Process $generatorUrl
}

Write-Host "✨ Development server is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Quick Links:" -ForegroundColor Cyan
Write-Host "   Generator:  $generatorUrl" -ForegroundColor White
Write-Host "   Server:     $url" -ForegroundColor White
Write-Host ""
Write-Host "🛠️  Development Workflow:" -ForegroundColor Cyan
Write-Host "   1. Open the generator in your browser" -ForegroundColor White
Write-Host "   2. Fill in your GitHub token and repository" -ForegroundColor White
Write-Host "   3. Generate your bookmarklet" -ForegroundColor White
Write-Host "   4. Test it on the built-in test page" -ForegroundColor White
Write-Host "   5. Use debug tools to analyze results" -ForegroundColor White
Write-Host ""
Write-Host "⏹️  Press Ctrl+C to stop the server" -ForegroundColor Yellow

try {
    # Start the Python HTTP server
    Push-Location $serverDir
    & $pythonCmd -m http.server $Port
} catch {
    Write-Host "❌ Server error: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Pop-Location
    Write-Host ""
    Write-Host "👋 Development server stopped" -ForegroundColor Yellow
}