# ENGINE 1: Log Collector
# LLM-powered real-time log collection and streaming

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Copy control taxonomy (self-contained)
COPY data/ ./data/

# Verify taxonomy
RUN test -f /app/data/control_taxonomy_validated.json && echo "✅ Control taxonomy present"

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
