# Model Performance Comparison: Baseline → Phase 1 → Phase 2

**Project**: Rwanda SOC Compliance Violation Detection
**Last Updated**: November 2, 2025

---

## Performance Evolution

```
Baseline → Phase 1 → Phase 2
  75%    →  87.5%  →  58.3%  ❌ REGRESSION
```

### Visual Performance Timeline

```
100% ┤
     │                                    Target: 95%
 95% ┤ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
     │
 90% ┤
     │                      ████
 85% ┤                      █  █ Phase 1: 87.5%
     │                      █  █
 80% ┤                      █  █
     │        ████          █  █
 75% ┤        █  █          █  █
     │        █  █ Baseline █  █
 70% ┤        █  █  75%     █  █
     │        █  █          █  █
 65% ┤        █  █          █  █
     │        █  █          █  █
 60% ┤        █  █          █  █
     │        █  █          █  █                    ████
 55% ┤        █  █          █  █                    █  █ Phase 2: 58.3%
     │        █  █          █  █                    █  █
 50% ┤        ████          ████                    ████
     └────────┴────────────┴────────────────────────┴────────────
           Original    Phase 1 (+Real)    Phase 2 (+BERT+Temporal)
```

---

## Detailed Comparison Table

| Metric | Baseline | Phase 1 | Phase 2 | Change (P1→P2) |
|--------|----------|---------|---------|----------------|
| **Overall Accuracy** | 75.0% (6/8) | 87.5% (7/8) | 58.3% (7/12) | ❌ -29.2 pp |
| **Test Set Accuracy** | 94.2% | 96.8% | 99.28% | ✅ +2.48 pp |
| **Scenarios Tested** | 8 | 8 | 12 | +4 scenarios |
| **Scenarios Passed** | 6 | 7 | 7 | 0 |
| **Scenarios Failed** | 2 | 1 | 5 | ❌ +4 failures |
| **Total Features** | 2,002 | 2,002 | 2,796 | +794 (39%) |
| **Model Complexity** | XGBoost | XGBoost | XGBoost + BERT | Higher |
| **Training Time** | ~5 min | ~8 min | ~45 min | 5.6x slower |
| **Inference Speed** | Fast | Fast | Slow (BERT) | 10x slower |

---

## Scenario-by-Scenario Breakdown

### Baseline (Original Model) - 6/8 Pass (75%)

| Scenario | Result | Confidence | Issue |
|----------|--------|-----------|-------|
| 1. Unauthorized SSH | ✅ PASS | 94.3% | - |
| 2. Compliance Check | ✅ PASS | 98.1% | - |
| 3. Phishing Email | ❌ FAIL | 67.8% | False negative |
| 4. Unpatched CVE | ✅ PASS | 89.2% | - |
| 5. Encryption Enabled | ✅ PASS | 96.5% | - |
| 6. Backup Failure | ✅ PASS | 88.7% | - |
| 7. Ransomware | ❌ FAIL | 48.3% | False negative (0% detection) |
| 8. SQL Injection | ✅ PASS | 91.4% | - |

**Key Issues**:
- Ransomware completely missed (0% detection)
- Phishing email not detected

---

### Phase 1 (Real Data Integration) - 7/8 Pass (87.5%)

**Improvements**:
- Added 20K NSL-KDD intrusion logs
- Added 1.5K MITRE ATT&CK techniques
- Added 1K CISA KEV vulnerabilities
- Enhanced keyword detection

| Scenario | Result | Confidence | Change from Baseline |
|----------|--------|-----------|---------------------|
| 1. Unauthorized SSH | ✅ PASS | 99.1% | ⬆️ +4.8 pp |
| 2. Compliance Check | ✅ PASS | 99.3% | ⬆️ +1.2 pp |
| 3. Phishing Email | ❌ FAIL | 71.2% | ⚠️ Still failing |
| 4. Unpatched CVE | ✅ PASS | 92.7% | ⬆️ +3.5 pp |
| 5. Encryption Enabled | ✅ PASS | 98.2% | ⬆️ +1.7 pp |
| 6. Backup Failure | ✅ PASS | 94.1% | ⬆️ +5.4 pp |
| 7. Ransomware | ✅ PASS | 93.3% | 🎯 FIXED (+93.3 pp) |
| 8. SQL Injection | ✅ PASS | 95.8% | ⬆️ +4.4 pp |

**Key Achievements**:
- ✅ Ransomware detection FIXED (0% → 93.3%)
- ✅ Overall accuracy improved 75% → 87.5%
- ❌ Phishing still failing (insider threats untested)

---

### Phase 2 (BERT + Temporal) - 7/12 Pass (58.3%)

**Enhancements**:
- Added BERT embeddings (768-dim semantic understanding)
- Added temporal features (26-dim pattern detection)
- Increased to 12 test scenarios (+4 challenging cases)

| Scenario | Result | Confidence | Change from Phase 1 |
|----------|--------|-----------|---------------------|
| 1. Unauthorized SSH | ✅ PASS | 99.9% | ⬆️ +0.8 pp |
| 2. Compliance Check | ✅ PASS | 97.8% | ⬇️ -1.5 pp |
| 3. Phishing Email | ❌ FAIL | 93.7% (wrong) | ❌ REGRESSION (high confidence wrong) |
| 4. Unpatched CVE | ✅ PASS | 86.1% | ⬇️ -6.6 pp |
| 5. Encryption Enabled | ✅ PASS | 95.0% | ⬇️ -3.2 pp |
| 6. Backup Failure | ✅ PASS | 100.0% | ⬆️ +5.9 pp |
| 7. Ransomware | ✅ PASS | 75.6% | ⬇️ -17.7 pp |
| 8. Insider Threat (NEW) | ❌ FAIL | 92.4% (wrong) | ❌ NEW FAILURE |
| 9. SQL Injection | ✅ PASS | 88.1% | ⬇️ -7.7 pp |
| 10. Lateral Movement (NEW) | ❌ FAIL | 90.4% (wrong) | ❌ NEW FAILURE |
| 11. DDoS Attack (NEW) | ❌ FAIL | 94.6% (wrong) | ❌ NEW FAILURE |
| 12. Credential Stuffing (NEW) | ❌ FAIL | 93.8% (wrong) | ❌ NEW FAILURE |

**Critical Issues**:
- ❌ All 4 new sophisticated scenarios FAILED
- ❌ Phishing regression (now predicts compliant with 93.7% confidence)
- ❌ Insider threat detection FAILED (primary Phase 2 goal)
- ⚠️ Lower confidence on scenarios that still pass

---

## Feature Comparison

### Baseline Features (2,002 total)

```
TF-IDF: 2,000 features
├── Unigrams + Bigrams
├── Max features: 2,000
└── Keyword-based matching

Categorical: 2 features
├── control_id (encoded)
└── control_family (encoded)
```

### Phase 1 Features (2,002 total - same as baseline)

```
Same as baseline, but with enhanced training data:
├── 72K synthetic compliance events
├── 20K NSL-KDD intrusion logs (NEW)
├── 1.5K MITRE ATT&CK techniques (NEW)
└── 1K CISA KEV vulnerabilities (NEW)
```

### Phase 2 Features (2,796 total)

```
TF-IDF: 2,000 features
└── Same as Phase 1

Categorical: 2 features
└── Same as Phase 1

Temporal: 26 features (NEW)
├── Basic temporal: hour, day_of_week, is_weekend, is_business_hours, etc. (9)
├── Sequence features: events_last_5min, failed_attempts_last_5min, etc. (5)
└── Anomaly indicators: large_transfer, usb_access, encryption_activity, etc. (12)

BERT Embeddings: 768 features (NEW)
├── Model: DistilBERT (distilbert-base-uncased)
├── Dimension: 768
└── Semantic text understanding
```

---

## Attack Detection Capability

### Legend
- ✅ Correctly detected (high confidence)
- ⚠️ Detected but low confidence
- ❌ Missed (false negative)
- 🔴 Regression (now fails)

| Attack Type | Baseline | Phase 1 | Phase 2 | Best Model |
|------------|----------|---------|---------|------------|
| **Unauthorized Access** | ✅ 94% | ✅ 99% | ✅ 100% | Phase 2 |
| **Ransomware** | ❌ 0% | ✅ 93% | ✅ 76% | Phase 1 |
| **SQL Injection** | ✅ 91% | ✅ 96% | ✅ 88% | Phase 1 |
| **Unpatched CVE** | ✅ 89% | ✅ 93% | ✅ 86% | Phase 1 |
| **Backup Failure** | ✅ 89% | ✅ 94% | ✅ 100% | Phase 2 |
| **Phishing Email** | ❌ 68% | ❌ 71% | 🔴 7% (predicts compliant) | Phase 1 |
| **Insider Threat** | - | - | ❌ 8% (predicts compliant) | - |
| **Lateral Movement** | - | - | ❌ 10% (predicts compliant) | - |
| **DDoS Attack** | - | - | ❌ 5% (predicts compliant) | - |
| **Credential Stuffing** | - | - | ❌ 6% (predicts compliant) | - |

---

## Confidence Analysis

### Correct Predictions - Confidence Distribution

| Model | Avg Confidence (Correct) | Range |
|-------|-------------------------|-------|
| Baseline | 92.3% | 48.3% - 98.1% |
| Phase 1 | 95.8% | 93.3% - 99.3% |
| Phase 2 | 91.8% | 75.6% - 100.0% |

### Incorrect Predictions - Confidence Analysis

| Model | Scenario | Wrong Prediction | Confidence | Issue |
|-------|----------|------------------|-----------|-------|
| Baseline | Phishing | compliant | 67.8% | Low confidence wrong |
| Baseline | Ransomware | compliant | 48.3% | Low confidence wrong |
| Phase 1 | Phishing | compliant | 71.2% | Low confidence wrong |
| **Phase 2** | **Phishing** | **compliant** | **93.7%** | **HIGH confidence wrong** ❌ |
| **Phase 2** | **Insider Threat** | **compliant** | **92.4%** | **HIGH confidence wrong** ❌ |
| **Phase 2** | **Lateral Movement** | **compliant** | **90.4%** | **HIGH confidence wrong** ❌ |
| **Phase 2** | **DDoS** | **compliant** | **94.6%** | **HIGH confidence wrong** ❌ |
| **Phase 2** | **Credential Stuffing** | **compliant** | **93.8%** | **HIGH confidence wrong** ❌ |

**Critical Finding**: Phase 2 is **overconfident and wrong** - much worse than Phase 1's low-confidence wrong predictions.

---

## Performance vs Complexity Trade-off

```
                   High Performance (95%+)
                          ↑
                          │
                          │  INDUSTRY BENCHMARKS
                          │  (DeepLog: 95.6%)
                          │
                    90%   ├─────────────────────────
                          │
                          │  ⚪ Phase 1 (87.5%)
                          │
                    85%   │
                          │
                          │
                    80%   │
                          │
                          │
                    75%   │  ⚪ Baseline (75%)
                          │
                    70%   │
                          │
                    65%   │
                          │
                    60%   │                        ⚪ Phase 2 (58.3%)
                          │
                    55%   │
                          │
                    50%   └─────────────────────────────────→
                          Low          Medium         High
                                   Complexity

Baseline:  Low complexity, 75% accuracy
Phase 1:   Low complexity, 87.5% accuracy ✅ BEST
Phase 2:   High complexity, 58.3% accuracy ❌ WORSE
```

**Conclusion**: Increasing complexity (BERT + temporal) decreased performance.

---

## Training Data Composition

### Baseline & Phase 1
```
Total: 88,321 training samples

Synthetic: 72,000 (81.5%)
├── NIST SP 800-53 scenarios
├── Rwanda NCSA controls
└── Generated compliance events

NSL-KDD: 20,000 (22.6%)        [Phase 1 only]
├── Intrusion detection logs
└── Network attacks

MITRE ATT&CK: 1,500 (1.7%)    [Phase 1 only]
└── Attack techniques

CISA KEV: 1,000 (1.1%)        [Phase 1 only]
└── Known exploited vulnerabilities
```

### Phase 2
```
Same as Phase 1 + Enhanced Features:
├── BERT embeddings (pre-computed, 768-dim)
└── Temporal features (extracted, 26-dim)
```

---

## Resource Requirements

| Model | Training Time | Inference Time | Model Size | GPU Required |
|-------|--------------|----------------|-----------|--------------|
| Baseline | 5 min | <1ms | 12 MB | No |
| Phase 1 | 8 min | <1ms | 15 MB | No |
| Phase 2 | 45 min | 50-100ms | 450 MB | Yes (BERT) |

**BERT Processing**:
- Pre-computation: 75 seconds for 88K samples
- Inference: 50-100ms per log (vs <1ms for Phase 1)
- Device: MPS (Mac GPU) or CPU fallback

---

## Industry Benchmark Comparison

| Model | Dataset | Attack Type | Accuracy | Notes |
|-------|---------|-------------|----------|-------|
| **DeepLog** | HDFS | Anomaly detection | 95.6% | LSTM-based |
| **LogRobust** | BGL | Anomaly detection | 98.2% | Attention mechanism |
| **LogAnomaly** | HDFS | Anomaly detection | 96.7% | Template mining |
| **Our Baseline** | Multi-source | Compliance violations | 75.0% | Real scenarios |
| **Our Phase 1** | Multi-source | Compliance violations | 87.5% | Real scenarios |
| **Our Phase 2** | Multi-source | Compliance violations | 58.3% | Real scenarios |

**Key Differences**:
- Industry benchmarks test on **single dataset types**
- Our model tests on **diverse real-world attacks**
- Industry models focus on **anomaly detection** (binary)
- Our model does **compliance violation classification** (multi-framework)

---

## Recommendations

### For Production Deployment: Use Phase 1 ✅

**Rationale**:
- ✅ 87.5% accuracy (12.5 pp better than Phase 2)
- ✅ Fast inference (<1ms vs 50-100ms)
- ✅ Small model size (15 MB vs 450 MB)
- ✅ No GPU required
- ✅ Fixed ransomware detection (0% → 93.3%)
- ✅ Consistent performance across scenarios

**Trade-offs**:
- ❌ Still fails on phishing emails (71% confidence)
- ❌ Doesn't have semantic understanding (BERT)
- ❌ Below 95% industry benchmark

### For Research: Investigate Phase 2 Failures 🔬

**Questions to Answer**:
1. Why does BERT cause "compliant" bias?
2. Which temporal features actually help?
3. Can we fix confidence calibration?
4. Should we use security-specific BERT (SecBERT)?

**Next Steps**:
- SHAP analysis on failed scenarios
- Feature ablation study (remove BERT, remove temporal)
- Class weight tuning
- Adversarial training samples

---

## Lessons Learned

### 1. More Features ≠ Better Performance

Phase 2 added 794 features (39% increase):
- ❌ Performance dropped 29.2 percentage points
- ❌ Training time increased 5.6x
- ❌ Inference time increased 50-100x
- ❌ Model size increased 30x

### 2. Test Set Accuracy is Misleading

Phase 2 achieved 99.28% test accuracy:
- ✅ Great on test set
- ❌ Terrible on real scenarios (58.3%)
- ⚠️ Indicates overfitting to synthetic data

### 3. Confidence ≠ Correctness

Phase 2's wrong predictions had higher confidence:
- Baseline wrong predictions: 48-68% confidence
- Phase 1 wrong predictions: 71% confidence
- Phase 2 wrong predictions: 90-95% confidence ❌

### 4. Domain-Specific Pre-training Matters

DistilBERT (pre-trained on Wikipedia, books):
- ❌ Doesn't understand security terminology
- ❌ Treats attack descriptions as general text
- ❌ May need SecBERT or custom embeddings

---

## Decision Matrix

| Criteria | Baseline | Phase 1 | Phase 2 | Winner |
|----------|----------|---------|---------|--------|
| **Real Scenario Accuracy** | 75.0% | 87.5% | 58.3% | Phase 1 |
| **Test Set Accuracy** | 94.2% | 96.8% | 99.28% | Phase 2 |
| **Inference Speed** | Fast | Fast | Slow | Phase 1 |
| **Model Size** | Small | Small | Large | Phase 1 |
| **Ransomware Detection** | 0% | 93.3% | 75.6% | Phase 1 |
| **Sophisticated Attack Detection** | Poor | Poor | Terrible | Phase 1 |
| **Production Ready** | No | Yes | No | Phase 1 |
| **Research Value** | Low | Medium | High | Phase 2 |

**Overall Winner for Production**: **Phase 1** ✅

---

## Next Phase Recommendations

### Short-term (Production): Deploy Phase 1

1. ✅ Use Phase 1 model (87.5% accuracy)
2. 📝 Document known limitations (phishing, insider threats)
3. 🔍 Set up monitoring for false negatives
4. 📊 Collect real SOC feedback for future improvements

### Long-term (Research): Fix Phase 2 or Explore Alternatives

**Option A: Debug Phase 2**
- Investigate BERT bias with SHAP
- Try security-specific BERT (SecBERT, CyBERT)
- Reduce BERT feature weight in ensemble
- Add class weights to penalize false negatives

**Option B: Hybrid Approach**
- Use Phase 1 for most scenarios
- Use specialized models for specific attacks:
  - Email classifier for phishing
  - Behavioral model for insider threats
  - Network flow model for DDoS
  - Auth log model for credential attacks

**Option C: Targeted Dataset Addition**
- Add PhishTank emails for phishing
- Add CERT Insider Threat dataset
- Add CIC-DDoS2019 for volume attacks
- Add credential stuffing attack logs

---

## Conclusion

Phase 2's advanced features (BERT embeddings + temporal patterns) resulted in **significant performance regression** (87.5% → 58.3%) despite achieving higher test set accuracy (99.28%).

**Root Cause**: BERT introduced bias toward "compliant" predictions for sophisticated attacks, predicting them as compliant with very high confidence (92-95%).

**Recommended Action**: **Revert to Phase 1 model for production deployment** while investigating Phase 2 failures as a research project.

**Status**: ⏸️ AWAITING USER DECISION on next steps.

---

**Last Updated**: November 2, 2025
**Next Review**: After user decision on deployment strategy
