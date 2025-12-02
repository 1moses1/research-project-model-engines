# ENGINE 7: Authentication Engine
# Rwanda NCSA Compliance Auditor

FROM python:3.11-slim

LABEL maintainer="Rwanda NCSA Compliance Team"
LABEL description="Authentication & Authorization Engine for compliance auditing"
LABEL version="1.0.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/keys

# Non-root user for security
RUN useradd -m -u 1000 authuser && \
    chown -R authuser:authuser /app
USER authuser

# Environment
ENV PYTHONPATH=/app
ENV AUTH_PORT=8007
ENV AUTH_HOST=0.0.0.0

# Expose port
EXPOSE 8007

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8007/health')" || exit 1

# Run
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]
