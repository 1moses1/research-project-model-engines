# Phase 2 Analysis: BERT + Temporal Features

**Date**: November 2, 2025
**Status**: ❌ REGRESSION - Below Target
**Overall Result**: 58.3% accuracy (7/12 scenarios)
**Previous Phase 1 Result**: 87.5% accuracy (7/8 scenarios)
**Target**: 95%+ accuracy

---

## Executive Summary

Phase 2 implementation added BERT embeddings (768-dim) and temporal features (26-dim) to achieve semantic understanding and pattern detection. While the model achieved **99.28% accuracy on the test set**, it performed **significantly worse** on real-world scenarios:

- **Phase 1**: 87.5% (7/8 scenarios)
- **Phase 2**: 58.3% (7/12 scenarios) ← **REGRESSION**

### Critical Issue Identified

The model exhibits a **systematic bias toward "compliant" predictions** for sophisticated attacks, predicting them as compliant with very high confidence (92-94%):

| Attack Type | Prediction | Confidence | Result |
|------------|-----------|-----------|---------|
| Phishing Email | compliant | 93.7% | ❌ WRONG |
| Insider Threat | compliant | 92.4% | ❌ WRONG |
| Lateral Movement | compliant | 90.4% | ❌ WRONG |
| DDoS Attack | compliant | 94.6% | ❌ WRONG |
| Credential Stuffing | compliant | 93.8% | ❌ WRONG |

---

## Phase 2 Implementation Details

### Features Added

**Total Features**: 2,796
- **TF-IDF**: 2,000 features (keyword matching)
- **BERT Embeddings**: 768 features (semantic understanding via DistilBERT)
- **Temporal Features**: 26 features (pattern detection)
- **Categorical**: 2 features (control_id, family)

### Temporal Features (26 total)

#### Basic Temporal (9 features)
- `hour`, `minute`, `day_of_week`, `day_of_month`, `month`
- `is_weekend`, `is_business_hours`, `is_late_night`, `is_unusual_time`

#### Sequence Features (5 features)
- `events_last_5min`, `failed_attempts_last_5min`
- `unique_ips_last_5min`, `unique_users_last_5min`
- `rapid_succession`

#### Anomaly Indicators (12 features)
- **Insider Threats**: `large_transfer`, `usb_access`, `sensitive_data`
- **Lateral Movement**: `multiple_connections`, `smb_rdp_ssh`
- **Volume Attacks**: `high_volume`, `spike_traffic`
- **Credentials**: `credential_related`, `multiple_ips`
- **Ransomware**: `encryption_activity`, `file_modification`
- **Combined**: `anomaly_score`

### Model Architecture

**XGBoost Parameters (Enhanced)**:
```python
{
    'max_depth': 8,           # Increased from 6
    'learning_rate': 0.05,    # Reduced for careful learning
    'n_estimators': 300,      # Increased from 200
    'tree_method': 'hist',    # Faster for large feature sets
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'min_child_weight': 3,
    'gamma': 0.1
}
```

### BERT Implementation

- **Model**: DistilBERT (`distilbert-base-uncased`)
- **Embedding Dimension**: 768
- **Processing Speed**: 19 batches/second on MPS (Mac GPU)
- **Total Processing Time**: ~75 seconds for 88,321 samples
- **Batch Size**: 64
- **Max Sequence Length**: 128 tokens

---

## Test Results Analysis

### Scenarios Passed (7/12)

| # | Scenario | Confidence | Phase 1 |
|---|----------|-----------|---------|
| 1 | Unauthorized SSH Access | 99.9% | ✅ PASS |
| 2 | Successful Compliance Check | 97.8% | ✅ PASS |
| 4 | Unpatched CVE | 86.1% | ✅ PASS |
| 5 | Encryption Enabled | 95.0% | ✅ PASS |
| 6 | Backup Failure | 100.0% | ✅ PASS |
| 7 | Ransomware Attack | 75.6% | ✅ FIXED (was 0% in baseline) |
| 9 | SQL Injection | 88.1% | ✅ PASS |

### Scenarios Failed (5/12)

| # | Scenario | Expected | Predicted | Confidence | Phase 1 | Issue |
|---|----------|----------|-----------|-----------|---------|-------|
| 3 | Phishing Email | non_compliant | **compliant** | 93.7% | ❌ FAIL | Regression from Phase 1 |
| 8 | Insider Threat | non_compliant | **compliant** | 92.4% | ❌ FAIL | Still failing (primary goal) |
| 10 | Lateral Movement | non_compliant | **compliant** | 90.4% | ❌ FAIL | New failure in Phase 2 |
| 11 | DDoS Attack | non_compliant | **compliant** | 94.6% | ❌ FAIL | New failure in Phase 2 |
| 12 | Credential Stuffing | non_compliant | **compliant** | 93.8% | ❌ FAIL | New failure in Phase 2 |

### Pattern Analysis

**Common characteristics of failures**:
1. All 5 failures are **sophisticated attacks** predicted as compliant
2. **Very high confidence** in wrong predictions (90-95%)
3. Attacks with **subtle/professional language** (phishing uses business terms)
4. Attacks requiring **volume/rate detection** (DDoS, credential stuffing)
5. **Novel attack patterns** not explicitly in training data

---

## Root Cause Analysis

### Hypothesis 1: BERT Semantic Bias

**BERT may be learning that "professional language" = "compliant"**

Example - Phishing Email:
```
"Email from unknown@suspicious-domain.ru blocked - Contains malicious link"
```

- BERT sees: "Email", "blocked", "domain" → professional business language
- Training data: Most compliant logs use professional language
- Result: BERT embeddings push prediction toward "compliant"

### Hypothesis 2: Temporal Features Lack Signal

**Temporal features only help when attacks have time-based patterns**

Attacks that PASSED (temporal signals present):
- ✅ Ransomware: "10,000 files encrypted in 5 minutes" → `rapid_succession=1`, `encryption_activity=1`
- ✅ Backup Failure: "7 consecutive days" → temporal pattern detected

Attacks that FAILED (weak temporal signals):
- ❌ Phishing: Single email event → no temporal pattern
- ❌ DDoS: "100,000 requests/sec from 500 IPs" → not in sequence features
- ❌ Credential Stuffing: "Login attempts from 200 IPs" → `multiple_ips=1` but BERT overrides

### Hypothesis 3: Overfitting to Synthetic Patterns

**Test Set Accuracy (99.28%) vs Real Scenario Accuracy (58.3%)**

This large gap suggests:
- Model learned synthetic data patterns very well
- Synthetic data doesn't capture real-world attack sophistication
- BERT embeddings memorize training data semantics

**Training Data Composition**:
- 72K synthetic compliance events (81.5%)
- 20K NSL-KDD intrusion logs (22.6%)
- 1.5K MITRE ATT&CK techniques (1.7%)
- 1K CISA KEV vulnerabilities (1.1%)

The synthetic data dominates training, potentially biasing BERT toward synthetic patterns.

### Hypothesis 4: Feature Importance Shift

**Top features may have shifted away from attack indicators**

Phase 2 top features (by importance):
1. Feature 478: 0.1553
2. Feature 610: 0.1141
3. Feature 1934: 0.0597

Without knowing which features these are (TF-IDF term, BERT dimension, or temporal), we can't verify if attack-specific keywords are still important.

---

## Why Phase 2 Performed Worse

### 1. Diluted Signal-to-Noise Ratio

**Phase 1**: 2,002 features (2000 TF-IDF + 2 categorical)
- Focused on keyword matching
- Clear attack indicators (e.g., "failed", "malicious", "blocked")

**Phase 2**: 2,796 features (+ 768 BERT + 26 temporal)
- Added 794 new features (39% increase)
- BERT embeddings may add noise for attacks with professional language
- Temporal features don't help attacks without time patterns

### 2. BERT Pre-training Bias

DistilBERT was pre-trained on:
- Wikipedia (general knowledge)
- BookCorpus (narrative text)

**NOT trained on**:
- Security logs
- Attack descriptions
- Compliance terminology

Result: BERT treats security logs like general text, potentially missing threat indicators.

### 3. Class Imbalance Amplification

**Training Distribution**:
- Compliant: 54,395 (61.6%)
- Non-compliant: 33,926 (38.4%)

With BERT adding 768 dimensions:
- More capacity for the model to learn "compliant" patterns
- BERT embeddings may cluster compliant logs together
- Minority class (non-compliant) gets overwhelmed

### 4. Temporal Feature Mismatch

**Designed for**: Insider threats, lateral movement, brute force
**Actually helps**: Only attacks with explicit temporal patterns (ransomware)
**Doesn't help**: Single-event attacks (phishing) or volume-based attacks without sequence data

---

## Comparison with Industry Benchmarks

| Model | Target Attacks | Accuracy | Notes |
|-------|---------------|----------|-------|
| **DeepLog** | Anomaly detection | 95.6% | LSTM-based, HDFS logs |
| **LogRobust** | Anomaly detection | 98.2% | Attention mechanism |
| **LogAnomaly** | Anomaly detection | 96.7% | LSTM + template mining |
| **Our Phase 1** | Compliance violations | 87.5% | Real scenarios, XGBoost |
| **Our Phase 2** | Compliance violations | 58.3% | Real scenarios, XGBoost+BERT |

**Key Difference**:
- Industry benchmarks test on **single dataset types** (HDFS, BGL, etc.)
- Our model tests on **diverse real-world attacks** across multiple frameworks
- Phase 2's advanced features hurt performance on sophisticated attacks

---

## Recommendations

### Option 1: Revert to Phase 1 Model (RECOMMENDED)

**Rationale**:
- Phase 1 achieved 87.5% on real scenarios
- Phase 2 achieved only 58.3% (worse than baseline 75%)
- 87.5% is closer to 95% target than 58.3%

**Action**:
- Deploy Phase 1 model to production
- Use Phase 2 as research experiment
- Document why "more features ≠ better performance"

### Option 2: Debug Phase 2 Bias

**Investigate**:
1. **SHAP Analysis**: Which features cause misclassifications?
   ```bash
   python analyze_phase2_failures.py --shap
   ```
2. **Feature Ablation**: Test without BERT, without temporal
3. **BERT Fine-tuning**: Train BERT on security-specific corpus

**Potential Fixes**:
- Reduce BERT weight in ensemble
- Add class weights to penalize false negatives
- Use adversarial training samples

### Option 3: Targeted Dataset Augmentation

**Add specific datasets for failing scenarios**:

| Scenario | Dataset Needed | Source |
|----------|---------------|--------|
| Phishing | Email security logs | PhishTank, OpenPhish |
| Insider Threat | Employee behavior logs | CERT Insider Threat Dataset |
| Lateral Movement | Network traffic logs | DARPA Intrusion Detection |
| DDoS | Traffic spike logs | CIC-DDoS2019 |
| Credential Stuffing | Auth failure logs | NCSA Auth logs |

**Risk**: May not fix BERT bias issue

### Option 4: Alternative Model Architecture

**Replace BERT with security-specific embeddings**:
- **SecBERT**: BERT pre-trained on CVE descriptions
- **CyBERT**: BERT for cybersecurity text
- **Custom Word2Vec**: Trained on security logs only

**Replace XGBoost with deep learning**:
- **Transformer encoder** with attention on attack patterns
- **CNN + LSTM** for sequence modeling
- **Graph Neural Network** for entity relationships

---

## Lessons Learned

### 1. More Features ≠ Better Performance

Adding 794 features (39% increase) made performance worse:
- BERT added semantic noise
- Temporal features only helped specific attack types
- Increased model complexity without proportional benefit

### 2. Test Set Accuracy is Misleading

99.28% test accuracy meant nothing when:
- Model failed on real sophisticated attacks
- Test set doesn't represent production scenarios
- Overfitting to synthetic data patterns

### 3. Domain-Specific Pre-training Matters

DistilBERT's general pre-training (Wikipedia, books) doesn't transfer well to:
- Security log analysis
- Threat detection
- Compliance terminology

### 4. Feature Engineering Requires Domain Knowledge

Blindly adding features without understanding:
- Which attacks they help detect
- How they interact with existing features
- What biases they introduce

Led to worse performance than simpler approach.

---

## Next Steps (Pending User Decision)

### Immediate Actions Required:

1. **User Decision**: Choose path forward
   - ✅ **Revert to Phase 1** (safest option)
   - 🔧 Debug Phase 2 (time-intensive)
   - 📊 Add targeted datasets (may not fix bias)
   - 🚀 Try new architecture (high risk)

2. **Documentation**: Update research log with Phase 2 findings

3. **Model Selection**:
   - If deploying: Use Phase 1 model (87.5%)
   - If researching: Investigate SHAP analysis

### Long-term Research Questions:

1. Can we fix BERT bias without losing semantic understanding?
2. Which temporal features actually help (feature ablation study)?
3. Should we use simpler models for production vs research?
4. How to better evaluate models on real-world scenarios?

---

## Files Created

### Phase 2 Implementation:
- `src/models/bert_feature_extractor.py` (366 lines)
- `src/models/temporal_feature_extractor.py` (300 lines)
- `train_phase2_ensemble.py` (420 lines)
- `test_phase2_model.py` (350 lines)

### Data Artifacts:
- `data/bert_embeddings/train_bert_embeddings.npy` (88321, 768)
- `data/bert_embeddings/val_bert_embeddings.npy` (18926, 768)
- `data/bert_embeddings/test_bert_embeddings.npy` (18927, 768)
- `data/temporal_enhanced/train_temporal_enhanced.csv`
- `data/temporal_enhanced/val_temporal_enhanced.csv`
- `data/temporal_enhanced/test_temporal_enhanced.csv`

### Model Artifacts:
- `results/models/xgboost_phase2/xgboost_phase2.pkl`
- `results/models/xgboost_phase2/tfidf_vectorizer.pkl`
- `results/models/xgboost_phase2/control_encoder.pkl`
- `results/models/xgboost_phase2/family_encoder.pkl`
- `results/models/xgboost_phase2/phase2_metrics.json`
- `results/models/xgboost_phase2/model_metadata.json`

### Logs:
- `logs/phase2_training.log` (training process)
- `logs/phase2_test_results.log` (detailed test results)

---

## Conclusion

Phase 2's advanced features (BERT embeddings + temporal patterns) **did not achieve the 95%+ target** and actually performed **significantly worse** than Phase 1's simpler approach (58.3% vs 87.5%).

The primary issue is a **systematic bias toward "compliant" predictions** for sophisticated attacks, likely caused by:
1. BERT learning that professional language = compliant
2. Temporal features not providing signal for all attack types
3. Overfitting to synthetic data patterns
4. Feature dilution reducing attack indicator importance

**Recommended Action**: Revert to Phase 1 model (87.5%) for production deployment while investigating Phase 2 failures as a research experiment.

---

**Status**: ⏸️ AWAITING USER DECISION
**Priority**: HIGH - Phase 2 regression must be addressed before production
**Contact**: Research Team
