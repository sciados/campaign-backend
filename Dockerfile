# Dockerfile for Railway deployment - Security-optimized for modular architecture
FROM python:3.11-slim

# Update package lists and install security updates
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Set working directory
WORKDIR /app

# Create non-root user early for security
RUN useradd --create-home --shell /bin/bash --uid 1000 app \
    && chown -R app:app /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with security flags
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Switch to non-root user
USER app

# Copy the rest of the application
COPY --chown=app:app . .

# Expose the port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start the application using the new modular main.py
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]