#!/usr/bin/env pwsh
# Install script for PrismWeave VS Code Extension
# Handles cross-platform ONNX Runtime installation issues

param(
    [switch]$SkipOptional,
    [switch]$Verbose
)

Write-Host "PrismWeave VS Code Extension - Installation Script" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green

$ErrorActionPreference = "Continue"

function Write-VerboseLog {
    param($Message)
    if ($Verbose) {
        Write-Host "[VERBOSE] $Message" -ForegroundColor Cyan
    }
}

function Test-ONNXRuntimeCompatibility {
    Write-VerboseLog "Testing ONNX Runtime compatibility..."
    
    # Check platform
    $platform = $env:RUNNER_OS ?? $env:OS
    $arch = $env:RUNNER_ARCH ?? [System.Environment]::OSVersion.Platform
    
    Write-VerboseLog "Platform: $platform, Architecture: $arch"
    
    # ONNX Runtime has known issues on certain platforms
    $incompatiblePlatforms = @('Linux')  # Add more as needed
    
    if ($platform -in $incompatiblePlatforms) {
        Write-Host "⚠️  Platform $platform may have ONNX Runtime compatibility issues" -ForegroundColor Yellow
        return $false
    }
    
    return $true
}

function Install-Dependencies {
    Write-Host "Installing dependencies..." -ForegroundColor Blue
    
    # Clean install
    if (Test-Path "node_modules") {
        Write-VerboseLog "Removing existing node_modules..."
        Remove-Item "node_modules" -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    if (Test-Path "package-lock.json") {
        Write-VerboseLog "Removing existing package-lock.json..."
        Remove-Item "package-lock.json" -Force -ErrorAction SilentlyContinue
    }
    
    # Install main dependencies first
    Write-Host "Installing main dependencies..." -ForegroundColor Blue
    npm install --production=false --audit=false --fund=false
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Main dependency installation failed" -ForegroundColor Red
        return $false
    }
    
    # Try to install optional dependencies
    if (-not $SkipOptional) {
        Write-Host "Installing optional dependencies..." -ForegroundColor Blue
        
        # Test ONNX Runtime compatibility first
        $isCompatible = Test-ONNXRuntimeCompatibility
        
        if ($isCompatible) {
            Write-VerboseLog "Attempting ONNX Runtime installation..."
            npm install onnxruntime-node --save-optional --ignore-scripts --audit=false --fund=false
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ ONNX Runtime installed successfully" -ForegroundColor Green
            } else {
                Write-Host "⚠️  ONNX Runtime installation failed (this is OK for CI/testing)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "⚠️  Skipping ONNX Runtime installation due to platform compatibility" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  Skipping optional dependencies" -ForegroundColor Yellow
    }
    
    return $true
}

function Test-Installation {
    Write-Host "Testing installation..." -ForegroundColor Blue
    
    # Test TypeScript compilation
    Write-VerboseLog "Testing TypeScript compilation..."
    npm run compile
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ TypeScript compilation failed" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✅ TypeScript compilation successful" -ForegroundColor Green
    
    # Test that required packages are available
    $requiredPackages = @('chromadb', 'axios', 'cheerio', 'marked')
    foreach ($package in $requiredPackages) {
        if (-not (Test-Path "node_modules/$package")) {
            Write-Host "❌ Required package missing: $package" -ForegroundColor Red
            return $false
        }
    }
    
    Write-Host "✅ All required packages are available" -ForegroundColor Green
    return $true
}

function Show-Summary {
    Write-Host "`nInstallation Summary:" -ForegroundColor Green
    Write-Host "=====================" -ForegroundColor Green
    
    # Check what's installed
    $hasONNX = Test-Path "node_modules/onnxruntime-node"
    
    if ($hasONNX) {
        Write-Host "✅ ONNX Runtime: Available" -ForegroundColor Green
        Write-Host "   Local AI models will work" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  ONNX Runtime: Not Available" -ForegroundColor Yellow
        Write-Host "   Extension will work but without local AI models" -ForegroundColor Gray
        Write-Host "   This is expected in CI environments" -ForegroundColor Gray
    }
    
    Write-Host "✅ Core dependencies: Installed" -ForegroundColor Green
    Write-Host "✅ TypeScript compilation: Working" -ForegroundColor Green
    
    Write-Host "`n🎉 Installation completed successfully!" -ForegroundColor Green
}

# Main execution
try {
    $success = Install-Dependencies
    if (-not $success) {
        exit 1
    }
    
    $success = Test-Installation
    if (-not $success) {
        exit 1
    }
    
    Show-Summary
    exit 0
}
catch {
    Write-Host "❌ Installation failed with error: $_" -ForegroundColor Red
    exit 1
}
