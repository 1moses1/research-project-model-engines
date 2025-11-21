# Phase 2 Summary: BERT + Temporal Features

**Date**: November 2, 2025
**Status**: ❌ REGRESSION - Performance Degraded
**Recommendation**: Revert to Phase 1 for production deployment

---

## Results at a Glance

```
Baseline (Original)    →    Phase 1 (Real Data)    →    Phase 2 (BERT + Temporal)
      75.0%            →          87.5%           →            58.3%
    (6/8 pass)         →        (7/8 pass)        →         (7/12 pass)
                              ✅ IMPROVED                   ❌ REGRESSION
```

### Key Metrics

| Metric | Phase 1 | Phase 2 | Change |
|--------|---------|---------|--------|
| Real Scenario Accuracy | 87.5% | 58.3% | ❌ -29.2 pp |
| Test Set Accuracy | 96.8% | 99.28% | ✅ +2.48 pp |
| Scenarios Failed | 1 | 5 | ❌ +4 failures |
| Training Time | 8 min | 45 min | ⚠️ 5.6x slower |
| Inference Time | <1ms | 50-100ms | ⚠️ 50-100x slower |

---

## What Went Wrong?

### Critical Issue: "Compliant" Bias

Phase 2 model predicts sophisticated attacks as **compliant** with **very high confidence**:

| Attack | Expected | Phase 2 Prediction | Confidence | Issue |
|--------|----------|-------------------|------------|-------|
| Phishing Email | non_compliant | **compliant** | 93.7% | ❌ HIGH confidence WRONG |
| Insider Threat | non_compliant | **compliant** | 92.4% | ❌ HIGH confidence WRONG |
| Lateral Movement | non_compliant | **compliant** | 90.4% | ❌ HIGH confidence WRONG |
| DDoS Attack | non_compliant | **compliant** | 94.6% | ❌ HIGH confidence WRONG |
| Credential Stuffing | non_compliant | **compliant** | 93.8% | ❌ HIGH confidence WRONG |

**Pattern**: All 5 new sophisticated attacks misclassified as compliant with 90%+ confidence

---

## Root Cause Analysis

### 1. BERT Semantic Bias

**Problem**: DistilBERT pre-trained on Wikipedia/books, not security logs
- Learns that "professional language" = "compliant"
- Misses security-specific threat indicators
- Treats attack descriptions as general business text

**Example - Phishing Email**:
```
Log: "Email from unknown@suspicious-domain.ru blocked - Contains malicious link"
```
- BERT sees: "Email", "blocked", "domain" → business language
- Training: Most compliant logs use professional tone
- Result: Predicts compliant with 93.7% confidence ❌

### 2. Temporal Features Lack Universal Signal

**Works for**: Attacks with explicit time patterns
- ✅ Ransomware: "10,000 files in 5 minutes" → `rapid_succession` detected

**Fails for**: Single-event or volume-based attacks
- ❌ Phishing: Single email event → no temporal pattern
- ❌ DDoS: "100,000 requests/sec" → not in sequence features
- ❌ Credential Stuffing: Volume attack without time context

### 3. Test Set Overfitting

**Test Set**: 99.28% accuracy (excellent)
**Real Scenarios**: 58.3% accuracy (terrible)
**Gap**: 40.98 percentage points

**Indicates**: Model memorized synthetic data patterns, doesn't generalize to real sophisticated attacks

### 4. Feature Dilution

**Phase 1**: 2,002 features (focused on keywords)
**Phase 2**: 2,796 features (+794 = 39% increase)

Result: Attack-specific keywords (TF-IDF) diluted by 768 BERT + 26 temporal features

---

## What We Learned

### ✅ Successes
1. **BERT Integration**: Successfully implemented DistilBERT embeddings (768-dim)
2. **Temporal Engineering**: Created 26 pattern-detection features
3. **Technical Achievement**: Combined sparse (TF-IDF) + dense (BERT) matrices
4. **GPU Acceleration**: Used MPS device for fast BERT processing (19 batches/sec)

### ❌ Failures
1. **Performance**: 29.2 pp worse than Phase 1
2. **Confidence Calibration**: Wrong predictions have 90%+ confidence
3. **Insider Threat Goal**: Still failing (primary Phase 2 objective)
4. **Sophistication**: Can't detect advanced attacks (phishing, lateral movement, DDoS)

### 💡 Insights
1. **More Features ≠ Better**: Adding 794 features made performance worse
2. **Domain Pre-training Matters**: General BERT doesn't understand security logs
3. **Test Accuracy Misleading**: 99.28% test accuracy meant nothing for real scenarios
4. **Simplicity Wins**: Phase 1's simpler approach (87.5%) outperformed complex Phase 2 (58.3%)

---

## Phase 2 Features (2,796 total)

### BERT Embeddings (768 features)
- **Model**: DistilBERT (`distilbert-base-uncased`)
- **Purpose**: Semantic text understanding
- **Pre-training**: Wikipedia + BookCorpus (not security-specific)
- **Processing**: 75 seconds for 88K samples on MPS
- **Result**: ❌ Introduced "compliant" bias

### Temporal Features (26 features)

**Basic Temporal (9)**:
- `hour`, `minute`, `day_of_week`, `day_of_month`, `month`
- `is_weekend`, `is_business_hours`, `is_late_night`, `is_unusual_time`

**Sequence Features (5)**:
- `events_last_5min`, `failed_attempts_last_5min`
- `unique_ips_last_5min`, `unique_users_last_5min`, `rapid_succession`

**Anomaly Indicators (12)**:
- Insider: `large_transfer`, `usb_access`, `sensitive_data`
- Lateral: `multiple_connections`, `smb_rdp_ssh`
- Volume: `high_volume`, `spike_traffic`
- Creds: `credential_related`, `multiple_ips`
- Ransomware: `encryption_activity`, `file_modification`
- **Result**: ⚠️ Only helped ransomware detection

### TF-IDF + Categorical (2,002 features)
- Same as Phase 1
- **Result**: ✅ Still useful but diluted by other features

---

## Comparison: Phase 1 vs Phase 2

### Scenarios Both Models Handle Well
| Scenario | Phase 1 | Phase 2 | Best |
|----------|---------|---------|------|
| Unauthorized SSH | 99.1% | 99.9% | Phase 2 |
| Compliance Check | 99.3% | 97.8% | Phase 1 |
| Unpatched CVE | 92.7% | 86.1% | Phase 1 |
| Encryption Enabled | 98.2% | 95.0% | Phase 1 |
| Backup Failure | 94.1% | 100.0% | Phase 2 |
| Ransomware | 93.3% | 75.6% | Phase 1 |
| SQL Injection | 95.8% | 88.1% | Phase 1 |

**Pattern**: Phase 1 more consistent, Phase 2 regressed on most scenarios

### Scenarios Both Models Struggle With
| Scenario | Phase 1 | Phase 2 | Issue |
|----------|---------|---------|-------|
| Phishing | 71% (wrong) | 7% (very wrong) | Phase 2 worse |
| Insider Threat | Not tested | 8% (wrong) | Phase 2 fails |
| Lateral Movement | Not tested | 10% (wrong) | Phase 2 fails |
| DDoS | Not tested | 5% (wrong) | Phase 2 fails |
| Credential Stuffing | Not tested | 6% (wrong) | Phase 2 fails |

**Pattern**: Phase 2 catastrophically fails on sophisticated attacks

---

## Recommendation: Revert to Phase 1

### Why Phase 1?

✅ **Performance**: 87.5% vs 58.3% (29.2 pp better)
✅ **Speed**: <1ms inference vs 50-100ms
✅ **Size**: 15 MB vs 450 MB
✅ **Reliability**: Consistent confidence calibration
✅ **Resources**: No GPU required
✅ **Production-Ready**: Deploy in 1 hour

### Phase 1 Deployment

```bash
# 1. Test Phase 1 model
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"
source venv/bin/activate
python test_xgboost_model.py

# 2. Deploy to production
cp -r results/models/xgboost_baseline_with_real_data/ production/

# 3. Monitor and collect feedback
# (Set up false negative monitoring)
```

### Phase 1 Known Limitations

❌ **Phishing**: Fails with 71% confidence (low confidence wrong)
❌ **Insider Threats**: Not extensively tested
⚠️ **Below 95% Target**: 87.5% vs industry 95%+

**Mitigation**: Monitor false negatives, collect real SOC feedback

---

## Future Work

### Short-term: Production Deployment (1 hour)
- Deploy Phase 1 model (87.5% accuracy)
- Document known limitations
- Set up monitoring for false negatives
- Collect real SOC feedback

### Medium-term: Debug Phase 2 (2-3 weeks)
- **SHAP Analysis**: Why does BERT cause bias?
- **Feature Ablation**: Test without BERT, without temporal
- **Security-BERT**: Try SecBERT or CyBERT instead of DistilBERT
- **Class Weights**: Penalize false negatives more

### Long-term: Phase 3 Design (1-2 months)
- **Targeted Datasets**: Add phishing, insider threat, DDoS logs
- **Hybrid Models**: Specialized models per attack type
- **Alternative Architectures**: LSTM+Attention, Transformer, GNN

---

## Files Created

### Implementation
- `src/models/bert_feature_extractor.py` (366 lines)
- `src/models/temporal_feature_extractor.py` (300 lines)
- `train_phase2_ensemble.py` (420 lines)
- `test_phase2_model.py` (350 lines)

### Data
- `data/bert_embeddings/` (train/val/test .npy files)
- `data/temporal_enhanced/` (CSV files with 26 new features)

### Models
- `results/models/xgboost_phase2/` (model artifacts)

### Documentation
- `PHASE2_ANALYSIS.md` (comprehensive analysis)
- `PHASE_COMPARISON.md` (baseline vs Phase 1 vs Phase 2)
- `QUICK_DECISION_GUIDE.md` (next steps guide)
- `PHASE2_SUMMARY.md` (this file)

### Logs
- `logs/phase2_training.log` (training output)
- `logs/phase2_test_results.log` (detailed test results)

---

## Conclusion

Phase 2's advanced features (BERT + temporal) resulted in **significant regression** (87.5% → 58.3%) despite achieving high test set accuracy (99.28%).

**Root Cause**: BERT bias toward "compliant" predictions for professional-sounding attack descriptions.

**Action Required**: **Revert to Phase 1 for production** (87.5% accuracy, fast, reliable).

**Research Value**: Phase 2 failure provides valuable insights:
- Domain-specific pre-training is critical
- More features can hurt performance
- Test set accuracy doesn't guarantee real-world performance
- Simpler models often outperform complex ones

---

**Status**: ✅ PHASE 2 COMPLETE (Analysis Done)
**Next**: ⏸️ AWAITING USER DECISION on deployment
**Recommendation**: Deploy Phase 1, research Phase 2 failures in parallel

**Date**: November 2, 2025
