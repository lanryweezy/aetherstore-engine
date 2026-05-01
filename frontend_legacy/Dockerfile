# Frontend Dockerfile for Aetherstore Engine
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Expose port (webpack dev server default)
EXPOSE 8080

# Start development server
CMD ["npm", "start"]

