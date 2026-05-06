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

> Response R: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment S — Some Claims Exceed the Presented Evidence

**Statements regarding major reductions in audit cycle time, broad transferability across nations, or production readiness appear stronger than what is directly demonstrated experimentally.**

For example, comparing automated inference latency with full manual audit duration may not represent equivalent tasks. Likewise, demonstrating one regulatory framework does not automatically establish continental portability.

*Required Revision:* Claims should be moderated and evidence-linked. Prefer formulations such as:
- "suggests potential efficiency gains"
- "may be adaptable to similar frameworks"
- "requires field validation before deployment claims"

> Response S: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 1 — Heavy Reliance on Synthetic Data Limits External Validity

**The manuscript explicitly states that 30% of the dataset is Rwanda-specific synthetic data, used to cover missing control classes, while legacy datasets such as NSL-KDD account for 52%. Furthermore, the authors acknowledge: "Synthetic data… ensures complete label coverage for all 143 control families." This indicates that a large portion of the learning signal is artificially generated rather than observed from real systems.**

Although the authors partially acknowledge this limitation ("Validation on production Rwandan institution logs remains for pilot deployment"), the conclusions still include strong claims about deployment readiness.

*Issue:* The dependence on synthetic augmentation is not peripheral—it directly affects generalization and real-world applicability.

*Required Revision:*
- Clearly distinguish synthetic vs. real-data results in all evaluation sections
- Reframe deployment claims to reflect current validation scope
- Expand discussion of limitations (Section 6.7 already partially addresses this)

> Response 1: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 2 — Near-Perfect Performance Metrics Require Stronger Contextualization

**The manuscript reports "F1-Score 99.99% ± 0.01%" on synthetic data and explicitly acknowledges "All three baseline models achieved 100% accuracy—a clear red flag." Additionally, the authors identify data leakage: "status_code exhibited −0.97 correlation with the compliance label."**

While it is commendable that the authors detected and corrected this issue, the presence of near-perfect results—even after correction—remains problematic without deeper statistical justification.

*Issue:* Such performance likely reflects low variability and template-driven structure rather than robust learning.

*Required Revision:*
- Provide per-label performance distribution
- Include confusion matrices
- Clarify whether synthetic templates overlap across folds
- Compare against simpler baselines

> Response 2: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 3 — Severe Generalization Gap Is Underemphasized

**One of the most important findings is: "Zero-shot F1 collapsed to 7.98%… a 92-point gap." This is a critical scientific result, yet the manuscript still foregrounds high synthetic performance.**

*Issue:* The generalization failure is more informative than the benchmark success.

*Required Revision:*
- Reposition the **generalization gap** as a primary contribution
- Provide deeper analysis of domain shift causes
- Discuss implications for deployment and model robustness

> Response 3: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 4 — Limited Real-World Validation Scope

**Real-world validation is relatively narrow:**
- SecRepo logs (single domain: SSH authentication)
- LLM evaluation: n = 200 samples total across 4 log types

The manuscript itself acknowledges: "Validation on production institutional logs (n ≥ 500 per type) remains for future deployment pilots."

*Issue:* This validation scope is insufficient to support broad generalization claims.

*Required Revision:*
- Clearly state limitations in abstract and conclusion
- Avoid generalizing beyond tested domains
- Expand evaluation if additional data is available

> Response 4: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 5 — Reproducibility Is Insufficiently Documented

**While the manuscript provides high-level model details, several key aspects are missing:**
- Label assignment process for 143 controls
- Class distribution across labels
- Handling of imbalance in multi-label setting
- Full hyperparameter configuration

For example, the manuscript states "Multi-output XGBoost via MultiOutputClassifier" but does not specify weighting, thresholding, or imbalance strategies.

*Issue:* The experiments cannot be fully reproduced with the current level of detail.

*Required Revision — Provide:*
- Labeling methodology
- Class distribution statistics
- Full training configuration (hyperparameters, seeds)
- Code repository details (partially mentioned in Data Availability)

> Response 5: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 6 — Some Claims Are Stronger Than the Evidence Supports

**The manuscript claims "≥50% audit cycle reduction" based on "0.77 s live audit vs. 1,000 h manual." However, these are not directly comparable tasks (partial automated audit vs. full manual audit across all controls).**

Similarly, the conclusion states: "replicable blueprint for automated compliance auditing across African nations."

*Issue:* These claims extend beyond the experimental evidence.

*Required Revision:*
- Replace strong claims with conditional statements
- Align conclusions strictly with demonstrated results

> Response 6: [PLACEHOLDER — to be completed after manuscript revision]

---
