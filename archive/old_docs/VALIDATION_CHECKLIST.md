# Validation Checklist - Before Proceeding to Phase 5

## Testing Status: READY FOR VALIDATION ✓

---

## Quick Start (Recommended Path)

### Step 1: Install Dependencies (5 minutes)

```bash
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"
./setup.sh
source venv/bin/activate
```

### Step 2: Run Quick Test (2 minutes)

```bash
./quick_test.sh
```

**Expected**: All 4 tests pass ✅

### Step 3: Generate Full Dataset (Optional - 10 minutes)

```bash
python src/data_pipeline/synthetic_generator.py
```

**Expected**: 100K events in 3 CSV files

---

## Detailed Validation Checklist

### ☐ Environment Setup

- [ ] Python 3.8+ installed
- [ ] Virtual environment created (`venv/` directory exists)
- [ ] Virtual environment activated (see `(venv)` in prompt)
- [ ] Dependencies installed (pyyaml, pandas, numpy minimum)

**Test**:
```bash
which python  # Should point to venv
python --version  # Should be 3.8+
pip list | grep -E "pyyaml|pandas|numpy"
```

---

### ☐ Configuration System

- [ ] `config/data_config.yaml` loads without errors
- [ ] `config/model_config.yaml` loads without errors
- [ ] 29 NIST controls defined
- [ ] 21 Rwanda controls defined
- [ ] ConfigLoader class works

**Test**:
```bash
python -c "from src.utils.config_loader import ConfigLoader; \
loader = ConfigLoader(); \
print(f'NIST: {len(loader.get_nist_controls())}, Rwanda: {len(loader.get_rwanda_controls())}')"
```

**Expected Output**: `NIST: 29, Rwanda: 21`

---

### ☐ Logging System

- [ ] Logger creates log files
- [ ] Console output works
- [ ] Log files in `logs/` directory
- [ ] No permission errors

**Test**:
```bash
python -c "from src.utils.logger import setup_logger; \
logger = setup_logger('validation_test', 'logs/validation.log'); \
logger.info('Test message')"

cat logs/validation.log
```

**Expected**: Log file contains test message

---

### ☐ Control Mapper

- [ ] Loads 50 controls (29 NIST + 21 Rwanda)
- [ ] Creates 12 control families
- [ ] Generates `data/processed/control_taxonomy.json`
- [ ] JSON file is valid (50-100KB)
- [ ] All controls have required fields (name, family, description, log_indicators)

**Test**:
```bash
python src/data_pipeline/control_mapper.py
ls -lh data/processed/control_taxonomy.json
```

**Expected**:
- Console shows "✅ Control taxonomy created successfully!"
- File size ~50-100KB
- 50 total controls, 12 families

**Verify Content**:
```bash
python -c "import json; \
data = json.load(open('data/processed/control_taxonomy.json')); \
print(f'Total: {data[\"metadata\"][\"total_controls\"]}'); \
print(f'Families: {len(data[\"control_families\"])}')"
```

---

### ☐ Synthetic Event Generator

#### Small Dataset Test (1K events)

- [ ] Generates 1,000 events without errors
- [ ] Events have all required columns (19 columns)
- [ ] Compliance ratio ~75%/25%
- [ ] Anomaly distribution ~80%/15%/5%
- [ ] Timestamps are realistic
- [ ] All 50 controls represented

**Test**:
```bash
python -c "from src.data_pipeline.synthetic_generator import SyntheticEventGenerator; \
gen = SyntheticEventGenerator(); \
df = gen.generate_dataset(1000); \
print(f'Events: {len(df)}'); \
print(f'Columns: {len(df.columns)}'); \
print(f'Compliant: {(df.compliance_status==\"compliant\").sum()}'); \
print(df.columns.tolist())"
```

**Expected**:
- Events: 1000
- Columns: 19
- Compliant: ~750 (±50)

#### Train/Val/Test Split

- [ ] 70/15/15 split works
- [ ] No data leakage between sets
- [ ] Shuffling is random
- [ ] Split preserves distributions

**Test**:
```bash
python -c "from src.data_pipeline.synthetic_generator import SyntheticEventGenerator; \
gen = SyntheticEventGenerator(); \
df = gen.generate_dataset(1000); \
train, val, test = gen.split_dataset(df); \
print(f'Train: {len(train)}, Val: {len(val)}, Test: {len(test)}'); \
print(f'Total: {len(train)+len(val)+len(test)}')"
```

**Expected**:
- Train: 700
- Val: 150
- Test: 150
- Total: 1000

---

### ☐ Full Dataset Generation (100K events)

- [ ] Generates 100,000 events
- [ ] Takes 5-10 minutes (reasonable performance)
- [ ] No memory errors
- [ ] Creates 3 CSV files (train/val/test)
- [ ] Creates statistics JSON
- [ ] File sizes reasonable (~50MB total)

**Test**:
```bash
python src/data_pipeline/synthetic_generator.py
```

**Verify Files**:
```bash
ls -lh data/synthetic/
# Should show:
# compliance_events_train.csv (~35MB, 70,000 rows)
# compliance_events_val.csv (~7.5MB, 15,000 rows)
# compliance_events_test.csv (~7.5MB, 15,000 rows)
# dataset_statistics.json (~2KB)
```

**Verify Row Counts**:
```bash
wc -l data/synthetic/*.csv
# compliance_events_train.csv: 70,001 (header + 70,000 rows)
# compliance_events_val.csv: 15,001
# compliance_events_test.csv: 15,001
```

---

### ☐ Data Quality Validation

#### Check for Missing Values

```bash
python -c "import pandas as pd; \
df = pd.read_csv('data/synthetic/compliance_events_train.csv'); \
print('Missing values:'); \
print(df.isnull().sum()); \
print(f'\nTotal missing: {df.isnull().sum().sum()}')"
```

**Expected**: Total missing: 0

#### Check Compliance Distribution

```bash
python -c "import pandas as pd; \
df = pd.read_csv('data/synthetic/compliance_events_train.csv'); \
print('Compliance distribution:'); \
print(df['compliance_status'].value_counts()); \
print(f'\nCompliant %: {(df.compliance_status==\"compliant\").sum()/len(df)*100:.1f}%')"
```

**Expected**: Compliant ~75% (±3%)

#### Check Anomaly Distribution

```bash
python -c "import pandas as pd; \
df = pd.read_csv('data/synthetic/compliance_events_train.csv'); \
print('Anomaly distribution:'); \
print(df['anomaly_label'].value_counts(normalize=True) * 100)"
```

**Expected**:
- normal: ~80%
- suspicious: ~15%
- critical: ~5%

#### Check Control Coverage

```bash
python -c "import pandas as pd; \
df = pd.read_csv('data/synthetic/compliance_events_train.csv'); \
print(f'Unique controls: {df.control_id.nunique()}'); \
print(f'Expected: 50'); \
print(f'\nControl distribution (top 10):'); \
print(df['control_id'].value_counts().head(10))"
```

**Expected**: Unique controls: 50 (all controls represented)

#### Sample Event Inspection

```bash
python -c "import pandas as pd; \
df = pd.read_csv('data/synthetic/compliance_events_train.csv'); \
print('Sample event:'); \
print(df.iloc[0].to_dict())"
```

**Verify**:
- [ ] Timestamp is valid ISO format
- [ ] User ID looks realistic
- [ ] Log message is coherent
- [ ] Control ID matches a real control
- [ ] Compliance status is 'compliant' or 'non_compliant'
- [ ] Anomaly label is 'normal', 'suspicious', or 'critical'
- [ ] Severity is 'low', 'medium', 'high', or 'critical'

---

### ☐ Statistics Validation

```bash
python -c "import json; \
stats = json.load(open('data/synthetic/dataset_statistics.json')); \
print(json.dumps(stats, indent=2))"
```

**Verify**:
- [ ] Total events: 100,000
- [ ] Train/val/test: 70K/15K/15K
- [ ] Compliance ratio: ~75%/25%
- [ ] Anomaly distribution matches config
- [ ] All frameworks present (NIST-800-53, Rwanda-NCSA)
- [ ] All 12 control families represented
- [ ] Date range covers ~1 year

---

### ☐ Comprehensive Test Suite

```bash
python test_pipeline.py
```

**Expected Output**:
```
======================================================================
 COMPLIANCE ML PIPELINE - COMPONENT TESTS
======================================================================

[All tests run...]

======================================================================
 TEST SUMMARY
======================================================================
✅ PASS: config_loader
✅ PASS: logger
✅ PASS: control_mapper
✅ PASS: synthetic_generator

======================================================================
🎉 ALL TESTS PASSED!
======================================================================
```

---

## Final Validation Summary

### ✅ READY TO PROCEED IF:

- [ ] All environment checks pass
- [ ] Config loader works (29 NIST + 21 Rwanda)
- [ ] Logger creates files
- [ ] Control taxonomy generated (50 controls)
- [ ] Small dataset test passes (1K events)
- [ ] Full dataset generated (100K events)
- [ ] All CSV files created with correct sizes
- [ ] No missing values in data
- [ ] Distributions match expectations (75%/25%, 80%/15%/5%)
- [ ] All 50 controls represented
- [ ] Statistics JSON looks correct
- [ ] test_pipeline.py shows "ALL TESTS PASSED"
- [ ] Sample events look realistic

### ⚠️ DO NOT PROCEED IF:

- [ ] Any test fails
- [ ] Missing values in dataset
- [ ] Wrong number of controls (<50)
- [ ] Distributions significantly off
- [ ] File sizes don't match expected
- [ ] Memory/performance issues
- [ ] Errors in logs

---

## Post-Validation Actions

### If All Tests Pass:

1. **Commit validation results**:
   ```bash
   git add TESTING_GUIDE.md VALIDATION_CHECKLIST.md quick_test.sh
   git commit -m "Add validation testing guides and scripts"
   ```

2. **Document data quality** (optional):
   - Screenshot of test results
   - Note any unusual patterns
   - Save validation logs

3. **Proceed to Phase 5**: Baseline Models
   - BERT classifier
   - XGBoost classifier
   - LSTM classifier

### If Tests Fail:

1. **Review error messages** carefully
2. **Check logs** in `logs/` directory
3. **Verify dependencies** are installed
4. **Re-run failed component** individually
5. **Ask for help** if stuck (don't waste hours debugging)

---

## Quick Validation Command

**One-liner to validate everything**:

```bash
source venv/bin/activate && ./quick_test.sh && echo "✅ VALIDATION COMPLETE - READY FOR PHASE 5"
```

---

## Time Estimate

- **Quick test**: 2-3 minutes
- **Full dataset generation**: 5-10 minutes
- **Data quality checks**: 2-3 minutes
- **Total**: ~15-20 minutes

---

## Success Metrics

| Metric | Expected | Acceptable Range |
|--------|----------|-----------------|
| Total Events | 100,000 | Exactly 100,000 |
| Train/Val/Test | 70K/15K/15K | ±100 events |
| Compliant % | 75% | 72-78% |
| Normal Anomaly % | 80% | 77-83% |
| Unique Controls | 50 | Exactly 50 |
| Missing Values | 0 | 0 |
| File Size (total) | ~50MB | 45-55MB |
| Generation Time | 5-10 min | <15 min |

---

**Ready to validate? Run:**

```bash
./quick_test.sh
```

---

**Last Updated**: October 20, 2025
**Status**: Ready for Validation Testing
