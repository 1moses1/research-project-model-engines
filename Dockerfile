# Rwanda NCSA Compliance Monitoring Model - Production Container
# Multi-stage build for optimized image size

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy minimal requirements for K8s
COPY requirements-k8s.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements-k8s.txt

# Production stage
FROM python:3.11-slim

# Metadata
LABEL maintainer="Moise Iradukunda <miraduku@andrew.cmu.edu>"
LABEL description="Rwanda NCSA Compliance Monitoring - XGBoost Phase 2.5"
LABEL version="2.5.0"

# Set working directory
WORKDIR /app

# Create non-root user for security first
RUN useradd -m -u 1000 compliance

# Copy Python dependencies from builder to compliance user's home
COPY --from=builder /root/.local /home/compliance/.local

# Copy application code
COPY src/ /app/src/
COPY results/models/xgboost_phase2_5/ /app/models/
COPY data/processed/control_taxonomy.json /app/data/

# Copy configuration
COPY config/ /app/config/

# Set ownership
RUN chown -R compliance:compliance /app /home/compliance/.local

# Switch to non-root user
USER compliance

# Set Python path
ENV PYTHONPATH=/app
ENV PATH=/home/compliance/.local/bin:$PATH

# Expose API port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import joblib; joblib.load('/app/models/xgboost_phase2_5.pkl')" || exit 1

# Run Kubernetes compliance monitoring API
CMD ["python", "/app/src/api/k8s_compliance_api.py"]
