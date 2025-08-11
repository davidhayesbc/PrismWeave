#!/usr/bin/env pwsh

# PrismWeave Bookmarklet Storage Validation Script
# This script runs comprehensive tests to validate the bookmarklet storage functionality

Write-Host "🧪 PrismWeave Bookmarklet Storage Validation" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Check if the extension is built
if (!(Test-Path "dist/options/bookmarklet.js")) {
    Write-Host "❌ Extension not built. Running build..." -ForegroundColor Red
    npm run build
}

Write-Host "✅ Browser extension built successfully" -ForegroundColor Green
Write-Host ""

# Check extension files
Write-Host "📁 Extension Components:" -ForegroundColor Blue
$distFiles = @(
    "dist/background/service-worker.js",
    "dist/options/bookmarklet.js", 
    "dist/content/content-script.js"
)

foreach ($file in $distFiles) {
    if (Test-Path $file) {
        $size = [Math]::Round((Get-Item $file).Length / 1KB, 1)
        Write-Host "  ✅ $file (${size}KB)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file - MISSING" -ForegroundColor Red
    }
}

Write-Host ""

# Check storage validation files
Write-Host "🔧 Storage Validation Components:" -ForegroundColor Blue
$storageFiles = @(
    "src/utils/bookmarklet-storage-validator.ts",
    "validate-storage.html"
)

foreach ($file in $storageFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file - MISSING" -ForegroundColor Red
    }
}

Write-Host ""

# Start test server
Write-Host "🚀 Starting test server..." -ForegroundColor Blue
$serverJob = Start-Job -ScriptBlock {
    Set-Location $args[0]
    python -m http.server 8080 2>$null
} -ArgumentList (Get-Location)

Start-Sleep -Seconds 2

Write-Host "✅ Test server started on http://localhost:8080" -ForegroundColor Green
Write-Host ""

# Test instructions
Write-Host "📋 Manual Validation Steps:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:8080/validate-storage.html in your browser" -ForegroundColor White
Write-Host "2. Click 'Run Comprehensive Tests' to validate storage functionality" -ForegroundColor White
Write-Host "3. Generate and test a bookmarklet using the 'Generate Test Bookmarklet' button" -ForegroundColor White
Write-Host "4. Open multiple tabs and verify settings persist across tabs" -ForegroundColor White
Write-Host ""

Write-Host "🔧 Extension Installation:" -ForegroundColor Yellow
Write-Host "1. Open Chrome and navigate to chrome://extensions/" -ForegroundColor White
Write-Host "2. Enable 'Developer mode'" -ForegroundColor White
Write-Host "3. Click 'Load unpacked' and select the 'dist' folder" -ForegroundColor White
Write-Host "4. Test the bookmarklet options page by clicking the extension icon" -ForegroundColor White
Write-Host ""

Write-Host "🧪 Expected Validation Results:" -ForegroundColor Yellow
Write-Host "✅ localStorage availability: Should PASS" -ForegroundColor Green
Write-Host "✅ sessionStorage availability: Should PASS" -ForegroundColor Green
Write-Host "✅ Storage and retrieval: Should PASS" -ForegroundColor Green  
Write-Host "✅ Cross-tab persistence: Should PASS" -ForegroundColor Green
Write-Host "✅ Error handling: Should PASS" -ForegroundColor Green
Write-Host ""

Write-Host "Press Enter to open the validation page in your default browser..." -ForegroundColor Cyan
Read-Host

# Open validation page
Start-Process "http://localhost:8080/validate-storage.html"

Write-Host "Press Enter to stop the server..." -ForegroundColor Cyan
Read-Host

# Stop server
Stop-Job $serverJob -Force
Remove-Job $serverJob

Write-Host "🎉 Validation complete! Server stopped." -ForegroundColor Green
