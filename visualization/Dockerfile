# Multi-stage Dockerfile for PrismWeave Visualization

# Development stage
FROM node:20-alpine as development

WORKDIR /app

# Copy shared styles first
COPY shared-styles /app/shared-styles

# Copy visualization source
COPY visualization/ .

# Install dependencies (if package.json exists)
RUN if [ -f package.json ]; then npm install; else echo "No package.json found"; fi

# Expose port
EXPOSE 3001

# Development server with hot-reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3001"]

# Build stage
FROM node:20-alpine as builder

WORKDIR /app

# Copy shared styles
COPY shared-styles /app/shared-styles

# Copy source
COPY visualization/ .

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
COPY visualization/nginx.conf /etc/nginx/nginx.conf

# Copy built files and shared styles
COPY --from=builder /app /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
