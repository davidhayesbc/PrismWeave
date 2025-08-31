# 🏗️ PrismWeave Build System Overview

## Simplified Build Architecture

The build system has been streamlined to eliminate complexity and redundancy.

## 📦 Available Builds

### 1. Browser Extension (`npm run build`)

- **Script**: `scripts/build-simple.js`
- **Purpose**: Builds the complete Chrome/Edge browser extension
- **Output**: `dist/` directory with extension files
- **Includes**:
  - Service worker
  - Content scripts
  - Popup and options pages
  - Injectable scripts for bookmarklet
- **Usage**:
  ```bash
  npm run build        # Development build
  npm run build:prod   # Production build (minified)
  ```

### 2. Bookmarklet Website (`npm run build:bookmarklet`)

- **Script**: `scripts/build-bookmarklet.js`
- **Purpose**: Builds the personal bookmarklet generator website
- **Output**: `dist/bookmarklet/` directory
- **Includes**:
  - HTML pages (generator, help, install, etc.)
  - CSS stylesheets
  - JavaScript for bookmarklet generation
- **Usage**:
  ```bash
  npm run build:bookmarklet
  ```

## 🛠️ Development Tools

### Development Server (`npm run dev`)

- **Script**: `scripts/serve-dev.js`
- **Purpose**: Local development with live reloading
- **Features**:
  - Auto-rebuild on file changes
  - Live browser refresh
  - File watching for HTML/CSS/TypeScript
  - Beautiful file browser interface
- **Usage**:
  ```bash
  npm run dev          # Start on localhost:3000
  npm run dev:port 8080 # Custom port
  npm run dev:quiet    # Quiet mode
  ```

## 🧹 What Was Removed

### Removed Scripts:

- ❌ `build-injectable.js` - **Redundant** (handled by build-simple.js)
- ❌ `serve-local.js` - **Replaced** by serve-dev.js
- ❌ `../build.js` references - **Simplified** to direct script calls

### Removed npm Scripts:

- ❌ `build:injectable` - Redundant
- ❌ `build:all` - Over-complex
- ❌ `build:fast` / `build:fast:prod` - Unnecessary variants
- ❌ `test:ci` - Simplified to just test/coverage
- ❌ `serve:local` - Replaced by dev commands
- ❌ `zip` - Renamed to `package` for clarity

## 📋 Current npm Scripts

### Core Commands:

```bash
npm run build              # Build browser extension
npm run build:prod         # Production build (minified)
npm run build:bookmarklet  # Build bookmarklet website
npm run clean              # Clean dist directory
npm run package            # Build and package extension
```

### Development:

```bash
npm run dev                # Start development server
npm run dev:port 8080      # Dev server on custom port
npm run dev:quiet          # Dev server in quiet mode
```

### Testing & Quality:

```bash
npm run test               # Run tests
npm run test:watch         # Run tests in watch mode
npm run test:coverage      # Run tests with coverage
npm run lint               # Lint TypeScript/JavaScript
npm run lint:fix           # Fix linting issues
npm run format             # Format code with Prettier
npm run format:check       # Check code formatting
```

## 🎯 Simplified Workflow

### For Browser Extension Development:

1. `npm run build` - Build extension
2. Load `dist/` in Chrome developer mode
3. Test and iterate

### For Bookmarklet Website Development:

1. `npm run dev` - Start development server
2. Open `http://localhost:3000`
3. Edit files and see changes live
4. `npm run build:bookmarklet` - Final build

### For Production Release:

1. `npm run build:prod` - Production browser extension
2. `npm run build:bookmarklet` - Bookmarklet website
3. `npm run package` - Create extension package

## 🔧 Build Configuration

### Environment Variables:

- `NODE_ENV=production` - Enable production optimizations
- `PRISMWEAVE_INJECTABLE_URL` - Custom injectable script URL

### Build Features:

- **TypeScript compilation** with esbuild
- **CSS processing** and optimization
- **IIFE format** for Chrome extension compatibility
- **Source maps** in development
- **Minification** in production
- **Bundle analysis** and size optimization

## 📁 Output Structure

```
dist/
├── background/           # Service worker
├── content/             # Content scripts
├── popup/               # Extension popup
├── options/             # Extension options
├── injectable/          # Bookmarklet injectable scripts
├── bookmarklet/         # 🌐 Bookmarklet website
│   ├── generator.html
│   ├── help.html
│   ├── install.html
│   ├── index.html
│   └── styles/         # CSS files
└── manifest.json        # Extension manifest
```

## 💡 Key Improvements

1. **Eliminated Redundancy**: Removed duplicate build scripts
2. **Simplified Commands**: Clearer, more intuitive npm scripts
3. **Single Source of Truth**: Each build has one clear script
4. **Better Development**: Enhanced dev server with live reload
5. **Cleaner Architecture**: Logical separation of concerns
6. **Easier Maintenance**: Fewer files to maintain and debug

The build system is now much simpler while maintaining all necessary
functionality! 🎉
