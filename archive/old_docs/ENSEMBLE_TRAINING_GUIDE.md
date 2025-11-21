# Ensemble Training Guide
## Phase 6: Hybrid BERT-XGBoost-LSTM Ensemble

**Status**: ✅ Training Started (Background Process)
**Expected Completion**: ~9-10 hours
**Target Accuracy**: 96-99%

---

## What's Running Now

**Command**:
```bash
python train_ensemble.py --data-dir data/real_formatted --bert-epochs 3 --lstm-epochs 5
```

**Training Pipeline**:
1. **Phase 1**: Train Base Models (~9 hours total)
   - BERT: 3 epochs on 140K samples (~8.4 hours)
   - XGBoost: 494 trees on 140K samples (~1.4 minutes)
   - LSTM: 5 epochs on 140K samples (~1.1 hours)

2. **Phase 2**: Train Stacking Ensemble (~30 seconds)
   - Get predictions from all base models on validation set
   - Train logistic regression meta-classifier
   - Learn optimal weights for combining predictions

3. **Phase 3**: Evaluation & Comparison (~2 minutes)
   - Evaluate ensemble on 30K test samples
   - Compare with individual base models
   - Generate metrics and visualizations

---

## Monitoring Training Progress

### Real-time Log Monitoring

```bash
# Basic progress (last 30 lines)
tail -30 logs/ensemble_full_training.log

# Continuous monitoring
tail -f logs/ensemble_full_training.log

# Filter for key events only
tail -f logs/ensemble_full_training.log | grep --line-buffered -E "Epoch|Validation|Accuracy|TRAINING|✅"

# Check for errors
tail -f logs/ensemble_full_training.log | grep --line-buffered -E "ERROR|Failed|Exception"
```

### Estimated Timeline

| Event | Time from Start | Status Indicator |
|-------|----------------|------------------|
| BERT Epoch 1/3 starts | 0 min | `TRAINING BERT` + `Epoch 1/3` |
| BERT Epoch 1/3 completes | ~168 min (2.8 hrs) | `Val Accuracy:` |
| BERT Epoch 2/3 completes | ~336 min (5.6 hrs) | `Val Accuracy:` |
| BERT Epoch 3/3 completes | ~504 min (8.4 hrs) | `✅ BERT training complete` |
| XGBoost training | ~505 min | `TRAINING XGBOOST` |
| XGBoost completes | ~506 min | `✅ XGBoost training complete` |
| LSTM Epoch 1/5 starts | ~507 min | `TRAINING LSTM` + `Epoch 1/5` |
| LSTM completes | ~574 min (9.6 hrs) | `✅ LSTM training complete` |
| Stacking ensemble trains | ~575 min | `TRAINING STACKING ENSEMBLE` |
| Ensemble completes | ~576 min | `✅ ENSEMBLE TRAINING COMPLETE!` |

**Total Estimated Time**: ~9.6 hours

---

## What the Ensemble Does

### Stacking Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    INPUT LOG MESSAGE                     │
└─────────────────────────────────────────────────────────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
    ┌──────────┐     ┌──────────┐     ┌──────────┐
    │   BERT   │     │ XGBoost  │     │   LSTM   │
    │ (96.15%) │     │ (95.99%) │     │ (96.11%) │
    └──────────┘     └──────────┘     └──────────┘
           │                │                │
           │  P(compliant)  │                │
           │       │        │                │
           ▼       ▼        ▼                ▼
    ┌──────────────────────────────────────────────┐
    │      LOGISTIC REGRESSION META-CLASSIFIER      │
    │  (Learns optimal combination of predictions)  │
    └──────────────────────────────────────────────┘
                            │
                            ▼
                ┌──────────────────────┐
                │  FINAL PREDICTION    │
                │  (Expected: 96-99%)  │
                └──────────────────────┘
```

### Why Ensemble Works

**Diversity Principle**:
- **BERT**: Strong at understanding context and semantics
- **XGBoost**: Strong at detecting structured patterns
- **LSTM**: Strong at capturing sequential dependencies

**Combination Benefits**:
- **Reduces variance**: Averages out individual model errors
- **Increases robustness**: Less likely to fail if one model is wrong
- **Learned weighting**: Meta-classifier finds optimal combination

**Expected Improvements**:
- **Accuracy**: 96.5-97.5% (vs 96.15% best individual)
- **Recall**: 95-99% (combine BERT's 92.6% with XGBoost's 98.5%)
- **Precision**: 75-80% (improve over XGBoost's 68.8%)
- **F1 Score**: 82-85% (better balance)

---

## Expected Results

### Best Case Scenario (96-99% target)

If ensemble works as expected:

| Model | Accuracy | Precision | Recall | F1 Score |
|-------|----------|-----------|--------|----------|
| BERT | 96.15% | 71.48% | 92.63% | 80.70% |
| XGBoost | 95.99% | 68.79% | **98.54%** | 81.02% |
| LSTM | 96.11% | 76.20% | 80.35% | 78.22% |
| **Ensemble** | **96.5-97.5%** | **73-78%** | **94-97%** | **82-85%** |

### Key Performance Indicators

**Target Metrics** (to declare success):
- ✅ Accuracy ≥ 96.5% (improvement over 96.15% BERT)
- ✅ Recall ≥ 94% (better than BERT's 92.6%, though lower than XGB's 98.5%)
- ✅ F1 Score ≥ 82% (improvement over all individual models)
- ✅ ROC-AUC ≥ 0.991 (improvement over 0.9905 BERT)

**Acceptable Range**:
- Accuracy: 96.3-98.0%
- Recall: 92-98%
- Precision: 72-80%
- F1: 81-86%

**Failure Indicators** (need to investigate):
- Accuracy < 96.0% (worse than best individual model)
- Recall < 90% (significant drop from base models)
- F1 < 80% (no improvement from stacking)

---

## After Training Completes

### Step 1: Check Results

```bash
# View final results
cat results/ensemble/ensemble_metrics.json

# View comparison with base models
cat results/ensemble/model_comparison.csv
```

### Step 2: Analyze Performance

**Questions to Answer**:
1. Did ensemble improve over best base model?
2. What are the meta-classifier weights?
   - High BERT weight → Relies on semantic understanding
   - High XGBoost weight → Relies on pattern matching
   - High LSTM weight → Relies on sequential context
3. Where does ensemble make errors?
   - Check confusion matrix: `ensemble_metrics.json`
4. Is the improvement worth the complexity?
   - Ensemble requires all 3 models (3x inference cost)
   - Only worthwhile if improvement > 0.5% accuracy

### Step 3: Interpret Meta-Classifier

The meta-classifier learns optimal weights for combining predictions:

**Example Output**:
```
Meta-classifier coefficients:
  BERT: 0.8234
  XGBoost: 0.6521
  LSTM: 0.3156
  Intercept: -0.4123
```

**Interpretation**:
- **Positive coefficient** = Model contributes to non-compliant prediction
- **Larger magnitude** = More influential in final decision
- **Example**: If BERT=0.82 and XGBoost=0.65:
  - When both predict non-compliant → High confidence ensemble prediction
  - When they disagree → BERT's prediction weighted more heavily

---

## Troubleshooting

### If Training Fails

**Common Issues**:

1. **Out of Memory (BERT)**
   - Symptom: `CUDA out of memory` or `RuntimeError`
   - Fix: Reduce batch size in `train_ensemble.py` (line 36)
   - Change: `bert.fit(..., batch_size=8)` instead of 16

2. **XGBoost Feature Error**
   - Symptom: `KeyError: 'severity'` or similar
   - Fix: Already handled by dynamic feature engineering
   - Verify: Check that `data/real_formatted` has correct columns

3. **LSTM Training Slow**
   - Symptom: Epoch takes >15 minutes
   - Fix: Normal on CPU - LSTM is sequential and can't parallelize well
   - Workaround: Reduce `--lstm-epochs 3` instead of 5

### If Results Are Poor

**Diagnostic Steps**:

1. **Check Base Model Performance**
   ```python
   # In results/ensemble/model_comparison.csv
   # Are base models performing as expected?
   # BERT ~96%, XGBoost ~96%, LSTM ~96%?
   ```

2. **Check Meta-Classifier Overfitting**
   ```python
   # If meta-classifier has 100% val accuracy but low test accuracy
   # → Overfitting on validation set
   # Solution: Use cross-validation instead of single val set
   ```

3. **Check Data Leakage**
   ```python
   # Verify validation set NOT used in base model training
   # Verify test set NEVER seen before
   # Check train/val/test split: 70/15/15
   ```

---

## Alternative Approaches (If Stacking Fails)

### Option 1: Simple Voting

Instead of learning weights, use fixed weights:

```bash
# Edit train_ensemble.py, change evaluate_ensemble():
# method='voting_soft'  # Weighted average
# Weights: BERT=40%, XGBoost=40%, LSTM=20%
```

**Pros**: No training needed, interpretable
**Cons**: May not be optimal

### Option 2: Best Model Selection

Just use the single best model (currently BERT at 96.15%):

```bash
# No ensemble needed
# Deploy BERT directly
```

**Pros**: Simplest, fastest inference
**Cons**: Misses diversity benefits

### Option 3: Two-Model Ensemble

Remove LSTM (lowest individual performance):

```python
# Only use BERT + XGBoost
# Expected: Similar performance with 33% less complexity
```

**Pros**: Faster inference, simpler
**Cons**: Lose sequential modeling capability

---

## Next Steps After Ensemble

Once ensemble training completes:

### Immediate (Within 1 Hour)
1. ✅ Analyze ensemble results
2. ✅ Update COMPREHENSIVE_PROGRESS_REPORT.md
3. ✅ Decide: Is ensemble worth the complexity?
4. ⏳ Move to Phase 6.2: SHAP Explainability

### Short-term (Next 1-2 Days)
1. ⏳ Implement SHAP for XGBoost
2. ⏳ Implement LIME for BERT/LSTM
3. ⏳ Create visualization dashboard (Streamlit)

### Long-term (Next Week)
1. ⏳ Deploy to production (Rwanda NCSA)
2. ⏳ A/B test against manual auditing
3. ⏳ Collect real Rwanda logs for fine-tuning

---

## Files Generated

After training completes, you'll have:

```
results/ensemble/
├── ensemble_metrics.json          # Detailed metrics
├── model_comparison.csv           # Side-by-side comparison
└── (future) ensemble_model.pkl    # Saved ensemble for deployment

logs/
├── ensemble_full_training.log     # Complete training log
└── ensemble_training.log          # Timestamped events
```

---

## Monitoring Commands Quick Reference

```bash
# Check if still running
ps aux | grep train_ensemble

# View last 50 lines
tail -50 logs/ensemble_full_training.log

# Continuous monitoring
tail -f logs/ensemble_full_training.log

# Check current epoch
grep "Epoch" logs/ensemble_full_training.log | tail -5

# Check if complete
grep "ENSEMBLE TRAINING COMPLETE" logs/ensemble_full_training.log

# View results (after completion)
cat results/ensemble/ensemble_metrics.json
cat results/ensemble/model_comparison.csv
```

---

## Success Criteria

**Minimum Acceptable Performance** (MAR):
- Accuracy ≥ 96.15% (matches BERT)
- Recall ≥ 92% (near BERT)
- F1 ≥ 80.7% (matches BERT)

**Target Performance** (TP):
- Accuracy ≥ 96.5% (+0.35% over BERT)
- Recall ≥ 94% (+1.4% over BERT)
- F1 ≥ 82% (+1.3% over BERT)

**Stretch Goal** (SG):
- Accuracy ≥ 97.0% (+0.85% over BERT)
- Recall ≥ 95%
- F1 ≥ 84%

---

**Training Started**: October 22, 2025, 19:36
**Expected Completion**: October 23, 2025, ~05:00 (next morning)

Monitor progress with: `tail -f logs/ensemble_full_training.log`

---

**Good luck! The ensemble is training in the background. Check back in ~9 hours for results!** 🚀
