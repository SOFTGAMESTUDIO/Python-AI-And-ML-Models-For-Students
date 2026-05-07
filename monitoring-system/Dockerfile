# ============================================================
# Monitoring System — Dockerfile
# Copyright (c) 2026 Soft Game Studio
# License: MIT
# ============================================================

FROM python:3.11-slim AS base

# Install system dependencies (libpcap for Scapy)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpcap-dev \
        tcpdump \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r monitor && useradd -r -g monitor -m monitor

# Set working directory
WORKDIR /app

# Copy requirements first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p logs database && \
    chown -R monitor:monitor /app

# Switch to non-root user
USER monitor

# Expose dashboard port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run application
CMD ["python", "app.py"]
