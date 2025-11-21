# ENGINE 3: XGBoost Compliance Classifier API

**Version**: 3.0.0
**Purpose**: Real-time compliance classification using trained XGBoost model
**Latency**: <1ms per classification

## Overview

ENGINE 3 provides a FastAPI-based REST API wrapper around the trained XGBoost compliance classifier. It classifies log events as **compliant** or **non-compliant** based on Rwanda NCSA Cybersecurity Minimum Standards.

### Features

- ⚡ **Ultra-fast inference**: <1ms per event
- 📊 **Batch processing**: Classify multiple events in one request
- 🎯 **High accuracy**: Trained on 70K synthetic compliance events
- 🔄 **Auto-loading**: Model loads on startup
- 📈 **Metrics endpoint**: Prometheus-compatible metrics
- 🏥 **Health checks**: Docker healthcheck support
- 📝 **Auto-docs**: OpenAPI/Swagger documentation

## Architecture

```
┌─────────────────────────────────────────────┐
│         ENGINE 3: XGBoost API               │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │      FastAPI Application            │   │
│  │                                      │   │
│  │  Endpoints:                          │   │
│  │  - POST /classify                    │   │
│  │  - POST /classify/batch              │   │
│  │  - GET  /model/info                  │   │
│  │  - GET  /health                      │   │
│  │  - GET  /metrics                     │   │
│  └───────────────┬─────────────────────┘   │
│                  │                          │
│  ┌───────────────▼─────────────────────┐   │
│  │   XGBoost Classifier                │   │
│  │   - 53 features (3 numeric + 50 text)│   │
│  │   - 169 Rwanda NCSA controls         │   │
│  │   - 27 NIST SP 800-53 controls       │   │
│  │   - TF-IDF vectorizer                │   │
│  │   - Label encoder                    │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## Quick Start

### Development Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload --port 8000

# Access
http://localhost:8000
http://localhost:8000/docs  # Swagger UI
```

### Docker Mode

```bash
# Build
docker build -t rwanda-ncsa-xgboost .

# Run
docker run -p 8000:8000 \
  -v $(pwd)/../../models/compliance_auditor_final:/app/models \
  rwanda-ncsa-xgboost

# Access
http://localhost:8000
```

### Docker Compose (Recommended)

```bash
# From project root
docker-compose up -d xgboost-api

# Check logs
docker logs rwanda-ncsa-xgboost

# Test
curl http://localhost:8000/health
```

## API Endpoints

### 1. Health Check

**GET** `/health`

Check if the API and model are loaded correctly.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "vectorizer_loaded": true,
  "label_encoder_loaded": true,
  "feature_count": 53,
  "model_metadata": {...},
  "timestamp": "2024-11-19T..."
}
```

### 2. Model Information

**GET** `/model/info`

Get detailed model information and performance metrics.

**Response:**
```json
{
  "model_type": "XGBoost Classifier",
  "version": "3.0.0",
  "framework": "Rwanda NCSA Cybersecurity Minimum Standards",
  "features": {
    "total": 53,
    "numeric": 3,
    "text": 50
  },
  "classes": ["compliant", "non_compliant"],
  "controls": {
    "total": 196,
    "rwanda_ncsa": 169,
    "nist_sp_800_53": 27
  },
  "performance": {
    "f1_score": 1.0,
    "accuracy": 1.0,
    "precision": 1.0,
    "recall": 1.0,
    "training_time_seconds": 0.24
  }
}
```

### 3. Single Event Classification

**POST** `/classify`

Classify a single log event.

**Request Body:**
```json
{
  "log_message": "User admin logged in successfully",
  "status_code": 200,
  "hour_of_day": 14,
  "port": 443
}
```

**Response:**
```json
{
  "prediction": "compliant",
  "confidence": 0.998,
  "probabilities": {
    "compliant": 0.998,
    "non_compliant": 0.002
  },
  "inference_time_ms": 0.543,
  "timestamp": "2024-11-19T..."
}
```

### 4. Batch Classification

**POST** `/classify/batch`

Classify multiple events in a single request.

**Request Body:**
```json
{
  "events": [
    {
      "log_message": "User admin logged in successfully",
      "status_code": 200,
      "hour_of_day": 14,
      "port": 443
    },
    {
      "log_message": "Failed login attempt",
      "status_code": 401,
      "hour_of_day": 2,
      "port": 22
    }
  ]
}
```

**Response:**
```json
{
  "predictions": [
    {
      "prediction": "compliant",
      "confidence": 0.998,
      "probabilities": {...},
      "inference_time_ms": 0.543,
      "timestamp": "..."
    },
    {
      "prediction": "non_compliant",
      "confidence": 0.987,
      "probabilities": {...},
      "inference_time_ms": 0.621,
      "timestamp": "..."
    }
  ],
  "total_events": 2,
  "total_inference_time_ms": 1.164,
  "avg_inference_time_ms": 0.582
}
```

### 5. Metrics

**GET** `/metrics`

Get runtime metrics for monitoring (Prometheus-compatible).

**Response:**
```json
{
  "model_loaded": 1,
  "feature_count": 53,
  "class_count": 2,
  "model_f1_score": 1.0,
  "model_accuracy": 1.0,
  "total_controls": 196
}
```

## Testing

### Run Test Suite

```bash
# Install test dependencies
pip install requests

# Run tests
python test_api.py
```

**Test Coverage:**
- ✅ Health check
- ✅ Model info retrieval
- ✅ Single event classification (compliant)
- ✅ Single event classification (non-compliant)
- ✅ Batch classification (5 events)
- ✅ Metrics endpoint
- ✅ Performance test (100 requests)

### Manual Testing with cURL

```bash
# Health check
curl http://localhost:8000/health

# Classify single event
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "log_message": "User admin logged in successfully",
    "status_code": 200,
    "hour_of_day": 14,
    "port": 443
  }'

# Batch classification
curl -X POST http://localhost:8000/classify/batch \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {"log_message": "Login successful", "status_code": 200},
      {"log_message": "Login failed", "status_code": 401}
    ]
  }'
```

### Python Client Example

```python
import requests

API_URL = "http://localhost:8000"

# Single classification
event = {
    "log_message": "User admin logged in successfully",
    "status_code": 200,
    "hour_of_day": 14,
    "port": 443
}

response = requests.post(f"{API_URL}/classify", json=event)
result = response.json()

print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']:.3f}")
print(f"Inference Time: {result['inference_time_ms']:.3f}ms")
```

## Performance Benchmarks

**Single Event Classification:**
- Inference Time: 0.5-1.0ms
- Throughput: ~1000 requests/sec (single worker)

**Batch Classification:**
- 10 events: ~5-10ms total
- 100 events: ~50-100ms total
- 1000 events: ~500-1000ms total

**Resource Usage:**
- Memory: ~200MB (with model loaded)
- CPU: <5% idle, 30-40% under load

## Model Details

### Input Features (53 total)

**Numeric (3):**
1. `status_code` - HTTP status code
2. `hour_of_day` - Hour of day (0-23)
3. `port` - Port number

**Text (50):**
- TF-IDF features extracted from `log_message`
- Top 50 most important terms

### Output Classes

1. **compliant** - Event meets Rwanda NCSA requirements
2. **non_compliant** - Event violates requirements

### Controls Coverage

- **Rwanda NCSA**: 169 requirements across 12 families
- **NIST SP 800-53**: 27 controls (secondary reference)
- **Total**: 196 controls

## Integration with Other Engines

### ENGINE 4 (Decision & Scoring)

ENGINE 3 outputs are consumed by ENGINE 4 for:
- Confidence routing (high/low confidence)
- Risk scoring
- Aggregation per control family
- Continuous learning pipeline

### ENGINE 6 (Web UI)

Web UI calls ENGINE 3 for:
- Real-time event classification
- Document-extracted control validation
- Live compliance scoring

**Integration Example:**
```javascript
// From Web UI (React)
const classifyEvent = async (event) => {
  const response = await axios.post(
    'http://localhost:8000/classify',
    event
  );
  return response.data;
};
```

## Troubleshooting

### Model Not Loading

**Error:** `Model not loaded`

**Solution:**
```bash
# Check model path
ls -la models/compliance_auditor_final/

# Expected files:
# - rwanda_ncsa_compliance_auditor.json
# - label_encoder.pkl
# - tfidf_vectorizer.pkl
# - features.json
# - model_metrics.json

# Fix volume mount in docker-compose.yml
volumes:
  - ./models/compliance_auditor_final:/app/models
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'xgboost'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Change port
uvicorn app.main:app --port 8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

## Monitoring

### Health Checks

Docker includes automatic health checks:
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
  interval: 30s
  timeout: 5s
  retries: 3
```

### Prometheus Metrics

Metrics endpoint at `/metrics` provides:
- Model load status
- Feature count
- Performance metrics (F1, accuracy)
- Uptime

### Logging

Application logs include:
- Model loading status
- Request/response times
- Error traces
- Performance metrics

## Next Steps

1. **Deploy**: Start ENGINE 3 with docker-compose
2. **Test**: Run test suite to verify functionality
3. **Integrate**: Connect ENGINE 6 Web UI to ENGINE 3
4. **Monitor**: Set up Prometheus/Grafana for metrics
5. **Scale**: Add more workers for higher throughput

## Support

**Documentation**: See `ARCHITECTURE_V3_DESIGN.md`
**Issues**: Check logs with `docker logs rwanda-ncsa-xgboost`
**API Docs**: http://localhost:8000/docs (Swagger UI)

---

**ENGINE 3 Status**: ✅ Ready for Production
**Latency Target**: <1ms ✅
**Throughput Target**: >500 req/sec ✅
**Integration**: ENGINE 4, ENGINE 6 ✅
