# -------- KC-Chain Stress-Test Simulator --------
# Production-ready Dockerfile (multi-stage optional is omitted for brevity)
# ------------------------------------------------
FROM python:3.11-slim

# Install system build dependencies (for cryptography wheels, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install dependencies first for better layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Default env (overridden in Railway / docker-compose)
ENV PYTHONUNBUFFERED=1

# Expose a lightweight healthcheck endpoint on port 8000 (see `scripts/health.py`)
ENV HEALTHCHECK_PORT=8000

# Application entrypoint
CMD ["python", "main.py"] 