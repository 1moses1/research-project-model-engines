# ENGINE 1: Log Collector
# LLM-powered real-time log collection and streaming

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY engine1-log-collector/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module FIRST (for unified pipeline)
COPY shared/ ./shared/

# Copy application
COPY engine1-log-collector/app/ ./app/

# Copy control taxonomy (self-contained)
COPY engine1-log-collector/data/ ./data/

# Verify taxonomy
RUN test -f /app/data/control_taxonomy_validated.json && echo "✅ Control taxonomy present"

# Health check (configurable via PORT env var, default 8001)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os; import requests; requests.get(f'http://localhost:{os.getenv(\"PORT\", \"8001\")}/health')" || exit 1

EXPOSE 8001

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}"]
