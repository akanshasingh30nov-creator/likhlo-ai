# Multi-stage production container for LikhLo AI
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for optimal Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source, frontend, and configuration
COPY pyproject.toml README.md ./
COPY likhlo_ai/ ./likhlo_ai/
COPY frontend/ ./frontend/

# Install package in editable/local mode
RUN pip install --no-cache-dir -e .

# Expose FastAPI application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start production server
CMD ["python", "-m", "uvicorn", "likhlo_ai.server:app", "--host", "0.0.0.0", "--port", "8000"]
