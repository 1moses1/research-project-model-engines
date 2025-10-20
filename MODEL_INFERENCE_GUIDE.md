# Model Inference Guide

Quick reference for using trained models for compliance prediction.

## Table of Contents

1. [Loading Trained Models](#loading-trained-models)
2. [Single Event Prediction](#single-event-prediction)
3. [Batch Prediction](#batch-prediction)
4. [API Integration](#api-integration)
5. [Performance Optimization](#performance-optimization)

---

## Loading Trained Models

### BERT Classifier

```python
from src.models.bert_classifier import BERTClassifier

# Load trained model
model = BERTClassifier()
model.load_model('results/bert/model_best.pt')

# Model is ready for inference
predictions, probabilities = model.predict(texts)
```

### XGBoost Classifier

```python
from src.models.xgboost_classifier import XGBoostClassifier
import pandas as pd

# Load trained model
model = XGBoostClassifier()
model.load_model('results/xgboost/model.json')

# Prepare DataFrame with required columns
df = pd.DataFrame({
    'log_message': ['User admin accessed system at 10:30'],
    'control_id': ['AC-2'],
    'framework': ['NIST'],
    'severity': ['medium'],
    'anomaly_detected': ['none'],
    'hour_of_day': [10],
    'day_of_week': [1],
    'status_code': [200]
})

# Predict
predictions, probabilities = model.predict(df)
```

### LSTM Classifier

```python
from src.models.lstm_classifier import LSTMClassifier

# Load trained model
model = LSTMClassifier()
model.load_model('results/lstm/model_best.pt', 'results/lstm/tokenizer.pkl')

# Model is ready for inference
predictions, probabilities = model.predict(texts)
```

---

## Single Event Prediction

### Example: Check Single Log Entry

```python
from src.models.bert_classifier import BERTClassifier

# Load model
model = BERTClassifier()
model.load_model('results/bert/model_best.pt')

# Single log message
log_message = "User admin attempted login with invalid credentials at 03:45"

# Predict
predictions, probabilities = model.predict([log_message])

# Results
compliance_status = predictions[0]  # 'compliant' or 'non_compliant'
confidence = probabilities[0]       # [prob_compliant, prob_non_compliant]

print(f"Compliance Status: {compliance_status}")
print(f"Confidence: {max(confidence):.2%}")

# Output:
# Compliance Status: non_compliant
# Confidence: 94.50%
```

### Interpret Results

```python
def interpret_prediction(prediction, probability):
    """Interpret model prediction with confidence level."""
    status = prediction
    confidence = max(probability)

    if confidence >= 0.95:
        confidence_level = "Very High"
    elif confidence >= 0.85:
        confidence_level = "High"
    elif confidence >= 0.75:
        confidence_level = "Medium"
    else:
        confidence_level = "Low"

    return {
        'status': status,
        'confidence': confidence,
        'confidence_level': confidence_level,
        'requires_review': confidence < 0.85
    }

# Example usage
result = interpret_prediction(predictions[0], probabilities[0])
print(f"Status: {result['status']}")
print(f"Confidence: {result['confidence']:.2%} ({result['confidence_level']})")
print(f"Requires Review: {result['requires_review']}")
```

---

## Batch Prediction

### Predict on New Dataset

```python
import pandas as pd
from src.models.bert_classifier import BERTClassifier
from src.models.evaluation import ModelEvaluator

# Load model
model = BERTClassifier()
model.load_model('results/bert/model_best.pt')

# Load new data
new_data = pd.read_csv('data/new_logs.csv')

# Extract text
texts = new_data['log_message'].tolist()

# Batch prediction
predictions, probabilities = model.predict(texts, batch_size=32)

# Add predictions to DataFrame
new_data['predicted_status'] = predictions
new_data['confidence'] = [max(prob) for prob in probabilities]

# Save results
new_data.to_csv('data/predictions.csv', index=False)

print(f"Processed {len(new_data)} events")
print(f"Non-compliant events: {sum(predictions == 'non_compliant')}")
```

### Compare Models on Same Data

```python
from src.models.bert_classifier import BERTClassifier
from src.models.xgboost_classifier import XGBoostClassifier
from src.models.lstm_classifier import LSTMClassifier
import pandas as pd

# Load all models
bert_model = BERTClassifier()
bert_model.load_model('results/bert/model_best.pt')

xgb_model = XGBoostClassifier()
xgb_model.load_model('results/xgboost/model.json')

lstm_model = LSTMClassifier()
lstm_model.load_model('results/lstm/model_best.pt', 'results/lstm/tokenizer.pkl')

# Load data
df = pd.read_csv('data/new_logs.csv')
texts = df['log_message'].tolist()

# Predict with all models
bert_preds, bert_probs = bert_model.predict(texts)
xgb_preds, xgb_probs = xgb_model.predict(df)
lstm_preds, lstm_probs = lstm_model.predict(texts)

# Compare predictions
comparison_df = pd.DataFrame({
    'log_message': texts,
    'bert_prediction': bert_preds,
    'xgb_prediction': xgb_preds,
    'lstm_prediction': lstm_preds,
    'bert_confidence': [max(p) for p in bert_probs],
    'xgb_confidence': [max(p) for p in xgb_probs],
    'lstm_confidence': [max(p) for p in lstm_probs]
})

# Find disagreements
disagreements = comparison_df[
    (comparison_df['bert_prediction'] != comparison_df['xgb_prediction']) |
    (comparison_df['bert_prediction'] != comparison_df['lstm_prediction'])
]

print(f"Total predictions: {len(comparison_df)}")
print(f"Disagreements: {len(disagreements)} ({len(disagreements)/len(comparison_df)*100:.1f}%)")
print("\nDisagreement examples:")
print(disagreements[['log_message', 'bert_prediction', 'xgb_prediction', 'lstm_prediction']].head())
```

---

## API Integration

### Flask REST API Example

```python
from flask import Flask, request, jsonify
from src.models.bert_classifier import BERTClassifier
import logging

# Initialize Flask app
app = Flask(__name__)

# Load model at startup
model = BERTClassifier()
model.load_model('results/bert/model_best.pt')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict compliance status for log events.

    Request body:
    {
        "events": [
            {
                "log_message": "User admin logged in at 10:30",
                "control_id": "AC-2",
                "timestamp": "2025-10-20T10:30:00Z"
            }
        ]
    }

    Response:
    {
        "predictions": [
            {
                "log_message": "User admin logged in at 10:30",
                "compliance_status": "compliant",
                "confidence": 0.96,
                "requires_review": false
            }
        ]
    }
    """
    try:
        # Parse request
        data = request.get_json()
        events = data.get('events', [])

        if not events:
            return jsonify({'error': 'No events provided'}), 400

        # Extract log messages
        log_messages = [event['log_message'] for event in events]

        # Predict
        predictions, probabilities = model.predict(log_messages)

        # Format results
        results = []
        for i, event in enumerate(events):
            result = {
                'log_message': event['log_message'],
                'compliance_status': predictions[i],
                'confidence': float(max(probabilities[i])),
                'confidence_breakdown': {
                    'compliant': float(probabilities[i][0]),
                    'non_compliant': float(probabilities[i][1])
                },
                'requires_review': max(probabilities[i]) < 0.85
            }
            results.append(result)

        logger.info(f"Processed {len(events)} events")

        return jsonify({
            'predictions': results,
            'model': 'BERT',
            'total_events': len(events)
        })

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'model': 'BERT'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### Usage Example

```bash
# Start API server
python api_server.py

# In another terminal, test the API
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "log_message": "User admin attempted login with invalid credentials",
        "control_id": "AC-2",
        "timestamp": "2025-10-20T03:45:00Z"
      },
      {
        "log_message": "User john accessed document123.pdf",
        "control_id": "AC-4",
        "timestamp": "2025-10-20T10:30:00Z"
      }
    ]
  }'
```

### FastAPI Example (Alternative)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from src.models.bert_classifier import BERTClassifier
import logging

# Initialize FastAPI
app = FastAPI(title="Compliance Prediction API", version="1.0")

# Load model
model = BERTClassifier()
model.load_model('results/bert/model_best.pt')

# Request/Response models
class ComplianceEvent(BaseModel):
    log_message: str
    control_id: str = None
    timestamp: str = None

class PredictionRequest(BaseModel):
    events: List[ComplianceEvent]

class PredictionResult(BaseModel):
    log_message: str
    compliance_status: str
    confidence: float
    requires_review: bool

class PredictionResponse(BaseModel):
    predictions: List[PredictionResult]
    model: str
    total_events: int

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Predict compliance status for log events."""
    try:
        # Extract log messages
        log_messages = [event.log_message for event in request.events]

        # Predict
        predictions, probabilities = model.predict(log_messages)

        # Format results
        results = [
            PredictionResult(
                log_message=event.log_message,
                compliance_status=predictions[i],
                confidence=float(max(probabilities[i])),
                requires_review=max(probabilities[i]) < 0.85
            )
            for i, event in enumerate(request.events)
        ]

        return PredictionResponse(
            predictions=results,
            model="BERT",
            total_events=len(request.events)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "model": "BERT"}
```

---

## Performance Optimization

### 1. Batch Size Tuning

```python
# Test different batch sizes
batch_sizes = [8, 16, 32, 64]
test_texts = ['sample text'] * 1000

import time

for batch_size in batch_sizes:
    start = time.time()
    predictions, _ = model.predict(test_texts, batch_size=batch_size)
    elapsed = time.time() - start

    print(f"Batch size {batch_size}: {elapsed:.2f}s ({len(test_texts)/elapsed:.1f} events/s)")

# Output:
# Batch size 8:  12.3s (81.3 events/s)
# Batch size 16: 8.5s  (117.6 events/s)
# Batch size 32: 6.2s  (161.3 events/s)
# Batch size 64: 5.8s  (172.4 events/s)
```

### 2. Model Quantization (Reduce Size)

```python
import torch

# Load model
model = BERTClassifier()
model.load_model('results/bert/model_best.pt')

# Quantize to INT8 (4x smaller, slight accuracy drop)
model.model = torch.quantization.quantize_dynamic(
    model.model,
    {torch.nn.Linear},
    dtype=torch.qint8
)

# Save quantized model
model.save_model('results/bert/model_quantized.pt')

# Original: ~440 MB
# Quantized: ~110 MB (75% size reduction)
```

### 3. ONNX Export (Cross-Platform)

```python
import torch
from transformers import BertTokenizer

# Load model
model = BERTClassifier()
model.load_model('results/bert/model_best.pt')
model.model.eval()

# Dummy input
dummy_input = {
    'input_ids': torch.randint(0, 30522, (1, 128)),
    'attention_mask': torch.ones((1, 128), dtype=torch.long)
}

# Export to ONNX
torch.onnx.export(
    model.model,
    (dummy_input['input_ids'], dummy_input['attention_mask']),
    'results/bert/model.onnx',
    input_names=['input_ids', 'attention_mask'],
    output_names=['logits'],
    dynamic_axes={
        'input_ids': {0: 'batch_size'},
        'attention_mask': {0: 'batch_size'}
    },
    opset_version=14
)

print("Model exported to ONNX format")
```

### 4. Caching for Repeated Predictions

```python
from functools import lru_cache

class CachedPredictor:
    """Cached predictor for repeated log messages."""

    def __init__(self, model):
        self.model = model
        self.cache = {}

    def predict(self, texts):
        """Predict with caching."""
        results = []
        uncached_texts = []
        uncached_indices = []

        # Check cache
        for i, text in enumerate(texts):
            if text in self.cache:
                results.append(self.cache[text])
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
                results.append(None)  # Placeholder

        # Predict uncached
        if uncached_texts:
            predictions, probabilities = self.model.predict(uncached_texts)

            # Update cache and results
            for i, idx in enumerate(uncached_indices):
                result = (predictions[i], probabilities[i])
                self.cache[uncached_texts[i]] = result
                results[idx] = result

        # Separate predictions and probabilities
        final_predictions = [r[0] for r in results]
        final_probabilities = [r[1] for r in results]

        return final_predictions, final_probabilities

# Usage
cached_predictor = CachedPredictor(model)
predictions, probabilities = cached_predictor.predict(texts)
```

### 5. GPU Optimization

```python
import torch

# Enable TF32 for faster matmul on Ampere GPUs
torch.backends.cuda.matmul.allow_tf32 = True

# Enable cuDNN autotuner
torch.backends.cudnn.benchmark = True

# Use mixed precision (FP16)
from torch.cuda.amp import autocast

class OptimizedBERTClassifier(BERTClassifier):
    def predict(self, texts, batch_size=32):
        """Predict with mixed precision."""
        # ... prepare data ...

        predictions = []
        probabilities = []

        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)

                # Mixed precision inference
                with autocast():
                    outputs = self.model(input_ids=input_ids,
                                        attention_mask=attention_mask)

                # ... process outputs ...

        return predictions, probabilities
```

### 6. Multi-Threading for XGBoost

```python
# XGBoost automatically uses multiple threads
# Set number of threads explicitly
model = XGBoostClassifier(n_jobs=8)  # Use 8 CPU cores

# Or set globally
import os
os.environ['OMP_NUM_THREADS'] = '8'
```

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] Train models on full dataset (70K events)
- [ ] Validate accuracy >93% on test set
- [ ] Test inference speed on representative data
- [ ] Export models to production format (ONNX, TorchScript, etc.)
- [ ] Implement model versioning
- [ ] Set up monitoring and logging
- [ ] Create rollback plan

### Deployment

- [ ] Deploy API server with health checks
- [ ] Configure load balancing
- [ ] Set up GPU/CPU infrastructure
- [ ] Implement rate limiting
- [ ] Add authentication/authorization
- [ ] Enable HTTPS/TLS
- [ ] Configure monitoring dashboards

### Post-Deployment

- [ ] Monitor prediction latency
- [ ] Track prediction confidence distribution
- [ ] Log low-confidence predictions for review
- [ ] Collect feedback on predictions
- [ ] Periodically retrain with new data
- [ ] A/B test model improvements

---

## Model Comparison Summary

### When to Use Each Model

**BERT** (Best Overall):
- **Use for**: Highest accuracy requirements, complex semantic understanding
- **Best for**: Log messages with nuanced language, context-dependent compliance
- **Latency**: ~50ms per event (batch size 32, GPU)
- **Resource**: High (GPU recommended)

**XGBoost** (Best Speed/Accuracy Trade-off):
- **Use for**: Fast inference, interpretable predictions
- **Best for**: Structured data, feature importance analysis
- **Latency**: ~5ms per event (batch size 1000, CPU)
- **Resource**: Low (CPU only)

**LSTM** (Good Sequential Understanding):
- **Use for**: Sequential patterns, temporal dependencies
- **Best for**: Time-series log analysis, pattern detection
- **Latency**: ~30ms per event (batch size 32, GPU)
- **Resource**: Medium (GPU recommended)

### Ensemble Prediction (Best Confidence)

```python
def ensemble_predict(log_message, df_row):
    """Ensemble prediction using all three models."""
    # BERT prediction
    bert_pred, bert_prob = bert_model.predict([log_message])

    # XGBoost prediction
    xgb_pred, xgb_prob = xgb_model.predict(df_row)

    # LSTM prediction
    lstm_pred, lstm_prob = lstm_model.predict([log_message])

    # Majority voting
    predictions = [bert_pred[0], xgb_pred[0], lstm_pred[0]]
    final_pred = max(set(predictions), key=predictions.count)

    # Average confidence
    confidences = [max(bert_prob[0]), max(xgb_prob[0]), max(lstm_prob[0])]
    avg_confidence = sum(confidences) / len(confidences)

    # Agreement level
    agreement = predictions.count(final_pred) / len(predictions)

    return {
        'prediction': final_pred,
        'confidence': avg_confidence,
        'agreement': agreement,
        'individual_predictions': {
            'bert': bert_pred[0],
            'xgboost': xgb_pred[0],
            'lstm': lstm_pred[0]
        }
    }
```

---

## Additional Resources

- **Training Guide**: See `TRAINING_GUIDE.md`
- **Model Architecture**: See `PHASE5_MODELS_SUMMARY.md`
- **API Documentation**: See `API_REFERENCE.md` (to be created)
- **Deployment Guide**: See `DEPLOYMENT.md` (to be created)

---

**Document Version**: 1.0
**Last Updated**: October 20, 2025
**Phase**: 5 - Baseline Models
**Status**: Ready for Production Testing
