# Comprehensive Revision Strategy: AI-Augmented Compliance Auditing Paper
**Manuscript:** futureinternet-4270373 | Future Internet (MDPI)  
**Status:** Major Revision — 3 Reviewers  
**Document generated:** 2026-05-05  
**Author:** Moise Iradukunda Ingabire | CMU Africa

---

## EXECUTIVE SUMMARY OF REVIEWER CROSS-ANALYSIS

Before the phases, here is the honest cross-reviewer diagnosis mapped against the manuscript and codebase findings:

| Issue | R1 | R2 | R3 | Root Cause (Codebase Reality) |
|---|---|---|---|---|
| 100% F1 unrealistic | C5 | C2 | C2 | **CONFIRMED: 40.4% of synthetic log_messages contain explicit compliance verdicts ("status: compliant", "violation detected")** |
| Synthetic data reliance | C6 | C1 | C2 | 196-control synthetic dataset with template leakage; real data in Git LFS inaccessible |
| n=50 LLM too small | C10 | C4 | C4 | `expanded_llm_eval.py` has exactly 50 hardcoded samples per type — **must be rebuilt** |
| Missing per-label F1 | C9(5) | C2,C5 | C1 | `model_metrics.json` stores only aggregate metrics — per-label never extracted |
| Overstated claims | C8 | C6,S | C6 | Manuscript uses "first methodologies", "proves insufficiency", "≥50% audit cycle reduction" without controlled comparison |
| Terminology blending | C3 | — | — | Engines 3,4 both described as "classifiers" and "decision engines" interchangeably |
| Adversarial scope narrow | — | — | C5 | Only 2 MITRE scenarios; Mordor Windows Events dataset with APT3 scenarios exists in `datasets/real_world/windows_events/` |
| Reproducibility | C9 | R,C5 | C1 | No public repo; no hyperparameter table; label assignment logic undocumented |
| Cost estimates vague | C2 | S | C6 | $50/month figure not broken down; variable API cost not separated |
| Scope too broad | C7 | S | C7 | 7 sections covering architecture + 4 ML models + adversarial + 3 eval phases |
| Metric inconsistency | C4 | — | C3 | Paper uses F1, Accuracy, MAcro-F1 interchangeably; micro vs macro not always stated |
| Missing Section 7 cite | C1 | — | — | Lines 92–94 of manuscript reference section outline but skip Section 7 |

---

## CRITICAL BLOCKER (Must Be Fixed First — Everything Else Depends On It)

### DATA LEAKAGE SEVERITY: CATASTROPHIC
**Finding from codebase inspection of `data/synthetic/compliance_events_train.csv`:**
- 40.4% (28,267/70,000) of training log messages contain explicit compliance verdicts embedded in text:
  - `"Compliance verification for RWNCSA-AT-47 - status: compliant"`
  - `"Control RWNCSA-CM-84: policy updated failed verification"`
  - `"audit log - compliance violation detected"`
- This is **worse than the status_code leakage** (−0.97 correlation) already disclosed in the paper
- It renders the 99.99% F1 completely invalid as a performance claim
- The manuscript already disclosed the status_code leakage and claimed it was fixed — **this text-embedded leakage was not identified or disclosed**
- Additionally: training uses 196 controls (169 RWNCSA + 27 NIST), but manuscript claims 143 — **taxonomy mismatch**

**Implication:** Every downstream result (cross-validation F1, generalization gap comparison, router evaluation) must be recomputed after fixing this.

---

## IMPLEMENTATION PHASES

---

## PHASE 0: DATA INTEGRITY AUDIT & SYNTHETIC DATA REGENERATION
**Priority:** CRITICAL BLOCKER | **Dependency:** All other phases depend on this  
**Estimated effort:** 2–3 days  
**Addresses:** R1-C5, R1-C6, R1-C9, R2-C1, R2-C2, R2-C5, R3-C2

### Step 0.1 — Quantify All Leakage Sources
**Action:** Write `scripts/data_audit.py` that:
- Scans all CSV files in `data/synthetic/`, `data/public_formatted/`, `data/validated_synthetic/`
- Checks for: (a) control_id embedded in log_message, (b) compliance_status embedded in log_message, (c) anomaly_label correlation with compliance_status
- Outputs a `reports/data_leakage_audit.json` with per-field Pearson correlations
- Also reconcile: manuscript says 143 controls, taxonomy has 196 — document which 143 are "system-auditable"

**Success metric:** Full leakage audit report; every leakage source identified and documented

### Step 0.2 — Regenerate Synthetic Data Without Leakage
**Action:** Rewrite the synthetic data generator in `scripts/generate_synthetic_data.py` to:
- Produce **realistic security log messages** that resemble actual syslog/Windows Event/HTTP formats — NOT "Compliance verification for X - status: compliant"
- Use a rule-based log template library derived from real log patterns in `datasets/real_world/linux_auth.log` and `data/public/LogHub/`
- **Never embed control IDs or compliance verdicts in the log_message field**
- Maintain the 143-control scope aligned with the manuscript (system-auditable NCSA controls only)
- Generate 60,000 Rwanda-specific events (the 30% slice) with realistic NCSA-context log messages:
  - Access control events: failed/successful login patterns, permission denials
  - Audit events: audit daemon status, log rotation events
  - Network events: TLS handshake failures, firewall denials
  - Configuration events: software install/patch events, policy changes

**Label assignment methodology (for paper disclosure):**
- For synthetic data: labels are assigned by a **rule-based heuristic taxonomy** derived from NIST SP 800-53 control descriptions. Each synthetic event is generated FROM a control context (not mapped after generation), so the ground-truth label is the generating control ID. This is disclosed as heuristic/generative labeling, not human annotation.
- All label rules are codified in `scripts/label_assignment_rules.json` for full reproducibility

**Success metric:** Zero correlation between log_message text and compliance_status label; zero control_id references in log_message; dataset regenerated and statistics verified

### Step 0.3 — Document Class Distribution
**Action:** After regeneration, extract and save:
- Per-label positive sample counts for all 143 controls
- Class imbalance ratio (overall and per-family)
- Min/max label frequency (head vs. tail controls)
- Output: `reports/class_distribution_143controls.json` and a bar chart figure

**Success metric:** Document confirms minimum 100+ positive examples per control; imbalance ratio reported

---

## PHASE 1: XGBOOST RE-TRAINING WITH RIGOROUS EVALUATION
**Priority:** HIGH | **Dependency:** Phase 0  
**Estimated effort:** 3–4 days  
**Addresses:** R1-C4, R1-C5, R1-C9, R2-C2, R2-C5, R3-C1, R3-C3

### Step 1.1 — Rebuild Training Pipeline with Proper Evaluation
**Action:** Write `scripts/train_xgboost_v2.py` that:
- Uses the cleaned synthetic dataset (from Phase 0) + NSL-KDD + LogHub
- Implements `MultiOutputClassifier(XGBClassifier(...))` with **explicit hyperparameter documentation**:
  - `n_estimators`, `max_depth`, `learning_rate`, `subsample`, `colsample_bytree`
  - `random_seed=42` (for reproducibility)
  - `scale_pos_weight` per label for class imbalance handling (since 3:1 ratio observed)
- 5-fold stratified cross-validation with per-label F1 extraction
- Outputs:
  - `reports/xgboost_per_label_f1.csv` (143 rows, one per control)
  - `reports/xgboost_confusion_matrices.pkl` (143 binary confusion matrices)
  - `reports/xgboost_cv_summary.json` (macro/micro F1, Hamming loss, per-fold scores)
  - `reports/xgboost_hyperparameters.json`

**Expected result after fixing leakage:** F1 will be significantly lower than 99.99% on clean synthetic data — this is the honest result that the paper should report. If performance on realistic synthetic data is, say, 70–85%, that is a more defensible and interesting finding.

### Step 1.2 — Cross-Dataset Generalization Re-evaluation
**Action:** Re-run zero-shot evaluation on:
- SecRepo SSH auth logs (86,839 samples) — previously done
- **NEW**: `datasets/real_world/linux_auth.log` (9.3MB real Linux auth)
- **NEW**: LogHub Linux logs (`data/public/LogHub/Linux/Linux.log`)
- **NEW**: LogHub OpenStack logs (cloud-native; maps to SC/AC controls)
- **NEW**: BGL supercomputer logs (`data/public/bgl/`) — maps to SI/AU controls

**Output:** `reports/cross_dataset_generalization_v2.csv` with per-dataset F1 and accuracy

**Success metric:** Zero-shot F1 reported on 5+ real datasets (not just 1); the generalization gap is now a cross-dataset finding, not a single-dataset anomaly

### Step 1.3 — Per-Label F1 Visualization
**Action:** Generate `figures/per_label_f1_distribution.png`:
- Histogram of per-label F1 across 143 controls
- Sorted bar chart colored by control family (AC=blue, AU=green, etc.)
- Highlight tail controls (bottom 10 by F1) in red
- This directly answers R2-C2 and R3-C1 (per-label performance distribution)

---

## PHASE 2: LLM EVALUATION EXPANSION (n=50 → n=200 PER TYPE)
**Priority:** HIGH | **Dependency:** None (can run in parallel with Phase 1)  
**Estimated effort:** 1–2 days  
**Addresses:** R1-C10, R2-C4, R3-C4

### Step 2.1 — Rebuild `expanded_llm_eval.py` at n=200 per type
**Action:** Rewrite `scripts/expanded_llm_eval_v2.py` with:
- **n=200 per log type** (800 total, 4 types)
- Balanced sampling: 40% compliant / 40% non-compliant / 20% partial per type
- Sources for additional samples:
  - SSH: `datasets/real_world/linux_auth.log` (9.3MB available) — sample additional unique entries
  - macOS: Expand existing synthetic macOS service logs with more realistic patterns
  - HTTP/API: Generate from Apache access log format + add scanner patterns (sqlmap, nikto, dirbuster)
  - Windows Events: Use `datasets/real_world/windows_events/` Mordor APT3 dataset samples (JSON → log_message text)
- **Models to evaluate:**
  - GPT-4o-mini (temperature=0)
  - Llama-3.2-3B via Ollama (temperature=0)
  - **NEW**: GPT-4o (for frontier baseline comparison)
  - **NEW**: Claude Haiku 4.5 (lightweight on-premise alternative)
- **Outputs per run:**
  - Per-sample predictions with ground truth
  - 95% Wilson confidence intervals per cell
  - Confusion matrix per log type per model
  - `reports/llm_eval_n200_results.json`

**Success metric:** n=200 per type; 95% CI ≤ ±7 pp per cell (vs. ±14 pp at n=50); all prompt text disclosed in appendix

### Step 2.2 — Standardize Evaluation Protocol Across ML and LLM
**Action:** Write a unified evaluation protocol document `reports/evaluation_protocol.md`:
- Same 200-sample evaluation set used for BOTH XGBoost zero-shot AND LLM zero-shot
- Same ground truth labels (rule-based classifiers + manual cross-validation)
- Explicitly state: metric = accuracy (binary: compliant vs. non-compliant/partial), not F1
- This directly addresses R3-C3 ("comparison is not fair due to different settings")

### Step 2.3 — Multi-Model Frontier Comparison Table
**Action:** Add a new table to Section 4 showing:
- GPT-4o-mini, GPT-4o, Llama-3.2-3B, Claude Haiku 4.5 on same n=200×4 evaluation
- Per-type accuracy + overall + 95% CI + cost per 10K logs + on-premise viable (Y/N)
- This adds the "frontier model compatibility" dimension the user requested (BIGGER PICTURE)

---

## PHASE 3: ADVERSARIAL VALIDATION EXPANSION (2 → 5 MITRE ATT&CK SCENARIOS)
**Priority:** MEDIUM-HIGH | **Dependency:** Isolated test environment  
**Estimated effort:** 3–5 days  
**Addresses:** R3-C5, R1-C7 (scope depth), R2-C2

### Current coverage: T1059.001 (Fileless Shell) + T1190 (XSS Injection)

### Step 3.1 — Map Additional MITRE ATT&CK Techniques to NCSA Controls

**New scenarios to add (3 additional):**

**Scenario 3: T1110 (Brute Force / Credential Stuffing) → AC-7, IA-2, IA-5**
- Method: Use public SSH honeypot data (e.g., from `datasets/real_world/linux_auth.log` which contains 9.3MB of real brute force attempts) OR use `hydra`/`medusa` against a local test VM
- Metric: Detection rate = (correctly flagged lockout events) / (total brute force attempts)
- Expected: AC-7 lockout threshold detection rate
- Tools needed: Local Docker container with SSH; or use real linux_auth.log data as passive evidence

**Scenario 4: T1078 (Valid Accounts / Credential Abuse) → IA-2, AC-2, AU-9**
- Method: Simulate using SecRepo SSH logs with successful logins from anomalous IPs/times
- Metric: Anomaly detection rate for after-hours or unusual-geolocation authentications
- Source: `datasets/real_world/linux_auth.log` — filter for "Accepted" events from suspicious IPs
- Evidence maps to: IA-2 (MFA bypass), AC-2 (account monitoring), AU-9 (audit protection)

**Scenario 5: T1562.001 (Impair Defenses / Disable/Modify Tools) → SI-3, AU-2, CM-7**
- Method: Use Mordor APT3 Windows Events dataset (`datasets/real_world/windows_events/datasets/compound/windows/apt3/`) — these contain real recorded attack sequences with Windows Event IDs
- Extract events showing: service stop, AV disable attempts, audit policy modification
- Metric: System detection rate (how many APT3 impairment events does the Decision Engine flag)
- This is particularly strong because it uses a **real recorded APT3 attack dataset**

### Step 3.2 — Formalize Adversarial Effectiveness Metrics
For each scenario, compute and report:
- $E_k$ = detection_rate = detected_events / total_attack_events
- $R_k$ = evasion_resistance = 1 - bypass_rate
- Full C(k) computation for each tested control

### Step 3.3 — MITRE ATT&CK Mapping Table
**Action:** Add a new Table to Section 3 (Methodology):
| MITRE Technique | TTP ID | Tested Against | NCSA Control | Detection Rate | C(k) Score |
|---|---|---|---|---|---|
| Fileless Shell | T1059.001 | Virtual machine | SI-3 | 20% | 0.403 |
| XSS Injection | T1190 | Web app | SI-10 | 68% | 0.746 |
| Brute Force SSH | T1110 | linux_auth.log | AC-7, IA-2 | TBD | TBD |
| Credential Abuse | T1078 | SecRepo logs | IA-2, AC-2 | TBD | TBD |
| Impair Defenses | T1562.001 | Mordor APT3 data | SI-3, AU-2 | TBD | TBD |

---

## PHASE 4: DATASET EXPANSION FOR EXTERNAL VALIDITY
**Priority:** MEDIUM | **Dependency:** Phase 0  
**Estimated effort:** 2–3 days  
**Addresses:** R1-C6, R2-C1, R2-C4, R3-C2

### Step 4.1 — Integrate New Real-World Datasets

**Datasets already available locally (to add to evaluation):**

| Dataset | Location | Size | Log Type | NCSA Control Coverage |
|---|---|---|---|---|
| Linux Auth Log | `datasets/real_world/linux_auth.log` | 9.3 MB | SSH/PAM auth | AC-7, IA-2, AU-2 |
| BGL Supercomputer | `data/public/bgl/BGL.tar.gz` | Large | System/kernel | SI-4, AU-12, CM-7 |
| LogHub OpenStack | `data/public/LogHub/OpenStack/` | ~5K logs | Cloud API | SC-7, AC-3, AU-9 |
| LogHub Linux | `data/public/LogHub/Linux/Linux.log` | Available | System | AU-12, CM-7, SI-2 |
| Mordor APT3 | `datasets/real_world/windows_events/` | JSON | Windows Security Events | AC-7, SI-3, AU-9 |
| HDFS Anomaly | `data/public/hdfs/` | Available | Distributed storage | AU-2, SC-8, SI-4 |

**Datasets to download (script-based):**

| Dataset | Source | NCSA Relevance |
|---|---|---|
| CICIDS 2017 | University of New Brunswick (public) | SC-7, SC-8, SI-4 (DDoS, portscan, brute force) |
| UNSW-NB15 | UNSW (public) | AC-7, IA-2, SI-3 (network intrusion) |
| SecRepo HTTP logs | secrepo.com | SI-10, AC-3 (web application attacks) |

**Action:** Write `scripts/download_additional_datasets.sh` for CICIDS 2017, UNSW-NB15, and SecRepo HTTP

**Africa/Cloud-Native context (to be added to manuscript):**
- Rwanda's tech stack is dominated by: (a) cloud providers (AWS, GCP, Azure), (b) open-source ELFK (Elasticsearch-Logstash-Fluentd-Kibana) stack, (c) mobile money systems (MTN/Airtel using Linux + Oracle DB backends)
- LogHub OpenStack logs directly map to cloud API activity in this context
- HDFS logs map to distributed data processing pipelines common in East African telcos
- NSL-KDD network traffic maps to perimeter controls (SC-7, SC-8) in cloud-hybrid environments

### Step 4.2 — Add Dataset Provenance Table to Manuscript
**Action:** Expand Table 2 (Hybrid Dataset Composition) to include all real datasets used for evaluation (not just training), with columns: Source, Type, Size, Real/Synthetic, NCSA Controls Covered, Access Date

---

## PHASE 5: MANUSCRIPT SURGICAL REVISIONS
**Priority:** HIGH | **Dependency:** Phases 0–4 results  
**Estimated effort:** 4–5 days  
**Addresses:** ALL remaining reviewer comments

### Step 5.1 — Fix Claims and Terminology (R1-C3, R1-C8, R2-C6, R3-C6)

**Terminology disambiguation (R1-C3):**
Add a paragraph to Section 3.1 explicitly defining component roles:
- **Compliance Auditor** = the complete seven-engine system
- **XGBoost Classifier** (Engine 3a) = multi-label evidence-to-control routing; outputs which controls are relevant to a log event
- **LLM Semantic Analyzer** (Engine 3b) = natural language reasoning for ambiguous/OOD log events
- **Vocabulary-Coverage Router** = OOD detection signal selecting between 3a and 3b
- **Decision Engine** (Engine 4) = deterministic rule evaluator that applies NCSA-specific thresholds to produce compliant/partial/non-compliant verdicts
- **Compliance Auditor ≠ Classifier**: Engine 4 makes the compliance decision; Engine 3 routes evidence

**Claims to moderate (R1-C8, R2-C6, R3-C6):**

| Current (too strong) | Revised (evidence-linked) |
|---|---|
| "proves insufficiency" | "demonstrates empirical insufficiency under tested conditions" |
| "fundamental constraint" | "an observed characteristic of vocabulary-dependent models" |
| "strictly more expressive" | "empirically more expressive across the tested evaluation set" |
| "first methodologies" | "among the early methodologies connecting..." |
| "≥50% audit cycle reduction" | "suggests potential audit cycle reduction (0.77s automated execution vs. reported 1,000+ annual audit hours [COGR 2022]); however, these represent different task scopes and direct comparison requires further controlled study" |
| "replicable blueprint for African nations" | "a replicable reference architecture for NIST SP 800-53 aligned frameworks; cross-national adaptation requires regulatory mapping and institutional validation" |

### Step 5.2 — Fix Missing Section Reference (R1-C1)
**Action:** In lines 92–94 of manuscript, add: "...Section~\ref{sec:conclusion} concludes; Section~\ref{sec:future_work} outlines short-, medium-, and long-term research directions."

### Step 5.3 — Clarify Cost Estimates (R1-C2)
**Action:** Replace vague "$50/month" with a breakdown table:

| Cost Component | Value | Assumptions |
|---|---|---|
| Kubernetes cluster (2.0 CPU, 2.66 GB RAM) | ~$35–45/month | AWS EKS t3.small equivalent; excludes storage |
| Object storage (audit logs, reports) | ~$5–10/month | 50 GB/month at $0.023/GB (AWS S3) |
| LLM API (variable) | ~$0.15/10K logs | GPT-4o-mini; zero if on-premise Llama used |
| Maintenance (automated) | $0 | No manual maintenance cost at steady state |
| **Total (cloud, API-based)** | ~$50/month + variable API | Excludes one-time setup |
| **Total (on-premise, CPU-only)** | ~$35–45/month | No API cost; Llama 3.2-3B locally |

### Step 5.4 — Metric Consistency Pass (R1-C4, R3-C3)
**Action:** Do a full manuscript pass adding consistent metric labels:
- Every F1 citation: specify "macro-F1 (unweighted mean across 143 binary classifiers)"
- Every accuracy citation: specify if binary (compliant vs. other) or multi-class
- Add a "Metrics Glossary" subsection in Section 3 (Methodology) defining all metrics used

### Step 5.5 — Strengthen Theoretical Section (R3-C1)
**Action:** In Section 5.3 (Theoretical Contributions):
- Add formal derivation of Equation C(k): explain why each weight was chosen (α=0.5 priority on detection because it is directly observable; β=0.3 coverage as a structural property; γ=0.2 evasion resistance as adversarial bound — currently empirically estimated)
- Define ALL variables explicitly before Equation (3): D_k, V_k, R_k with precise measurement definitions
- Add justification references: cite Boran et al. on continuous risk scoring, CVSS v3.1 for the weighted linear model form, and the ISO/IEC 27004:2016 measurement framework as precedent for quantitative control assessment
- Replace "provably insufficient" with "demonstrably insufficient under the tested conditions, consistent with the binary presence model's theoretical limitations"

### Step 5.6 — Expand Limitations Section (R2-C4, R2-C1)
**Action:** Add three new limitation paragraphs:
1. **Synthetic Data Scope**: Explicitly state that training performance metrics (F1 ≥ 99%) are reported on clean-generated synthetic data and should not be interpreted as real-world performance benchmarks. Real-world performance is characterized by cross-dataset evaluation (Section 4.2).
2. **LLM Sample Size**: Acknowledge n=200 (even after expansion) represents preliminary validation. State the planned validation scope (n≥500 per type per institutional pilot).
3. **Adversarial Scope**: Five MITRE scenarios tested represent coverage of the most relevant controls; full ATT&CK framework coverage remains future work.

### Step 5.7 — Add Evaluation Methodology Subsection (R1-C9)
**Action:** Add `Section 3.6: Evaluation Methodology` explicitly stating:
1. **Label generation**: Synthetic labels generated via rule-based control-context templates (heuristic); real log labels established by domain-specific rule-based classifiers with manual review of ambiguous cases (documented in supplementary appendix)
2. **Ground truth creation**: Two-stage — automated rule classifier first pass; manual review of boundary cases (5–10% of samples)
3. **Human annotation**: No independent human annotation; labels derived from rule-based classifiers validated against known-good log patterns
4. **Class imbalance**: Addressed via per-label `scale_pos_weight` in XGBoost; reported in class distribution table
5. **Per-label metrics**: Reported in Supplementary Table S1 (per-label F1 for all 143 controls)
6. **Leakage prevention**: Training/validation/test split done before feature extraction; synthetic data regenerated to remove control-ID and compliance-status references from log_message text; status_code removed from feature set
7. **Confidence intervals**: 95% Wilson CI for LLM evaluation; 95% CI via 5-fold CV for XGBoost

---

## PHASE 6: REPRODUCIBILITY PACKAGE & GITHUB REPOSITORY
**Priority:** HIGH | **Dependency:** Phases 0–5  
**Estimated effort:** 2 days  
**Addresses:** R2-R, R2-C5, reviewer credibility**

### Step 6.1 — Repository Pruning and Cleanup
**Action:**
- Remove irrelevant files from git history: `archive/old_docs/`, old model versions, personal credentials from `.env`
- Add `.gitignore` entries for: `*.env`, `config/credentials/`, `models/checkpoints/`
- Ensure `.env.example` has all required variables documented with descriptions
- Tag the reproduction release: `git tag v1.0-revision-1`

### Step 6.2 — Supplementary Appendix Document
**Action:** Create `supplementary_appendix.tex` containing:
- **Table S1**: Per-label F1 for all 143 NCSA controls (output of Phase 1)
- **Table S2**: Full LLM evaluation results n=200 per type (output of Phase 2)
- **Table S3**: Complete XGBoost hyperparameter configuration with seeds
- **Table S4**: Label assignment rules for synthetic data generation (control_id → log template → label)
- **Table S5**: MITRE ATT&CK to NCSA control mapping for all 5 adversarial scenarios
- **Figure S1**: Class distribution across 143 controls
- **Figure S2**: Per-label F1 distribution histogram
- **Listing 1**: Vocabulary-coverage router implementation (10 lines of Python)

### Step 6.3 — Data Availability Statement Update
**Action:** Update the Data Availability section to:
- Provide the exact GitHub URL
- List which datasets are publicly available, which are synthetic (script-generated), and which require institutional access
- Include a DOI-linked Zenodo archive of the evaluation results

---

## PHASE 7: GENERATE AUTHOR RESPONSES
**Priority:** HIGH | **Dependency:** All phases complete  
**Estimated effort:** 1–2 days  

**Action:** For each reviewer file (`reviewer1_comments.md`, `reviewer2_comments.md`, `reviewer3_comments.md`), replace all `[PLACEHOLDER]` entries with structured responses following the MDPI template:
- State the reviewer concern in one sentence
- State agreement or disagreement
- Explain what was changed (with manuscript section and line reference)
- Show [updated text in red] where applicable

---

## DEPENDENCY GRAPH (Execution Order)

```
Phase 0 (Data Audit + Synthetic Regen)
    ↓
Phase 1 (XGBoost Retrain)          Phase 2 (LLM Expansion)    ← These two run in PARALLEL
    ↓                                    ↓
Phase 3 (Adversarial Expansion) ← uses Mordor dataset (available)
    ↓
Phase 4 (Dataset Expansion) ← uses local data + downloads
    ↓
Phase 5 (Manuscript Revision) ← uses all new results
    ↓
Phase 6 (Reproducibility Package)
    ↓
Phase 7 (Author Responses)
```

---

## SUCCESS METRICS (Publication Readiness Checklist)

| Criterion | Current State | Target State | How Measured |
|---|---|---|---|
| Data leakage eliminated | 40.4% leaky synthetic data | 0% leakage confirmed | Re-run leakage audit |
| XGBoost F1 credible | 99.99% (leaky) | 70–90% range (clean) | 5-fold CV on clean data |
| Per-label F1 reported | Missing | All 143 controls reported | Table S1 in supplementary |
| Confusion matrices | Missing | Per log-type confusion matrices | Phase 1 output |
| Class distribution | Missing | Full table + figure | Phase 0 output |
| LLM sample size | n=50 per type | n=200 per type | Rebuilt eval script |
| LLM CI width | ±14 pp per cell | ≤ ±7 pp per cell | Wilson CI formula |
| LLM models evaluated | 2 (GPT-4o-mini, Llama-3.2-3B) | 4+ (add GPT-4o, Claude Haiku) | Phase 2 output |
| Adversarial scenarios | 2 (fileless, XSS) | 5 (+ brute force, cred abuse, impair defenses) | Phase 3 output |
| Real datasets evaluated | 1 (SecRepo SSH) | 6+ (SecRepo + BGL + OpenStack + Linux auth + HDFS + Mordor) | Phase 4 output |
| Overstated claims | 6 identified | All moderated with evidence links | Phase 5.1 |
| Terminology disambiguated | Blended | Clear component roles defined | Phase 5.1 |
| Cost breakdown | Vague "$50/month" | Itemized table | Phase 5.3 |
| Evaluation methodology | Missing | Explicit Section 3.6 | Phase 5.7 |
| Metric consistency | Mixed | Unified glossary + consistent labels | Phase 5.4 |
| Theoretical equations | Variables undefined | All variables formally defined | Phase 5.5 |
| Public repository | Private/none | Public GitHub with tags | Phase 6 |
| Supplementary appendix | Missing | All 5 tables + 2 figures | Phase 6.2 |
| Author responses | Placeholder | Complete point-by-point | Phase 7 |
| Frontier LLM compatibility | 2 models | 4+ models incl. 2026 frontier | Phase 2.3 |

---

## REVIEWER-TO-PHASE MAPPING (Traceability)

| Comment | Phase | Step | Notes |
|---|---|---|---|
| R1-C1 (Section 7 cite) | 5 | 5.2 | 30-min fix |
| R1-C2 (Cost vague) | 5 | 5.3 | Add breakdown table |
| R1-C3 (Terminology) | 5 | 5.1 | Add component roles paragraph |
| R1-C4 (Metric inconsistency) | 5 | 5.4 | Full manuscript pass |
| R1-C5 (Unrealistic metrics) | 0,1 | 0.2, 1.1 | Fix leakage → retrain → honest results |
| R1-C6 (Synthetic reliance) | 0,4 | 0.2, 4.1 | Fix data + add 5+ real datasets |
| R1-C7 (Scope too broad) | 5 | 5.1 | Reframe as one focused system; move secondary findings to supplementary |
| R1-C8 (Strong claims) | 5 | 5.1 | Replace 6 flagged phrases |
| R1-C9 (Eval methodology) | 5 | 5.7 | Add Section 3.6 |
| R1-C10 (n=50 too small) | 2 | 2.1 | Expand to n=200 |
| R2-R (Repository) | 6 | 6.1,6.3 | Public GitHub + Zenodo |
| R2-S (Claims exceed evidence) | 5 | 5.1 | Moderate language |
| R2-C1 (Synthetic data) | 0,4 | 0.2, 4.1 | Fix + expand real data |
| R2-C2 (Near-perfect metrics) | 0,1 | 0.2, 1.1,1.3 | Fix leakage + per-label distribution |
| R2-C3 (Generalization gap) | 1,5 | 1.2, 5.6 | Reposition gap as primary finding |
| R2-C4 (Limited real-world validation) | 4 | 4.1 | Add 5+ real datasets |
| R2-C5 (Reproducibility) | 1,6 | 1.1, 6.2 | Hyperparams + supplementary |
| R2-C6 (Strong claims) | 5 | 5.1 | Same as R1-C8 |
| R3-C1 (Equations) | 5 | 5.5 | Formal derivation + variable definitions |
| R3-C2 (Near-100% F1) | 0,1 | 0.2, 1.1 | Fix leakage → retrain |
| R3-C3 (Unfair comparison) | 2 | 2.2 | Unified evaluation protocol |
| R3-C4 (n=50 + CIs) | 2 | 2.1 | n=200 + Wilson CIs |
| R3-C5 (Adversarial narrow) | 3 | 3.1,3.2 | 5 MITRE scenarios |
| R3-C6 (Overstated conclusions) | 5 | 5.1 | Moderate claims |
| R3-C7 (Validation not robust) | 0,1,2,3,4 | All | Full experimental rebuild |

---

## IMPORTANT NOTE ON FRONTIER LLM INTEGRATION (BIGGER PICTURE)

Per the user's vision: the architecture should be **modular and compatible with all upcoming frontier models**. The current `engines/engine3-mcp-analyzer/app/services/llm_client.py` uses OpenAI SDK. The revision should:

1. **Abstract the LLM interface** via the existing MCP integration to be provider-agnostic
2. **Add model-routing configuration** in `config/model_config.yaml`:
   - `preferred_model`: configurable (GPT-4o, Claude Opus 4.7, Llama-3.3-70B, Mistral-7B, Phi-4, Gemma-2-27B)
   - `fallback_model`: on-premise option
   - `model_tier`: "cloud_api" | "on_premise" | "hybrid"
3. In the paper: frame Phase 3 router as a **model-agnostic routing framework** — vocabulary coverage gating is independent of which LLM is called on the semantic path; as better models emerge, plug them in without architectural changes
4. Evaluate at minimum 4 models in Phase 2 to empirically demonstrate this modularity

---

*This document is the living strategy guide. Update it as phases complete and results are obtained. All phase outputs feed directly into the manuscript revision and author response files.*
