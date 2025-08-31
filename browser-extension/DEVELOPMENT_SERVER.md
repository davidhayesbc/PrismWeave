# 🔧 PrismWeave Development Server

A comprehensive development server for the PrismWeave website with live
reloading, automatic rebuilding, and real-time file watching.

## ✨ Features

- **🔄 Auto-rebuild**: Automatically rebuilds when you save HTML, CSS, or
  TypeScript files
- **📱 Live reload**: Pages refresh automatically after rebuilds
- **👀 File watching**: Monitors `src/bookmarklet/` and `src/styles/`
  directories
- **🚫 No caching**: Always serves fresh content during development
- **📂 File browser**: Built-in file browser with direct access to all pages
- **🎯 Visual indicators**: Shows development mode status in browser
- **📊 Build monitoring**: Real-time console output for build status and file
  changes

## 🚀 Quick Start

### Option 1: Use npm scripts (Recommended)

```bash
# Start development server on port 3000
npm run dev

# Start on a different port
npm run dev:port 8080

# Start in quiet mode (less verbose logging)
npm run dev:quiet
```

### Option 2: Direct command

```bash
# Basic usage - serves on localhost:3000
node scripts/serve-dev.js

# Custom port and host
node scripts/serve-dev.js --port 8080 --host 0.0.0.0

# Disable live reload (just static serving)
node scripts/serve-dev.js --no-reload

# Adjust file watching sensitivity
node scripts/serve-dev.js --watch-interval 1000
```

## 📱 Using the Development Server

1. **Start the server** using any method above
2. **Open your browser** to `http://localhost:3000`
3. **Browse available pages** from the file browser dashboard
4. **Edit files** in `src/bookmarklet/` or `src/styles/`
5. **See changes automatically** - the server will:
   - Detect your file changes
   - Rebuild the project
   - Refresh your browser automatically

## 🎯 Available Pages

Once the server is running, you can access:

- **🏠 File Browser**: `http://localhost:3000/` - Overview and navigation
- **🔧 Generator**: `http://localhost:3000/generator.html` - Bookmarklet
  Generator
- **📖 Help**: `http://localhost:3000/help.html` - Help Documentation
- **📋 Index**: `http://localhost:3000/index.html` - File Index
- **🔌 Install**: `http://localhost:3000/install.html` - Installation Guide

## 🛠️ Development Workflow

### Typical workflow:

1. Start development server: `npm run dev`
2. Open browser to `http://localhost:3000`
3. Click on the page you want to work on
4. Edit files in your code editor
5. See changes automatically without manual refresh

### Watched directories:

- `src/bookmarklet/` - HTML templates and TypeScript files
- `src/styles/` - CSS stylesheets
- Recursive watching for all `.html`, `.css`, `.ts`, `.js`, `.md` files

### Build process:

- Uses the same `PersonalBookmarkletBuilder` as the production build
- Automatically copies CSS files and fixes HTML paths
- No caching - always fresh content
- Source maps and debugging friendly

## 📊 Console Output

The development server provides helpful console output:

```
🚀 Starting PrismWeave Development Server...
📁 Source: d:\source\PrismWeave\browser-extension\src
📦 Output: d:\source\PrismWeave\browser-extension\dist\bookmarklet
🔧 Building website...
✅ Build completed successfully
👀 Starting file watcher...
✅ Development server running at http://localhost:3000/

📂 Available pages:
   🏠 http://localhost:3000/ - File browser
   🔧 http://localhost:3000/generator.html - Bookmarklet Generator
   📖 http://localhost:3000/help.html - Help Documentation
   📋 http://localhost:3000/index.html - File Index
   🔌 http://localhost:3000/install.html - Installation Guide

💡 Development Features:
   🔄 Auto-rebuild: ✅ Enabled
   👀 File watching: ✅ Active
   📱 Live reload: ✅ Available
   🕒 Watch interval: 500ms

🎯 Quick Commands:
   • Ctrl+C to stop server
   • Edit CSS/HTML files and see changes instantly
   • Check console for rebuild notifications
```

When you make changes, you'll see:

```
📝 Changes detected in 1 file(s):
   🔄 styles/bookmarklet-generator.css
🔧 Rebuilding...
✅ Build completed successfully
```

## 🎛️ Configuration Options

### Command Line Options

| Option             | Short | Description                           | Default     |
| ------------------ | ----- | ------------------------------------- | ----------- |
| `--port`           | `-p`  | Port to listen on                     | `3000`      |
| `--host`           | `-h`  | Host to bind to                       | `localhost` |
| `--no-reload`      |       | Disable auto-reload and file watching | `false`     |
| `--watch-interval` |       | File check interval in milliseconds   | `500`       |
| `--quiet`          |       | Disable verbose logging               | `false`     |
| `--help`           |       | Show help message                     |             |

### Examples

```bash
# Development server on port 8080
npm run dev:port 8080

# Server accessible from network (bind to all interfaces)
node scripts/serve-dev.js --host 0.0.0.0

# Faster file checking (every 250ms)
node scripts/serve-dev.js --watch-interval 250

# Static server only (no live reload)
node scripts/serve-dev.js --no-reload

# Quiet mode for cleaner output
npm run dev:quiet
```

## 🔍 Troubleshooting

### Common Issues

**Q: Server won't start on port 3000**

```bash
# Try a different port
npm run dev:port 8080
```

**Q: Changes not being detected**

```bash
# Check if files are in the watched directories
# Only src/bookmarklet/ and src/styles/ are watched
# Try faster watching interval
node scripts/serve-dev.js --watch-interval 250
```

**Q: Build errors**

```bash
# Check the console output for build errors
# Ensure TypeScript and CSS files are valid
# Try building manually first: npm run build:fast
```

**Q: Live reload not working**

```bash
# Make sure you're accessing HTML pages (not just viewing files)
# Live reload script is only injected into HTML content
# Check browser console for live reload messages
```

### Debug Information

The file browser shows useful debug information:

- Number of directories watched
- Number of files tracked
- Check interval timing
- Last check timestamp

## 🚫 Security Notes

**Development server only!** This server is designed for local development and
includes:

- No authentication
- CORS headers allowing all origins
- No rate limiting
- Development-friendly error messages
- Live reload functionality

Never use this server in production or expose it to untrusted networks.

## 📝 File Structure

```
browser-extension/
├── scripts/
│   ├── serve-dev.js          # Development server (this file)
│   ├── serve-local.js        # Original bookmarklet testing server
│   └── build-bookmarklet.js  # Build system
├── src/
│   ├── bookmarklet/          # 👀 WATCHED - HTML templates
│   └── styles/               # 👀 WATCHED - CSS files
└── dist/
    └── bookmarklet/          # 📦 OUTPUT - Built files served
```

## 🤝 Integration with VS Code

Works great with VS Code's integrated terminal:

1. Open terminal in VS Code (`Ctrl+``)
2. Run `npm run dev`
3. Edit files in VS Code
4. See changes in browser automatically

The development server respects VS Code's file saving behavior and will detect
changes immediately when you save files.
