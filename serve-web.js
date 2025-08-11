#!/usr/bin/env node

/**
 * Simple HTTP server for testing the web build
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const WEB_DIR = path.join(__dirname, 'dist', 'web');

// MIME types
const mimeTypes = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.md': 'text/markdown',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.ico': 'image/x-icon',
  '.svg': 'image/svg+xml'
};

function getMimeType(filepath) {
  const ext = path.extname(filepath);
  return mimeTypes[ext] || 'application/octet-stream';
}

function serveFile(res, filepath) {
  const fullPath = path.join(WEB_DIR, filepath);
  
  fs.stat(fullPath, (err, stats) => {
    if (err || !stats.isFile()) {
      // Try to serve index.html if it's a directory
      const indexPath = path.join(fullPath, 'index.html');
      fs.stat(indexPath, (indexErr, indexStats) => {
        if (indexErr || !indexStats.isFile()) {
          res.writeHead(404, { 'Content-Type': 'text/plain' });
          res.end('404 Not Found');
        } else {
          serveFile(res, path.join(filepath, 'index.html'));
        }
      });
      return;
    }

    fs.readFile(fullPath, (readErr, data) => {
      if (readErr) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('500 Internal Server Error');
        return;
      }

      const mimeType = getMimeType(fullPath);
      res.writeHead(200, { 'Content-Type': mimeType });
      res.end(data);
    });
  });
}

const server = http.createServer((req, res) => {
  let url = req.url || '/';
  
  // Remove query parameters
  url = url.split('?')[0];
  
  // Handle root request
  if (url === '/') {
    url = '/index.html';
  }
  
  // Remove leading slash
  const filepath = url.slice(1);
  
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url} -> ${filepath}`);
  
  serveFile(res, filepath);
});

server.listen(PORT, () => {
  if (!fs.existsSync(WEB_DIR)) {
    console.error(`❌ Web directory not found: ${WEB_DIR}`);
    console.error('   Please run "node build.js web" first to build the web deployment');
    process.exit(1);
  }
  
  console.log(`🌐 PrismWeave web server started:`);
  console.log(`   Local: http://localhost:${PORT}`);
  console.log(`   Directory: ${WEB_DIR}`);
  console.log(`   Press Ctrl+C to stop`);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`❌ Port ${PORT} is already in use. Try a different port.`);
  } else {
    console.error(`❌ Server error:`, err);
  }
  process.exit(1);
});
