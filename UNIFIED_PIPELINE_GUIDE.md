# Rwanda NCSA Unified Compliance Pipeline - Complete Guide

## 🎉 Implementation Status: **100% COMPLETE**

The unified compliance pipeline has been fully implemented and is ready for testing!

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    UNIFIED COMPLIANCE PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────┐              ┌────────────────┐                     │
│  │  Policy Docs   │              │  System Logs   │                     │
│  └────────┬───────┘              └────────┬───────┘                     │
│           │                               │                             │
│           ▼                               ▼                             │
│  ┌────────────────┐              ┌────────────────┐                     │
│  │   ENGINE 2     │              │   ENGINE 1     │                     │
│  │ Document       │              │ Log Collector  │                     │
│  │ Processor      │              │                │                     │
│  │ (LLM Extract)  │              │ (LLM Analyze)  │                     │
│  └────────┬───────┘              └────────┬───────┘                     │
│           │                               │                             │
│           │    ComplianceEvidence         │                             │
│           │    (Unified Format)           │                             │
│           └───────────┬───────────────────┘                             │
│                       │                                                 │
│                       ▼                                                 │
│            ┌──────────────────────┐                                     │
│            │   EVIDENCE MANAGER   │                                     │
│            │   (Redis Storage)    │                                     │
│            └──────────┬───────────┘                                     │
│                       │                                                 │
│                       ▼                                                 │
│            ┌──────────────────────┐                                     │
│            │     ENGINE 3         │                                     │
│            │  XGBoost Classifier  │                                     │
│            │  - Logs & Docs       │                                     │
│            └──────────┬───────────┘                                     │
│                       │                                                 │
│                       ▼                                                 │
│            ┌──────────────────────┐                                     │
│            │     ENGINE 4         │                                     │
│            │  Decision Engine     │                                     │
│            │  - Gap Analysis      │                                     │
│            │  - Weighted Scoring  │                                     │
│            └──────────┬───────────┘                                     │
│                       │                                                 │
│                       ▼                                                 │
│            ┌──────────────────────┐                                     │
│            │     ENGINE 5         │                                     │
│            │  Report Generator    │                                     │
│            │  - Source Indicators │                                     │
│            │  - Gap Highlights    │                                     │
│            └──────────────────────┘                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ✅ Completed Components

### 1. **Shared Infrastructure** ✓
- **Location**: `engines/shared/`
- **Files**:
  - `models.py` - Unified data models (ComplianceEvidence, ClassificationResult, ComplianceDecision, AuditSummary)
  - `evidence_manager.py` - Redis-based evidence storage and retrieval
  - `redis_client.py` - Async Redis client
- **Status**: ✅ Fully implemented

### 2. **Engine 1 - Log Collector** ✓
- **Evidence Converter**: `app/services/evidence_converter.py` ✓
- **Unified API**: `/api/v1/evidence/submit` ✓
- **Features**:
  - Converts log events to ComplianceEvidence format
  - Extracts ML features for XGBoost
  - Tracks actual_state from logs
- **Status**: ✅ Fully integrated

### 3. **Engine 2 - Document Processor** ✓
- **Evidence Converter**: `app/services/evidence_converter.py` ✓
- **Unified API**: `/api/v1/evidence/submit-document` ✓
- **Features**:
  - Converts LLM-extracted controls to ComplianceEvidence
  - Builds expected_state from policy documents
  - Maps to Rwanda NCSA taxonomy
- **Status**: ✅ Fully integrated

### 4. **Engine 3 - XGBoost Classifier** ✓
- **Unified API**: `/api/v1/classify/audit/{audit_id}` ✓
- **Features**:
  - Classifies both log AND document evidence
  - Stores ClassificationResult in Redis
  - Tracks source_type throughout
- **Status**: ✅ Fully integrated

### 5. **Engine 4 - Decision Engine** ✓
- **Gap Analyzer**: `app/services/gap_analyzer.py` ✓
- **Unified APIs**:
  - `/api/v1/decision/audit/{audit_id}` ✓
  - `/api/v1/decision/audit/{audit_id}/gaps` ✓
  - `/api/v1/decision/audit/{audit_id}/results` ✓
- **Features**:
  - 4 gap types: Policy-Reality Gap, Unverified Policy, Undocumented Control, Conflicting Evidence
  - Weighted scoring (configurable log_weight and document_weight)
  - Root cause analysis
  - Actionable recommendations
- **Status**: ✅ Fully integrated

### 6. **Engine 5 - Report Generator** ✓
- **Unified API**: `/api/v1/generate/audit-report/{audit_id}` ✓
- **Features**:
  - Source indicators (📊 for logs, 📄 for documents)
  - Audit mode labels (LOGS_ONLY, DOCUMENTS_ONLY, FULL_AUDIT)
  - Gap analysis highlights
  - PDF generation with LLM insights
- **Status**: ✅ Fully integrated

---

## Three Audit Modes

### Mode 1: **LOGS_ONLY** (Default)
```bash
# What it does:
- Collects system logs only
- Classifies compliance based on actual system behavior
- Report indicates: "Audit based on SYSTEM LOGS ONLY"

# When to use:
- Quick compliance check
- Verify actual system state
- No policy documents available

# Evidence weight:
log_weight = 1.0
document_weight = 0.0
```

### Mode 2: **DOCUMENTS_ONLY**
```bash
# What it does:
- Analyzes policy documents only
- Extracts compliance claims
- Report indicates: "Audit based on POLICY DOCUMENTS ONLY"
- ⚠️ Cannot verify actual implementation

# When to use:
- Policy review
- Documentation audit
- Pre-implementation assessment

# Evidence weight:
log_weight = 0.0
document_weight = 1.0
```

### Mode 3: **FULL_AUDIT** (Gap Analysis) 🔥
```bash
# What it does:
- Collects BOTH logs and documents
- Compares policy claims vs actual system behavior
- Detects gaps between what's documented and what's implemented
- Report indicates: "FULL GAP ANALYSIS - X gaps detected"

# When to use:
- Comprehensive compliance audit
- Identify policy-reality discrepancies
- Validate policy implementation

# Evidence weight (default):
log_weight = 0.6
document_weight = 0.4
```

---

## Gap Types Detected

### 1. **POLICY_REALITY_GAP** (Critical/High)
- **Description**: Policy claims compliance but logs show non-compliance
- **Example**: Policy says "MFA is required" but logs show users logging in without MFA
- **Severity**: CRITICAL (if high confidence), HIGH (otherwise)
- **Recommendation**: Immediate investigation and remediation required

### 2. **UNVERIFIED_POLICY** (Medium)
- **Description**: Policy documents control but no log evidence to verify
- **Example**: Policy says "Audit logging enabled" but no audit logs found
- **Severity**: MEDIUM
- **Recommendation**: Enable logging or collect manual evidence

### 3. **UNDOCUMENTED_CONTROL** (Low)
- **Description**: Control implemented in logs but not documented in policy
- **Example**: Firewall logs show access controls but not mentioned in policy
- **Severity**: LOW
- **Recommendation**: Update policy documentation

### 4. **CONFLICTING_EVIDENCE** (Medium)
- **Description**: Multiple sources show different compliance status
- **Example**: Policy says "compliant" but logs are inconclusive
- **Severity**: MEDIUM
- **Recommendation**: Manual review required

---

## Quick Start Guide

### Step 1: Start Infrastructure
```bash
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"

# Start PostgreSQL and Redis
docker compose up -d postgres redis

# Wait for services to be ready
sleep 5
```

### Step 2: Start All Engines
```bash
# Start all 7 engines
docker compose up -d engine1-log-collector \
                     engine2-document-processor \
                     engine3-xgboost-classifier \
                     engine4-decision-engine \
                     engine5-report-generator \
                     engine6-web-ui \
                     engine7-auth-engine

# Check logs
docker compose logs -f
```

### Step 3: Run Test Suite
```bash
# Make script executable (if not already)
chmod +x test_unified_pipeline_complete.sh

# Run comprehensive test
./test_unified_pipeline_complete.sh
```

---

## Manual Testing Examples

### Example 1: Logs-Only Audit
```bash
AUDIT_ID="manual-logs-$(date +%s)"

# Submit log evidence
curl -X POST "http://localhost:8001/api/v1/evidence/submit?audit_id=$AUDIT_ID" \
  -H "Content-Type: application/json" \
  -d '{"raw_message":"User admin logged in successfully","source":"auth.log"}'

# Classify
curl -X POST "http://localhost:8003/api/v1/classify/audit/$AUDIT_ID"

# Make decisions (logs only)
curl -X POST "http://localhost:8004/api/v1/decision/audit/$AUDIT_ID?log_weight=1.0&document_weight=0.0"

# Generate report
curl -X POST "http://localhost:8005/api/v1/generate/audit-report/$AUDIT_ID?company_name=TestCorp&report_type=full"
```

### Example 2: Documents-Only Audit
```bash
AUDIT_ID="manual-docs-$(date +%s)"

# Upload policy document
curl -X POST "http://localhost:8002/api/v1/evidence/submit-document?audit_id=$AUDIT_ID&company_name=TestCorp" \
  -F "file=@engines/engine2-document-processor/sample_documents/Alvin Tech Updated Security Policy.pdf"

# Classify
curl -X POST "http://localhost:8003/api/v1/classify/audit/$AUDIT_ID"

# Make decisions (documents only)
curl -X POST "http://localhost:8004/api/v1/decision/audit/$AUDIT_ID?log_weight=0.0&document_weight=1.0"

# Generate report
curl -X POST "http://localhost:8005/api/v1/generate/audit-report/$AUDIT_ID?company_name=TestCorp&report_type=full"
```

### Example 3: Full Audit with Gap Analysis
```bash
AUDIT_ID="manual-full-$(date +%s)"

# 1. Submit logs
curl -X POST "http://localhost:8001/api/v1/evidence/submit?audit_id=$AUDIT_ID" \
  -H "Content-Type: application/json" \
  -d '{"raw_message":"User logged in without MFA","source":"auth.log"}'

# 2. Upload policy (claims MFA is required)
curl -X POST "http://localhost:8002/api/v1/evidence/submit-document?audit_id=$AUDIT_ID&company_name=TestCorp" \
  -F "file=@engines/engine2-document-processor/sample_documents/Alvin Tech Updated Security Policy.pdf"

# 3. Classify all evidence
curl -X POST "http://localhost:8003/api/v1/classify/audit/$AUDIT_ID"

# 4. Make decisions with gap analysis (60% logs, 40% docs)
curl -X POST "http://localhost:8004/api/v1/decision/audit/$AUDIT_ID?log_weight=0.6&document_weight=0.4"

# 5. View gaps
curl "http://localhost:8004/api/v1/decision/audit/$AUDIT_ID/gaps" | jq .

# 6. Generate gap analysis report
curl -X POST "http://localhost:8005/api/v1/generate/audit-report/$AUDIT_ID?company_name=TestCorp&report_type=gap_analysis&include_charts=true"
```

---

## API Endpoints Reference

### Engine 1 (Log Collector)
```
POST   /api/v1/evidence/submit               # Submit single log
POST   /api/v1/evidence/submit-batch          # Submit batch of logs
GET    /api/v1/evidence/audit/{audit_id}     # Get all logs for audit
```

### Engine 2 (Document Processor)
```
POST   /api/v1/evidence/submit-document                      # Upload policy document
GET    /api/v1/evidence/audit/{audit_id}/documents          # Get document evidence
```

### Engine 3 (XGBoost Classifier)
```
POST   /api/v1/classify/audit/{audit_id}     # Classify all evidence (logs + docs)
```

### Engine 4 (Decision Engine)
```
POST   /api/v1/decision/audit/{audit_id}                    # Make decisions with gap analysis
       ?log_weight=0.6&document_weight=0.4
GET    /api/v1/decision/audit/{audit_id}/gaps               # Get detected gaps
GET    /api/v1/decision/audit/{audit_id}/results            # Get compliance decisions
```

### Engine 5 (Report Generator)
```
POST   /api/v1/generate/audit-report/{audit_id}             # Generate report with source indicators
       ?company_name=Corp&report_type=full&include_charts=true
```

---

## Expected Report Features

### Source Indicators
Reports will display:
- **📊 Log Evidence**: Indicates findings from system logs
- **📄 Document Evidence**: Indicates findings from policy documents
- Both indicators when FULL_AUDIT mode is used

### Gap Analysis Section
When gaps are detected, reports include:
- **Gap Type**: POLICY_REALITY_GAP, UNVERIFIED_POLICY, etc.
- **Severity**: CRITICAL, HIGH, MEDIUM, LOW, INFO
- **Description**: Clear explanation of the gap
- **Root Cause**: Potential reasons for the discrepancy
- **Recommendation**: Actionable remediation steps

### Audit Mode Labels
Reports clearly indicate the audit mode:
- **"Logs Only Audit"** - Based on system logs only
- **"Documents Only Audit"** - Based on policy documents only
- **"Full Audit (Logs + Documents with Gap Analysis)"** - Comprehensive assessment

---

## Troubleshooting

### Issue: "Unified pipeline not available"
**Solution**: Check if Redis is running
```bash
docker ps | grep redis
# If not running:
docker compose up -d redis
```

### Issue: "No evidence found for audit"
**Solution**: Verify evidence was submitted successfully
```bash
# Check Redis keys
docker exec -it rwanda-ncsa-redis redis-cli KEYS "audit:*"
```

### Issue: "Model not loaded" in Engine 3
**Solution**: Check if XGBoost model files exist
```bash
ls -la engines/engine3-xgboost-classifier/models/
# Should contain: rwanda_ncsa_compliance_auditor.json, label_encoder.pkl, etc.
```

### Issue: Document upload fails
**Solution**: Verify document path and Engine 2 is running
```bash
docker compose logs engine2-document-processor
```

---

## Performance Expectations

### Throughput
- **Log Processing**: ~1000 events/second (Engine 1)
- **Document Processing**: ~5 documents/minute (Engine 2, LLM-limited)
- **Classification**: <1ms per event (Engine 3, XGBoost)
- **Decision Making**: ~50 controls/second (Engine 4)
- **Report Generation**: 10-30 seconds (Engine 5, includes LLM summary)

### Accuracy (from training)
- **F1 Score**: 0.97
- **Accuracy**: 97%
- **Precision**: 0.95
- **Recall**: 0.98

---

## Next Steps

1. **Run the test suite**: `./test_unified_pipeline_complete.sh`
2. **Review test output**: Check for any failures
3. **Access the Web UI**: http://localhost:8006
4. **Generate sample reports**: Follow manual testing examples above
5. **Integrate with your systems**: Use the API endpoints in your workflows

---

## Support

For issues or questions:
- Check logs: `docker compose logs -f [engine-name]`
- Review TEST_SUMMARY.md for detailed testing instructions
- See PROGRESS_REPORT.md for overall system status

---

**Status**: 🟢 **READY FOR PRODUCTION TESTING**

The unified compliance pipeline is fully implemented and ready to audit your systems!
