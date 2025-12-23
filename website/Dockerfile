# Multi-stage Dockerfile for PrismWeave Website

# Development stage
FROM node:20-alpine as development

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source
COPY . .
COPY ../shared-styles ./shared-styles

# Expose port
EXPOSE 3000

# Development server with hot-reload
CMD ["npm", "run", "dev"]

# Build stage
FROM node:20-alpine as builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source
COPY . .

# Build static site (adjust based on your build command)
RUN npm run build 2>/dev/null || echo "No build script found, using source directly"

# Production stage
FROM nginx:alpine as production

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built files or source
COPY --from=builder /app/dist /usr/share/nginx/html 2>/dev/null || \
COPY --from=builder /app /usr/share/nginx/html

# Copy shared styles
COPY --from=builder /app/shared-styles /usr/share/nginx/html/shared-styles

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
