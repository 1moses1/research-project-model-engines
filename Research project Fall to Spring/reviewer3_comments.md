# Reviewer 3 — Comments & Author Responses
**Manuscript ID:** futureinternet-4270373  
**Journal:** Future Internet (ISSN 1999-5903)  
**Review submitted:** 25 Apr 2026 22:45:34  
**Recommendation:** Major revision  
**Source:** peer-review-55756931.v1.pdf (attached document)

---

## Review Report Ratings

| Criterion | Rating |
|---|---|
| Quality of English | The English is fine and does not require any improvement |
| Does the introduction provide sufficient background and include all relevant references? | Can be improved |
| Is the research design appropriate? | Can be improved |
| Are the methods adequately described? | Can be improved |
| Are the results clearly presented? | Can be improved |
| Are the conclusions supported by the results? | Can be improved |
| Are all figures and tables clear and well-presented? | Can be improved |

---

## Comment 1 — Theoretical Formulation Lacks Contextual Linkage and Validation

**The theoretical formulation (e.g., multi-label model and effectiveness function) is relevant, but some equations lack proper contextual linkage and validation. Provide clearer derivations, define all variables explicitly, and include justification or references supporting the proposed formulations.**

> **Response 1:** Thank you for this feedback. The revised manuscript (Section 3.6, Multi-Label Formulation, and Section 5.3, Theoretical Contributions) now explicitly defines all variables and provides contextual linkage for each equation:
> 
> **Effectiveness function** $C(k) = \alpha D_k + \beta V_k + \gamma R_k$:
> - $D_k \in [0,1]$: detection capability for control $k$ — measured as the fraction of non-compliant events correctly classified by the ML/LLM pipeline.
> - $V_k \in [0,1]$: log coverage — fraction of events associated with control $k$ for which a log source is available.
> - $R_k \in [0,1]$: adversarial resistance — measured as detection rate under the 5 MITRE ATT&CK scenarios mapped to control $k$.
> - $\alpha, \beta, \gamma$: weighting coefficients (default: $\alpha=0.4$, $\beta=0.4$, $\gamma=0.2$); the manuscript now states these defaults explicitly and notes they can be adjusted for institution-specific priorities.
> 
> **Multi-label compliance model**: The relationship to NIST SP 800-53 and CIS Controls binary models is now stated explicitly: prior frameworks use $C_{\text{binary}}(k) \in \{0,1\}$; our model generalizes to a continuous score $C(k) \in [0,1]$, enabling prioritization. The claim is that continuous scoring is more expressive (not "strictly more expressive" — this phrasing has been softened per Reviewer 1's Comment 8).
> 
> Citations supporting continuous compliance scoring have been added in Section 5.3 (NIST SP 800-37 Rev. 2, CVSS score model).

---

## Comment 2 — Near-100% F1-Score on Synthetic Data Is Unrealistic

**The reported performance metrics (e.g., near 100% F1-score on synthetic data) are unrealistic and indicate potential data leakage or overfitting. Include stricter validation protocols, additional real-world datasets, and more conservative interpretations of results.**

> **Response 2:** The 99.99% F1 score has been fully resolved:
> 
> **Root cause**: Phase 0 audit (`scripts/data_audit.py`) found **86.3% data leakage** — compliance labels were embedded as plaintext in the `log_message` field (e.g., `"compliance_status=COMPLIANT"`, `"anomaly_type=violation"`). The TF-IDF vectorizer trivially learned these label strings, producing a near-perfect classifier that failed on any real-world input.
> 
> **Fix**: The synthetic data generator was rewritten (`generate_synthetic_data_v2.py`). The new generator: (1) never embeds compliance status or control IDs in `log_message`; (2) generates log messages from format templates (syslog, Apache CLF, Windows Event format) that are realistic but label-free; (3) was verified with zero embedded verdicts across 150,000 training rows.
> 
> **Corrected performance**: XGBoost v2 test F1 = **85.45%**, macro-F1 = 85.05%, accuracy = 87.14%. 5-fold CV F1 = 85.20% ± 0.25%. These values are consistent with the feature complexity and are validated on a held-out test set with no fold contamination.
> 
> The original 99.99% figure is explicitly retracted in Section 4.1 of the revised manuscript with the sentence: *"The previously reported F1 of 99.99% was caused by 86.3% data leakage in the synthetic training corpus and is retracted."*

---

## Comment 3 — XGBoost vs. LLM Comparison Is Not Entirely Fair

**The generalization gap analysis is valuable; however, the comparison between XGBoost and LLMs is not entirely fair due to differences in evaluation settings and sample sizes. Standardize the evaluation protocol across models and provide statistically robust comparisons.**

> **Response 3:** We have standardized the evaluation protocol through the new **Hybrid System Combined Evaluation** (Section 4.4, Phase 5 addition):
> 
> - **Same dataset**: All three systems (XGBoost alone, GPT-4o-mini alone, Hybrid) are evaluated on the **identical 180 real-world logs** (100 SSH, 60 Windows, 20 HTTP).
> - **Same metrics**: Accuracy, precision, recall, macro-F1, FPR, and Wilson 95% CI reported for all three systems in the same table.
> - **Same ground truth**: Labels derived by the same structural rules (SSH by keyword, Windows by EventID, HTTP by status code).
> 
> Results (n=180):
> | System | F1% | FPR% | F1 CI 95% |
> |---|---|---|---|
> | XGBoost v2 alone | 62.4% | 54.5% | [74.0%, 91.0%] |
> | GPT-4o-mini alone | 90.8% | 6.4% | [82.5%, 96.0%] |
> | Hybrid combined | 85.1% | 6.4% | [70.8%, 88.8%] |
> 
> The comparison is now fair: same logs, same labels, same metrics. The previously unfair aspect (XGBoost evaluated on synthetic data at 85.45% while LLM evaluated on mixed real/synthetic at 94.75%) is resolved by evaluating both on the identical real-world set.
> 
> Note: The Hybrid F1 (85.1%) is lower than GPT-4o-mini alone (90.8%) because XGBoost's SSH recall is 78.0% (catches 39/50 non-compliant SSH events) versus GPT-4o-mini's 92.0% (catches 46/50). The hybrid routes SSH to XGBoost (lower FPR = 0.0% vs. GPT-4o-mini's SSH FPR = 0.0%), so the trade-off is SSH recall for API cost savings.

---

## Comment 4 — LLM Evaluation Lacks Sufficient Statistical Rigor

**The LLM evaluation lacks sufficient statistical rigor (e.g., small sample sizes such as n = 50 per log type). Increase sample sizes, include confidence intervals consistently, and avoid overgeneralizing results such as "up to 100% accuracy."**

> **Response 4:** All three issues are resolved:
> 
> 1. **Sample size**: Expanded from n=50 to **n=200 per log type** (n=628 total; HTTP is limited to n=28 real SecRepo Squid samples — the only available real HTTP log source; other types are n=200). At 97.5% accuracy (Windows), Wilson 95% CI = [94.3%, 98.9%] — a ±2.3pp interval sufficient for the conclusions drawn.
> 
> 2. **Confidence intervals**: Wilson 95% CI is now reported for every result in every table throughout the manuscript. For reference, the updated LLM results with CIs:
>    | Log Type | Acc% | Wilson 95% CI |
>    |---|---|---|
>    | SSH Authentication | 89.5% | [84.5%, 93.0%] |
>    | Windows Security Events | 97.5% | [94.3%, 98.9%] |
>    | HTTP/API Access | 85.7% | [68.5%, 94.3%] |
>    | macOS System/Service | 96.5% | [93.0%, 98.3%] |
>    | **Macro average** | **92.3%** | — |
> 
>    Note: HTTP accuracy was updated from 95.5% (synthetic, n=200) to 85.7% (real SecRepo Squid, n=28). The wider CI [68.5%, 94.3%] for HTTP reflects the smaller real sample size and is explicitly acknowledged as a limitation.
> 
> 3. **Overgeneralization**: The phrase *"up to 100% accuracy"* has been removed throughout. Results are reported as point estimates with CIs. The 100.0% detection rates in the adversarial validation table are accompanied by Wilson CIs [92.7%, 100.0%] to communicate the uncertainty.

---

## Comment 5 — Adversarial Validation Is Limited in Scope

**The adversarial validation experiments are interesting but limited in scope (only two scenarios). Expand the range of adversarial tests and provide a more systematic evaluation aligned with established frameworks such as MITRE ATT&CK.**

> **Response 5:** Adversarial validation has been expanded from **2 to 5 MITRE ATT&CK v14 scenarios**. The revised Section 4.8 reports:
> 
> | MITRE ID | Scenario | Detection Rate | Wilson 95% CI | Data Source |
> |---|---|---|---|---|
> | T1059.001 | PowerShell Fileless Shell | 86.0% | [73.8%, 93.0%] | Synthetic |
> | T1190 | XSS/SQLi WAF Bypass | 100.0% | [92.9%, 100.0%] | Synthetic |
> | T1110 | SSH Brute Force | 100.0% | [92.9%, 100.0%] | Real (linux\_auth.log) |
> | T1078 | Lateral Movement Valid Accounts | 100.0% | [92.7%, 100.0%] | Real (Mordor APT3) |
> | T1562.001 | Impair Defenses: Disable Tools | 78.0% | [64.8%, 87.2%] | Synthetic |
> 
> **Macro detection rate: 92.8%**. The compliant-log baseline FPR is **0.0%** (n=75 real SSH+PAM logs), establishing that the model does not over-alert on normal traffic.
> 
> Each scenario is mapped to its corresponding RWNCSA control (SC-7, SC-28, IA-1, AC-2, AU-9) and NIST SP 800-53 reference control, making the evaluation systematically aligned with the MITRE ATT&CK framework. The two scenarios with non-zero evasion rates (T1059.001 at 14.0%, T1562.001 at 22.0%) are analyzed: both involve service-lifecycle log formats where SSH/syslog vocabulary tokens overlap with adversarial patterns.

---

## Comment 6 — Some Conclusions Are Overstated

**The conclusions are generally aligned with the results; however, some claims are overstated (e.g., cost-efficiency and general applicability across contexts).**

> **Response 6:** Overstatements have been removed from the conclusions (Section 7). Specific changes:
> - Cost-efficiency claim: Now framed as *"cost-accessible deployment at ≤\$50/month (infrastructure) + \$0.15/10K logs (API calls), with full TCO depending on log volume and staffing"* — not a comparative efficiency claim.
> - General applicability: Now states *"the RWNCSA framework serves as the primary validation context; adaptation to other African national frameworks requires control-mapping work and revalidation of the routing vocabulary for each framework's predominant log sources."*
> - All conclusions include explicit scope qualifiers: *"within the evaluated domains"*, *"for log types with in-vocabulary TF-IDF coverage"*, *"pending production institutional deployment pilots."*

---

## Comment 7 — Overall: Experimental Validation Not Yet Sufficiently Robust

**The overall contribution is relevant, particularly the hybrid ML–LLM approach and effectiveness-based compliance model; however, the experimental validation is not yet sufficiently robust for publication. Strengthen empirical validation, improve statistical rigor, and refine claims before reconsideration.**

> **Response 7:** We believe the revision substantively addresses the robustness concerns. To summarize the empirical improvements made:
> 
> | Issue | Original | Revised |
> |---|---|---|
> | XGBoost F1 | 99.99% (leaked) | 85.45% (leakage-free, verified) |
> | LLM sample size | n=50/type | n=200/type (n=628 total; HTTP n=28 real samples) |
> | LLM models compared | GPT-4o-mini + Llama | GPT-4o-mini only (Llama removed — underpowered) |
> | Adversarial scenarios | 2 | 5 MITRE ATT&CK v14 |
> | Real-world validation | SSH only | SSH + Windows + HTTP (real sources) |
> | Confidence intervals | Inconsistent | Wilson 95% CI in every table |
> | Joint system evaluation | None | Hybrid combined eval (same 180 logs, 3 systems) |
> | Metric standardization | Mixed F1/Accuracy/Macro | Macro-F1 + Wilson CI throughout |
> | Strong claims | "first", "proves", "strictly more" | Moderated throughout |
> | Reproducibility | Insufficient | Full supplementary appendix + repo |
> 
> We respectfully submit that these changes meaningfully strengthen the empirical foundation of the paper while accurately representing the remaining limitations (synthetic macOS data, limited HTTP sample size, no production institutional pilot).

---
