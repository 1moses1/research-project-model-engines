# Dataset Alignment Analysis: Research Proposal vs. Current Implementation

## Research Proposal Requirements (From PDF)

### Primary Goal
**"AI-Augmented Unified Compliance Auditor for Hybrid Cloud Environments"**
- Focus: **Rwanda's NCSA Minimum Cybersecurity Standards (2023)** + **NIST SP 800-53**
- Target: **Hybrid cloud compliance auditing**
- Use case: **Automated compliance classification** (not intrusion detection, not attack classification)

### Required Datasets (Table 1, Page 4)

| Dataset | Purpose in Proposal | Current Status |
|---------|---------------------|----------------|
| **CICIDS 2017** | Train baseline classifiers (RF, SVM, LSTM) for anomaly detection | ✅ Likely available |
| **NSL-KDD / UNSW-NB15** | Cross-dataset generalization, augment training | ✅ NSL-KDD downloaded |
| **CERT Insider Threat** | User behavior patterns for anomaly detection | ❌ NOT found |
| **LogHub** | Log parsing and template extraction | ✅ Downloaded (apache, bgl, hdfs) |

### Synthetic Dataset Requirements (Page 3)

**Primary Purpose**: Map events to Rwanda NCSA controls and NIST 800-53
**Required attributes**:
- Control Definitions (AC-2, AU-6, etc.)
- Event Attributes (timestamp, user_id, action, resource, status_code)
- Compliance outcome (compliant/non-compliant)
- Anomaly labels (normal vs. anomalous)

---

## Current Dataset Inventory

### 1. Validated Synthetic Data ✅ CORRECT
**Location**: `data/validated_synthetic/`
**Size**: 70K events (50K train, 10K val, 10K test)
**Purpose**: Rwanda NCSA compliance mapping
**Alignment**: ✅ **PERFECT** - This is exactly what the proposal requires

### 2. Public Datasets (LogHub) ✅ CORRECT
**Location**: `data/public/LogHub/`
**Contents**: BGL, HDFS, Apache logs
**Purpose**: Log parsing and template extraction
**Alignment**: ✅ **CORRECT** - Matches Table 1 requirements

**Converted to compliance format**:
- `data/real/bgl_compliance.csv` (26MB)
- `data/real/hdfs_compliance.csv` (24MB)
- `data/real_formatted/` (50MB total)
**Alignment**: ✅ **CORRECT** - Used for log parsing training

### 3. NSL-KDD ✅ CORRECT (if present)
**Location**: `data/public/NSL-KDD/`
**Purpose**: Cross-dataset generalization
**Alignment**: ✅ **CORRECT** - Matches proposal

### 4. Targeted Attack Datasets ⚠️ OUT OF SCOPE
**Location**: `data/targeted/`
**Contents**:
- Phishing (3.5MB)
- DDoS (1.7MB)
- Credential stuffing (1.9MB)
- Insider threat (2.0MB)

**Purpose in your code**: Attack classification
**Purpose in proposal**: **NONE** - These are intrusion detection datasets

**Alignment**: ⚠️ **SCOPE CREEP** - Not in original proposal

**Why this matters**:
- Proposal is about **compliance auditing**, not **attack detection**
- These datasets train the model to classify attacks, not compliance violations
- Rwanda NCSA is about **security controls compliance**, not IDS/IPS

### 5. Integrated Datasets ❌ WRONG FOCUS
**Location**: `data/integrated_targeted/`
**Size**: 52MB (train 37MB, test 7.9MB, val 7.9MB)
**Contains**: Phishing + DDoS + Credential + Insider mixed with compliance

**Problem**: Controls like "RW-VM-003" (Vulnerability Management) are **FICTIONAL** (from old taxonomy)
**Alignment**: ❌ **OUT OF SCOPE** - This is attack detection, not compliance auditing

### 6. BERT Embeddings ✅ CORRECT
**Location**: `data/bert_embeddings_integrated/`
**Purpose**: NLP for log-to-control mapping
**Alignment**: ✅ **CORRECT** - Matches proposal (fine-tuned BERT for log mapping)

### 7. Temporal Enhanced Data ⚠️ UNCLEAR
**Location**: `data/temporal_enhanced/`
**Purpose**: Time-based features
**Alignment**: ⚠️ **NOT IN PROPOSAL** - Possible improvement but not required

---

## The Bigger Picture: What Your Research Is REALLY About

### According to the Research Proposal PDF:

**PRIMARY RESEARCH QUESTION**:
> "Can a localized AI-augmented compliance auditor achieve >93% classification accuracy and ≥50% audit cycle reduction for **Rwanda's NCSA Minimum Cybersecurity Standards**?"

**NOT about**:
- ❌ Intrusion detection (detecting attacks)
- ❌ Attack classification (phishing, DDoS, etc.)
- ❌ SOC/SIEM automation

**ACTUALLY about**:
- ✅ **Compliance auditing** - Are organizations following Rwanda NCSA rules?
- ✅ **Control mapping** - Which logs violate which controls?
- ✅ **Audit automation** - Reduce manual compliance checking time
- ✅ **Hybrid cloud** - AWS, Azure, on-prem systems

### What Compliance Auditing Means

**Example compliance violations**:
1. **Access Control (AC-2)**: User account created without approval → NON-COMPLIANT
2. **Audit Review (AU-6)**: Security logs not reviewed for 30 days → NON-COMPLIANT
3. **Incident Response (IR-4)**: Security incident not reported within 24h → NON-COMPLIANT
4. **System Integrity (SI-7)**: Software patch not applied within SLA → NON-COMPLIANT

**NOT this**:
- ❌ "Detected DDoS attack" → This is IDS, not compliance
- ❌ "Phishing email blocked" → This is email security, not compliance
- ❌ "Credential stuffing attempt" → This is threat detection, not compliance

**Compliance is about**:
- Did you follow the **process** required by regulations?
- Are your **controls** properly configured and monitored?
- Can you **prove** compliance to auditors?

---

## Dataset Alignment Verdict

### ✅ CORRECT - Keep These

1. **Validated Synthetic Dataset** (data/validated_synthetic/)
   - 70K compliance events mapped to Rwanda NCSA + NIST
   - **This is your PRIMARY dataset** ✅

2. **LogHub Logs** (data/public/LogHub/ + data/real/)
   - Real system logs for log parsing training
   - **Use for Table 1: Log parsing models** ✅

3. **NSL-KDD** (if complete)
   - **Use for Table 1: Baseline anomaly detectors** ✅

4. **BERT Embeddings** (data/bert_embeddings_integrated/)
   - **Use for RQ-a: BERT log-to-control mapping** ✅

### ⚠️ OUT OF SCOPE - Reconsider

5. **Targeted Attack Datasets** (data/targeted/)
   - Phishing, DDoS, Credential, Insider
   - **Not in proposal - scope creep** ⚠️
   - **Decision needed**: Remove or justify why attacks = compliance violations

6. **Integrated Targeted** (data/integrated_targeted/)
   - Mixes attacks with compliance
   - **Confuses attack detection with compliance auditing** ⚠️
   - **Uses old FICTIONAL controls (RW-VM-003)** ❌

### ❌ MISSING - Need to Add

7. **CERT Insider Threat Dataset**
   - **Required by Table 1** ❌
   - Purpose: User behavior anomalies (relevant for compliance monitoring)
   - **TODO**: Download and process

8. **CICIDS 2017**
   - **Required by Table 1** ❌
   - Purpose: Baseline anomaly detection training
   - **TODO**: Verify if downloaded, or download

---

## The Core Misunderstanding

### What You've Been Building
A **multi-purpose security system** that:
1. Detects attacks (phishing, DDoS, credential stuffing)
2. Maps logs to compliance controls
3. Classifies anomalies
4. Does everything

### What Your Proposal Requires
A **focused compliance auditor** that:
1. Maps audit logs → Rwanda NCSA controls
2. Classifies: compliant vs. non-compliant
3. Detects anomalies **in compliance behavior** (not attacks)
4. Reduces audit time by 50%

### Why This Matters for Defense

**If reviewer asks**: "Why are you training on DDoS attack data?"
- **Current answer**: "To detect security threats"
- **Problem**: That's not what your proposal is about
- **Better answer**: "I'm not - I'm training on compliance violation patterns"

**If reviewer asks**: "How does phishing detection relate to Rwanda NCSA compliance?"
- **Current answer**: "Phishing is a security threat"
- **Problem**: Compliance auditing ≠ threat detection
- **Better answer**: "It doesn't directly - my focus is on regulatory compliance, not intrusion detection"

---

## Recommended Action Plan

### Phase 1: Align with Proposal (THIS WEEK)

1. **PRIMARY DATASET**: Use `data/validated_synthetic/` ✅
   - 169 Rwanda NCSA controls
   - 70K compliance events
   - This IS your research

2. **SECONDARY**: Use LogHub for log parsing ✅
   - Train Drain algorithm on real logs
   - Extract templates
   - Map to compliance controls

3. **REMOVE or JUSTIFY**: Targeted attack datasets ⚠️
   - **Option A**: Remove entirely (stay focused)
   - **Option B**: Reframe as "compliance violations that happen to be attacks"
     - Example: "Failed to block known phishing domain" = Access Control violation
     - Example: "No DDoS mitigation in place" = Incident Response violation

### Phase 2: Fill Gaps (OPTIONAL)

4. **Download CERT Insider Threat** (if time permits)
   - Use for anomaly detection in compliance context
   - Example: "User accessing audit logs outside normal hours" = potential compliance violation

5. **Verify CICIDS 2017** (if needed for baseline)
   - Use ONLY for training baseline anomaly detectors
   - NOT for compliance classification

### Phase 3: Simplify Message

6. **For thesis defense**:
   - **Primary contribution**: "First ML system for Rwanda NCSA compliance auditing"
   - **Dataset**: "Validated synthetic data based on 169 official requirements"
   - **Public data**: "LogHub for log parsing, NSL-KDD for baseline anomaly detection"
   - **DO NOT emphasize**: Attack detection (it's out of scope)

---

## Dataset Size Analysis

### What You Actually Need

**For 93% accuracy target**:
- Proposal expects: Synthetic + public datasets
- Minimum viable: 50K-100K labeled compliance events
- **Current validated synthetic**: 70K events ✅ SUFFICIENT

**For 50% audit time reduction**:
- Need: Fast inference (<1s per 1000 events)
- **Current XGBoost**: <1ms per event ✅ EXCEEDS REQUIREMENT

### What You Currently Have (Relevant to Proposal)

| Dataset | Size | Proposal Alignment | Keep? |
|---------|------|-------------------|-------|
| Validated synthetic | 70K | ✅ PRIMARY | YES ✅ |
| LogHub (BGL, HDFS) | 50MB | ✅ REQUIRED | YES ✅ |
| NSL-KDD | Unknown | ✅ REQUIRED | YES ✅ |
| Targeted attacks | 9.1MB | ❌ OUT OF SCOPE | NO ⚠️ |
| Integrated targeted | 52MB | ❌ SCOPE CREEP | NO ⚠️ |
| BERT embeddings | 479MB | ✅ CORRECT | YES ✅ |

**Total RELEVANT data**: ~600MB (synthetic + LogHub + BERT)
**Total IRRELEVANT data**: ~61MB (targeted attacks)

---

## Final Verdict

### What to Train On (According to Proposal)

**PRIMARY TRAINING DATA**:
```
data/validated_synthetic/
├── train_validated.csv    # 50K compliance events
├── val_validated.csv      # 10K events
└── test_validated.csv     # 10K events
```
**Controls**: 169 Rwanda NCSA + 27 NIST SP 800-53
**Task**: Binary classification (compliant / non-compliant)

**SECONDARY (for log parsing)**:
```
data/public/LogHub/
├── BGL/
├── HDFS/
└── Apache/
```
**Purpose**: Train Drain algorithm for template extraction

**SECONDARY (for baseline anomaly detection)**:
```
data/public/NSL-KDD/  # If available
```
**Purpose**: Train One-Class SVM/LSTM baselines (Table 1)

### What NOT to Train On

**REMOVE**:
```
data/targeted/             # Attack detection (not compliance)
data/integrated_targeted/  # Mixed attacks + old controls
```

**Unless you can justify**: "These attacks represent specific compliance violations"
- Example: DDoS → IR-4 (Incident Response) violation
- Example: Phishing → SC-7 (Boundary Protection) violation

But this is a stretch and not in your original proposal.

---

## Summary: The Bigger Picture

**Your research proposal is about**:
- Automating compliance audits for Rwanda organizations
- Reducing manual audit time from 1000+ hours to <500 hours
- Achieving 93%+ accuracy in classifying compliance violations
- Focusing on Rwanda NCSA + NIST 800-53 controls

**Your research proposal is NOT about**:
- Building an intrusion detection system
- Detecting DDoS, phishing, or other attacks
- Replacing SOC analysts
- General cybersecurity threat detection

**Current model alignment**:
- ✅ XGBoost with validated controls: PERFECT
- ✅ BERT for log mapping: PERFECT
- ⚠️ Attack datasets: OUT OF SCOPE
- ❌ Integrated targeted data: CONFUSED FOCUS

**Recommendation**:
1. **Focus on compliance auditing** (validated synthetic + LogHub)
2. **Remove or minimize attack datasets** (not in proposal)
3. **Emphasize Rwanda NCSA** (your unique contribution)
4. **Be honest**: This is proof-of-concept, needs real institutional logs

**Bottom line**: You have the RIGHT data for your proposal (validated synthetic). The attack datasets are scope creep that dilute your message.
