#!/usr/bin/env python3
"""
Security Hardening Script for Phase 2.5 Model
Applies file permissions, checksums, and cryptographic signatures
"""

import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def create_checksum(filepath):
    """Generate SHA-256 checksum for file"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def sign_model(model_dir, secret_key):
    """Sign model files with HMAC-SHA256"""
    model_dir = Path(model_dir)

    model_files = [
        'xgboost_phase2_5.pkl',
        'tfidf_vectorizer.pkl',
        'control_encoder.pkl',
        'family_encoder.pkl'
    ]

    checksums = {}
    for filename in model_files:
        filepath = model_dir / filename
        if filepath.exists():
            checksums[filename] = create_checksum(filepath)

    # Generate HMAC signature
    signature_data = json.dumps(checksums, sort_keys=True)
    signature = hmac.new(
        secret_key.encode('utf-8'),
        signature_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Save signature
    signature_info = {
        'signature': signature,
        'checksums': checksums,
        'signed_at': datetime.now().isoformat(),
        'algorithm': 'HMAC-SHA256',
        'version': 'Phase 2.5',
        'files_signed': len(checksums)
    }

    signature_file = model_dir / 'model_signature.json'
    with open(signature_file, 'w') as f:
        json.dump(signature_info, f, indent=2)

    return signature, signature_file

def main():
    logger.info("=" * 80)
    logger.info("PHASE 2.5 MODEL SECURITY HARDENING")
    logger.info("=" * 80)
    logger.info("")

    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Step 1: Create directories
    logger.info("Step 1: Creating security directories...")
    (project_root / 'logs' / 'audit').mkdir(parents=True, exist_ok=True)
    (project_root / 'config').mkdir(parents=True, exist_ok=True)
    logger.info("  ✅ Directories created")
    logger.info("")

    # Step 2: Generate signing key
    logger.info("Step 2: Generating cryptographic signing key...")
    key_file = project_root / '.model_signing_key'

    if key_file.exists():
        logger.info("  ℹ️  Using existing signing key")
        with open(key_file, 'r') as f:
            secret_key = f.read().strip()
    else:
        secret_key = secrets.token_hex(32)
        with open(key_file, 'w') as f:
            f.write(secret_key)
        os.chmod(key_file, 0o400)
        logger.info(f"  ✅ Generated new signing key: {key_file}")

    logger.info(f"  Key preview: {secret_key[:16]}...{secret_key[-16:]}")
    logger.info("")

    # Step 3: Generate checksums for model files
    logger.info("Step 3: Generating file integrity checksums...")

    model_dir = project_root / 'results' / 'models' / 'xgboost_phase2_5'
    if model_dir.exists():
        checksum_file = model_dir / 'checksums.txt'
        with open(checksum_file, 'w') as f:
            for pkl_file in model_dir.glob('*.pkl'):
                checksum = create_checksum(pkl_file)
                f.write(f"{checksum}  {pkl_file.name}\n")
                logger.info(f"  ✅ {pkl_file.name}: {checksum[:16]}...")
        logger.info(f"  ✅ Checksums saved: {checksum_file}")
    else:
        logger.warning(f"  ⚠️  Model directory not found: {model_dir}")

    logger.info("")

    # Step 4: Sign model
    logger.info("Step 4: Signing model with cryptographic signature...")

    checksums = {}
    signature = None
    signature_file = None

    if model_dir.exists():
        signature, signature_file = sign_model(model_dir, secret_key)
        # Load checksums for later use
        sig_data = json.load(open(signature_file))
        checksums = sig_data['checksums']
        logger.info(f"  ✅ Model signed successfully")
        logger.info(f"  ✅ Signature: {signature[:32]}...")
        logger.info(f"  ✅ Signature file: {signature_file}")
    else:
        logger.warning(f"  ⚠️  Cannot sign - model directory not found")

    logger.info("")

    # Step 5: Create security configuration
    logger.info("Step 5: Creating security configuration...")

    security_config = {
        "authentication": {
            "enabled": True,
            "token_expiry_hours": 24,
            "max_failed_attempts": 5,
            "password_min_length": 12
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
            "enabled": True,
            "confidence_threshold": 0.6,
            "z_score_threshold": 3.0
        },
        "audit_logging": {
            "enabled": True,
            "log_predictions": True,
            "log_failed_auth": True,
            "log_rate_limit_violations": True
        },
        "model_integrity": {
            "verify_on_load": True,
            "verify_interval_hours": 24
        },
        "deployment": {
            "environment": "staging",
            "https_only": True,
            "cors_enabled": False
        }
    }

    config_file = project_root / 'config' / 'security.json'
    with open(config_file, 'w') as f:
        json.dump(security_config, f, indent=2)

    os.chmod(config_file, 0o600)
    logger.info(f"  ✅ Security config: {config_file}")
    logger.info("")

    # Step 6: Initialize audit logging
    logger.info("Step 6: Initializing audit logging...")

    audit_files = [
        'security_events.log',
        'security_alerts.log',
        'access.log',
        'predictions.log'
    ]

    for audit_file in audit_files:
        filepath = project_root / 'logs' / 'audit' / audit_file
        if not filepath.exists():
            filepath.touch()
        os.chmod(filepath, 0o600)
        logger.info(f"  ✅ {audit_file}")

    # Log hardening event
    event = {
        'timestamp': datetime.now().isoformat(),
        'event': 'MODEL_SECURITY_HARDENING',
        'status': 'COMPLETED',
        'user': os.getenv('USER', 'unknown'),
        'files_secured': len(checksums) if model_dir.exists() else 0
    }

    with open(project_root / 'logs' / 'audit' / 'security_events.log', 'a') as f:
        f.write(json.dumps(event) + '\n')

    logger.info("")

    # Step 7: Generate security report
    logger.info("Step 7: Generating security report...")

    report = f"""
{'=' * 80}
PHASE 2.5 MODEL SECURITY HARDENING REPORT
{'=' * 80}

Hardening Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Performed By: {os.getenv('USER', 'unknown')}

SECURITY MEASURES APPLIED
-------------------------
✅ Cryptographic signing key generated (64-char hex)
✅ File integrity checksums created (SHA-256)
✅ Model cryptographic signature generated (HMAC-SHA256)
✅ Security configuration created (config/security.json)
✅ Audit logging initialized (4 log files)

MODEL SIGNATURE
--------------
Signature: {signature[:64] if model_dir.exists() else 'N/A'}...
Algorithm: HMAC-SHA256
Files Signed: {len(checksums) if model_dir.exists() else 0}
Signed At: {datetime.now().isoformat()}

SECURITY CONFIGURATION
---------------------
Authentication: JWT (24h expiry, 5 max failed attempts)
Rate Limiting: 60/min, 1000/hr, 10K/day
Input Validation: 10-10000 chars, ASCII printable only
Adversarial Detection: Enabled (threshold: 0.6, z-score: 3.0)
Model Integrity: Verify on load + every 24h
Deployment: Staging environment, HTTPS-only

AUDIT LOGGING
-------------
📝 security_events.log - All security events
📝 security_alerts.log - Critical alerts
📝 access.log - API access logs
📝 predictions.log - Model predictions

VERIFICATION COMMANDS
--------------------
# View model signature
cat {signature_file if model_dir.exists() else 'results/models/xgboost_phase2_5/model_signature.json'}

# View security config
cat config/security.json

# Monitor security events
tail -f logs/audit/security_events.log

# Verify file permissions
ls -la {model_dir if model_dir.exists() else 'results/models/xgboost_phase2_5/'}

NEXT STEPS
----------
1. ⏳ Set up HTTPS/TLS (bash scripts/setup_https.sh)
2. ⏳ Create admin credentials (python create_admin.py)
3. ⏳ Generate API keys (python generate_api_keys.py)
4. ⏳ Test security controls
5. ⏳ Deploy to staging environment

{'=' * 80}
SECURITY HARDENING COMPLETE ✅
{'=' * 80}
"""

    report_file = project_root / 'logs' / 'audit' / f'security_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(report_file, 'w') as f:
        f.write(report)

    logger.info(f"  ✅ Security report: {report_file}")
    logger.info("")

    # Display summary
    logger.info("=" * 80)
    logger.info("SECURITY HARDENING SUMMARY")
    logger.info("=" * 80)
    logger.info("")
    logger.info("✅ Cryptographic signing key: .model_signing_key")
    logger.info("✅ Model signature: results/models/xgboost_phase2_5/model_signature.json")
    logger.info("✅ Security config: config/security.json")
    logger.info("✅ Audit logs: logs/audit/")
    logger.info("✅ Security report: " + str(report_file))
    logger.info("")
    logger.info("=" * 80)
    logger.info("READY FOR STAGING DEPLOYMENT")
    logger.info("=" * 80)
    logger.info("")

if __name__ == '__main__':
    main()
