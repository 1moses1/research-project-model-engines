# Research Novelty and Unique Contributions

## Executive Summary

This research project addresses a significant gap in AI-driven compliance auditing by developing the first machine learning system specifically designed for **regulatory control classification** with >95% accuracy and explainability requirements. Based on comprehensive literature review, no existing work has achieved >93% accuracy on compliance-specific log anomaly detection.

---

## 1. Identified Gaps in Current Research

### 1.1 Compliance-Specific Log Anomaly Detection
**Current State**:
- Best compliance auditing model: 90.12% (Random Forest for financial audit)
- General log anomaly models: 95-99% (but NOT compliance-focused)
- Gap: **No models >93% exist for regulatory control classification**

**Our Opportunity**: Achieve 95-99% accuracy specifically for compliance events

### 1.2 Lack of Explainability in High-Accuracy Models
**Current State**:
- Ensemble methods (ER-VEC): 99.99% but **black box**
- BERT-Log: 99.3% but **limited interpretability**
- EU AI Act (2024) requires **explainable AI** for compliance decisions

**Our Opportunity**: Combine high accuracy (>95%) with SHAP/LIME explainability

### 1.3 Single-Framework Focus
**Current State**:
- Existing models trained on ONE regulatory framework
- No multi-country regulatory adaptability
- Separate models for NIST, ISO 27001, PCI DSS

**Our Opportunity**: Base model with transfer learning for multi-country extensibility

### 1.4 Synthetic Dataset Generation Gap
**Current State**:
- Rwanda NCSA: No publicly available compliance datasets
- Privacy constraints prevent real compliance data sharing
- Existing synthetic generators NOT compliance-aware

**Our Opportunity**: First synthetic dataset for Rwanda cybersecurity controls

### 1.5 Real-Time Compliance Monitoring
**Current State**:
- Most models focus on batch processing
- Limited research on real-time compliance classification
- No integrated training/monitoring dashboards

**Our Opportunity**: Real-time system with live training visibility

---

## 2. Our Novel Contributions

### 2.1 Hybrid BERT-XGBoost Ensemble for Compliance Classification
**Innovation**:
```
BERT (regulatory text understanding)
    ↓
+ XGBoost (tabular compliance features)
    ↓
→ Stacking Ensemble
    ↓
→ SHAP Explainability Layer
```

**Why Novel**:
- First application of BERT+XGBoost to regulatory controls
- Combines text understanding with structured compliance data
- Expected accuracy: **96-99%** (exceeding current 90.12% baseline)
- Interpretable outputs via SHAP values

**Avoids Replication**:
- BERT-Log (2022): Only log anomaly, no compliance focus
- XGBoost (2024): Only network intrusion, no regulatory controls
- Our work: **Compliance-specific fusion model**

---

### 2.2 Rwanda-NIST Control Mapping Framework
**Innovation**:
- First comprehensive mapping of Rwanda NCSA controls to NIST SP 800-53
- Automated control taxonomy extraction from regulatory documents
- Multi-level abstraction for cross-country comparison

**Novelty**:
- No existing work maps Rwanda cybersecurity standards to international frameworks
- Enables transfer learning between regulatory systems
- Facilitates compliance harmonization

---

### 2.3 Synthetic Compliance Dataset Generator
**Innovation**:
- Rule-based + generative AI for compliance event creation
- Preserves control semantics while increasing diversity
- Labels: Control ID, compliance status, anomaly type, severity

**Dataset Schema** (Novel):
```python
{
    "event_id": str,
    "timestamp": datetime,
    "control_id": str,      # AC-2, AU-6, IR-4, etc.
    "framework": str,       # "NIST-800-53", "Rwanda-NCSA"
    "compliance_status": str,  # "compliant", "non-compliant"
    "anomaly_label": str,   # "normal", "suspicious", "critical"
    "evidence": list,       # Supporting log entries
    "explanation": str      # Human-readable reason
}
```

**Why Novel**:
- First compliance-aware synthetic dataset
- Multi-framework support (Rwanda + NIST)
- Explainability built into data structure

---

### 2.4 Transfer Learning for Multi-Country Regulatory Frameworks
**Innovation**:
- Base model trained on Rwanda + NIST controls
- Fine-tuning adapter for new countries (ISO 27001, PCI DSS, GDPR)
- Few-shot learning for rapid adaptation

**Architecture**:
```
Base Model (Rwanda + NIST)
    ↓
Regulatory Adapter Layer (country-specific)
    ↓
Fine-tuning on new controls (10-20 examples)
    ↓
>90% accuracy on new framework
```

**Why Novel**:
- First transfer learning approach for regulatory compliance
- Reduces training data requirements for new countries
- Enables global scalability

---

### 2.5 RAG-Enhanced Compliance Reasoning
**Innovation**:
- Retrieval Augmented Generation for regulatory text interpretation
- Dynamic retrieval of relevant control definitions during classification
- Claude/GPT integration for complex compliance queries

**Workflow**:
```
1. Log event detected
2. RAG retrieves relevant NIST/Rwanda control text
3. BERT+XGBoost classifies with context
4. LLM generates human-readable explanation
5. SHAP highlights decision factors
```

**Why Novel**:
- First RAG application to compliance auditing
- Combines structured ML with generative AI
- Provides audit-trail quality explanations

---

### 2.6 Interactive Training Dashboard with Claude Integration
**Innovation**:
- Real-time training progress visualization
- Integrated Claude assistant for guidance
- File upload for incremental training on new regulations

**Features**:
- Live accuracy/loss graphs per model (BERT, SVM, LSTM)
- Model comparison dashboard
- Interactive hyperparameter tuning
- Regulatory document upload → automatic control extraction
- Claude chatbot for training recommendations

**Why Novel**:
- First compliance ML system with integrated LLM assistant
- Democratizes AI-driven auditing for non-ML experts
- Real-time explainability during training

---

## 3. Avoiding Replication - Comparison to Top Models

| Model | Accuracy | Domain | Our Differentiation |
|-------|----------|--------|---------------------|
| BERT-Log (2022) | 99.3% | Log anomaly | We add **compliance-specific** classification |
| ER-VEC (2023) | 99.99% | IoT attacks | We add **explainability** + **regulatory focus** |
| Hybrid LSTM-CNN (2024) | 99.87% | IoT security | We focus **compliance**, not IoT |
| XGBoost (2024) | 99.54% | Network intrusion | We add **BERT text understanding** + **compliance** |
| Log2graphs (2023) | 97.39% | Unsupervised anomaly | We add **supervised compliance** labels |

**Key Differentiators**:
1. ✅ **Compliance-specific** (vs. general anomaly detection)
2. ✅ **Explainable** (SHAP/LIME + LLM explanations)
3. ✅ **Multi-framework** (Rwanda + NIST + extensible)
4. ✅ **Transfer learning** (adapt to new countries)
5. ✅ **Interactive dashboard** (Claude-assisted training)

---

## 4. Research Questions Addressed

### RQ1: How can ML effectively automate compliance auditing?
**Our Answer**: Hybrid BERT-XGBoost with RAG for text+tabular compliance data

**Novelty**: First fusion of transformer NLP with tree-based structured learning for regulatory controls

---

### RQ2: What models achieve optimal accuracy (>93%) in compliance classification?
**Our Answer**:
- **Baseline**: BERT (95-97%), XGBoost (94-96%), LSTM (92-94%)
- **Hybrid Ensemble**: 96-99% (exceeds current 90.12% state-of-art)

**Novelty**: First comparative evaluation of ML models specifically for compliance logs

---

### RQ3: How can a base model be designed for multi-country extensibility?
**Our Answer**: Transfer learning with regulatory adapter layers + few-shot fine-tuning

**Novelty**: First transfer learning framework for cross-country regulatory compliance

---

### RQ4: What role does explainability play in AI-driven auditing?
**Our Answer**: SHAP/LIME + RAG-generated explanations ensure regulatory trust

**Novelty**: First compliance system meeting EU AI Act explainability requirements

---

## 5. Algorithms and Datasets - Explicit Documentation

### 5.1 Algorithms Used

**For Mid-October Deliverable**:

1. **BERT Classifier**
   - Model: `bert-base-uncased` (110M parameters)
   - Fine-tuning: Rwanda control descriptions + NIST text
   - Loss: Cross-entropy
   - Optimizer: AdamW (lr=2e-5)
   - Expected accuracy: 95-97%

2. **XGBoost Classifier**
   - Trees: 500
   - Max depth: 6
   - Learning rate: 0.1
   - Features: Structured compliance attributes (user, action, resource, time)
   - Expected accuracy: 94-96%

3. **LSTM Classifier**
   - Architecture: Bi-directional LSTM (128 hidden units)
   - Embedding: 100-dim word vectors
   - Dropout: 0.3
   - Optimizer: Adam
   - Expected accuracy: 92-94%

4. **Drain Log Parser**
   - Template extraction: Similarity threshold 0.5
   - Depth: 4
   - Purpose: Convert raw logs → structured templates

5. **SMOTE (Class Balancing)**
   - Oversampling non-compliant events
   - k-neighbors: 5
   - Purpose: Handle imbalanced compliance data

---

### 5.2 Datasets

**Synthetic Dataset** (Primary):
- Records: 100,000 compliance events
- Controls: 50 NIST controls + 30 Rwanda controls
- Split: 70% train / 15% validation / 15% test
- Labels: Compliance status + anomaly type

**Public Benchmarking Datasets**:
1. **HDFS Logs**
   - Source: Hadoop Distributed File System
   - Size: 11M log entries
   - Purpose: Baseline log parsing evaluation

2. **BGL Logs**
   - Source: BlueGene/L Supercomputer
   - Size: 4.7M log entries
   - Purpose: Long-sequence anomaly detection

3. **NSL-KDD** (if needed)
   - Source: Network intrusion dataset
   - Purpose: Security event classification baseline

---

### 5.3 Evaluation Metrics

**Primary Metrics**:
- Accuracy: Overall correctness
- Precision: True positive rate (avoid false alarms)
- Recall: Coverage of compliance violations
- F1-Score: Harmonic mean
- **Error Rate**: Critical for auditing (target <5%)

**Explainability Metrics**:
- SHAP consistency: Feature attribution stability
- Human agreement: Explanations match auditor reasoning (>80%)

---

## 6. Expected Outcomes

### Mid-October Deliverable:
✅ Baseline models: BERT (95-97%), XGBoost (94-96%), LSTM (92-94%)
✅ Data pipeline: Synthetic dataset + log parsing
✅ Comparison framework: Side-by-side accuracy/error analysis

### Mid-November Deliverable:
✅ Hybrid ensemble: 96-99% accuracy
✅ Explainability: SHAP integration
✅ Prototype dashboard: Real-time training monitoring

### Spring 2026:
✅ Transfer learning: ISO 27001 + PCI DSS adaptation
✅ RAG integration: LLM-powered explanations
✅ Journal paper: Full system evaluation

---

## 7. Supervisor Feedback Integration

### Feedback #1: Check models with >93%, identify novelty
**✅ Addressed**: Literature review found 10 models (95-99.99%)
**✅ Novelty**: None focus on compliance-specific classification

### Feedback #2: Explicitly mention models, datasets, algorithms, results
**✅ Addressed**: Documented in Section 5 above + research report

### Feedback #3: Fine-tune existing models instead of from scratch
**✅ Addressed**: Using pre-trained BERT + XGBoost with domain adaptation

### Feedback #4: Build base model for multi-country extensibility
**✅ Addressed**: Transfer learning architecture (Section 2.4)

### Feedback #5: Try different algorithms, compare results
**✅ Addressed**: BERT vs SVM vs LSTM vs Hybrid Ensemble

### Feedback #6: Create UI with training visibility
**✅ Addressed**: Streamlit dashboard with Claude integration (Phase 7)

### Feedback #7: Answer research questions
**✅ Addressed**: Explicit mapping in Section 4

### Feedback #8: Choose 1 model or group by features
**✅ Addressed**: Hybrid ensemble (BERT+XGBoost) as primary, baselines for comparison

---

## 8. Contribution to Research Community

1. **First Rwanda cybersecurity compliance dataset** (synthetic)
2. **First BERT+XGBoost fusion** for regulatory classification
3. **First transfer learning framework** for cross-country compliance
4. **First explainable compliance AI** meeting EU AI Act standards
5. **Open-source dashboard** democratizing compliance automation

---

## 9. Publication Strategy

### Conference Paper (December 2025)
**Title**: "Explainable AI for Multi-Framework Compliance Auditing: A Transfer Learning Approach"

**Venues**:
- ACM CCS (Computer and Communications Security)
- NDSS (Network and Distributed System Security)
- IEEE S&P (Security and Privacy)

**Key Contributions**:
- Novel BERT-XGBoost hybrid achieving 96-99% accuracy
- First Rwanda NCSA compliance dataset
- Transfer learning for regulatory extensibility

### Journal Article (May 2026)
**Title**: "Automated Compliance Auditing for National Cybersecurity Standards: A Machine Learning Framework with Global Applicability"

**Venues**:
- IEEE Transactions on Dependable and Secure Computing
- ACM Transactions on Privacy and Security
- Computers & Security (Elsevier)

**Key Contributions**:
- Comprehensive system evaluation
- Multi-country validation (Rwanda, US, EU)
- Explainability analysis

---

## 10. Timeline Alignment

| Phase | Deliverable | Novel Contribution |
|-------|-------------|-------------------|
| Mid-Oct 2025 | Baseline models + pipeline | Synthetic dataset + comparative evaluation |
| Mid-Nov 2025 | Hybrid ensemble + dashboard | 96-99% accuracy + interactive training |
| Dec 2025 | Conference paper | BERT-XGBoost fusion + explainability |
| Feb 2026 | Explainability analysis | SHAP/LIME validation |
| Mar 2026 | Transfer learning | ISO 27001 + PCI DSS adaptation |
| May 2026 | Journal paper | Full system + global validation |

---

**Conclusion**: This research makes 5 significant novel contributions while avoiding replication of existing work. The combination of high accuracy (>95%), explainability (SHAP+LLM), multi-framework support (Rwanda+NIST+extensible), and interactive tooling (Claude dashboard) positions this as a unique and impactful contribution to cybersecurity compliance automation.

---

**Last Updated**: October 2025
**Author**: Moise Iradukunda - Carnegie Mellon University
**Supervisor Feedback**: Fully integrated
