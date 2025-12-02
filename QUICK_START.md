# Rwanda NCSA Unified Pipeline - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Start the System (30 seconds)
```bash
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"
docker compose up -d
```

Wait for all services to start (watch logs):
```bash
docker compose logs -f
# Press Ctrl+C when you see "✅ ENGINE X READY" for all engines
```

### Step 2: Run the Test Suite (2 minutes)
```bash
./test_unified_pipeline_complete.sh
```

### Step 3: Check Results
- ✅ All tests pass? **You're ready to go!**
- ❌ Some tests fail? See troubleshooting below

---

## 📊 Three Ways to Audit

### Option 1: Logs Only (Quick Check)
```bash
AUDIT_ID="logs-$(date +%s)"

curl -X POST "http://localhost:8001/api/v1/evidence/submit?audit_id=$AUDIT_ID" \
  -H "Content-Type: application/json" \
  -d '{"raw_message":"User admin logged in successfully","source":"auth.log"}'

curl -X POST "http://localhost:8003/api/v1/classify/audit/$AUDIT_ID"
curl -X POST "http://localhost:8004/api/v1/decision/audit/$AUDIT_ID?log_weight=1.0&document_weight=0.0"
curl -X POST "http://localhost:8005/api/v1/generate/audit-report/$AUDIT_ID?company_name=MyCompany"
```

### Option 2: Documents Only (Policy Review)
```bash
AUDIT_ID="docs-$(date +%s)"

curl -X POST "http://localhost:8002/api/v1/evidence/submit-document?audit_id=$AUDIT_ID&company_name=MyCompany" \
  -F "file=@path/to/policy.pdf"

curl -X POST "http://localhost:8003/api/v1/classify/audit/$AUDIT_ID"
curl -X POST "http://localhost:8004/api/v1/decision/audit/$AUDIT_ID?log_weight=0.0&document_weight=1.0"
curl -X POST "http://localhost:8005/api/v1/generate/audit-report/$AUDIT_ID?company_name=MyCompany"
```

### Option 3: Full Audit (Gap Analysis) 🔥
```bash
AUDIT_ID="full-$(date +%s)"

# Submit logs
curl -X POST "http://localhost:8001/api/v1/evidence/submit?audit_id=$AUDIT_ID" \
  -d '{"raw_message":"User logged in","source":"auth.log"}'

# Submit policy document
curl -X POST "http://localhost:8002/api/v1/evidence/submit-document?audit_id=$AUDIT_ID&company_name=MyCompany" \
  -F "file=@path/to/policy.pdf"

# Run full pipeline with gap analysis
curl -X POST "http://localhost:8003/api/v1/classify/audit/$AUDIT_ID"
curl -X POST "http://localhost:8004/api/v1/decision/audit/$AUDIT_ID?log_weight=0.6&document_weight=0.4"
curl "http://localhost:8004/api/v1/decision/audit/$AUDIT_ID/gaps" | jq .
curl -X POST "http://localhost:8005/api/v1/generate/audit-report/$AUDIT_ID?company_name=MyCompany&report_type=gap_analysis"
```

---

## 🌐 Access Points

- **Web UI**: http://localhost:8006
- **Engine 1 (Logs)**: http://localhost:8001
- **Engine 2 (Docs)**: http://localhost:8002
- **Engine 3 (ML)**: http://localhost:8003
- **Engine 4 (Decisions)**: http://localhost:8004
- **Engine 5 (Reports)**: http://localhost:8005
- **Engine 7 (Auth)**: http://localhost:8007

---

## 🔍 Check System Status

### All Services Healthy?
```bash
curl -s http://localhost:8001/health | jq .
curl -s http://localhost:8002/health | jq .
curl -s http://localhost:8003/health | jq .
curl -s http://localhost:8004/health | jq .
curl -s http://localhost:8005/health | jq .
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific engine
docker compose logs -f engine3-xgboost-classifier
```

### Check Running Containers
```bash
docker ps
# Should see: postgres, redis, engine1-7
```

---

## 🛠️ Common Issues

### Issue: "Connection refused"
**Solution**: Start services
```bash
docker compose up -d
# Wait 30 seconds for startup
```

### Issue: "Model not loaded"
**Solution**: Check if model files exist
```bash
ls engines/engine3-xgboost-classifier/models/
# Should contain: rwanda_ncsa_compliance_auditor.json, etc.
```

### Issue: "Redis connection failed"
**Solution**: Restart Redis
```bash
docker compose restart redis
```

### Issue: "Unified pipeline not available"
**Solution**: Check if shared module is accessible
```bash
docker compose logs engine4-decision-engine | grep "Unified Pipeline"
# Should see: "✅ Unified Pipeline: Active"
```

---

## 📖 Full Documentation

- **Complete Guide**: UNIFIED_PIPELINE_GUIDE.md
- **Implementation Details**: UNIFIED_PIPELINE_COMPLETE.md
- **Architecture**: UNIFIED_PIPELINE_IMPLEMENTATION.md
- **Test Guide**: TEST_SUMMARY.md

---

## 🎯 What You Can Do

### ✅ Logs-Only Audits
- Real-time system compliance verification
- Audit actual system behavior
- No policy documents needed

### ✅ Documents-Only Audits
- Policy review and assessment
- Documentation completeness check
- Pre-implementation validation

### ✅ Full Audits with Gap Analysis
- Compare policy claims vs actual implementation
- Detect 4 types of compliance gaps
- Get actionable remediation recommendations

---

## 🚦 Next Steps

1. ✅ Run test suite to validate installation
2. ✅ Try each audit mode (logs, docs, full)
3. ✅ Access web UI to monitor system
4. ✅ Review sample reports generated
5. ✅ Integrate with your CI/CD pipeline

---

## 💡 Pro Tips

### Tip 1: Use JQ for Pretty Output
```bash
curl -s "http://localhost:8004/api/v1/decision/audit/$AUDIT_ID/gaps" | jq .
```

### Tip 2: Save Audit IDs
```bash
AUDIT_ID="my-audit-$(date +%s)"
echo $AUDIT_ID > last_audit_id.txt
```

### Tip 3: Batch Upload Documents
```bash
for doc in policies/*.pdf; do
    curl -X POST "http://localhost:8002/api/v1/evidence/submit-document?audit_id=$AUDIT_ID" -F "file=@$doc"
done
```

### Tip 4: Monitor Real-Time
```bash
watch -n 2 "curl -s http://localhost:8006/api/v3/system-health | jq ."
```

---

## 📞 Need Help?

1. **Check logs**: `docker compose logs -f`
2. **Review documentation**: See files listed above
3. **Run health checks**: Use commands in "Check System Status" section
4. **Restart services**: `docker compose restart`

---

**Ready?** Run the test suite now:
```bash
./test_unified_pipeline_complete.sh
```

🎉 **Happy Auditing!** 🎉
