# Backend Dockerfile for Aetherstore Engine
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with increased timeout
# Note: If you get timeout errors, try again or check your network connection
RUN pip install --no-cache-dir \
    --timeout=300 \
    --retries=3 \
    -r requirements.txt || \
    (echo "First attempt failed, retrying..." && \
     pip install --no-cache-dir --timeout=300 --retries=3 -r requirements.txt)

# Copy application code
COPY . .

# Create uploads and temp directories
RUN mkdir -p uploads temp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Run the application
CMD ["python", "main_app.py"]

