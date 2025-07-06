FROM node:14-alpine

WORKDIR /app

# Install dependencies for native modules
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package.json ./
RUN npm install --omit=dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8083

# Run the application
CMD ["node", "index.js"]