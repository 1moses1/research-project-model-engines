# ENGINE 3: XGBoost Compliance Classifier
# Rwanda NCSA Compliance Auditor
# Self-contained deployment with all model artifacts included

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Copy model artifacts (self-contained!)
COPY models/ ./models/

# Verify models are present
RUN ls -lh /app/models/ && \
    test -f /app/models/rwanda_ncsa_compliance_auditor.json && \
    test -f /app/models/label_encoder.pkl && \
    test -f /app/models/tfidf_vectorizer.pkl && \
    echo "✅ All model artifacts present"

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
