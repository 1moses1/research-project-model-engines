# ENGINE 2: Document Processor
# LLM-powered policy analysis and control extraction

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PDF/DOCX/XLSX processing
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY engine2-document-processor/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module FIRST (for unified pipeline)
COPY shared/ ./shared/

# Copy application code
COPY engine2-document-processor/app/ ./app/

# Copy control taxonomy (self-contained!)
COPY engine2-document-processor/data/ ./data/

# Copy sample documents for testing
COPY engine2-document-processor/sample_documents/ ./sample_documents/

# Verify control taxonomy is present
RUN test -f /app/data/control_taxonomy_validated.json && \
    echo "✅ Control taxonomy present"

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8002/health')" || exit 1

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
