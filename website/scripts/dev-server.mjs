import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

import { startTelemetry } from './telemetry.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function parseArgs(argv) {
  const args = { port: 3000 };
  for (let i = 2; i < argv.length; i++) {
    const token = argv[i];
    if (token === '--port') {
      args.port = Number(argv[i + 1]);
      i++;
    }
  }
  return args;
}

function contentTypeFor(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  switch (ext) {
    case '.html':
      return 'text/html; charset=utf-8';
    case '.css':
      return 'text/css; charset=utf-8';
    case '.js':
      return 'text/javascript; charset=utf-8';
    case '.json':
      return 'application/json; charset=utf-8';
    case '.svg':
      return 'image/svg+xml';
    case '.png':
      return 'image/png';
    case '.ico':
      return 'image/x-icon';
    default:
      return 'application/octet-stream';
  }
}

async function fileExists(p) {
  try {
    await fs.stat(p);
    return true;
  } catch {
    return false;
  }
}

async function main() {
  const { port } = parseArgs(process.argv);

  const telemetry = await startTelemetry({ serviceName: 'website' });

  const repoRoot = path.resolve(__dirname, '..');
  const distRoot = path.join(repoRoot, 'dist');
  const staticRoot = (await fileExists(distRoot)) ? distRoot : repoRoot;

  const server = http.createServer(async (req, res) => {
    try {
      const url = new URL(req.url || '/', `http://${req.headers.host || 'localhost'}`);
      const requestPath = decodeURIComponent(url.pathname);

      const normalized = path
        .normalize(requestPath)
        .replace(/^\.{1,2}(\/|\\)/, '')
        .replace(/^\//, '');

      const candidate = path.join(staticRoot, normalized);
      const stat = await fs.stat(candidate).catch(() => null);

      let filePath = candidate;
      if (!stat) {
        // SPA-ish fallback: serve index.html if present.
        const indexPath = path.join(staticRoot, 'index.html');
        if (await fileExists(indexPath)) {
          filePath = indexPath;
        } else {
          res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
          res.end('Not found');
          telemetry.logWarn?.('404', { path: requestPath, method: req.method || 'GET' });
          return;
        }
      } else if (stat.isDirectory()) {
        filePath = path.join(candidate, 'index.html');
      }

      const body = await fs.readFile(filePath);
      res.writeHead(200, { 'content-type': contentTypeFor(filePath) });
      res.end(body);

      telemetry.logInfo?.('http_request', {
        method: req.method || 'GET',
        path: requestPath,
        status: 200,
      });
    } catch (err) {
      res.writeHead(500, { 'content-type': 'text/plain; charset=utf-8' });
      res.end('Internal Server Error');
      telemetry.logError?.('http_error', {
        message: err instanceof Error ? err.message : String(err),
      });
    }
  });

  server.listen(port, '0.0.0.0', () => {
    telemetry.logInfo?.('server_listening', { port });
  });

  const shutdown = async () => {
    server.close(() => {
      telemetry.shutdown?.().finally(() => process.exit(0));
    });
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}

main().catch((err) => {
  // Avoid console noise unless telemetry is disabled.
  // eslint-disable-next-line no-console
  console.error(err);
  process.exit(1);
});
