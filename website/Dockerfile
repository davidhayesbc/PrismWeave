# Multi-stage Dockerfile for PrismWeave Website

# Development stage
FROM node:20-alpine as development

# The website dev script uses `python -m http.server`, so ensure python exists.
RUN apk add --no-cache python3 && ln -sf python3 /usr/bin/python

WORKDIR /app

# Copy website source
COPY website/ .

# The website repo includes a symlink at website/shared-styles -> ../shared-styles.
# Remove it and replace with a real directory to avoid Docker COPY collisions.
RUN rm -f /app/shared-styles

# Copy shared styles
COPY shared-styles /app/shared-styles

# Install dependencies (if package.json exists)
RUN if [ -f package.json ]; then npm install; else echo "No package.json found"; fi

# Expose port
EXPOSE 3000

# Development server with hot-reload
CMD ["npm", "run", "dev"]

# Build stage
FROM node:20-alpine as builder

WORKDIR /app

# Copy source
COPY website/ .

# Replace website/shared-styles symlink with real directory
RUN rm -f /app/shared-styles

# Copy shared styles
COPY shared-styles /app/shared-styles

# Install dependencies and build
RUN if [ -f package.json ]; then \
      npm ci --only=production && \
      (npm run build || echo "No build script, using source directly"); \
    else \
      echo "No package.json found, using source directly"; \
    fi

# Production stage
FROM nginx:alpine as production

# Copy nginx config
COPY website/nginx.conf /etc/nginx/nginx.conf

# Copy built files and shared styles
COPY --from=builder /app /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
