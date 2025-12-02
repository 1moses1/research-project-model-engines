# ENGINE 6: Web UI Backend
# FastAPI + WebSocket for Rwanda NCSA Compliance Dashboard

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Create required directories
RUN mkdir -p uploads static

# Expose port
EXPOSE 8006

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8006/health')"

# Run the application
CMD ["uvicorn", "api:socket_app", "--host", "0.0.0.0", "--port", "8006", "--reload"]
