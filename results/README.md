# Results Directory (`results/`)

This directory contains trained models, evaluation metrics, and explainability artifacts.

## Directory Structure

```
results/
├── models/                 # Trained model files (.pkl, .pt, .h5)
│   ├── xgboost_phase2_5/  # Production model ⭐
│   ├── xgboost_phase2/    # Initial model (deprecated)
│   ├── xgboost_enhanced/  # Experimental variant
│   └── xgboost_no_leakage/# Data leakage test model
├── evaluation/             # Performance metrics and confusion matrices
├── explainability/         # SHAP values and interpretability plots
└── ensemble/               # Ensemble model experiments
```

## Production Model: XGBoost Phase 2.5

**Location**: `results/models/xgboost_phase2_5/`

**Files**:
```
xgboost_phase2_5/
├── xgboost_phase2_5.pkl           # Trained XGBoost model (999 KB)
├── tfidf_vectorizer.pkl           # TF-IDF vectorizer (1.2 MB)
├── control_encoder.pkl            # Control ID label encoder (10 KB)
├── family_encoder.pkl             # Control family label encoder (5 KB)
├── model_signature.json           # Cryptographic signature (HMAC-SHA256)
├── checksums.txt                  # File integrity checksums (SHA-256)
├── model_metadata.json            # Training metadata and hyperparameters
└── phase2_5_metrics.json          # Performance metrics
```

### Model Specifications

| Attribute | Value |
|-----------|-------|
| **Algorithm** | XGBoost (Gradient Boosting) |
| **Trees** | 500 |
| **Max Depth** | 6 |
| **Learning Rate** | 0.1 |
| **Features** | 1,003 (1,000 TF-IDF + 3 control encodings) |
| **Total Size** | 3.2 MB |
| **Training Time** | ~1.5 minutes |
| **Inference Time** | ~1 ms per log |

### Performance Metrics

**Test Set** (24,477 events):
```json
{
  "accuracy": 0.9949,  // 99.49%
  "precision_non_compliant": 0.9990,  // 99.90%
  "recall_non_compliant": 0.9896,  // 98.96%
  "f1_score": 0.9943,
  "confusion_matrix": [[13541, 11], [114, 10811]]
}
```

**Real Scenarios**: 12/12 correct (100%)

**Novel Attacks**: 6/6 detected (100%)

### Model Signature

**Purpose**: Verify model integrity and prevent tampering

**File**: `model_signature.json`
```json
{
  "signature": "4e9594afdc505e4675758be4385c75a7...",
  "algorithm": "HMAC-SHA256",
  "signed_at": "2025-11-03T01:02:53Z",
  "checksums": {
    "xgboost_phase2_5.pkl": "e8a3f2b1...",
    "tfidf_vectorizer.pkl": "9c7d4a3f...",
    "control_encoder.pkl": "5b2e8f1c...",
    "family_encoder.pkl": "7a4d9e2b..."
  }
}
```

**Verification**:
```python
from src.security.model_signing import ModelSigner

signer = ModelSigner(secret_key)
is_valid = signer.verify_model('results/models/xgboost_phase2_5')
print(f"Model integrity: {'✅ VALID' if is_valid else '❌ TAMPERED'}")
```

## Phase 2 vs Phase 2.5 Comparison

**File**: `results/models/phase2_vs_phase2_5_comparison.csv`

| Scenario | Phase 2 | Phase 2.5 | Improvement |
|----------|---------|-----------|-------------|
| Phishing Detection | ❌ 6.6% (wrong) | ✅ 99.9% (correct) | +93.3% |
| Insider Threat | ❌ 9.0% (wrong) | ✅ 100.0% (correct) | +91.0% |
| DDoS Attack | ❌ 6.3% (wrong) | ✅ 100.0% (correct) | +93.7% |
| Credential Stuffing | ❌ 6.7% (wrong) | ✅ 100.0% (correct) | +93.3% |
| Lateral Movement | ❌ 11.3% (wrong) | ✅ 96.9% (correct) | +85.6% |
| **Overall** | **7/12 (58.3%)** | **12/12 (100%)** | **+41.7%** |

**Verdict**: Phase 2.5 is the **production-ready** model, fixing all critical detection failures.

## Explainability Artifacts

**Location**: `results/explainability/`

### SHAP Visualizations

**Files**:
- `shap_global_importance.png` - Top 20 features by mean absolute SHAP value
- `shap_summary_plot.png` - Beeswarm plot of feature value vs SHAP value
- `shap_dependence_1_tfidf_537.png` - Most important feature dependence plot
- `shap_dependence_2_tfidf_950.png` - Second most important feature
- `shap_force_plot_compliant.png` - Example compliant prediction explanation
- `shap_force_plot_non_compliant.png` - Example non-compliant prediction explanation

### SHAP Feature Importance

**File**: `results/explainability/shap_feature_importance.csv`

| Rank | Feature | SHAP Value | Interpretation |
|------|---------|------------|----------------|
| 1 | tfidf_537 | 2.1430 | Dominant predictor (attack keywords) |
| 2 | tfidf_950 | 0.4259 | Secondary strong predictor |
| 3 | tfidf_426 | 0.3528 | Tertiary predictor |
| 4 | tfidf_473 | 0.3378 | Access control terms |
| 5 | tfidf_198 | 0.2260 | Authentication terms |

**Key Finding**: TF-IDF feature 537 has **5x higher importance** than the second feature, suggesting it captures critical attack/violation keywords.

### Example Predictions

**Compliant Log**:
```
Log: "Successful SSH login for user admin from 10.0.0.1"
Prediction: compliant (99.0% confidence)
Top SHAP contributors:
  - tfidf_742 ("successful"): +1.2 (pushes toward compliant)
  - tfidf_128 ("login"): +0.8
  - control_AC-3: +0.3
```

**Non-Compliant Log**:
```
Log: "Failed SSH login from 192.168.1.100 - Access denied"
Prediction: non_compliant (99.9% confidence)
Top SHAP contributors:
  - tfidf_537 ("failed"): +2.3 (pushes toward non-compliant)
  - tfidf_622 ("denied"): +0.2
  - tfidf_542 ("access"): +0.1
```

## Loading Models

### Python
```python
import joblib

# Load XGBoost model
model = joblib.load('results/models/xgboost_phase2_5/xgboost_phase2_5.pkl')

# Load vectorizers and encoders
vectorizer = joblib.load('results/models/xgboost_phase2_5/tfidf_vectorizer.pkl')
control_encoder = joblib.load('results/models/xgboost_phase2_5/control_encoder.pkl')
family_encoder = joblib.load('results/models/xgboost_phase2_5/family_encoder.pkl')

# Verify model signature before use
from src.security.model_signing import ModelSigner
signer = ModelSigner(secret_key)
if not signer.verify_model('results/models/xgboost_phase2_5'):
    raise ValueError("Model integrity check failed - model may be tampered")

# Make prediction
features = vectorizer.transform([log_message])
# ... add control encodings ...
prediction = model.predict(features)
confidence = model.predict_proba(features).max()
```

## Evaluation Metrics

**Location**: `results/evaluation/`

**Files**:
- `confusion_matrix.png` - Visual confusion matrix
- `roc_curve.png` - ROC curve with AUC score
- `precision_recall_curve.png` - Precision-recall trade-off
- `classification_report.txt` - Detailed per-class metrics

### Confusion Matrix (Test Set)

```
                 Predicted
                 Compliant  Non-Compliant
Actually
Compliant        13,541     11 (FP)
Non-Compliant    114 (FN)   10,811
```

**Metrics**:
- **True Negatives (TN)**: 13,541
- **False Positives (FP)**: 11 (0.08% of compliant events misclassified)
- **False Negatives (FN)**: 114 (1.04% of violations missed) ⭐ LOW
- **True Positives (TP)**: 10,811

**Key Insight**: Only 114 false negatives out of 10,925 violations - critical for security where missing attacks is costly.

## Model Storage Best Practices

### File Permissions
```bash
# Secure model files
chmod 400 results/models/xgboost_phase2_5/xgboost_phase2_5.pkl
chmod 400 results/models/xgboost_phase2_5/model_signature.json

# Secure signing key
chmod 400 .model_signing_key
```

### Backup Strategy
```bash
# Create dated backup
cp -r results/models/xgboost_phase2_5/ backups/xgboost_phase2_5_2025-11-03/

# Verify backup integrity
diff -r results/models/xgboost_phase2_5/ backups/xgboost_phase2_5_2025-11-03/
```

### Version Control
- ✅ Model files tracked in Git LFS
- ✅ Model metadata (JSON) in regular Git
- ❌ Never commit signing keys or credentials

## Model Retraining

To retrain with new data:

```bash
# 1. Prepare new training data
python src/data_pipeline/prepare_training_data.py --data-dir data/new_samples/

# 2. Train new model
python train_xgboost_phase2_5.py --data-dir data/real_formatted/ --output results/models/xgboost_phase2_6/

# 3. Evaluate on test set
python evaluate_model.py --model results/models/xgboost_phase2_6/

# 4. Sign new model
python -c "from src.security.model_signing import ModelSigner; ModelSigner(open('.model_signing_key').read().strip()).sign_model('results/models/xgboost_phase2_6')"

# 5. Compare with Phase 2.5
python compare_models.py --model1 results/models/xgboost_phase2_5/ --model2 results/models/xgboost_phase2_6/

# 6. Deploy if improved
if [ $? -eq 0 ]; then
    cp -r results/models/xgboost_phase2_6/ results/models/production/
fi
```

**Recommended Retraining Frequency**: Quarterly (every 3 months) or when:
- New attack types emerge
- Model accuracy drops below 98%
- Significant distribution shift detected in production logs

---

**Last Updated**: November 3, 2025
**Production Model**: XGBoost Phase 2.5
**Model Version**: 2.5.0
**Accuracy**: 99.49% (24,477 test events)
**Recall**: 98.96% (critical for security)
