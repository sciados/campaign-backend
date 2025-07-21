# Dockerfile for Railway deployment
FROM python:3.11-slim

# Install system dependencies including libmagic
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libmagic-dev \
    file \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8080

# Start the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]