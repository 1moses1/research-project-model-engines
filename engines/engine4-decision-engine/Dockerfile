# ENGINE 4: Decision & Scoring Engine

FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY engine4-decision-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module FIRST (for unified pipeline)
COPY shared/ ./shared/

# Copy application code
COPY engine4-decision-engine/app/ ./app/

# Health check (configurable via PORT env var, default 8004)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os; import requests; requests.get(f'http://localhost:{os.getenv(\"PORT\", \"8004\")}/health')" || exit 1

# Expose port (configurable via PORT env var, default 8004)
EXPOSE 8004

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8004}"]
