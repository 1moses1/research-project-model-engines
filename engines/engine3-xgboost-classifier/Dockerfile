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
