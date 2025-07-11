FROM node:20-alpine AS builder

# Build arguments
ARG SENTRY_DSN
ARG API_URL
ARG APP_VERSION

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies (this layer will be cached if package.json doesn't change)
RUN npm ci --prefer-offline --no-audit

# Copy scripts directory for environment generation
COPY scripts ./scripts

# Copy source code
COPY . .

# Generate environment files with build arguments
ENV SENTRY_DSN=${SENTRY_DSN}
ENV API_URL=${API_URL}
ENV APP_VERSION=${APP_VERSION}
RUN node scripts/generate-env.js

# Build the app
RUN npm run build

# Install Sentry CLI and inject debug-ids into built files
RUN npm install -g @sentry/cli
RUN npx @sentry/cli sourcemaps inject ./dist/frontend || echo "Debug ID injection skipped"

# Production stage
FROM nginx:alpine

# Copy built app
COPY --from=builder /app/dist/frontend /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 4200

CMD ["nginx", "-g", "daemon off;"]