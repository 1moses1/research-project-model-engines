# Model Selection Strategy

## Executive Decision

**Primary Approach**: Implement 3 baseline models + 1 hybrid ensemble

### Selected Models for Mid-October Deliverable:

1. ✅ **BERT Classifier** (Fine-tuned)
2. ✅ **XGBoost** (Gradient Boosting)
3. ✅ **LSTM** (Deep Learning Baseline)
4. ✅ **BERT-XGBoost Hybrid Ensemble** (Novel Contribution)

**Rationale**: Covers transformer-based, tree-based, and recurrent architectures while staying focused

---

## 1. BERT vs SVM vs LSTM vs XGBoost Comparison

### 1.1 BERT (Transformer-Based)

**Strengths**:
- ✅ State-of-art text understanding (99.3% on HDFS logs)
- ✅ Pre-trained on massive corpora → transfer learning
- ✅ Bidirectional context → better compliance text interpretation
- ✅ Handles regulatory language nuances

**Weaknesses**:
- ❌ High computational cost (110M parameters)
- ❌ Requires GPU for training
- ❌ Slower inference than traditional ML
- ❌ Less interpretable than tree models

**Use Case**: Regulatory text classification, log message understanding

**Expected Accuracy**: 95-97%

**Decision**: ✅ **INCLUDE** (best for text-based compliance)

---

### 1.2 SVM (Support Vector Machine)

**Strengths**:
- ✅ Effective with high-dimensional data
- ✅ Works well with small datasets
- ✅ Mathematically interpretable (support vectors)
- ✅ Fast training and inference

**Weaknesses**:
- ❌ Requires extensive feature engineering
- ❌ Performance plateaus around 90-92% (not >93%)
- ❌ Kernel selection can be tricky
- ❌ Doesn't scale well to very large datasets

**Literature Performance**:
- SVM with Naive Bayes: 99.35% (NSL-KDD) ← but with ensemble
- Standalone SVM: 85-90% typically

**Decision**: ❌ **EXCLUDE** (replaced by XGBoost for better accuracy + interpretability)

---

### 1.3 LSTM (Long Short-Term Memory)

**Strengths**:
- ✅ Excellent for sequential/temporal patterns
- ✅ Captures long-range dependencies in logs
- ✅ Proven effectiveness in log anomaly detection
- ✅ Good for time-series compliance events

**Weaknesses**:
- ❌ Training can be slow and unstable
- ❌ Requires careful hyperparameter tuning
- ❌ Less effective than BERT for text understanding
- ❌ Gradient vanishing issues with long sequences

**Literature Performance**:
- Hybrid LSTM-CNN: 99.87% (IoT)
- Standalone LSTM: 88-93% (log analysis)

**Expected Accuracy**: 92-94%

**Decision**: ✅ **INCLUDE** (important baseline for sequential analysis)

---

### 1.4 XGBoost (Extreme Gradient Boosting)

**Strengths**:
- ✅ Highest accuracy among traditional ML (99.54%)
- ✅ Highly interpretable (feature importance, SHAP)
- ✅ Fast training and inference
- ✅ Robust to overfitting with regularization
- ✅ Handles mixed data types (categorical + numerical)

**Weaknesses**:
- ❌ Requires feature engineering for text data
- ❌ Can overfit on small datasets
- ❌ Less effective for raw text than BERT

**Literature Performance**:
- XGBoost: 99.54% (network intrusion)
- LightGBM: 99.651% (IoT security)

**Expected Accuracy**: 94-96%

**Decision**: ✅ **INCLUDE** (replaces SVM, better for tabular compliance features)

---

## 2. Fine-Tuning vs Training from Scratch

### Decision Matrix

| Model | Strategy | Rationale |
|-------|----------|-----------|
| **BERT** | ✅ **Fine-tune** `bert-base-uncased` | Pre-trained weights understand language; just adapt to compliance domain |
| **XGBoost** | ✅ **Train from scratch** | No pre-trained boosting models; fast to train anyway |
| **LSTM** | ⚖️ **Hybrid**: Pre-trained embeddings (GloVe/Word2Vec) + train LSTM layers | Embeddings provide linguistic knowledge, LSTM learns compliance patterns |
| **Ensemble** | ✅ **Fine-tune** BERT + **Train** XGBoost + **Stacking** | Combine best of both |

### Why Fine-Tuning BERT?

**Advantages**:
- 🚀 **10-100x faster** than training from scratch
- 📈 **5-10% higher accuracy** than random initialization
- 💾 **Less data required** (can work with 10K examples vs 1M+)
- 🎯 **Transfer learning** from general language to compliance domain

**Pre-trained Model**:
- `bert-base-uncased` (Hugging Face)
- 110M parameters
- Pre-trained on Books Corpus + English Wikipedia

**Fine-tuning Approach**:
```python
from transformers import BertForSequenceClassification

model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=2,  # compliant vs non-compliant
    problem_type="single_label_classification"
)

# Freeze early layers, train classification head + last 2 layers
for param in model.bert.encoder.layer[:10].parameters():
    param.requires_grad = False
```

**Training Strategy**:
- Epochs: 3-5 (avoid overfitting)
- Learning rate: 2e-5 (small adjustments to pre-trained weights)
- Batch size: 16-32
- Optimizer: AdamW with warmup

---

## 3. Pre-trained Models for Compliance/Log Analysis

### 3.1 BERT Variants

| Model | Parameters | Use Case | Our Choice |
|-------|-----------|----------|------------|
| `bert-base-uncased` | 110M | General text | ✅ **Selected** |
| `bert-large-uncased` | 340M | Higher accuracy, slower | ❌ Too slow for prototype |
| `roberta-base` | 125M | Improved BERT | ⚖️ Alternative if BERT fails |
| `distilbert-base` | 66M | Faster, 95% BERT performance | ⚖️ For deployment optimization |

**Decision**: Start with `bert-base-uncased`, switch to RoBERTa if accuracy <95%

---

### 3.2 Specialized Models

| Model | Domain | Relevance | Decision |
|-------|--------|-----------|----------|
| **SecBERT** | Cybersecurity text | High (trained on CVE, MITRE ATT&CK) | ✅ **Test if available** |
| **LogBERT** | System logs | High (optimized for log structure) | ✅ **Research for Phase II** |
| **Legal-BERT** | Legal/regulatory text | Medium (regulatory language) | ⚖️ Consider for Rwanda law parsing |

**Action**:
1. Start with `bert-base-uncased` (well-documented, stable)
2. Benchmark against SecBERT if publicly available
3. Document performance difference

---

### 3.3 Word Embeddings for LSTM

| Embedding | Dimensions | Use Case | Our Choice |
|-----------|-----------|----------|------------|
| GloVe | 100-300 | General text | ✅ **Selected** (GloVe-100d) |
| Word2Vec | 300 | Alternative | ❌ GloVe performs better |
| FastText | 300 | Handles OOV words | ⚖️ If many unknown compliance terms |

**Decision**: Use GloVe 100-dimensional embeddings for LSTM

---

## 4. Model Grouping by Features

### Group 1: Text-Centric Models (Log Messages)
**Feature**: Raw log text, regulatory descriptions

| Model | Feature Type | Strength |
|-------|-------------|----------|
| **BERT** | Text → Contextual embeddings | Best text understanding |
| **LSTM** | Text → Word embeddings → Sequences | Temporal patterns |

**Shared Pipeline**:
```
Raw Log Text → Tokenization → Embeddings → Classification
```

---

### Group 2: Structured-Feature Models (Compliance Attributes)
**Feature**: User ID, action, resource, timestamp, control_id, status_code

| Model | Feature Type | Strength |
|-------|-------------|----------|
| **XGBoost** | Tabular (categorical + numerical) | Best for structured data |

**Feature Engineering**:
```python
features = [
    'user_id_encoded',      # Categorical encoding
    'action_type',          # One-hot encoding
    'hour_of_day',          # Temporal feature
    'control_category',     # Multi-class
    'resource_sensitivity', # Ordinal
    'recent_failures_count' # Aggregated
]
```

---

### Group 3: Hybrid (Text + Structured)
**Feature**: Combined

| Model | Architecture | Strength |
|-------|-------------|----------|
| **BERT-XGBoost Ensemble** | Text (BERT) + Tabular (XGBoost) → Stacking | Best of both worlds |

**Pipeline**:
```
Text → BERT → Prob_text
Structured → XGBoost → Prob_struct
     ↓
Meta-Classifier (Logistic Regression)
     ↓
Final Prediction
```

---

## 5. Optimal Approach Selection

### For Mid-October Deliverable

**Baseline Models** (Individual):
1. **BERT**: Text-only compliance classification
2. **XGBoost**: Structured-only compliance classification
3. **LSTM**: Sequence-based compliance classification

**Hybrid Model** (Novel):
4. **BERT-XGBoost Stacking Ensemble**: Combined text + structured

### Rationale

| Requirement | Solution |
|-------------|----------|
| >93% accuracy | BERT (95-97%) + XGBoost (94-96%) + Ensemble (96-99%) ✅ |
| Interpretability | XGBoost feature importance + SHAP ✅ |
| Avoid replication | No existing BERT-XGBoost for compliance ✅ |
| Compare algorithms | 3 different paradigms (transformer, boosting, RNN) ✅ |
| Multi-country | BERT fine-tuning on new regulations ✅ |
| Computational feasibility | All trainable on single GPU in <24 hours ✅ |

---

## 6. Evaluation Framework Design

### 6.1 Metrics

**Primary Metrics**:
- Accuracy: `(TP + TN) / Total`
- Precision: `TP / (TP + FP)`
- Recall: `TP / (TP + FN)`
- F1-Score: `2 * (Precision * Recall) / (Precision + Recall)`
- **Error Rate**: `(FP + FN) / Total` ← Critical for auditing

**Secondary Metrics**:
- AUC-ROC: Area under ROC curve
- Confusion Matrix: Breakdown by control category
- Training Time: Computational efficiency
- Inference Time: Real-time applicability

---

### 6.2 Comparison Framework

**Automated Comparison Script**:
```python
# src/utils/model_comparator.py

class ModelComparator:
    def __init__(self, models, test_data):
        self.models = models
        self.test_data = test_data

    def compare_all(self):
        results = {}
        for name, model in self.models.items():
            results[name] = {
                'accuracy': self.evaluate_accuracy(model),
                'precision': self.evaluate_precision(model),
                'recall': self.evaluate_recall(model),
                'f1': self.evaluate_f1(model),
                'error_rate': self.evaluate_error_rate(model),
                'train_time': model.train_time,
                'inference_time': self.measure_inference(model)
            }
        return pd.DataFrame(results).T
```

**Visualization Dashboard**:
- Side-by-side accuracy bar chart
- ROC curves overlaid
- Confusion matrices grid
- Training curves (loss/accuracy over epochs)

---

## 7. Implementation Priorities

### Phase 1 (Week 1): Data Pipeline
- [ ] Synthetic dataset generation
- [ ] Control mapper (NIST + Rwanda)
- [ ] Log parser (Drain)
- [ ] Train/val/test split (70/15/15)

### Phase 2 (Week 2): Baseline Models
- [ ] BERT classifier
- [ ] XGBoost classifier
- [ ] LSTM classifier
- [ ] Evaluation metrics

### Phase 3 (Week 3): Hybrid Ensemble
- [ ] BERT-XGBoost stacking
- [ ] Hyperparameter optimization
- [ ] Comparative evaluation

### Phase 4 (Week 4): Dashboard & Documentation
- [ ] Training monitoring UI
- [ ] Model comparison visualizations
- [ ] Mid-October deliverable report

---

## 8. Resource Requirements

### Computational

| Model | Training Time | GPU Memory | Inference Time |
|-------|--------------|------------|----------------|
| BERT | 2-4 hours | 8-12 GB | 10-20 ms |
| XGBoost | 5-15 minutes | CPU only | 1-2 ms |
| LSTM | 1-2 hours | 4-6 GB | 5-10 ms |
| Ensemble | 3-5 hours | 8-12 GB | 15-25 ms |

**Recommended Setup**:
- GPU: NVIDIA RTX 3090 / A100 (24GB VRAM)
- CPU: 16+ cores for XGBoost parallelization
- RAM: 32GB+
- Storage: 100GB SSD

### Data

| Dataset | Size | Purpose |
|---------|------|---------|
| Synthetic (Rwanda + NIST) | 100K events | Primary training |
| HDFS | 11M logs | Benchmarking log parser |
| BGL | 4.7M logs | Sequence length testing |

---

## 9. Risk Mitigation

### Risk 1: BERT fails to achieve 95% accuracy
**Mitigation**: Switch to RoBERTa or SecBERT

### Risk 2: Synthetic data too simple
**Mitigation**: Integrate HDFS/BGL for realistic log patterns

### Risk 3: XGBoost overfits
**Mitigation**: Cross-validation + regularization (max_depth=6, min_child_weight=3)

### Risk 4: Ensemble doesn't improve over baselines
**Mitigation**: Document comparative analysis; single best model is acceptable

---

## 10. Success Criteria

### Mid-October Deliverable Success:
✅ At least ONE model achieves >93% accuracy
✅ All three baselines implemented and evaluated
✅ Comparison framework generates automated reports
✅ Data pipeline processes Rwanda + NIST controls
✅ Dashboard visualizes training progress

### Stretch Goals:
🎯 Ensemble achieves >95% accuracy
🎯 Error rate <5%
🎯 All models explainable via SHAP
🎯 Transfer learning demo (fine-tune on new control set)

---

## Final Recommendation

**Primary Models**:
1. BERT (fine-tuned `bert-base-uncased`)
2. XGBoost (trained from scratch)
3. LSTM (GloVe embeddings + trained LSTM)
4. BERT-XGBoost Ensemble (stacking)

**Why This Combination**:
- ✅ Covers transformer, boosting, RNN paradigms
- ✅ Text + structured data fusion
- ✅ Interpretability (XGBoost + SHAP)
- ✅ State-of-art accuracy potential (96-99%)
- ✅ Novel contribution (hybrid ensemble)
- ✅ Focused scope (avoids SVM/CNN distractions)

**Next Steps**:
→ Proceed to Phase 4: Data Pipeline Implementation
→ Start with control mapper and synthetic dataset generator

---

**Document Version**: 1.0
**Last Updated**: October 2025
**Status**: Approved for Implementation
