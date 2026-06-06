FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Upgrade pip and install dependencies
# Use --no-build-isolation to avoid setuptools issues
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --no-build-isolation -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/data/audio /app/data/chroma_db /app/logs

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]