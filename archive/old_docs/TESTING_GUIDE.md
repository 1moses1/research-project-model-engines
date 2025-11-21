# Testing Guide - Data Pipeline Validation

## Prerequisites Check

Before running tests, ensure you have:
- Python 3.8 or higher
- pip package manager
- At least 2GB free disk space
- Terminal/command line access

## Step-by-Step Testing Instructions

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"

# Run setup script (creates venv and installs packages)
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Verify activation (you should see (venv) in your prompt)
which python
# Should show: .../model-engine/venv/bin/python
```

**If setup.sh fails**, manually install:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install pyyaml numpy pandas
```

---

### Step 2: Test Configuration Loader

```bash
# Test config loader standalone
python -c "
from src.utils.config_loader import ConfigLoader
loader = ConfigLoader()
print('✅ Config loader works!')
print(f'NIST controls: {len(loader.get_nist_controls())}')
print(f'Rwanda controls: {len(loader.get_rwanda_controls())}')
"
```

**Expected Output:**
```
✅ Config loader works!
NIST controls: 29
Rwanda controls: 21
```

---

### Step 3: Test Logger

```bash
# Test logger standalone
python -c "
from src.utils.logger import setup_logger
logger = setup_logger('test')
logger.info('✅ Logger works!')
"
```

**Expected Output:**
```
2025-10-20 XX:XX:XX - test - INFO - ✅ Logger works!
```

---

### Step 4: Generate Control Taxonomy

```bash
# Generate control taxonomy JSON
python src/data_pipeline/control_mapper.py
```

**Expected Output:**
```
2025-10-20 XX:XX:XX - control_mapper - INFO - Loaded 29 NIST controls
2025-10-20 XX:XX:XX - control_mapper - INFO - Loaded 21 Rwanda controls
2025-10-20 XX:XX:XX - control_mapper - INFO - Created 29 NIST control definitions
2025-10-20 XX:XX:XX - control_mapper - INFO - Created 21 Rwanda control definitions
2025-10-20 XX:XX:XX - control_mapper - INFO - Control taxonomy saved to: data/processed/control_taxonomy.json
2025-10-20 XX:XX:XX - control_mapper - INFO - Total controls: 50

✅ Control taxonomy created successfully!
📁 Output: data/processed/control_taxonomy.json

📊 Summary:
  - Total Controls: 50
  - NIST Controls: 29
  - Rwanda Controls: 21
  - Control Families: 12

🏷️  Control Families:
  - Access Control: X controls
  - Audit and Accountability: X controls
  - ...
```

**Verify File Created:**
```bash
ls -lh data/processed/control_taxonomy.json
# Should show file size ~50-100KB
```

---

### Step 5: Test Synthetic Generator (Small Dataset)

```bash
# Generate small test dataset (1,000 events)
python -c "
from src.data_pipeline.synthetic_generator import SyntheticEventGenerator

print('Initializing generator...')
generator = SyntheticEventGenerator()

print('Generating 1,000 test events...')
df = generator.generate_dataset(num_events=1000)

print(f'✅ Generated {len(df)} events')
print(f'✅ Columns: {len(df.columns)}')
print(f'\nFirst event:')
print(df.iloc[0].to_dict())

print(f'\nCompliance distribution:')
print(df['compliance_status'].value_counts())

print(f'\nAnomal y distribution:')
print(df['anomaly_label'].value_counts())
"
```

**Expected Output:**
```
Initializing generator...
2025-10-20 XX:XX:XX - synthetic_generator - INFO - Loaded 50 controls from taxonomy
Generating 1,000 test events...
2025-10-20 XX:XX:XX - synthetic_generator - INFO - Dataset generation complete: 1000 events
✅ Generated 1000 events
✅ Columns: 19

First event:
{'event_id': 'EVT-123456', 'timestamp': '2024-XX-XX...', ...}

Compliance distribution:
compliant        750
non_compliant    250
Name: compliance_status, dtype: int64

Anomaly distribution:
normal         800
suspicious     150
critical        50
Name: anomaly_label, dtype: int64
```

---

### Step 6: Run Complete Pipeline Test

```bash
# Run comprehensive test suite
python test_pipeline.py
```

**Expected Output:**
```
======================================================================
 COMPLIANCE ML PIPELINE - COMPONENT TESTS
======================================================================

============================================================
Testing Configuration Loader...
============================================================
✅ Data config loaded: X keys
✅ Model config loaded: X keys
✅ NIST controls: 29
✅ Rwanda controls: 21

============================================================
Testing Logger...
============================================================
✅ Logger works!

============================================================
Testing Control Mapper...
============================================================
✅ Total controls: 50
✅ NIST controls: 29
✅ Rwanda controls: 21
✅ Control families: 12
✅ Taxonomy saved to: data/processed/control_taxonomy.json

============================================================
Testing Synthetic Event Generator...
============================================================
Generating 1000 test events...
✅ Generated 1000 events
✅ Columns: ['event_id', 'timestamp', ...]
Sample event:
{...}

✅ Split complete:
  Train: 700
  Val: 150
  Test: 150

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

### Step 7: Generate Full 100K Dataset (Optional)

**⚠️ WARNING**: This will take 5-10 minutes and create ~50MB of data

```bash
# Generate full 100,000 event dataset
python src/data_pipeline/synthetic_generator.py
```

**Expected Output:**
```
2025-10-20 XX:XX:XX - synthetic_generator - INFO - Loaded 50 controls from taxonomy
2025-10-20 XX:XX:XX - synthetic_generator - INFO - Generating 100000 synthetic compliance events...
2025-10-20 XX:XX:XX - synthetic_generator - INFO - Generated 10000/100000 events
2025-10-20 XX:XX:XX - synthetic_generator - INFO - Generated 20000/100000 events
...
2025-10-20 XX:XX:XX - synthetic_generator - INFO - Dataset generation complete: 100000 events
2025-10-20 XX:XX:XX - synthetic_generator - INFO - Dataset split:
2025-10-20 XX:XX:XX - synthetic_generator - INFO -   Train: 70000 events (70.0%)
2025-10-20 XX:XX:XX - synthetic_generator - INFO -   Val:   15000 events (15.0%)
2025-10-20 XX:XX:XX - synthetic_generator - INFO -   Test:  15000 events (15.0%)
2025-10-20 XX:XX:XX - synthetic_generator - INFO - Saved train set to data/synthetic/compliance_events_train.csv
2025-10-20 XX:XX:XX - synthetic_generator - INFO - Saved val set to data/synthetic/compliance_events_val.csv
2025-10-20 XX:XX:XX - synthetic_generator - INFO - Saved test set to data/synthetic/compliance_events_test.csv
2025-10-20 XX:XX:XX - synthetic_generator - INFO - Statistics saved to data/synthetic/dataset_statistics.json

============================================================
✅ SYNTHETIC DATASET GENERATION COMPLETE
============================================================

📊 Dataset Summary:
  Total Events: 100,000
  Train: 70,000
  Validation: 15,000
  Test: 15,000

📈 Compliance Distribution:
  compliant: 75,000 (75.0%)
  non_compliant: 25,000 (25.0%)

🚨 Anomaly Distribution:
  normal: 80,000 (80.0%)
  suspicious: 15,000 (15.0%)
  critical: 5,000 (5.0%)

⚠️  Severity Distribution:
  low: XX,XXX (XX.X%)
  medium: XX,XXX (XX.X%)
  high: XX,XXX (XX.X%)
  critical: XX,XXX (XX.X%)

📁 Output Files:
  train: data/synthetic/compliance_events_train.csv
  val: data/synthetic/compliance_events_val.csv
  test: data/synthetic/compliance_events_test.csv

📄 Statistics: data/synthetic/dataset_statistics.json

============================================================
```

**Verify Files Created:**
```bash
ls -lh data/synthetic/
# Should show:
# compliance_events_train.csv (~35MB)
# compliance_events_val.csv (~7.5MB)
# compliance_events_test.csv (~7.5MB)
# dataset_statistics.json (~2KB)
```

---

### Step 8: Inspect Generated Data

```bash
# View first few rows of training data
head -n 5 data/synthetic/compliance_events_train.csv

# Or use Python to inspect
python -c "
import pandas as pd
df = pd.read_csv('data/synthetic/compliance_events_train.csv')
print(f'Shape: {df.shape}')
print(f'\nColumns: {list(df.columns)}')
print(f'\nFirst event:')
print(df.iloc[0])
print(f'\nData types:')
print(df.dtypes)
print(f'\nMissing values:')
print(df.isnull().sum())
"
```

---

### Step 9: View Dataset Statistics

```bash
# Pretty-print statistics JSON
python -c "
import json
with open('data/synthetic/dataset_statistics.json', 'r') as f:
    stats = json.load(f)
print(json.dumps(stats, indent=2))
"
```

---

## Validation Checklist

After running all tests, verify:

- [ ] Virtual environment activated
- [ ] All dependencies installed (pyyaml, pandas, numpy)
- [ ] Config loader works (29 NIST + 21 Rwanda controls)
- [ ] Logger creates log files in `logs/`
- [ ] Control taxonomy JSON created (50 controls, 12 families)
- [ ] Synthetic generator creates events
- [ ] Train/val/test split works (70/15/15)
- [ ] Dataset files created in `data/synthetic/`
- [ ] Statistics JSON generated
- [ ] No errors or exceptions
- [ ] Data quality looks reasonable (check sample events)

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'yaml'"

**Solution:**
```bash
pip install pyyaml
```

### Issue: "FileNotFoundError: control_taxonomy.json not found"

**Solution:**
```bash
# Generate taxonomy first
python src/data_pipeline/control_mapper.py
```

### Issue: Virtual environment not activating

**Solution (macOS/Linux):**
```bash
source venv/bin/activate
```

**Solution (Windows):**
```bash
venv\Scripts\activate
```

### Issue: Permission denied on setup.sh

**Solution:**
```bash
chmod +x setup.sh
./setup.sh
```

### Issue: Data generation takes too long

**Solution:**
- Start with smaller dataset (1,000 events) for testing
- 100K events should take 5-10 minutes max
- If slower, check system resources

---

## Success Criteria

✅ **Pipeline is ready for next phase if:**
1. All tests pass (config, logger, mapper, generator)
2. 100K dataset generated successfully
3. Train/val/test files created (70K/15K/15K)
4. Statistics JSON shows correct distributions
5. No missing values in dataset
6. Sample events look realistic
7. All 50 controls represented in data

---

## Next Steps After Validation

Once all tests pass:

1. **Commit validated data** (optional - data files are in .gitignore)
2. **Proceed to Phase 5**: Implement baseline models (BERT, XGBoost, LSTM)
3. **Train first model**: Start with BERT or XGBoost
4. **Evaluate accuracy**: Target >93%

---

## Quick Test Command

For a fast validation run:

```bash
# One-liner to test everything
python test_pipeline.py && echo "✅ Ready to proceed!"
```

---

**Last Updated**: October 20, 2025
**Estimated Testing Time**: 10-15 minutes
