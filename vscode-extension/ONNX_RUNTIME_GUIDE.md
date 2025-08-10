# ONNX Runtime Installation Guide for PrismWeave VS Code Extension

## Problem Description

The `onnxruntime-node` package is an optional dependency that provides local AI model inference capabilities. However, it has platform-specific installation issues, particularly on Linux systems where it may fail to find Windows-specific CUDA libraries.

**Error Example:**
```
Error: Failed to find runtimes/win-x64/native/libonnxruntime_providers_cuda.so in NuGet package
```

## Solution Overview

We've implemented a robust solution that handles cross-platform compatibility issues:

1. **Optional Dependency Pattern**: ONNX Runtime is configured as an optional dependency
2. **Graceful Fallback**: The extension works with or without ONNX Runtime
3. **Dynamic Loading**: Runtime detection and loading of ONNX Runtime
4. **Cross-Platform CI**: GitHub Actions configuration for all platforms

## Installation Methods

### Method 1: Automated Script (Recommended)

Use the provided PowerShell script that handles platform detection:

```powershell
# Windows/Development
.\scripts\install.ps1 -Verbose

# CI/Production (Skip optional dependencies)
.\scripts\install.ps1 -SkipOptional -Verbose
```

### Method 2: Manual Installation

```bash
# Install main dependencies
npm install --ignore-optional

# Try to install ONNX Runtime (may fail on some platforms)
npm install onnxruntime-node --save-optional --ignore-scripts
```

### Method 3: Platform-Specific Installation

```bash
# Windows (Usually works)
npm install

# Linux/macOS (Skip optional deps)
npm install --ignore-optional
```

## Code Integration

### Type-Safe ONNX Runtime Usage

```typescript
import { AIModelManager } from './ai/onnx-runtime';

const modelManager = new AIModelManager();

// Check if ONNX Runtime is available
if (modelManager.isONNXAvailable) {
    console.log('✅ Local AI models available');
    console.log(modelManager.providerInfo);
    
    // Load and use models
    await modelManager.loadModel('my-model', './path/to/model.onnx');
    const result = await modelManager.runInference('my-model', inputs);
} else {
    console.log('⚠️ ONNX Runtime not available - using external AI services');
    // Fallback to external AI services
}
```

### Dynamic Import Pattern

```typescript
// Graceful loading with fallback
class ONNXRuntimeProvider {
    private async _initializeORT(): Promise<void> {
        try {
            this._ort = await import('onnxruntime-node');
            this._isAvailable = true;
        } catch (error) {
            // Graceful fallback - extension continues to work
            this._isAvailable = false;
        }
    }
}
```

## Platform Compatibility Matrix

| Platform | ONNX Runtime | Status | Notes |
|----------|--------------|--------|-------|
| Windows x64 | ✅ Available | ✅ Full Support | All execution providers |
| Windows ARM | ⚠️ Limited | ⚠️ CPU Only | Limited provider support |
| macOS Intel | ✅ Available | ✅ Full Support | CPU + CoreML |
| macOS Apple Silicon | ✅ Available | ✅ Full Support | CPU + CoreML |
| Linux x64 | ❌ Installation Issues | ⚠️ Fallback Mode | Use external AI services |
| Linux ARM | ❌ Not Supported | ⚠️ Fallback Mode | Use external AI services |

## GitHub Actions Configuration

The CI workflow handles cross-platform installation:

```yaml
- name: Install dependencies (Windows)
  if: runner.os == 'Windows'
  shell: pwsh
  working-directory: vscode-extension
  run: ./scripts/install.ps1 -Verbose

- name: Install dependencies (Linux/macOS - Skip Optional)
  if: runner.os != 'Windows'
  shell: pwsh
  working-directory: vscode-extension
  run: ./scripts/install.ps1 -SkipOptional -Verbose
```

## Troubleshooting

### Common Issues

1. **"Failed to find runtimes/win-x64/native/..." on Linux**
   - **Solution**: Use `-SkipOptional` flag or `--ignore-optional`
   - **Why**: Linux tries to install Windows-specific binaries

2. **"ort.InferenceSession.getAvailableProviders is not a function"**
   - **Solution**: API compatibility is handled in the code
   - **Why**: Different ONNX Runtime versions have different APIs

3. **Package installation succeeds but runtime fails**
   - **Solution**: Use dynamic import with try/catch
   - **Why**: Binary compatibility issues at runtime

### Development Tips

1. **Local Development**: Install normally, ONNX Runtime should work on Windows/macOS
2. **CI/CD**: Always use `--ignore-optional` on Linux
3. **Production**: Design features to work with or without ONNX Runtime
4. **Testing**: Mock ONNX Runtime for unit tests

## Extension Architecture

```
Extension Startup
       │
       ├─► Try Load ONNX Runtime
       │   ├─► Success: Local AI Available
       │   └─► Failure: External AI Only
       │
       ├─► Initialize UI (Always works)
       ├─► Setup Document Indexing (Always works)
       └─► Configure AI Provider (Adaptive)
```

## Benefits of This Approach

1. **Cross-Platform**: Extension works on all platforms
2. **Graceful Degradation**: Features adapt to available capabilities  
3. **Developer Friendly**: Clear error messages and fallbacks
4. **CI/CD Ready**: Handles installation issues automatically
5. **User Transparent**: Users don't see installation failures

## Configuration Options

Users can configure the AI provider in VS Code settings:

```json
{
  "prismweave.model.provider": "onnx",        // or "custom" for external
  "prismweave.model.name": "phi-3-mini",     // Model name
  "prismweave.web.enabled": true             // Fallback to web services
}
```

## Future Improvements

1. **WebAssembly ONNX**: Use `onnxruntime-web` for better cross-platform support
2. **Model Optimization**: Pre-quantized models for better performance
3. **Provider Detection**: Automatic detection of available execution providers
4. **Fallback Strategies**: Multiple AI service options

This solution ensures the VS Code extension works reliably across all platforms while providing optimal performance where ONNX Runtime is available.
