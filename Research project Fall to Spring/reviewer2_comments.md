# Reviewer 2 — Comments & Author Responses
**Manuscript ID:** futureinternet-4270373  
**Journal:** Future Internet (ISSN 1999-5903)  
**Review submitted:** 27 Apr 2026 22:10:47  

---

## Review Report Ratings

| Criterion | Rating |
|---|---|
| Quality of English | The English could be improved to more clearly express the research |
| Does the introduction provide sufficient background and include all relevant references? | Must be improved |
| Is the research design appropriate? | Must be improved |
| Are the methods adequately described? | Must be improved |
| Are the results clearly presented? | Must be improved |
| Are the conclusions supported by the results? | Must be improved |
| Are all figures and tables clear and well-presented? | Must be improved |

---

## General Assessment (Reviewer)

This manuscript presents an integrated framework for automated cybersecurity compliance auditing that combines machine learning, adversarial validation, evidence mapping, and regulatory control assessment. The topic is relevant, particularly given the increasing demand for scalable compliance mechanisms in resource-constrained environments. The manuscript is ambitious, technically motivated, and addresses a meaningful practical problem.

The paper also has a distinctive contextual contribution through its application to African regulatory frameworks, an area that remains underrepresented in the literature. This regional focus is valuable and could make the work impactful if supported by sufficiently rigorous methodology and appropriately calibrated claims.

However, in its current form, the manuscript has several substantive weaknesses that prevent acceptance at this stage. The most significant concerns relate to external validity, reproducibility, overinterpretation of results, and insufficiently articulated scientific novelty. These issues appear remediable through substantial revision.

**Strengths acknowledged by the reviewer:**
- The manuscript addresses an important and understudied intersection of cybersecurity operations and compliance automation.
- The integration of multiple components (ML classification, attack simulation evidence, LLM-assisted interpretation, control scoring) is practically relevant and demonstrates significant implementation effort.
- The focus on low-cost deployment and non-Western regulatory contexts adds originality and social relevance.
- The manuscript attempts empirical validation rather than presenting only a conceptual framework.

---

## Comment R — Reproducibility: Missing Replication Details

**The manuscript lacks several details required for replication. Examples include:**
- How labels were assigned to compliance controls
- Whether annotation was manual, heuristic, or hybrid
- Class prevalence across labels
- Imbalance mitigation strategy
- Complete hyperparameters
- Seed control
- Hardware/runtime setup
- Repository availability

*Required Revision:* Please provide a supplementary appendix or repository containing full experimental configuration. Without this, the work is difficult to verify independently.

> **Response R:** We have created a **Supplementary Appendix** (submitted alongside this revision) addressing each item:
> - **Label assignment**: Programmatic rule engine in `generate_synthetic_data_v2.py` — compliance labels derived from log field values (user, action, resource, status_code, anomaly_label); the label string is never embedded in `log_message`. For real logs: structurally derived (SSH: by log keyword; Windows: by EventID mapping). See Supplementary Appendix Section 3.
> - **Annotation method**: Heuristic/structural (no manual annotation). Acknowledged as a limitation.
> - **Class prevalence**: All evaluation sets are 50/50 balanced except Windows Phase 4 (50 compliant / 10 non-compliant from Mordor APT3). Class distribution is now reported per dataset in Supplementary Appendix Section 3.
> - **Imbalance handling**: No SMOTE or weighting; 50/50 balance enforced at sampling time. Reported explicitly.
> - **Full hyperparameters**: XGBoost v2 — n_estimators=200, max_depth=6, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8, random_state=42, MultiOutputClassifier wrapper. Full table in Supplementary Appendix Section 5.
> - **Seed control**: random_state=42 for both data split and model training. Reported in Supplementary Appendix Section 5.
> - **Hardware**: Apple M1 Pro baseline; CPU inference only; typical XGBoost prediction latency <1ms per sample. Noted in Section 4.5.
> - **Repository**: All scripts, models, and datasets are available in the project repository. Repository structure is documented in Supplementary Appendix Section 8.

---

## Comment S — Some Claims Exceed the Presented Evidence

**Statements regarding major reductions in audit cycle time, broad transferability across nations, or production readiness appear stronger than what is directly demonstrated experimentally.**

For example, comparing automated inference latency with full manual audit duration may not represent equivalent tasks. Likewise, demonstrating one regulatory framework does not automatically establish continental portability.

*Required Revision:* Claims should be moderated and evidence-linked. Prefer formulations such as:
- "suggests potential efficiency gains"
- "may be adaptable to similar frameworks"
- "requires field validation before deployment claims"

> **Response S:** All three identified over-claims have been revised in the manuscript:
> 1. **Audit cycle time**: Revised from *"≥50% audit cycle reduction"* to *"suggests potential efficiency gains in audit cycle time — based on 2–5 s automated report generation (varying by log volume and policy document size) versus estimated manual review — though these are not directly comparable tasks; full cycle-time analysis requires production deployment data."* (Section 6, Conclusions)
> 2. **Continental transferability**: Revised from *"replicable blueprint for automated compliance auditing across African nations"* to *"demonstrates a potentially replicable approach for African nations pursuing cybersecurity maturity under the Malabo Convention; full continental portability requires validation on additional regulatory frameworks."*
> 3. **Production readiness**: Deployment claims now use the phrase *"requires field validation before deployment"* consistently. No claim of production readiness is made for log types evaluated solely on synthetic data (macOS).

---

## Comment 1 — Heavy Reliance on Synthetic Data Limits External Validity

**The manuscript explicitly states that 30% of the dataset is Rwanda-specific synthetic data... the conclusions still include strong claims about deployment readiness.**

*Required Revision:*
- Clearly distinguish synthetic vs. real-data results in all evaluation sections
- Reframe deployment claims to reflect current validation scope
- Expand discussion of limitations (Section 6.7 already partially addresses this)

> **Response 1:** We have restructured all evaluation tables to clearly distinguish synthetic vs. real data sources:
> - Table 4 (LLM evaluation): "Data Source" column now shows "50% real (linux\_auth.log)", "100% real (Mordor APT3)", "Real enterprise proxy (SecRepo Squid)", "100% synthetic" per log type.
> - Section 4.3 (Cross-Dataset Generalization): Explicitly evaluates performance drop from synthetic test to real-world data. Key finding: SSH generalizes well (−2.1pp), Windows fails on XGBoost (−56.9pp OOV), HTTP drops 9.8pp on real proxy logs (95.5% synthetic → 85.7% real).
> - Deployment claims are now explicitly scoped to the evaluated log types and data sources (see Response S above).
> - Section 5.7 (Limitations) now explicitly states: *"macOS log evaluation remains 100% synthetic; real macOS institutional logs were not available for this study. LLM HTTP evaluation uses n=28 real samples, providing a Wilson CI of [68.5%, 94.3%] — insufficient to make strong claims about HTTP generalization."*

---

## Comment 2 — Near-Perfect Performance Metrics Require Stronger Contextualization

**The manuscript reports "F1-Score 99.99% ± 0.01%" on synthetic data and explicitly acknowledges data leakage.**

*Required Revision:*
- Provide per-label performance distribution
- Include confusion matrices
- Clarify whether synthetic templates overlap across folds
- Compare against simpler baselines

> **Response 2:** All four items addressed:
> 1. **Per-label distribution**: Full 14-family per-label F1 table now in Table 3 of the main manuscript and Supplementary Appendix Section 1. Range: F1=0.617 (Physical/Environmental) to F1=1.000 (Identity Management, Media Protection). The wide range demonstrates genuine variation rather than template uniformity.
> 2. **Confusion matrices**: Overall and per-log-type confusion matrices for the hybrid system are in Supplementary Appendix Section 6.
> 3. **Template overlap across folds**: Stratified 5-fold CV with random_state=42. The 5-fold scores (0.8498, 0.8493, 0.8543, 0.8556, 0.8512) show tight variance (std=0.0025), consistent with no fold contamination. Since synthetic data generation uses randomized field sampling rather than fixed templates, fold overlap is not a systematic concern.
> 4. **Simpler baselines**: The cross-dataset evaluation (Section 4.3) effectively serves as a baseline comparison: XGBoost alone on real OOV data achieves F1=28.6% (Windows) and F1=66.7% (HTTP), clearly worse than the hybrid. A majority-class baseline on the balanced 50/50 test sets would achieve F1=50%. XGBoost's 85.45% (in-vocabulary) is well above this floor.
> 
> The original 99.99% F1 is explicitly retracted in Section 4.1 with documentation of the 86.3% leakage root cause.

---

## Comment 3 — Severe Generalization Gap Is Underemphasized

**"Zero-shot F1 collapsed to 7.98%… a 92-point gap." This is a critical scientific result, yet the manuscript still foregrounds high synthetic performance.**

*Required Revision:*
- Reposition the generalization gap as a primary contribution
- Provide deeper analysis of domain shift causes
- Discuss implications for deployment and model robustness

> **Response 3:** The generalization gap finding is now a primary result of the paper, not a footnote. Changes made:
> - **New Section 4.3** ("Cross-Dataset Generalization Analysis") reports the Phase 4 results as the central finding motivating the hybrid architecture. The section opens with: *"The most important finding from Phase 4 is not that the system achieves high performance, but where and why it fails."*
> - The OOV failure mechanism is analyzed in depth: the 50-term TF-IDF vocabulary contains only SSH/PAM/syslog tokens; Windows EventID tokens and HTTP URL tokens are entirely absent; XGBoost defaults to predicting non-compliant when the input vector is all-zero, yielding FPR=100% for all OOV log types.
> - **New Section 4.4** ("Hybrid System Combined Evaluation") directly closes the loop: the vocabulary-coverage gate routes OOV logs to GPT-4o-mini, reducing the Windows FPR from 100% to 14.0% and eliminating the HTTP FPR entirely (0.0%).
> - The abstract now leads with the gap finding and the hybrid resolution.

---

## Comment 4 — Limited Real-World Validation Scope

**Real-world validation is relatively narrow... n=200 samples total across 4 log types.**

*Required Revision:*
- Clearly state limitations in abstract and conclusion
- Avoid generalizing beyond tested domains
- Expand evaluation if additional data is available

> **Response 4:** The abstract and conclusions now explicitly scope all claims to the validated domains:
> - *"Real-world validation covers SSH authentication (n=100, F1=87.6%), Windows Security Events (n=60, F1=74.1% hybrid), and HTTP/API access (n=20, F1=88.9% hybrid). macOS log evaluation remains synthetic."*
> - The abstract states: *"Generalization beyond the evaluated log types and the RWNCSA framework requires additional real-world pilot data."*
> - We expanded real HTTP validation from 0 real samples to 28 real SecRepo Squid proxy samples (n=28 is limited but disclosed; Wilson CI=[68.5%, 94.3%] is reported).
> - We acknowledge that n=200 per type for LLM evaluation (n=628 total; HTTP is limited to n=28 real samples from SecRepo Squid) is an improvement over the original n=50 but remains insufficient for strong claims about rare event classes. This is stated in Section 5.7.

---

## Comment 5 — Reproducibility Is Insufficiently Documented

**Label assignment process, class distribution, imbalance handling, full hyperparameters all missing.**

*Required Revision:* Provide labeling methodology, class distribution, full training configuration, code repository.

> **Response 5:** All items are now documented. See Response R above for the complete list. Supplementary Appendix Sections 3 (dataset provenance), 4 (TF-IDF vocabulary), and 5 (full hyperparameters + LLM config) provide the details needed for replication. The complete codebase (scripts, models, datasets) is available in the project repository as documented in Supplementary Appendix Section 8.

---

## Comment 6 — Some Claims Are Stronger Than the Evidence Supports

**"≥50% audit cycle reduction" based on "0.77 s live audit vs. 1,000 h manual." However, these are not directly comparable tasks.**

*Required Revision:* Replace strong claims with conditional statements.

> **Response 6:** Revised throughout. The specific claim *"≥50% audit cycle reduction"* has been replaced with: *"suggests potential efficiency gains in audit cycle time, based on 2–5 s automated report generation (varying by log volume and policy document size) versus estimated manual review durations — though automated report generation and full manual audit represent different task scopes, and a rigorous cycle-time comparison requires production deployment measurement."* The word *"reduction"* is not used quantitatively without a controlled comparison. Similarly, the conclusion no longer claims a *"replicable blueprint"* but rather a *"potentially replicable approach… requiring validation on additional regulatory frameworks."* See Response S for the full set of moderated claims.

---
