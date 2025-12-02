#!/bin/bash
# Fix all Dockerfiles to use correct paths from engines/ build context

cd engines

# Engine 2
cat > engine2-document-processor/Dockerfile << 'EOF'
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
EOF

# Engine 3
cat > engine3-xgboost-classifier/Dockerfile << 'EOF'
# ENGINE 3: XGBoost Compliance Classifier
# Lightweight real-time inference engine

FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY engine3-xgboost-classifier/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module FIRST (for unified pipeline)
COPY shared/ ./shared/

# Copy application code
COPY engine3-xgboost-classifier/app/ ./app/

# Copy model artifacts (self-contained!)
COPY engine3-xgboost-classifier/models/ ./models/

# Verify model artifacts are present
RUN ls -lh /app/models/ && \
    test -f /app/models/rwanda_ncsa_compliance_auditor.json && \
    test -f /app/models/label_encoder.pkl && \
    test -f /app/models/tfidf_vectorizer.pkl && \
    echo "✅ All model artifacts present"

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8003/health')" || exit 1

EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
EOF

# Engine 4
cat > engine4-decision-engine/Dockerfile << 'EOF'
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
EOF

# Engine 5
cat > engine5-report-generator/Dockerfile << 'EOF'
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
EOF

echo "✅ All Dockerfiles updated with correct paths"
