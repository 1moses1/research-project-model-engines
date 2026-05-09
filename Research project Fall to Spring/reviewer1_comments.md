# Reviewer 1 — Comments & Author Responses
**Manuscript ID:** futureinternet-4270373  
**Journal:** Future Internet (ISSN 1999-5903)  
**Review submitted:** 29 Apr 2026 16:22:02  

---

## Review Report Ratings

| Criterion | Rating |
|---|---|
| Quality of English | The English is fine and does not require any improvement |
| Does the introduction provide sufficient background and include all relevant references? | Can be improved |
| Is the research design appropriate? | Must be improved |
| Are the methods adequately described? | Must be improved |
| Are the results clearly presented? | Must be improved |
| Are the conclusions supported by the results? | Must be improved |
| Are all figures and tables clear and well-presented? | Must be improved |

---

## General Assessment (Reviewer)

The authors of the study address the problem of how to automate cybersecurity compliance auditing in resource-constrained environments using a hybrid AI approach (ML + LLM). The topic of the study is very relevant, especially for public-sector and SME deployments where commercial GRC/compliance tools may be too expensive.

A number of concerns and issues were identified and should be addressed by the authors:

---

## Comment 1
**Lines 92–94. No mention of Section 7 which exists.**

> **Response 1:** Thank you for this catch. The introduction (Section 1.4, Research Contributions) now explicitly references Section 7 (Future Work). Specifically, in the paragraph enumerating research contributions, we have added the sentence: *"Section 7 identifies open research directions including production institutional deployment pilots, expansion to additional African regulatory frameworks, and active learning strategies to reduce synthetic-data dependency."* The revised manuscript reflects this at lines 188–192.

---

## Comment 2
**Cost estimates (e.g. $50/month total deployment and $0.15/10K logs) are very vague and need clearer explanation: HW type, is storage included, is maintenance included, etc.**

> **Response 2:** Thank you for this important clarification request. We have updated the cost footnote in the manuscript (Section 4.5, Latency and Throughput) to explicitly state: *"Cost estimate: \$50/month assumes a 2-vCPU / 4 GB RAM cloud VM instance (e.g., AWS t3.small or equivalent); storage (\$0.023/GB-month EBS) and network transfer are excluded; software maintenance labor is excluded. The \$0.15/10K logs figure covers only OpenAI API calls at GPT-4o-mini pricing (\$0.15/1M input tokens, approximately 150 tokens/log); it excludes infrastructure, storage, and engineer time. Full deployment TCO depends heavily on log volume and staffing."* This more conservative framing appears in Section 4.5 of the revised manuscript.

---

## Comment 3
**Authors should pay attention to terminology. Terms like "compliance auditor", "classifier", "decision engine", "routing engine" are a little bit blended. Authors should distinguish components and roles more clearly.**

> **Response 3:** We agree. The revised manuscript uses the following consistent terminology throughout:
> - **Compliance Classifier**: the XGBoost v2 binary classifier that labels log events as compliant/non-compliant per RWNCSA control family.
> - **Evidence Router**: the rule-based TF-IDF vocabulary-coverage gate that decides which classifier to invoke (XGBoost if active TF-IDF features > 0; GPT-4o-mini otherwise).
> - **LLM Semantic Analyzer**: GPT-4o-mini invoked for out-of-vocabulary log types (Windows, HTTP).
> - **Audit Engine**: the orchestration backend that collects per-event labels, maps them to RWNCSA controls, and computes posture scores.
> 
> The deprecated term "decision engine" has been replaced throughout. A terminology clarification table is provided in Supplementary Appendix Section 7. The architecture diagram (Figure 1) label text has also been updated to reflect this vocabulary.

---

## Comment 4
**Metric inconsistency. Different metrics are used throughout the paper (F1, Accuracy, Macro-F1, …) without consistently specifying whether multilabel macro/micro/subset metrics are used.**

> **Response 4:** Thank you — this was a genuine inconsistency in the original manuscript. The revised manuscript now uses **macro-F1** (unweighted average of per-class F1 across binary compliant/non-compliant labels) as the primary metric throughout, with Wilson 95% confidence intervals consistently reported for all classification results. Specifically:
> - XGBoost v2: macro-F1 = 85.05%, test F1 = 85.45% (Wilson CI [84.9%, 86.0%]) — Section 4.1
> - LLM evaluation: macro average over 4 log types — Section 4.3
> - Adversarial validation: per-scenario detection rate (binary) + Wilson CI — Section 4.8
> - Cross-dataset generalization: per-dataset F1 + Wilson CI — Section 4.3
> - Hybrid evaluation: macro-F1 per system + Wilson CI — Section 4.4
>
> All tables now include "Wilson 95% CI" columns. The term "accuracy" is retained only where it adds interpretability alongside F1 (e.g., to show precision/recall trade-off direction). No subset or micro averaging is used; all multi-output results are computed per-label and then macro-averaged.

---

## Comment 5
**Extremely high values for some performance metrics which look unrealistic. Usually these unrealistic values are tied with problems in the data set or problems with methodology. The authors partially acknowledge this issue, but stronger validation is needed.**

> **Response 5:** We have fully resolved this. The originally reported 99.99% F1 was caused by **86.3% data leakage** in the synthetic training data: compliance labels were embedded verbatim in the `log_message` field (e.g., `"status=COMPLIANT"`, `"violation_type=non_compliant"`), allowing the TF-IDF features to trivially predict the label. Our Phase 0 audit (script: `scripts/data_audit.py`) identified 8 leakage pattern types across 86.3% of training rows. After fixing the data generator (`generate_synthetic_data_v2.py`), the XGBoost v2 test F1 dropped to **85.45%** (macro-F1: 85.05%), a realistic value consistent with the TF-IDF feature complexity and class balance. This fix and its impact are documented in Section 4.1 of the revised manuscript, with a footnote explicitly stating: *"The previously reported F1 of 99.99\% was caused by 86.3\% data leakage in the synthetic training corpus and is retracted."*

---

## Comment 6
**Heavy reliance on synthetic data. This fact significantly limits external validity. Real-life enterprise logs are noisy, inconsistent, incomplete, and adversarially messy. Need much stronger validation on real production datasets.**

> **Response 6:** We substantially expanded real-world validation in this revision:
> - **SSH (50% real)**: 86,000-line AWS EC2 honeypot log (`linux_auth.log`); Phase 2 LLM eval uses 50% real SSH events; Phase 4 cross-dataset generalization uses 100 real SSH lines. Result: F1 = 87.6% (in-vocabulary), demonstrating that the model generalizes to real SSH traffic with only a −2.1pp gap versus synthetic.
> - **Windows (100% real)**: Mordor APT3 dataset (`purplesharp_ad_playbook_I`), real Windows Security Event log from a live attack simulation. XGBoost F1 = 28.6% (out-of-vocabulary failure, well-documented); GPT-4o-mini F1 = 74.1% after EventID enrichment.
> - **HTTP (real enterprise proxy)**: SecRepo Squid proxy access log with internal RFC1918 IPs (10.105.x.x) and named users. LLM accuracy = 85.7% on 28 real samples (CI: [68.5%, 94.3%]), down from 95.5% on synthetic — confirming that real HTTP traffic (ad-tracker URLs, messaging apps) is meaningfully harder than clean synthetic templates.
> 
> We acknowledge that macOS logs remain 100% synthetic, and that no production Rwandan institutional logs were available. These limitations are explicitly stated in Section 5.7 (Limitations) and in the abstract.

---

## Comment 7
**The scope of the study is too broad. The authors should choose narrower scope in order to increase the impact of the paper.**

> **Response 7:** We agree that the original manuscript attempted to cover too many sub-problems simultaneously. In this revision, we have restructured the narrative around a single central contribution: **the vocabulary-coverage gating hybrid architecture and its empirical validation on real-world logs**. Specifically:
> - The theoretical formalization (Section 3.6) has been tightened to focus on the effectiveness function $C(k) = \alpha D_k + \beta V_k + \gamma R_k$ directly motivating the hybrid design.
> - Sections on Kubernetes scaling, live deployment, and resource utilization (Sections 4.5–4.7) are retained but clearly framed as implementation feasibility rather than core scientific contributions.
> - The paper's primary claim is now: *"A TF-IDF vocabulary-coverage gate routes log events to the appropriate classifier, combining XGBoost's low-latency SSH/syslog performance with GPT-4o-mini's semantic generalization for OOV log types, achieving 85.1% hybrid F1 at 6.4% FPR on real-world logs."*

---

## Comment 8
**Some claims made by the authors are too strong. E.g. "first methodologies", "proves insufficiency", "fundamental constraint" or "strictly more expressive" should be used only if they can be formally demonstrated.**

> **Response 8:** All identified strong claims have been revised:
> - *"first methodologies"* → removed; replaced with *"among the first to apply…"* with appropriate citations to position the work.
> - *"strictly more expressive"* → revised to *"more expressive"* (line 1295 of revised manuscript).
> - *"proves insufficiency"* → revised to *"empirically demonstrates insufficient performance"*.
> - *"fundamental constraint"* → revised to *"a practical constraint observed in our evaluation"*.
> - Conclusions now use conditional framing: *"suggests potential efficiency gains"*, *"may be adaptable"*, *"requires field validation before deployment claims"* — consistent with Reviewer 2's guidance.

---

## Comment 9
**Evaluation methodology needs clearer explanation of:**
1. Exact label generation process
2. How ground truth was created
3. Whether humans annotated logs independently
4. Class imbalance handling
5. Per-label metrics
6. Leakage prevention protocol
7. Confidence interval computation details

> **Response 9:** Each sub-point is addressed:
> 1. **Label generation**: Compliance labels are assigned by a deterministic rule engine in `generate_synthetic_data_v2.py` based on log fields (user, action, resource, status_code, anomaly_label) — the label is never embedded in the `log_message` field.
> 2. **Ground truth creation**: For synthetic data: rule-based (see above). For real SSH data: structural — `Accepted password`/`session opened` = compliant; `Failed password`/`Invalid user` = non-compliant. For real Windows data (Mordor APT3): EventID-based mapping (4624/5156/4634/4776/4688 = compliant; 4625/4648/4771/5145 = non-compliant).
> 3. **Independent human annotation**: No independent human annotation was performed. Ground truth for real data is structurally derived from log semantics. This is a limitation acknowledged in Section 5.7 and Supplementary Appendix Section 3.
> 4. **Class imbalance handling**: All evaluation sets are 50/50 balanced except the Windows Phase 4 set (50 compliant / 10 non-compliant from Mordor APT3, which naturally has more compliant events). No SMOTE or class weighting was applied; imbalance is reported in per-dataset tables.
> 5. **Per-label metrics**: Per-family F1 for all 14 RWNCSA control families is now provided in Table 3 of the revised manuscript and in full in Supplementary Appendix Section 1.
> 6. **Leakage prevention protocol**: Documented in Section 3.2 (Dataset Strategy): data generator verified to produce zero embedded compliance verdicts, zero control-ID references in `log_message`. Audit script `data_audit.py` checks 8 leakage pattern types.
> 7. **Wilson CI**: Wilson score interval at 95% confidence. Let p^ = observed proportion, n = sample size, z = 1.96. Then: CI = p^ ± z · √[(p^ · (1 − p^) + z²/4n) / n] / (1 + z²/n). Here z² = 3.84 for 95% confidence. All tables now include CI columns.

---

## Comment 10
**Comparing GPT-4o-mini and Llama with only 50 samples/type is too small for strong conclusions. Prompt wording and parsing procedures should be fully disclosed.**

> **Response 10:** Both issues are resolved:
> 1. **Sample size**: Expanded from n=50 to **n=200 per log type** (n=628 total; HTTP is limited to n=28 real SecRepo Squid samples — the only available real HTTP log source). This gives Wilson 95% CIs with ±3–5pp width at 90–97% accuracy levels, sufficient for the conclusions drawn. The HTTP CI [68.5%, 94.3%] reflects the smaller sample and is explicitly disclosed as a limitation.
> 2. **Llama comparison**: Removed from the manuscript. With n=50 the Llama comparison was underpowered and added confusion. The revised manuscript reports GPT-4o-mini only.
> 3. **Prompt disclosure**: The full system prompt is now quoted verbatim in Section 3.5 (Evolution to Semantic LLM Analysis) and reproduced in Supplementary Appendix Section 5.
> 4. **Response parsing**: The parsing procedure — extract first occurrence of `COMPLIANT` or `NON_COMPLIANT` from the response string; if neither found, classify as `NON_COMPLIANT` (conservative default) — is described in Section 3.5 and in `scripts/expanded_llm_eval_v2.py` (publicly available).

---
