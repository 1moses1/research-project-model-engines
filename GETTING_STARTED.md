# Getting Started with Rwanda NCSA Compliance Model

**Welcome!** This guide assumes you're starting fresh and will walk you through everything you need to know.

---

## 📦 Package Information

**Package Name**: `rwanda-ncsa-compliance-model-v2.5-FULL.tar.gz`
**Size**: 2.8 GB (compressed)
**Checksums**:
- **SHA-256**: `92aa1b85586c4c11ba00435d471b402fa98566838a33864f51da6f7981ce17bf`
- **MD5**: `13610d14640ab07eb793dc0846ca2891`

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Extract the Package

```bash
# Navigate to where you want to extract
cd /path/to/your/destination

# Extract the archive
tar -xzf rwanda-ncsa-compliance-model-v2.5-FULL.tar.gz

# Enter the directory
cd model-engine/
```

### Step 2: Activate the Environment

The package includes a pre-configured Python environment with all dependencies:

```bash
# Activate the virtual environment
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### Step 3: Test the Model

```bash
# Quick test to verify everything works
python test_phase2_5.py

# Expected output:
# ✅ Model loaded successfully
# ✅ 12/12 real scenarios passed (100% accuracy)
# ✅ Model is working correctly!
```

**That's it!** Your model is ready to use. 🎉

---

## 📚 What's Inside This Repository?

### 1. **The Production Model** ⭐

**Location**: `results/models/xgboost_phase2_5/`

This is your trained AI model that detects cybersecurity compliance violations:

```
results/models/xgboost_phase2_5/
├── xgboost_phase2_5.pkl          # Main model (999 KB)
├── tfidf_vectorizer.pkl          # Text processor (1.2 MB)
├── control_encoder.pkl           # Control ID encoder
├── family_encoder.pkl            # Control family encoder
├── phase2_5_metrics.json         # Performance: 99.49% accuracy
└── model_signature.json          # Security signature
```

**What it does**: Analyzes security logs and tells you if they're compliant or non-compliant with Rwanda NCSA standards.

### 2. **Training Data** (200,000 Events)

**Location**: `data/real_formatted/`

The model was trained on a mix of:
- **52%** Real network attacks (NSL-KDD dataset)
- **18%** Real system logs (LogHub: Hadoop, OpenStack, Linux)
- **30%** Synthetic Rwanda NCSA compliance scenarios

```
data/real_formatted/
├── compliance_events_train.csv   # 140,000 events (70%)
├── compliance_events_val.csv     # 30,000 events (15%)
└── compliance_events_test.csv    # 30,000 events (15%)
```

**Why this matters**: The model learned from real-world attacks, not just fake data, making it robust.

### 3. **Source Code** (11 Modules)

**Location**: `src/`

All the Python code that powers the system:

```
src/
├── api/                 # API to serve predictions
├── data_pipeline/       # Data processing and generation
├── explainability/      # Explain why predictions were made
├── models/              # ML model implementations
├── security/            # Security features (auth, encryption)
└── utils/               # Helper functions
```

**For developers**: See `src/README.md` for detailed module documentation.

### 4. **Documentation** (7 Guides)

All documentation is in the root directory:

| File | Purpose | When to Read |
|------|---------|--------------|
| **README.md** | Complete system overview | Start here! |
| **GETTING_STARTED.md** (this file) | Step-by-step tutorial | You're reading it |
| **INSTALLATION.md** | Detailed setup | If you have issues |
| **TRAINING_GUIDE.md** | How to retrain the model | If you want to improve it |
| **MODEL_INFERENCE_GUIDE.md** | How to use the API | For integration |
| **MODEL_COMPARISON_AND_USE_CASES.md** | When to use this model | For decision makers |
| **MODEL_SECURITY_HARDENING.md** | Security features | For security teams |

### 5. **Configuration Files**

**Location**: `config/`

Contains settings and credentials:

```
config/
├── credentials/          # User accounts and API keys
│   ├── admin_user.json
│   ├── soc_analyst_1.json
│   └── ...
├── security.json         # Security settings
└── model_config.yaml     # Model parameters
```

⚠️ **IMPORTANT**: The credentials directory contains sensitive API keys. Never share these publicly!

---

## 🎯 Common Use Cases

### Use Case 1: Test with Your Own Log

```python
# test_custom_log.py
import joblib

# Load the model
model = joblib.load('results/models/xgboost_phase2_5/xgboost_phase2_5.pkl')
vectorizer = joblib.load('results/models/xgboost_phase2_5/tfidf_vectorizer.pkl')

# Your log message
log = "Failed SSH login from 192.168.1.100 - Access denied"

# Get prediction
features = vectorizer.transform([log])
prediction = model.predict(features)[0]
confidence = model.predict_proba(features).max()

print(f"Status: {prediction}")          # compliant or non_compliant
print(f"Confidence: {confidence:.1%}")  # 99.9%
```

**Run it**:
```bash
python test_custom_log.py
```

### Use Case 2: Start the API Server

If you want to integrate this model into another system:

```bash
# Start the secure API
python src/api/secure_api.py

# API will be available at: https://localhost:5000
```

Then make predictions via HTTP:

```bash
curl -X POST https://localhost:5000/api/predict \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -k \
  -d '{
    "log_message": "Failed SSH login from 192.168.1.100",
    "control_id": "AC-3",
    "control_family": "Access Control"
  }'
```

**Get your API key**: See `config/credentials/soc_analyst_1.json`

### Use Case 3: Batch Process Many Logs

```python
# batch_test.py
import joblib
import pandas as pd

# Load model
model = joblib.load('results/models/xgboost_phase2_5/xgboost_phase2_5.pkl')
vectorizer = joblib.load('results/models/xgboost_phase2_5/tfidf_vectorizer.pkl')

# Your logs (CSV file with 'log_message' column)
logs_df = pd.read_csv('your_logs.csv')

# Batch prediction
features = vectorizer.transform(logs_df['log_message'])
predictions = model.predict(features)
confidences = model.predict_proba(features).max(axis=1)

# Add results to dataframe
logs_df['compliance_status'] = predictions
logs_df['confidence'] = confidences

# Save results
logs_df.to_csv('logs_with_predictions.csv', index=False)
print(f"✅ Processed {len(logs_df)} logs")
```

---

## 📊 Understanding the Model

### What Controls Does It Support?

**50 Compliance Controls** across 7 families:

1. **Access Control (AC)** - Who can access what
2. **Audit & Accountability (AU)** - Logging and tracking
3. **Identification & Authentication (IA)** - User verification
4. **System Protection (SC)** - Network security
5. **System Integrity (SI)** - Malware protection
6. **Incident Response (IR)** - Handling attacks
7. **Configuration Management (CM)** - System settings

**Examples**:
- `AC-3`: Access enforcement (e.g., failed login = violation)
- `IA-5`: Password management (e.g., weak password = violation)
- `SI-4`: System monitoring (e.g., missing logs = violation)

See full list: `src/data_pipeline/control_mapper.py`

### What Attacks Can It Detect?

**42 Attack Types** from real-world data:

| Category | Examples | What It Means |
|----------|----------|---------------|
| **Unauthorized Access** | Buffer overflow, rootkit, privilege escalation | Someone trying to break in |
| **Password Attacks** | Brute force, credential stuffing | Guessing passwords |
| **DoS Attacks** | DDoS, UDP storm, SYN flood | Overwhelming the system |
| **Reconnaissance** | Port scanning, IP sweep | Mapping your network |
| **Malware** | Worms, trojans, phishing | Malicious software |

### How Accurate Is It?

**Test Results** (24,477 events):
- **Overall Accuracy**: 99.49%
- **Detects 98.96% of actual violations** (only 114 missed out of 10,925)
- **99.90% precision** on violations (rarely wrong when it says there's a problem)

**Real-World Validation**: 100% (12/12) on diverse attack scenarios including:
- ✅ Phishing emails
- ✅ Insider threats
- ✅ DDoS attacks
- ✅ SQL injection
- ✅ Ransomware
- ✅ Credential stuffing

### How Fast Is It?

- **Single prediction**: 1 millisecond
- **Throughput**: 1,000 logs per second
- **Batch (1,000 logs)**: 50 milliseconds

**What this means**: You can analyze millions of logs per day on a single machine.

---

## 🔧 Advanced Operations

### Retrain the Model

If you get new data or want to improve accuracy:

```bash
# 1. Add your new data to data/new_samples/
# 2. Retrain
python train_phase2_5.py --data-dir data/new_samples/

# 3. Evaluate
python test_phase2_5.py

# 4. If better, replace the production model
cp results/models/xgboost_phase2_5/xgboost_phase2_5.pkl \
   results/models/production/xgboost_phase2_5.pkl
```

**Recommended frequency**: Every 3 months or when accuracy drops below 98%

### View Model Explanations

Want to understand WHY the model made a prediction?

```bash
# Explain a specific prediction
python explain_predictions_cli.py \
  --log-message "Failed SSH login from 192.168.1.100"

# Output shows which keywords influenced the decision
```

### Check Security Status

The model has 9 security layers. Verify they're working:

```bash
# Run security validation
python tests/test_security.py

# Check audit logs
tail -f logs/audit/security_events.log
```

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError"

**Solution**: Make sure you activated the virtual environment:
```bash
source venv/bin/activate
```

### Problem: "Model file not found"

**Solution**: You're in the wrong directory. Navigate to the repository root:
```bash
cd /path/to/model-engine/
ls results/models/xgboost_phase2_5/  # Should list model files
```

### Problem: "Permission denied" when accessing credentials

**Solution**: Credentials are secured. Use `sudo` or contact the admin:
```bash
sudo cat config/credentials/admin_user.json
```

### Problem: API returns 401 Unauthorized

**Solution**: You need to provide an API key. Get it from credentials:
```bash
# View your API key
cat config/credentials/soc_analyst_1.json

# Use in API call
curl -H 'Authorization: Bearer YOUR_API_KEY_HERE' ...
```

### Problem: Model predictions seem wrong

**Solution**: Check the model signature to ensure it hasn't been tampered with:
```python
from src.security.model_signing import ModelSigner

signer = ModelSigner(open('.model_signing_key').read().strip())
is_valid = signer.verify_model('results/models/xgboost_phase2_5')

if not is_valid:
    print("❌ Model has been tampered with! Restore from backup.")
else:
    print("✅ Model integrity verified")
```

---

## 📖 Learning Path

### Beginner (Day 1)

1. ✅ Read this guide (you're here!)
2. ✅ Run `python test_phase2_5.py` to verify setup
3. ✅ Try the "Test with Your Own Log" example
4. ✅ Read `README.md` for system overview

### Intermediate (Week 1)

1. Read `MODEL_INFERENCE_GUIDE.md` for API integration
2. Start the API server and make predictions via HTTP
3. Process a batch of logs using the batch example
4. Explore `data/real_formatted/` to see training data

### Advanced (Month 1)

1. Read `TRAINING_GUIDE.md` and retrain with custom data
2. Read `MODEL_SECURITY_HARDENING.md` for security features
3. Set up continuous learning pipeline
4. Integrate with your SIEM (Splunk/QRadar)

---

## 🎓 Key Concepts to Understand

### What is "Compliance"?

**Compliance** = Following cybersecurity rules (Rwanda NCSA standards)

**Example**:
- ✅ **Compliant**: "Successful SSH login for admin"
- ❌ **Non-Compliant**: "Failed SSH login attempt" (possible attack)

The model reads log messages and classifies them.

### What is "Confidence"?

**Confidence** = How sure the model is about its prediction (0-100%)

**Example**:
- 99.9% confidence = Model is very sure
- 60% confidence = Model is uncertain, review manually

**Rule of thumb**:
- >90% = Trust the prediction
- 60-90% = Review manually
- <60% = Investigate thoroughly

### What is TF-IDF?

**TF-IDF** = A way to identify important words in text

**Example**: In "Failed SSH login attempt from 192.168.1.100":
- "Failed" = High importance (indicates problem)
- "SSH" = Medium importance (type of access)
- "from" = Low importance (common word)

The model uses TF-IDF to understand log messages.

### What is SHAP?

**SHAP** = Explanation tool that shows WHY the model made a prediction

**Example**:
```
Log: "Failed SSH login from 192.168.1.100"
Prediction: non_compliant (99.9% confidence)

SHAP Explanation:
  - "failed" → +2.3 (strong signal for non-compliant)
  - "login" → +0.8
  - "denied" → +0.2
```

Use `explain_predictions_cli.py` to see SHAP values.

---

## 🔐 Security Features

This model includes 9 security layers:

1. **Input Validation** - Checks log messages for malicious content
2. **Authentication** - JWT tokens and API keys
3. **Authorization** - Role-based access (admin, analyst, viewer)
4. **Rate Limiting** - Prevents API abuse (60 requests/minute)
5. **Adversarial Detection** - Identifies evasion attempts
6. **Model Integrity** - Cryptographic signatures detect tampering
7. **Data Protection** - Encryption for sensitive files
8. **Audit Logging** - Tracks all activity
9. **Monitoring** - Alerts for security incidents

See `MODEL_SECURITY_HARDENING.md` for details.

---

## 📞 Getting Help

### Documentation

- **General questions**: Read `README.md`
- **Setup issues**: Read `INSTALLATION.md`
- **API integration**: Read `MODEL_INFERENCE_GUIDE.md`
- **Retraining**: Read `TRAINING_GUIDE.md`

### Code Examples

All examples are in the root directory:
```bash
ls *.py | grep test_  # List all test scripts
python test_phase2_5.py      # Basic test
python explain_predictions_cli.py --help  # Get help
```

### Directory READMEs

Each major directory has its own guide:
- `src/README.md` - Source code organization
- `data/README.md` - Dataset documentation
- `results/README.md` - Model artifacts
- `config/README.md` - Configuration guide

---

## 🎯 Next Steps

Now that you understand the basics, here's what to do next:

### Option 1: Use the Model As-Is
✅ Best for: Quick deployment, testing, demonstration

**Steps**:
1. Test with sample logs: `python test_phase2_5.py`
2. Process your logs using batch script
3. Start API server for integration
4. Monitor predictions in `logs/audit/predictions.log`

### Option 2: Customize for Your Needs
🔧 Best for: Adapting to Rwanda SOC production environment

**Steps**:
1. Collect sample Rwanda SOC logs
2. Test model on your logs: `python test_custom_log.py`
3. If accuracy <95%, retrain with your data
4. Fine-tune security settings in `config/security.json`
5. Deploy to staging environment

### Option 3: Deep Dive into the System
🎓 Best for: Understanding how everything works

**Steps**:
1. Read all documentation (7 guides)
2. Explore source code in `src/`
3. Review training data in `data/`
4. Understand security features
5. Experiment with retraining

---

## ✅ Checklist: Are You Ready?

Before deploying to production, verify:

- [ ] ✅ Model loads successfully: `python test_phase2_5.py`
- [ ] ✅ Tested on sample Rwanda SOC logs
- [ ] ✅ API server starts: `python src/api/secure_api.py`
- [ ] ✅ Security verified: `python tests/test_security.py`
- [ ] ✅ Credentials secured: `chmod 600 config/credentials/*.json`
- [ ] ✅ Backup created: `cp -r model-engine/ /backup/location/`
- [ ] ✅ Team trained on using the system
- [ ] ✅ Monitoring setup: Grafana/Splunk dashboards
- [ ] ✅ Incident response plan documented

---

## 📊 Quick Reference

### File Sizes
- **Model**: 3.2 MB
- **Training Data**: 50 MB (200K events)
- **Full Repository**: 10 GB (2.8 GB compressed)

### Performance
- **Accuracy**: 99.49%
- **Recall**: 98.96% (detects 98.96% of violations)
- **Speed**: 1 ms per log
- **Throughput**: 1,000 logs/second

### System Requirements
- **CPU**: Any modern CPU (no GPU needed)
- **RAM**: 2 GB minimum (100 MB for inference)
- **Storage**: 500 MB (or 10 GB with all data)
- **OS**: macOS, Linux, Windows

### Important Locations
- **Production Model**: `results/models/xgboost_phase2_5/`
- **Training Data**: `data/real_formatted/`
- **Credentials**: `config/credentials/`
- **Logs**: `logs/audit/`
- **Documentation**: Root directory (*.md files)

---

## 🎉 Congratulations!

You now understand:
- ✅ What this model does
- ✅ How to use it
- ✅ Where everything is located
- ✅ How to test and deploy it
- ✅ How to get help when needed

**Start experimenting!** The best way to learn is by trying things out.

---

**Version**: 2.0
**Last Updated**: November 3, 2025
**Author**: Moise Iradukunda (Carnegie Mellon University)
**Package**: rwanda-ncsa-compliance-model-v2.5-FULL.tar.gz

**Questions?** Read `README.md` for comprehensive documentation.
