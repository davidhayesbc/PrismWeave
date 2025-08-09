# PrismWeave Unified Build System

This document describes the unified, standard build system for PrismWeave that handles all components in a consistent, simple way.

## Overview

The unified build system replaces the complex, component-specific build scripts with a single, standard esbuild-based system that:

✅ **Handles all components**: Browser extension, bookmarklet, and dev tools
✅ **Standard tooling**: Uses esbuild for fast, reliable builds
✅ **Individual builds**: Can build components separately or all together  
✅ **Web publishing**: Supports deployment to websites
✅ **Simple configuration**: No complex hybrid approaches
✅ **Path-aware**: Works from root directory or component directories

## Components

### 🌐 Browser Extension
- **Service Worker**: Background script with ES6 modules support
- **Content Scripts**: Page content extraction and processing
- **Popup**: Extension popup interface  
- **Options**: Settings and configuration pages
- **Bookmarklet Options**: Bookmarklet generator and help

### 📖 Bookmarklet  
- **Runtime**: Main bookmarklet functionality (`enhanced-runtime-compatible.ts`)
- **Loader**: Minimal bootstrap loader (`hybrid-loader.ts`)
- **Standalone**: Self-contained bookmarklet version

### 🛠️ Dev Tools
- **Capture CLI**: Command-line tool for testing page capture
- **Node.js compatible**: Built for server-side execution

## Build Commands

### Root Level Commands
```bash
# Build everything
npm run build

# Build specific components
npm run build:browser-extension
npm run build:bookmarklet  
npm run build:dev-tools

# Build for web deployment
npm run build:web

# Clean all outputs
npm run clean

# Serve web build locally
npm run serve:web
```

### Component Level Commands
```bash
# From browser-extension directory
cd browser-extension
npm run build              # Build just the browser extension
npm run build:bookmarklet  # Build just the bookmarklet
npm run clean             # Clean browser extension outputs

# From dev-tools directory  
cd browser-extension/dev-tools
npm run build             # Build just the dev tools
```

## File Structure

### Input Structure
```
PrismWeave/
├── build.js                          # Unified build system
├── browser-extension/
│   ├── src/
│   │   ├── background/               # Service worker
│   │   ├── content/                  # Content scripts
│   │   ├── popup/                    # Extension popup
│   │   ├── options/                  # Settings pages
│   │   ├── bookmarklet/             # Bookmarklet source
│   │   └── styles/                   # Shared CSS
│   ├── icons/                        # Extension icons
│   └── manifest.json                 # Extension manifest
└── browser-extension/dev-tools/
    ├── capture-cli.ts               # CLI tool source
    └── README.md
```

### Output Structure
```
PrismWeave/
├── browser-extension/dist/           # Built browser extension
│   ├── background/service-worker.js
│   ├── content/content-script.js  
│   ├── popup/popup.js
│   ├── options/options.js
│   ├── bookmarklet/
│   │   ├── runtime.js               # Hosted version
│   │   ├── loader.js                # Minimal loader
│   │   └── standalone.js            # Self-contained
│   ├── styles/shared-ui.css
│   ├── icons/
│   └── manifest.json
├── browser-extension/dev-tools/dist/
│   └── capture-cli.js               # Built CLI tool
└── dist/web/                        # Web deployment ready
    ├── index.html                   # Landing page
    ├── extension/                   # Extension files
    └── bookmarklet/                 # Bookmarklet files
```

## Key Features

### ✅ Fixes Previous Issues
- **Missing entry points**: Fixed `src/bookmarklet/runtime.ts` → uses existing `enhanced-runtime-compatible.ts`
- **Complex build scripts**: Replaced `build-simple.js` and `build-hybrid-bookmarklet.js` with unified system
- **Inconsistent tooling**: Standardized on esbuild across all components
- **Path issues**: Smart path resolution works from any directory

### ✅ Standard Build Process
- **esbuild**: Fast, reliable bundling with TypeScript support
- **Source maps**: Generated in development mode
- **Minification**: Applied in production mode (`NODE_ENV=production`)
- **Error handling**: Clear error reporting with file sizes
- **Asset copying**: HTML, CSS, and icon files copied automatically

### ✅ Web Deployment Ready
- **Static hosting**: All files ready for static web hosting
- **CDN friendly**: Optimized file structure for CDN deployment  
- **Landing page**: Auto-generated index.html with component links
- **Self-contained**: No server-side dependencies required

## Usage Examples

### Development Workflow
```bash
# Start fresh development
npm run clean
npm run build

# Build and test specific component
npm run build:bookmarklet
cd browser-extension && npm run serve:local

# Build for production deployment
NODE_ENV=production npm run build
npm run build:web
```

### Publishing to Web
```bash
# Build everything for web
npm run build:web

# Files ready for deployment at:
# ./dist/web/

# Serve locally to test
cd dist/web
python -m http.server 8080
# Visit: http://localhost:8080
```

### Component Development
```bash
# Working on browser extension
cd browser-extension
npm run build
# Test extension in Chrome

# Working on bookmarklet  
npm run build:bookmarklet
# Test bookmarklet files in dist/bookmarklet/

# Working on dev tools
cd browser-extension/dev-tools  
npm run build
node dist/capture-cli.js --help
```

## Migration from Old System

### Removed Files
- ❌ `scripts/build-simple.js` - Replaced by unified system
- ❌ `scripts/build-hybrid-bookmarklet.js` - Replaced by unified system  
- ❌ Complex build configurations - Simplified to standard esbuild

### Updated Files
- ✅ `package.json` - Updated scripts to use unified system
- ✅ `browser-extension/package.json` - Simplified build scripts
- ✅ `dev-tools/package.json` - Standardized build process

### Benefits of Migration
- 🚀 **Faster builds**: esbuild is significantly faster than webpack
- 🔧 **Simpler maintenance**: One build system instead of multiple scripts
- 📦 **Standard tooling**: Uses industry-standard esbuild
- 🌐 **Web-ready**: Built-in support for web deployment
- 🛠️ **Better DX**: Clear error messages and progress reporting

## Troubleshooting

### Common Issues

**Build fails with "Could not resolve" error**
```bash
# Make sure you're in the right directory
pwd
# Should be either /PrismWeave or /PrismWeave/browser-extension

# Clean and rebuild
npm run clean
npm run build
```

**Assets not copying**
```bash
# Check if source files exist
ls -la browser-extension/src/popup/popup.html
ls -la browser-extension/icons/

# Rebuild with verbose output
node build.js build --verbose
```

**Web build missing files**
```bash
# Ensure components are built first
npm run build
npm run build:web

# Check web output
ls -la dist/web/
```

### Getting Help

1. **Check build output**: Look for specific error messages
2. **Use verbose mode**: Add `--verbose` flag for detailed logging  
3. **Verify file paths**: Ensure source files exist at expected locations
4. **Check dependencies**: Make sure `npm install` completed successfully

## Future Enhancements

- [ ] Watch mode for development (`npm run dev`)
- [ ] Production optimizations (tree shaking, code splitting)
- [ ] Source map uploads for error tracking
- [ ] Automated testing integration
- [ ] Bundle analysis and optimization reports
