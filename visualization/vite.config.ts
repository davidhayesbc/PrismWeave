import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    {
      name: 'startup-log',
      configureServer(server) {
        const httpServer = server.httpServer;
        if (!httpServer) return;

        httpServer.once('listening', () => {
          const host = server.config.server.host;
          const bindHost = typeof host === 'string' ? host : host ? '0.0.0.0' : 'localhost';
          const port = server.config.server.port ?? 3001;

          const displayHost = bindHost === '0.0.0.0' ? 'localhost' : bindHost;
          // eslint-disable-next-line no-console
          console.log(
            `[visualization] Listening on http://${bindHost}:${port} (local: http://${displayHost}:${port})`,
          );
        });
      },
    },
    {
      name: 'health-endpoint',
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          if (req.url === '/health') {
            res.statusCode = 200;
            res.setHeader('Content-Type', 'text/plain; charset=utf-8');
            res.end('healthy\n');
            return;
          }
          next();
        });
      },
    },
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: true,
    port: 3001,
    proxy: {
      '/api': {
        target: process.env.API_URL || 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
