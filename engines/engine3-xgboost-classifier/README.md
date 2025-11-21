# ENGINE 3: XGBoost Compliance Classifier

**Rwanda NCSA Compliance Auditor - Real-time ML Classification**

## Overview

ENGINE 3 provides real-time compliance classification using a trained XGBoost model with 196 government-validated controls (169 Rwanda NCSA + 27 NIST SP 800-53).

### Key Features

- **Self-Contained**: All model artifacts included in this directory
- **Fast Inference**: 1-4ms latency per event
- **Realistic API**: Automatic temporal feature extraction from timestamps
- **Batch Processing**: Classify multiple events in single request
- **High Accuracy**: 100% F1-score on synthetic compliance data

## Model Information

| Metric | Value |
|--------|-------|
| **Model Type** | XGBoost Classifier |
| **Total Controls** | 196 |
| **Rwanda NCSA Controls** | 169 |
| **NIST SP 800-53 Controls** | 27 |
| **Features** | 30 (25 text + 5 numeric) |
| **Model Size** | 9.2 KB |
| **Training Time** | 90 seconds |
| **Inference Time** | 1-4ms |

## Directory Structure

```
engine3-xgboost-classifier/
├── app/
│   └── main.py                      # FastAPI application
├── models/                          # Model artifacts (self-contained)
│   ├── rwanda_ncsa_compliance_auditor.json
│   ├── label_encoder.pkl
│   ├── tfidf_vectorizer.pkl
│   ├── day_encoder.pkl
│   ├── features.json
│   └── model_metrics.json
├── tests/
├── Dockerfile                       # Optimized container image
├── docker-compose.standalone.yml    # Standalone deployment
├── requirements.txt
├── .env.example
└── README.md                        # This file
```

## Quick Start

### Option 1: Standalone Deployment (Docker Compose)

```bash
# 1. Copy environment variables
cp .env.example .env

# 2. Deploy standalone
docker-compose -f docker-compose.standalone.yml up -d

# 3. Test the API
curl http://localhost:8000/health
```

### Option 2: Direct Docker Build

```bash
# Build image
docker build -t rwanda-ncsa-engine3:latest .

# Run container
docker run -d -p 8000:8000 --name engine3-xgboost rwanda-ncsa-engine3:latest

# Check logs
docker logs -f engine3-xgboost
```

### Option 3: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check

```bash
GET /health

# Response:
{
  "status": "healthy",
  "model_loaded": true,
  "feature_count": 30,
  "model_metadata": {...}
}
```

### Model Information

```bash
GET /model/info

# Response:
{
  "model_type": "XGBoost Classifier",
  "framework": "Rwanda NCSA Cybersecurity Minimum Standards",
  "controls": {
    "total": 196,
    "rwanda_ncsa": 169,
    "nist_sp_800_53": 27
  },
  "performance": {
    "f1_score": 1.0,
    "accuracy": 1.0
  }
}
```

### Single Event Classification

```bash
POST /classify

# Request:
{
  "timestamp": "2025-11-21T14:30:00Z",
  "log_message": "User admin logged in successfully",
  "status_code": 200,
  "port": 443
}

# Response:
{
  "prediction": "compliant",
  "confidence": 0.95,
  "probabilities": {
    "compliant": 0.95,
    "non_compliant": 0.05
  },
  "inference_time_ms": 2.145,
  "timestamp": "2025-11-21T14:30:01Z"
}
```

### Batch Classification

```bash
POST /classify/batch

# Request:
{
  "events": [
    {
      "timestamp": "2025-11-21T14:30:00Z",
      "log_message": "User admin logged in successfully",
      "status_code": 200,
      "port": 443
    },
    {
      "timestamp": "2025-11-21T02:15:00Z",
      "log_message": "Failed login attempt for user john",
      "status_code": 401,
      "port": 22
    }
  ]
}

# Response:
{
  "predictions": [...],
  "total_events": 2,
  "total_inference_time_ms": 3.456,
  "avg_inference_time_ms": 1.728
}
```

## Feature Extraction

ENGINE 3 automatically extracts temporal features from timestamps (realistic approach):

```python
timestamp = "2025-11-21T14:30:00Z"
↓
Automatic extraction:
- hour_of_day = 14
- day_of_week = "Thursday"
- is_business_hours = true  # Mon-Fri, 8AM-6PM
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `MODEL_PATH` | Path to XGBoost model | /app/models/rwanda_ncsa_compliance_auditor.json |
| `LOG_LEVEL` | Logging level | INFO |
| `WORKERS` | Uvicorn workers | 4 |

## Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test model info
curl http://localhost:8000/model/info

# Test classification
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-11-21T14:30:00Z",
    "log_message": "User admin logged in successfully",
    "status_code": 200,
    "port": 443
  }'
```

## Integration with Other Engines

ENGINE 3 receives events from:
- **ENGINE 1** (Log Collector): Real-time log events
- **ENGINE 4** (Decision Engine): Batch classification requests

ENGINE 3 sends results to:
- **ENGINE 4** (Decision Engine): Classification results
- **ENGINE 5** (Web UI): Real-time predictions

## Performance Tuning

### Optimize for Throughput

```bash
# Increase workers
WORKERS=8 uvicorn app.main:app --workers 8

# Use batch endpoint for high volume
curl -X POST http://localhost:8000/classify/batch -d '{"events": [...]}'
```

### Optimize for Latency

```bash
# Single worker for lowest latency
WORKERS=1 uvicorn app.main:app --workers 1
```

## Monitoring

```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Runtime statistics
{
  "model_loaded": 1,
  "feature_count": 30,
  "class_count": 2,
  "model_f1_score": 1.0,
  "total_controls": 196
}
```

## Troubleshooting

### Model Not Loading

```bash
# Check model files are present
docker exec engine3-xgboost ls -lh /app/models/

# Expected output:
# rwanda_ncsa_compliance_auditor.json (9.2KB)
# label_encoder.pkl (431B)
# tfidf_vectorizer.pkl (15KB)
# day_encoder.pkl (579B)
# features.json (401B)
```

### Low Inference Speed

```bash
# Check CPU usage
docker stats engine3-xgboost

# Reduce batch size
MAX_BATCH_SIZE=100
```

## License

Rwanda NCSA Compliance Auditor - Carnegie Mellon University Africa

## Support

For issues specific to ENGINE 3, check:
1. Model files are present in `models/` directory
2. Container has sufficient CPU/RAM
3. Port 8000 is not already in use
4. Check logs: `docker logs engine3-xgboost`
