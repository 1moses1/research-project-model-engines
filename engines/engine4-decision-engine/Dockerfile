FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

# Run the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
