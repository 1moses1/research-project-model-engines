# Next Steps - Implementation Roadmap

## Current Status (October 20, 2025)

**Progress**: 16/45 tasks completed (35.6%)
**Phase**: 4 (Data Pipeline Implementation)
**Next Milestone**: Mid-October Deliverable

---

## Immediate Actions Required

### 1. Install Dependencies & Test Control Mapper

```bash
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"

# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install pyyaml numpy pandas

# Test control mapper
python src/data_pipeline/control_mapper.py
```

**Expected Output**:
- `data/processed/control_taxonomy.json` created
- 50 total controls (29 NIST + 21 Rwanda)
- 12 control families identified

---

## Week 1: Complete Data Pipeline (Oct 20-27)

### Priority 1: Implement Synthetic Event Generator

**File**: `src/data_pipeline/synthetic_generator.py`

**Requirements**:
- Generate 100,000 compliance events
- Use control taxonomy from control_mapper.py
- Apply distributions from `config/data_config.yaml`:
  - 75% compliant / 25% non-compliant
  - 80% normal / 15% suspicious / 5% critical
- Output formats: CSV, JSON, Parquet

**Output**:
```
data/synthetic/
├── compliance_events_train.csv (70,000 events)
├── compliance_events_val.csv (15,000 events)
├── compliance_events_test.csv (15,000 events)
└── dataset_statistics.json
```

**Key Features to Implement**:
1. Load control taxonomy
2. Generate realistic log messages per control
3. Assign compliance labels based on rules
4. Add temporal patterns (time-of-day, day-of-week)
5. Create user/resource/IP distributions
6. Apply 70/15/15 train/val/test split

---

### Priority 2: Implement Log Parser (Drain Algorithm)

**File**: `src/data_pipeline/log_parser.py`

**Requirements**:
- Implement Drain algorithm for log template extraction
- Parameters from config: similarity_threshold=0.5, depth=4
- Parse synthetic logs into structured templates
- Extract variable tokens vs static templates

**Output**:
```
data/processed/
├── log_templates.json
└── parsed_logs.csv
```

---

### Priority 3: Implement Data Augmentation

**File**: `src/data_pipeline/data_augmentation.py`

**Requirements**:
- Synonym replacement for log messages
- Template variations
- Increase dataset by 1.5x (augmentation_factor from config)
- Preserve semantic meaning

---

### Priority 4: Implement Class Balancing

**File**: `src/data_pipeline/preprocessor.py`

**Requirements**:
- SMOTE for oversampling non-compliant events
- Balance to 50/50 ratio (from config)
- k_neighbors=5

---

## Week 2: Implement Baseline Models (Oct 28 - Nov 3)

### Priority 5: BERT Classifier

**File**: `src/models/bert_classifier.py`

**Requirements**:
- Load `bert-base-uncased` from Hugging Face
- Fine-tune on compliance dataset
- Freeze first 10 layers (from config)
- Training: 5 epochs, batch_size=16, lr=2e-5
- Save model checkpoints to `outputs/models/bert/`

**Expected Performance**: 95-97% accuracy

---

### Priority 6: XGBoost Classifier

**File**: `src/models/xgboost_classifier.py`

**Requirements**:
- Feature engineering for structured data
- Hyperparameters from `config/model_config.yaml`
- SHAP explainability integration
- Save model to `outputs/models/xgboost/`

**Expected Performance**: 94-96% accuracy

---

### Priority 7: LSTM Classifier

**File**: `src/models/lstm_classifier.py`

**Requirements**:
- Load GloVe 100d embeddings
- Bi-directional LSTM (2 layers, 128 hidden units)
- Training: 20 epochs, batch_size=32
- Save model to `outputs/models/lstm/`

**Expected Performance**: 92-94% accuracy

---

### Priority 8: Evaluation Metrics

**File**: `src/utils/evaluation.py`

**Requirements**:
- Calculate accuracy, precision, recall, F1, error rate
- Generate confusion matrices
- Plot ROC curves
- Save results to `outputs/evaluation/`

---

## Week 3: Hybrid Ensemble & Dashboard (Nov 4-10)

### Priority 9: BERT-XGBoost Ensemble

**File**: `src/models/ensemble.py`

**Requirements**:
- Stacking meta-classifier
- Combine BERT + XGBoost predictions
- Logistic regression meta-model
- Cross-validation

**Expected Performance**: 96-99% accuracy

---

### Priority 10: Training Dashboard

**File**: `src/ui/dashboard.py`

**Requirements**:
- Streamlit-based UI
- Real-time training progress visualization
- Model comparison charts
- File upload for new data
- Integrated Claude assistant (if API available)

---

## Detailed Implementation Order

### This Week (Oct 20-27)

**Monday-Tuesday (Oct 20-21)**:
- [x] Install dependencies
- [ ] Test control_mapper.py
- [ ] Implement synthetic_generator.py (core logic)
- [ ] Generate initial 100K dataset

**Wednesday-Thursday (Oct 22-23)**:
- [ ] Implement log_parser.py (Drain algorithm)
- [ ] Implement data_augmentation.py
- [ ] Implement class balancing (SMOTE)

**Friday-Sunday (Oct 24-27)**:
- [ ] Complete data pipeline testing
- [ ] Validate dataset quality
- [ ] Commit data pipeline code
- [ ] Update documentation

---

### Next Week (Oct 28 - Nov 3)

**Monday-Tuesday (Oct 28-29)**:
- [ ] Implement BERT classifier
- [ ] Set up training pipeline
- [ ] Train on synthetic dataset

**Wednesday-Thursday (Oct 30-31)**:
- [ ] Implement XGBoost classifier
- [ ] Feature engineering
- [ ] SHAP integration

**Friday-Sunday (Nov 1-3)**:
- [ ] Implement LSTM classifier
- [ ] Implement evaluation metrics
- [ ] Run comparative experiments

---

## Key Files to Create (Priority Order)

1. ✅ `src/utils/config_loader.py` - DONE
2. ✅ `src/utils/logger.py` - DONE
3. ✅ `src/data_pipeline/control_mapper.py` - DONE
4. ⏳ `src/data_pipeline/synthetic_generator.py` - NEXT
5. ⏳ `src/data_pipeline/log_parser.py`
6. ⏳ `src/data_pipeline/data_augmentation.py`
7. ⏳ `src/data_pipeline/preprocessor.py`
8. ⏳ `src/models/base_model.py` (interface)
9. ⏳ `src/models/bert_classifier.py`
10. ⏳ `src/models/xgboost_classifier.py`
11. ⏳ `src/models/lstm_classifier.py`
12. ⏳ `src/models/ensemble.py`
13. ⏳ `src/utils/evaluation.py`
14. ⏳ `src/ui/dashboard.py`

---

## Testing Strategy

### Unit Tests

Create `tests/` directory with:
- `test_control_mapper.py`
- `test_synthetic_generator.py`
- `test_log_parser.py`
- `test_models.py`
- `test_evaluation.py`

Run tests:
```bash
pytest tests/ -v --cov=src
```

---

## Success Criteria for Mid-October Deliverable

### Must Have (Critical):
- ✅ Control taxonomy generated (50 controls)
- ⏳ Synthetic dataset (100K events)
- ⏳ BERT classifier trained (>93% accuracy)
- ⏳ XGBoost classifier trained (>93% accuracy)
- ⏳ LSTM classifier trained (>90% accuracy)
- ⏳ Comparative evaluation report

### Should Have (Important):
- ⏳ Log parsing engine (Drain)
- ⏳ Data augmentation pipeline
- ⏳ SHAP explainability for XGBoost
- ⏳ Training visualization

### Nice to Have (Optional):
- ⏳ Hybrid ensemble (96-99%)
- ⏳ Interactive dashboard
- ⏳ HDFS dataset integration

---

## Git Workflow

### Before Starting Implementation

```bash
# Create feature branch
git checkout -b feature/data-pipeline

# Work on implementation
# Commit frequently with descriptive messages

# When feature complete
git add .
git commit -m "Implement synthetic event generator

- Generate 100K compliance events
- Apply 70/15/15 train/val/test split
- Support CSV/JSON/Parquet formats
- Include dataset statistics

Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin feature/data-pipeline
```

### Merge to Main

```bash
git checkout main
git merge feature/data-pipeline
git push origin main
```

---

## Push to GitHub (First Time)

```bash
# Make sure GitHub repo is created first:
# https://github.com/1moses1/research-project-model-engines

# Then push
git remote -v  # Verify remote is set
git push -u origin main
```

---

## Questions to Resolve

1. **Claude API Integration**: Do you have access to Claude API for dashboard integration?
2. **GPU Access**: Do you have GPU available for BERT training?
3. **Dataset Size**: Is 100K events sufficient, or should we generate more?
4. **Public Datasets**: Should we download HDFS logs for validation?

---

## Resources

### Documentation
- `docs/research/ML_Models_High_Accuracy_Research_Report.md`
- `docs/research/MODEL_SELECTION_STRATEGY.md`
- `docs/research/RESEARCH_NOVELTY.md`
- `docs/regulatory_frameworks/FRAMEWORKS_OVERVIEW.md`

### Configuration
- `config/data_config.yaml`
- `config/model_config.yaml`

### Progress Tracking
- `PROGRESS_SUMMARY.md`
- `PROJECT_STRUCTURE.md`

---

## Estimated Time Investment

| Component | Estimated Hours |
|-----------|----------------|
| Synthetic Generator | 8-10 hours |
| Log Parser (Drain) | 6-8 hours |
| Data Augmentation | 4-6 hours |
| BERT Classifier | 10-12 hours |
| XGBoost Classifier | 6-8 hours |
| LSTM Classifier | 8-10 hours |
| Evaluation Framework | 4-6 hours |
| Testing & Debugging | 8-10 hours |
| **Total** | **54-70 hours** |

**Estimated Timeline**: 2-3 weeks full-time, 4-6 weeks part-time

---

## Tips for Success

1. **Start Simple**: Get basic synthetic generator working first, then add complexity
2. **Test Incrementally**: Test each component before moving to next
3. **Commit Often**: Small, frequent commits are better than large infrequent ones
4. **Document as You Go**: Add docstrings and comments while implementing
5. **Validate Early**: Check dataset quality before training models
6. **Monitor Performance**: Track training metrics continuously
7. **Save Checkpoints**: Don't lose progress if training crashes

---

## Support & Communication

If you encounter blockers or have questions:
1. Review existing documentation in `docs/`
2. Check `PROGRESS_SUMMARY.md` for current status
3. Consult research papers in literature review
4. Test with smaller datasets first (e.g., 1K events)
5. Ask for help when stuck (don't waste hours debugging alone)

---

**Good luck with the implementation! The foundation is solid. Now it's time to build the ML pipeline.** 🚀

---

**Last Updated**: October 20, 2025
**Next Review**: October 27, 2025 (End of Week 1)
