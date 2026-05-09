# AI-Augmented Compliance Auditing for Cloud Systems: A Hybrid ML–LLM Approach

**Research Repository — Carnegie Mellon University Africa**

[![Journal](https://img.shields.io/badge/Journal-Future%20Internet%20(MDPI)-blue)]()
[![Status](https://img.shields.io/badge/Status-Under%20Review-orange)]()
[![XGBoost F1](https://img.shields.io/badge/XGBoost%20F1-85.45%25-brightgreen)]()
[![LLM Accuracy](https://img.shields.io/badge/LLM%20Macro--Acc-92.3%25-brightgreen)]()
[![License](https://img.shields.io/badge/License-Academic-yellow)]()

---

## Overview

This repository contains the full research codebase, evaluation scripts, datasets, and manuscript artifacts for the paper:

> **"AI-Augmented Compliance Auditing for Cloud Systems: A Hybrid ML–LLM Approach"**
> Moise Iradukunda Ingabire — Carnegie Mellon University Africa
> *Submitted to Future Internet (MDPI), Manuscript ID: futureinternet-4270373 — Major Revision*

The research proposes and evaluates a hybrid machine learning + large language model (LLM) pipeline for automated compliance auditing against the Rwanda National Cybersecurity Authority (RWNCSA) Minimum Cybersecurity Standards (169 controls, 14 families), grounded in NIST SP 800-53.

---

## Research Questions

| RQ | Question | Key Result |
|---|---|---|
| RQ1 | Can ML classify compliance across 169 RWNCSA controls? | XGBoost v2: F1 = 85.45%, Accuracy = 87.14% (leakage-free) |
| RQ2 | Can LLMs accurately classify diverse log types? | GPT-4o-mini: Macro-Acc = 92.3%, n=628 (Wilson 95% CI) |
| RQ3 | Does a hybrid system outperform either alone? | Hybrid F1 = 85.1% at FPR = 6.4% on 180 real-world logs |
| RQ4 | Is the system robust to adversarial evasion? | 5 MITRE ATT&CK v14 scenarios, macro detection = 92.8% |
| RQ5 | What is the deployment cost? | ≤$50/month infrastructure + $0.15/10K logs (API) |

---

## Key Results

### XGBoost v2 (Leakage-Free)
- Test F1: **85.45%** | Macro-F1: 85.05% | Accuracy: 87.14%
- 5-fold CV F1: 85.20% ± 0.25% | Wilson 95% CI: [84.9%, 86.0%]
- Training corpus: 150,000 rows, verified zero label leakage

### LLM Evaluation (GPT-4o-mini, n=628)
| Log Type | Accuracy | Wilson 95% CI |
|---|---|---|
| SSH Authentication | 89.5% | [84.5%, 93.0%] |
| Windows Security Events | 97.5% | [94.3%, 98.9%] |
| HTTP/API Access | 85.7% | [68.5%, 94.3%] |
| macOS System/Service | 96.5% | [93.0%, 98.3%] |
| **Macro Average** | **92.3%** | — |

### Adversarial Validation (MITRE ATT&CK v14)
| MITRE ID | Scenario | Detection Rate |
|---|---|---|
| T1059.001 | PowerShell Fileless Shell | 86.0% |
| T1190 | XSS/SQLi WAF Bypass | 100.0% |
| T1110 | SSH Brute Force | 100.0% |
| T1078 | Lateral Movement Valid Accounts | 100.0% |
| T1562.001 | Impair Defenses: Disable Tools | 78.0% |
| **Macro** | | **92.8%** |

---

## Repository Structure

```
model-engine/
├── Research project Fall to Spring/
│   ├── deliverable_4_full_manuscript_v3_mdpi_v3.tex   # Revised manuscript (v3, MDPI format)
│   ├── supplementary_appendix.tex                      # Supplementary materials
│   ├── reviewer1_comments.md                           # Response to Reviewer 1
│   ├── reviewer2_comments.md                           # Response to Reviewer 2
│   ├── reviewer3_comments.md                           # Response to Reviewer 3
│   ├── generate_reviewer_pdfs.py                       # PDF generation (LaTeX→Unicode math)
│   ├── manuscript_final_consistency_fixes.md           # Consistency tracking log
│   ├── poster_figures/                                 # Research poster charts
│   └── presentation_assets/                            # Course presentation assets
├── scripts/
│   ├── expanded_llm_eval_v2.py                        # Phase 2 LLM evaluation (n=200/type)
│   ├── hybrid_system_eval.py                          # Phase 5 hybrid combined evaluation
│   ├── adversarial_validation_v2.py                   # 5-scenario MITRE ATT&CK eval
│   ├── cross_dataset_eval_v1.py                       # Generalization gap analysis
│   └── generate_synthetic_data_v2.py                  # Leakage-free data generator
├── reports/
│   ├── hybrid_system_eval.*                           # Hybrid eval results (JSON/CSV/log)
│   ├── adversarial_validation_v2.*                    # Adversarial results
│   └── cross_dataset_eval.*                           # Cross-dataset generalization results
└── models/                                            # Trained model artifacts (Git LFS)
```

---

## Reproducibility

All experiments are fully reproducible. See `Research project Fall to Spring/supplementary_appendix.tex` for:
- Dataset provenance and construction details
- Hyperparameter tables (XGBoost, GPT-4o-mini)
- Evaluation protocol and ground-truth labeling rules
- Phase-by-phase experimental log

---

## Citation

```bibtex
@article{iradukunda2026hybrid,
  title     = {AI-Augmented Compliance Auditing for Cloud Systems: A Hybrid ML--LLM Approach},
  author    = {Iradukunda Ingabire, Moise},
  journal   = {Future Internet},
  publisher = {MDPI},
  year      = {2026},
  note      = {Under review, Manuscript ID: futureinternet-4270373}
}
```

---

**Institution:** Carnegie Mellon University Africa
**Author:** Moise Iradukunda Ingabire — mii@andrew.cmu.edu
