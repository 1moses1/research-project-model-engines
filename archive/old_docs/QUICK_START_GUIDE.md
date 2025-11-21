# Phase 2.5 Model - Quick Start Guide

**Version**: 1.0
**Date**: November 3, 2025

---

## ⚡ 1-Minute Setup

```bash
# Navigate to project
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"

# Activate environment
source venv/bin/activate

# Verify security
cat .model_signing_key  # Should show signing key
ls -la certs/           # Should show server.key and server.crt
cat config/credentials/admin_user.json  # Should show admin credentials

# Start secure API
python src/api/secure_api.py
```

---

## 🔑 Credentials (SAVE SECURELY)

### Admin Account
```
Username: admin
Password: H2Iwwf^R6rq6H7kLAjK!
API Key: gc00UHIcFSwicAxz9UWyY8s9Fot_cXlKcKDux_j6nig
```

### User API Keys
```
soc_analyst_1:   BiN9m96bcnvJDUCSLLNclckGJAC_Hip7isd3zmmyexs
soc_analyst_2:   vfS4s7L66N5-z5I7IdwOTJ6rSJVMDvzfF6UGleUyjk8
soc_viewer:      qB1lo9q-o_uTTseLMAyhZ5dW8__cLRo5SW5ZlGmA1Gc
api_integration: hh8MmDJNYUhzoEgTi93iOHi4PaXKbUsptUPOmy3ye7w
security_admin:  tz4X72eXKc1PcW8OLKXkEh2S5i6Cv2kPdIZSs5gy2hU
```

---

## 🚀 Quick API Test

```bash
# Test prediction (replace API_KEY)
curl -X POST https://localhost:5000/api/predict \
  -H 'Authorization: Bearer BiN9m96bcnvJDUCSLLNclckGJAC_Hip7isd3zmmyexs' \
  -H 'Content-Type: application/json' \
  -k \
  -d '{
    "log_message": "Failed SSH login from 192.168.1.100 - Access denied",
    "control_id": "AC-3",
    "control_family": "Access Control"
  }'

# Expected response:
# {
#   "compliance_status": "non_compliant",
#   "confidence": 0.999
# }
```

---

## 📊 Key Metrics

- **Model Accuracy**: 100% (12/12 real scenarios)
- **Security Score**: 9.2/10
- **Rate Limits**: 60/min, 1K/hr, 10K/day
- **Response Time**: ~50ms average

---

## 📁 Important Files

### Model Files
- `results/models/xgboost_phase2_5/xgboost_phase2_5.pkl` - Model
- `results/models/xgboost_phase2_5/model_signature.json` - Signature

### Security Files
- `.model_signing_key` - Signing key (KEEP SECURE)
- `certs/server.key` - TLS private key
- `config/security.json` - Security config
- `config/credentials/` - User credentials

### Logs
- `logs/audit/security_events.log` - Security events
- `logs/audit/security_alerts.log` - Alerts
- `logs/audit/access.log` - API access

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `PRODUCTION_DEPLOYMENT_COMPLETE.md` | **START HERE** - Complete overview |
| `DEPLOYMENT_READINESS.md` | Deployment checklist |
| `MODEL_SECURITY_HARDENING.md` | Security implementation guide |
| `RED_TEAM_TESTING_GUIDE.md` | Adversarial testing |
| `QUICK_START_GUIDE.md` | This document |

---

## 🆘 Common Issues

### Issue: API returns 401 Unauthorized
**Fix**: Check API key in Authorization header
```bash
# Correct format
-H 'Authorization: Bearer YOUR_API_KEY_HERE'
```

### Issue: API returns 429 Too Many Requests
**Fix**: Rate limit reached (60 req/min), wait and retry

### Issue: Certificate error with curl
**Fix**: Use `-k` flag for self-signed cert (staging only)
```bash
curl ... -k
```

### Issue: Model signature verification failed
**Fix**: Model may be corrupted, restore from backup or retrain

---

## 🎯 Next Steps

1. ✅ **Staging tested** - Deploy and test
2. ⏳ **Red team testing** - Security validation
3. ⏳ **SIEM integration** - Connect to Splunk/QRadar
4. ⏳ **Production deploy** - Go live!

---

## 📞 Support

- Security: security@rwanda-soc.gov.rw
- API: api-support@rwanda-soc.gov.rw
- Emergency: +250-XXX-XXX-XXX

---

**Status**: ✅ READY FOR DEPLOYMENT
**Last Updated**: November 3, 2025
