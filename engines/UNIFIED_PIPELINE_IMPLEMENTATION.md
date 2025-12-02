# Unified Compliance Pipeline Implementation Guide

## Executive Summary

This document describes the complete architectural refactoring of the Rwanda NCSA Compliance Auditor to support a **unified evidence model** that enables:

1. **Dual-source auditing** (logs AND documents)
2. **Single-source flexibility** (logs only OR documents only)
3. **Gap analysis** (compare policy claims vs actual system behavior)
4. **Source tracking** throughout the pipeline
5. **Proper data flow** through all engines

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    UNIFIED COMPLIANCE PIPELINE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐          ┌─────────────────────┐                   │
│  │   Policy Documents  │          │    System Logs      │                   │
│  └──────────┬──────────┘          └──────────┬──────────┘                   │
│             │                                 │                              │
│             ▼                                 ▼                              │
│  ┌─────────────────────┐          ┌─────────────────────┐                   │
│  │     ENGINE 2        │          │     ENGINE 1        │                   │
│  │ Document Processor  │          │   Log Collector     │                   │
│  │ (GPT-4 LLM)        │          │ (GPT-4 LLM)         │                   │
│  └──────────┬──────────┘          └──────────┬──────────┘                   │
│             │                                 │                              │
│             │    ┌─────────────────────┐     │                              │
│             │    │ ComplianceEvidence  │     │                              │
│             └───►│   (Unified Model)   │◄────┘                              │
│                  └──────────┬──────────┘                                    │
│                             │                                               │
│                             ▼                                               │
│              ┌──────────────────────────────┐                               │
│              │     EVIDENCE MANAGER         │                               │
│              │    (Redis Caching)           │                               │
│              │  - Store by audit_id         │                               │
│              │  - Index by control_id       │                               │
│              │  - Index by source_type      │                               │
│              └──────────────┬───────────────┘                               │
│                             │                                               │
│                             ▼                                               │
│              ┌──────────────────────────────┐                               │
│              │        ENGINE 3              │                               │
│              │   XGBoost Classifier         │                               │
│              │  - Accepts unified format    │                               │
│              │  - Tracks source_type        │                               │
│              │  - Returns classification    │                               │
│              └──────────────┬───────────────┘                               │
│                             │                                               │
│                             ▼                                               │
│              ┌──────────────────────────────┐                               │
│              │        ENGINE 4              │                               │
│              │    Decision Engine           │                               │
│              │  - Compare log vs document   │                               │
│              │  - Gap analysis              │                               │
│              │  - Weighted scoring          │                               │
│              │  - Final compliance status   │                               │
│              └──────────────┬───────────────┘                               │
│                             │                                               │
│                             ▼                                               │
│              ┌──────────────────────────────┐                               │
│              │        ENGINE 5              │                               │
│              │   Report Generator           │                               │
│              │  - Show sources used         │                               │
│              │  - Highlight gaps            │                               │
│              │  - Evidence from both        │                               │
│              └──────────────────────────────┘                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Files Created/Modified

### NEW FILES (Shared Infrastructure)

| File | Status | Purpose |
|------|--------|---------|
| `engines/shared/models.py` | ✅ CREATED | Unified data models (ComplianceEvidence, ClassificationResult, ComplianceDecision, AuditConfig, AuditSummary) |
| `engines/shared/evidence_manager.py` | ✅ CREATED | Redis-based evidence storage, indexing, and retrieval |
| `engines/shared/__init__.py` | ✅ UPDATED | Export all new models and utilities |

### ENGINE 1 (Log Collector)

| File | Status | Purpose |
|------|--------|---------|
| `engine1-log-collector/app/services/evidence_converter.py` | ✅ CREATED | Convert normalized log events to ComplianceEvidence |
| `engine1-log-collector/app/main.py` | ⏳ PENDING | Add evidence output endpoint, integrate Redis |

### ENGINE 2 (Document Processor)

| File | Status | Purpose |
|------|--------|---------|
| `engine2-document-processor/app/services/evidence_converter.py` | ⏳ PENDING | Convert extracted controls to ComplianceEvidence |
| `engine2-document-processor/app/main.py` | ⏳ PENDING | Add evidence output endpoint, use semantic matching |

### ENGINE 3 (XGBoost Classifier)

| File | Status | Purpose |
|------|--------|---------|
| `engine3-xgboost-classifier/app/main.py` | ⏳ PENDING | Accept unified format, track source_type |

### ENGINE 4 (Decision Engine)

| File | Status | Purpose |
|------|--------|---------|
| `engine4-decision-engine/app/services/gap_analyzer.py` | ⏳ PENDING | Compare log vs document evidence |
| `engine4-decision-engine/app/services/weighted_scorer.py` | ⏳ PENDING | Apply configurable weights |
| `engine4-decision-engine/app/main.py` | ⏳ PENDING | Accept both sources, output ComplianceDecision |

### ENGINE 5 (Report Generator)

| File | Status | Purpose |
|------|--------|---------|
| `engine5-report-generator/app/services/source_indicator.py` | ⏳ PENDING | Generate source descriptions for reports |
| `engine5-report-generator/app/main.py` | ⏳ PENDING | Include source info in reports |

---

## Key Data Models

### 1. ComplianceEvidence (Unified Evidence)

```python
class ComplianceEvidence(BaseModel):
    evidence_id: str          # Unique ID
    audit_id: str             # Parent audit
    control_id: str           # Rwanda NCSA control (e.g., "AC-2")
    control_name: str         # Human-readable name
    control_family: str       # Control family

    source_type: EvidenceSourceType  # "log" | "document"
    source_file: str          # Original file/system

    evidence_text: str        # Actual evidence
    evidence_summary: str     # Brief summary
    expected_state: str       # What compliance looks like (from policy)
    actual_state: str         # What we found (from logs)

    timestamp: datetime
    confidence: float         # 0.0 - 1.0
    features: Dict[str, Any]  # ML features
```

### 2. ClassificationResult (Engine 3 Output)

```python
class ClassificationResult(BaseModel):
    evidence_id: str
    audit_id: str
    control_id: str
    source_type: EvidenceSourceType

    prediction: ComplianceStatus    # compliant/non_compliant
    confidence: float
    model_version: str
```

### 3. ComplianceDecision (Engine 4 Output)

```python
class ComplianceDecision(BaseModel):
    decision_id: str
    audit_id: str
    control_id: str

    final_status: ComplianceStatus
    severity: SeverityLevel
    risk_score: float

    # Source tracking
    has_log_evidence: bool
    has_document_evidence: bool
    audit_mode: AuditMode       # "logs_only" | "documents_only" | "full_audit"

    # Log findings
    log_status: ComplianceStatus
    log_confidence: float
    log_summary: str

    # Document findings
    document_status: ComplianceStatus
    document_confidence: float
    policy_requirement: str

    # Gap analysis
    gap_detected: bool
    gap_description: str

    weighted_confidence: float
    decision_rationale: str
```

### 4. AuditConfig (Audit Settings)

```python
class AuditConfig(BaseModel):
    audit_id: str
    mode: AuditMode             # logs_only | documents_only | full_audit

    include_logs: bool = True
    include_documents: bool = False

    # Weighting for full_audit mode
    log_weight: float = 0.6
    document_weight: float = 0.4

    enable_gap_analysis: bool = True
```

---

## Audit Modes

### 1. LOGS_ONLY Mode (Default)

```
Input: System logs only
Process: Engine 1 → Engine 3 → Engine 4 → Engine 5
Report indicates: "Audit based on SYSTEM LOGS ONLY"
```

### 2. DOCUMENTS_ONLY Mode

```
Input: Policy documents only
Process: Engine 2 → Engine 3 → Engine 4 → Engine 5
Report indicates: "Audit based on POLICY DOCUMENTS ONLY"
```

### 3. FULL_AUDIT Mode (Gap Analysis)

```
Input: Both logs and documents
Process:
  - Engine 1 outputs log evidence
  - Engine 2 outputs document evidence
  - Both feed to Engine 3
  - Engine 4 compares and detects gaps
  - Engine 5 highlights gaps in report

Report indicates:
  "FULL GAP ANALYSIS - X gaps detected between policy and reality"
```

---

## Gap Analysis Logic (Engine 4)

```python
def analyze_gap(log_evidence, doc_evidence, control_id):
    """
    Detect gaps between what policy says and what logs show.
    """
    gap = {
        "detected": False,
        "description": ""
    }

    # Case 1: Policy says compliant, logs say non-compliant
    if doc_evidence.status == COMPLIANT and log_evidence.status == NON_COMPLIANT:
        gap["detected"] = True
        gap["description"] = (
            f"GAP: Policy claims {control_id} is implemented, "
            f"but system logs show non-compliance. "
            f"Policy: '{doc_evidence.policy_requirement}' | "
            f"Reality: '{log_evidence.actual_state}'"
        )

    # Case 2: Control in policy but no log evidence
    elif doc_evidence and not log_evidence:
        gap["detected"] = True
        gap["description"] = (
            f"GAP: {control_id} defined in policy but no log evidence found. "
            f"Cannot verify implementation."
        )

    # Case 3: Log evidence but not in policy (optional control)
    elif log_evidence and not doc_evidence:
        gap["detected"] = False
        gap["description"] = (
            f"NOTE: {control_id} found in logs but not required by policy."
        )

    return gap
```

---

## Weighted Scoring Logic (Engine 4)

```python
def weighted_decision(
    log_status: ComplianceStatus,
    log_confidence: float,
    doc_status: ComplianceStatus,
    doc_confidence: float,
    config: AuditConfig
) -> ComplianceDecision:
    """
    Calculate weighted compliance decision.
    """
    log_weight = config.log_weight      # Default: 0.6
    doc_weight = config.document_weight  # Default: 0.4

    # Convert status to score
    log_score = 1.0 if log_status == COMPLIANT else 0.5 if log_status == PARTIAL else 0.0
    doc_score = 1.0 if doc_status == COMPLIANT else 0.5 if doc_status == PARTIAL else 0.0

    # Weighted score
    if config.mode == AuditMode.LOGS_ONLY:
        final_score = log_score
        final_confidence = log_confidence
    elif config.mode == AuditMode.DOCUMENTS_ONLY:
        final_score = doc_score
        final_confidence = doc_confidence
    else:  # FULL_AUDIT
        final_score = (log_score * log_weight) + (doc_score * doc_weight)
        final_confidence = (log_confidence * log_weight) + (doc_confidence * doc_weight)

    # Determine final status
    if final_score >= 0.9:
        final_status = COMPLIANT
    elif final_score >= 0.5:
        final_status = PARTIAL
    else:
        final_status = NON_COMPLIANT

    return ComplianceDecision(
        final_status=final_status,
        weighted_confidence=final_confidence,
        decision_rationale=f"Score: {final_score:.2f} (log: {log_weight*100}%, doc: {doc_weight*100}%)"
    )
```

---

## Report Source Indicator

The report MUST clearly indicate which sources were used:

```python
def generate_source_indicator(summary: AuditSummary) -> str:
    """Generate source indicator for report header."""

    if summary.audit_mode == AuditMode.LOGS_ONLY:
        return """
        ╔═══════════════════════════════════════════════════════════════╗
        ║  AUDIT SOURCE: SYSTEM LOGS ONLY                               ║
        ║  ─────────────────────────────────────────────────────────── ║
        ║  This audit analyzed {log_count} log entries from {target}.   ║
        ║  No policy documents were included in this assessment.        ║
        ║                                                               ║
        ║  ⚠️  For comprehensive compliance verification, consider      ║
        ║      including policy documents for gap analysis.             ║
        ╚═══════════════════════════════════════════════════════════════╝
        """.format(log_count=summary.log_evidence_count, target=summary.target_host)

    elif summary.audit_mode == AuditMode.DOCUMENTS_ONLY:
        return """
        ╔═══════════════════════════════════════════════════════════════╗
        ║  AUDIT SOURCE: POLICY DOCUMENTS ONLY                          ║
        ║  ─────────────────────────────────────────────────────────── ║
        ║  This audit analyzed {doc_count} policy requirements.         ║
        ║  No system logs were collected for verification.              ║
        ║                                                               ║
        ║  ⚠️  This represents CLAIMED compliance only.                 ║
        ║      System logs needed to verify actual implementation.      ║
        ╚═══════════════════════════════════════════════════════════════╝
        """.format(doc_count=summary.document_evidence_count)

    else:  # FULL_AUDIT
        return """
        ╔═══════════════════════════════════════════════════════════════╗
        ║  AUDIT SOURCE: FULL GAP ANALYSIS                              ║
        ║  ─────────────────────────────────────────────────────────── ║
        ║  ✓ System Logs: {log_count} entries analyzed                  ║
        ║  ✓ Policy Documents: {doc_count} requirements extracted       ║
        ║  ✓ Gap Analysis: {gap_count} gaps detected                    ║
        ║                                                               ║
        ║  This audit compares stated policy against actual system      ║
        ║  behavior to identify compliance gaps.                        ║
        ╚═══════════════════════════════════════════════════════════════╝
        """.format(
            log_count=summary.log_evidence_count,
            doc_count=summary.document_evidence_count,
            gap_count=summary.gaps_detected
        )
```

---

## Redis Key Structure

```
audit:{audit_id}:config                    # AuditConfig JSON
audit:{audit_id}:evidence:{evidence_id}    # Individual evidence
audit:{audit_id}:evidence:list             # List of evidence IDs
audit:{audit_id}:evidence:source:log       # Log evidence IDs
audit:{audit_id}:evidence:source:document  # Document evidence IDs
audit:{audit_id}:evidence:control:{ctrl}   # Evidence by control
audit:{audit_id}:classification:{eid}      # Classification results
audit:{audit_id}:decision:{control_id}     # Compliance decisions
audit:{audit_id}:decisions:list            # List of decided controls
audit:{audit_id}:summary                   # Audit summary
```

---

## Implementation Steps

### Phase 1: Core Infrastructure ✅
1. ✅ Create `engines/shared/models.py`
2. ✅ Create `engines/shared/evidence_manager.py`
3. ✅ Update `engines/shared/__init__.py`

### Phase 2: Engine 1 Updates
1. ✅ Create `evidence_converter.py` for log events
2. ⏳ Add `/evidence/submit` endpoint to main.py
3. ⏳ Integrate with EvidenceManager

### Phase 3: Engine 2 Updates
1. ⏳ Create `evidence_converter.py` for documents
2. ⏳ Enable semantic matching (currently disabled)
3. ⏳ Add `/evidence/submit` endpoint

### Phase 4: Engine 3 Updates
1. ⏳ Accept ComplianceEvidence format
2. ⏳ Track source_type in classification
3. ⏳ Return ClassificationResult

### Phase 5: Engine 4 Updates
1. ⏳ Create `gap_analyzer.py`
2. ⏳ Create `weighted_scorer.py`
3. ⏳ Accept both evidence sources
4. ⏳ Output ComplianceDecision

### Phase 6: Engine 5 Updates
1. ⏳ Create `source_indicator.py`
2. ⏳ Include source info in PDF
3. ⏳ Highlight gaps in report

### Phase 7: Integration Testing
1. ⏳ Test logs-only audit
2. ⏳ Test documents-only audit
3. ⏳ Test full gap analysis audit

---

## API Endpoints (New/Modified)

### Engine 1
```
POST /evidence/submit           # Submit log evidence to pipeline
GET  /evidence/batch/{audit_id} # Get batch for audit
```

### Engine 2
```
POST /evidence/submit           # Submit document evidence
POST /process/for-audit         # Process doc and output evidence
```

### Engine 3
```
POST /classify/evidence         # Classify ComplianceEvidence
POST /classify/batch/evidence   # Batch classification
```

### Engine 4
```
POST /decide/evidence           # Make decision from evidence
POST /decide/control/{ctrl_id}  # Decide for specific control
GET  /gaps/{audit_id}           # Get detected gaps
```

### Engine 5
```
POST /report/generate           # Generate with source indicator
GET  /report/{audit_id}/summary # Get summary with sources
```

---

## Next Steps

To continue implementation, run:

```bash
# Continue from Engine 1 integration
cd engines/engine1-log-collector
# Update main.py to use evidence_converter and evidence_manager

# Then Engine 2
cd engines/engine2-document-processor
# Create evidence_converter.py
# Update main.py

# And so on...
```

---

*Document version: 1.0*
*Created: November 23, 2024*
*Status: Implementation in progress*
