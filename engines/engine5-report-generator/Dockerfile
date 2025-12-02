# ENGINE 5: Report Generation Engine
# LLM-powered PDF report generation

FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for PDF generation
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY engine5-report-generator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module FIRST (for unified pipeline)
COPY shared/ ./shared/

# Copy application code
COPY engine5-report-generator/app/ /app/app/

# Create reports directory
RUN mkdir -p /app/reports

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8005/health')" || exit 1

EXPOSE 8005

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
