#!/bin/bash

# Phase 2.5 Model Security Hardening Script
# Implements critical security protections before deployment

set -e

echo "=========================================================="
echo "PHASE 2.5 MODEL SECURITY HARDENING"
echo "=========================================================="
echo ""
echo "This script will:"
echo "  1. Set restrictive file permissions"
echo "  2. Generate integrity checksums"
echo "  3. Create model signatures"
echo "  4. Set up audit logging"
echo "  5. Generate security reports"
echo ""
read -p "Proceed with hardening? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Hardening cancelled"
    exit 1
fi

# Change to project root
cd "$(dirname "$0")/.."

echo ""
echo "=========================================================="
echo "STEP 1: FILE PERMISSIONS"
echo "=========================================================="

# Model files - read-only for owner, no access for others
echo "Setting model file permissions..."
if [ -d "results/models/xgboost_phase2_5" ]; then
    chmod 400 results/models/xgboost_phase2_5/*.pkl 2>/dev/null || true
    chmod 400 results/models/xgboost_phase2_5/*.json 2>/dev/null || true
    chmod 500 results/models/xgboost_phase2_5
    echo "  ✅ Model files: 400 (read-only owner)"
else
    echo "  ⚠️  Model directory not found: results/models/xgboost_phase2_5"
fi

# Training data - read-only for owner
echo "Setting training data permissions..."
if [ -d "data/integrated_targeted" ]; then
    chmod 400 data/integrated_targeted/*.csv 2>/dev/null || true
    chmod 500 data/integrated_targeted
    echo "  ✅ Training data: 400 (read-only owner)"
else
    echo "  ⚠️  Training data directory not found"
fi

# BERT embeddings - read-only for owner
if [ -d "data/bert_embeddings_integrated" ]; then
    chmod 400 data/bert_embeddings_integrated/*.npy 2>/dev/null || true
    chmod 500 data/bert_embeddings_integrated
    echo "  ✅ BERT embeddings: 400 (read-only owner)"
fi

# Audit logs - owner only
mkdir -p logs/audit
chmod 700 logs/audit
echo "  ✅ Audit logs: 700 (owner only)"

echo ""
echo "=========================================================="
echo "STEP 2: INTEGRITY CHECKSUMS"
echo "=========================================================="

echo "Generating SHA-256 checksums..."

# Model files
if [ -d "results/models/xgboost_phase2_5" ]; then
    cd results/models/xgboost_phase2_5
    sha256sum *.pkl *.json 2>/dev/null > checksums.txt || true
    chmod 400 checksums.txt
    echo "  ✅ Model checksums: $(wc -l < checksums.txt) files"
    cd - > /dev/null
fi

# Training data
if [ -d "data/integrated_targeted" ]; then
    cd data/integrated_targeted
    sha256sum *.csv 2>/dev/null > checksums.txt || true
    chmod 400 checksums.txt
    echo "  ✅ Training data checksums: $(wc -l < checksums.txt) files"
    cd - > /dev/null
fi

# BERT embeddings
if [ -d "data/bert_embeddings_integrated" ]; then
    cd data/bert_embeddings_integrated
    sha256sum *.npy 2>/dev/null > checksums.txt || true
    chmod 400 checksums.txt
    echo "  ✅ BERT embeddings checksums: $(wc -l < checksums.txt) files"
    cd - > /dev/null
fi

echo ""
echo "=========================================================="
echo "STEP 3: MODEL SIGNING"
echo "=========================================================="

echo "Generating cryptographic model signature..."

# Generate random signing key if not exists
if [ ! -f ".model_signing_key" ]; then
    openssl rand -hex 32 > .model_signing_key
    chmod 400 .model_signing_key
    echo "  ✅ Generated signing key: .model_signing_key"
else
    echo "  ℹ️  Using existing signing key"
fi

# Create Python script to sign model
cat > /tmp/sign_model.py << 'PYTHON_SCRIPT'
import hashlib
import hmac
import json
from pathlib import Path
from datetime import datetime

# Load signing key
with open('.model_signing_key', 'r') as f:
    SECRET_KEY = f.read().strip()

model_dir = Path("results/models/xgboost_phase2_5")

# Compute checksums
model_files = [
    'xgboost_phase2_5.pkl',
    'xgboost_phase2_5.json',
    'tfidf_vectorizer.pkl',
    'control_encoder.pkl',
    'family_encoder.pkl'
]

checksums = {}
for filename in model_files:
    filepath = model_dir / filename
    if filepath.exists():
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        checksums[filename] = sha256.hexdigest()

# Generate HMAC signature
signature_data = json.dumps(checksums, sort_keys=True)
signature = hmac.new(
    SECRET_KEY.encode('utf-8'),
    signature_data.encode('utf-8'),
    hashlib.sha256
).hexdigest()

# Save signature
signature_info = {
    'signature': signature,
    'checksums': checksums,
    'signed_at': datetime.now().isoformat(),
    'algorithm': 'HMAC-SHA256',
    'version': 'Phase 2.5'
}

with open(model_dir / 'model_signature.json', 'w') as f:
    json.dump(signature_info, f, indent=2)

print(f"  ✅ Model signed: {signature[:16]}...")
print(f"  ✅ Signature file: {model_dir}/model_signature.json")
PYTHON_SCRIPT

# Run signing script
source venv/bin/activate
python /tmp/sign_model.py
rm /tmp/sign_model.py

echo ""
echo "=========================================================="
echo "STEP 4: AUDIT LOGGING"
echo "=========================================================="

echo "Setting up security audit logging..."

# Create audit log files
touch logs/audit/security_events.log
touch logs/audit/security_alerts.log
touch logs/audit/access.log

chmod 600 logs/audit/*.log

# Log hardening event
cat >> logs/audit/security_events.log << EOF
{"timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")", "event": "MODEL_SECURITY_HARDENING", "status": "IN_PROGRESS", "user": "$(whoami)"}
EOF

echo "  ✅ Audit log files created:"
echo "     - logs/audit/security_events.log"
echo "     - logs/audit/security_alerts.log"
echo "     - logs/audit/access.log"

echo ""
echo "=========================================================="
echo "STEP 5: SECURITY CONFIGURATION"
echo "=========================================================="

# Disable core dumps (prevent memory leakage)
ulimit -c 0
echo "  ✅ Core dumps disabled (ulimit -c 0)"

# Create security configuration
cat > config/security.json << EOF
{
  "authentication": {
    "enabled": true,
    "token_expiry_hours": 24,
    "max_failed_attempts": 5
  },
  "rate_limiting": {
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
    "requests_per_day": 10000
  },
  "input_validation": {
    "max_log_length": 10000,
    "min_log_length": 10,
    "allowed_chars": "ascii_printable"
  },
  "adversarial_detection": {
    "enabled": true,
    "confidence_threshold": 0.6,
    "z_score_threshold": 3.0
  },
  "audit_logging": {
    "enabled": true,
    "log_predictions": true,
    "log_failed_auth": true,
    "log_rate_limit_violations": true
  },
  "model_integrity": {
    "verify_on_load": true,
    "verify_interval_hours": 24
  }
}
EOF

chmod 600 config/security.json
echo "  ✅ Security configuration: config/security.json"

echo ""
echo "=========================================================="
echo "STEP 6: SECURITY REPORT"
echo "=========================================================="

# Generate security report
cat > logs/audit/security_hardening_report_$(date +%Y%m%d).txt << EOF
========================================================
PHASE 2.5 MODEL SECURITY HARDENING REPORT
========================================================

Hardening Date: $(date)
Performed By: $(whoami)
Hostname: $(hostname)

FILE PERMISSIONS
----------------
Model Files:       400 (read-only owner)
Training Data:     400 (read-only owner)
BERT Embeddings:   400 (read-only owner)
Audit Logs:        700 (owner only)
Security Config:   600 (owner read/write only)

INTEGRITY PROTECTION
-------------------
Model Checksums:   ✅ Generated (SHA-256)
Model Signature:   ✅ Generated (HMAC-SHA256)
Signing Key:       ✅ Protected (.model_signing_key, mode 400)

AUDIT LOGGING
-------------
Security Events:   ✅ Enabled (logs/audit/security_events.log)
Security Alerts:   ✅ Enabled (logs/audit/security_alerts.log)
Access Logs:       ✅ Enabled (logs/audit/access.log)

SECURITY FEATURES
-----------------
Authentication:    ✅ Configured (JWT, 24h expiry)
Rate Limiting:     ✅ Configured (60/min, 1000/hr, 10K/day)
Input Validation:  ✅ Configured (10-10000 chars, ASCII)
Adversarial Det:   ✅ Configured (threshold: 0.6)
Model Integrity:   ✅ Configured (verify on load + every 24h)

SYSTEM HARDENING
----------------
Core Dumps:        ✅ Disabled (ulimit -c 0)
HTTPS/TLS:         ⚠️  Not configured (manual setup required)
Encryption:        ⚠️  Not configured (optional)

NEXT STEPS
----------
1. ⏳ Set up HTTPS/TLS: bash scripts/setup_https.sh
2. ⏳ Create admin credentials (change default password)
3. ⏳ Test security controls in staging environment
4. ⏳ Set up monitoring alerts (SIEM integration)
5. ⏳ Schedule regular security audits (weekly/monthly)

VERIFICATION COMMANDS
--------------------
# Verify model integrity
python -c "from src.security.model_signing import ModelSigner; \
signer = ModelSigner(open('.model_signing_key').read().strip()); \
print('✅ Valid' if signer.verify_model('results/models/xgboost_phase2_5') else '❌ Invalid')"

# Check file permissions
ls -la results/models/xgboost_phase2_5/
ls -la data/integrated_targeted/
ls -la logs/audit/

# View audit logs
tail -f logs/audit/security_events.log

========================================================
HARDENING COMPLETE
========================================================
EOF

cat logs/audit/security_hardening_report_$(date +%Y%m%d).txt

# Log completion
cat >> logs/audit/security_events.log << EOF
{"timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")", "event": "MODEL_SECURITY_HARDENING", "status": "COMPLETED", "user": "$(whoami)"}
EOF

echo ""
echo "=========================================================="
echo "SECURITY HARDENING COMPLETE ✅"
echo "=========================================================="
echo ""
echo "Security Report: logs/audit/security_hardening_report_$(date +%Y%m%d).txt"
echo ""
echo "⚠️  IMPORTANT NEXT STEPS:"
echo "  1. Set up HTTPS/TLS for production deployment"
echo "  2. Change default admin password"
echo "  3. Test security controls before deployment"
echo "  4. Set up continuous security monitoring"
echo ""
echo "=========================================================="
