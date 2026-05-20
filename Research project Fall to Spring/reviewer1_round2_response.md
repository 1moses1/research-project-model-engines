# Author's Notes to Reviewer 1 — Round 2
**Manuscript ID:** futureinternet-4270373
**Round:** 2

---

We sincerely thank Reviewer 1 for the thorough and encouraging re-evaluation of the revised manuscript. We are pleased that the data leakage correction, expanded validation, and toned-down claims were recognized as meaningful improvements. Below we address the two remaining issues raised.

---

## Issue 1 — Old numbers (99.99%, 99.88%, 100%) remaining in the manuscript

**Reviewer comment:** "The revised paper still contains remnants of old numbers in several places (e.g. 99.99%, 99.88%, 100%) inside the uploaded manuscript itself."

**Response:** We have carefully reviewed every occurrence of these figures in the revised manuscript and addressed each category:

**99.99% (7 occurrences):** All occurrences are in explicit retraction context — e.g., *"the previously reported 99.99% F1, attributable to an 86.3% data-leakage rate, is retracted"* — and are therefore intentional and necessary for transparency. No change was made to these, as removing them would obscure the correction narrative.

**99.88% (2 occurrences — fixed):** This figure appeared in the Phase 2 narrative (Section 3.5) describing fine-tuning on 5% of SecRepo SSH logs, and in the RQ3 evidence row of Table 9. While the 99.88% result itself is legitimate (SSH-domain fine-tuning on structured logs does converge to near-perfect performance given sufficient labeled data), we agree it could be misread as another inflated general claim. Both occurrences have been updated with an explicit scope qualifier:

> *"99.88% F1 (on the same SSH domain; this result reflects SSH-specific vocabulary adaptation and should not be interpreted as cross-domain or general-purpose performance)"*

And in Table 9 (RQ summary):
> *"99.88% (SSH-domain fine-tune only)"*

**100% occurrences:** All remaining 100% figures are either: (a) the 100% total in the dataset composition table; (b) per-family F1 values for IA and MP families, each accompanied by Wilson 95% CIs (`[99.7%, 100.0%]` and `[99.5%, 100.0%]`); (c) adversarial detection rates for T1190, T1110, and T1078 scenarios, each accompanied by Wilson 95% CIs (`[92.7%–92.9%, 100.0%]`); or (d) the 100% FPR reported for OOV Windows/HTTP log types, which is explained as expected architectural behavior (vocabulary absence) rather than a performance claim. None of these represent inflated performance claims and all are appropriately bounded by confidence intervals or contextual explanation.

---

## Issue 2 — LLM sample size too small for broad generalization claims

**Reviewer comment:** "The evaluation is still relatively small for strong claims regarding general semantic generalization. The study is now acceptable for exploratory/applied evaluation, but not strong enough for broader claims about LLM superiority in cybersecurity auditing."

**Response:** We fully agree with this framing and have made targeted edits to bring the manuscript's language into alignment with the exploratory/applied scope of the evaluation. Specifically:

1. **Phase 3 description (Section 3.5):** The phrase *"a direct solution to the generalization gap"* has been replaced with *"preliminary evidence that semantic LLM reasoning can address the vocabulary-based generalization gap at acceptable deployment cost, while remaining insufficient for broad claims of LLM superiority in cybersecurity auditing without larger-scale validation."*

2. **Finding F4 (Section 4.3):** The phrase *"consistently superior to XGBoost zero-shot across all categories"* has been updated to *"consistently higher than XGBoost zero-shot across all evaluated categories; this constitutes preliminary applied validation and does not support broad claims of LLM superiority in general cybersecurity auditing contexts."*

3. **Statistical Scope paragraph (Section 4.3):** A new clarifying sentence has been added: *"These sample sizes support exploratory and applied evaluation conclusions; they are not sufficient to support broad claims of LLM superiority in general cybersecurity auditing, and results should be interpreted as preliminary evidence for the specific log types and compliance context evaluated."*

We believe these changes accurately represent the contribution as a solid applied system validated in a specific regulatory context, consistent with the Reviewer's own characterization of the work as *"a solid applied contribution to the field of AI-assisted cybersecurity compliance auditing."*

---

We thank Reviewer 1 again for the constructive and detailed engagement across both review rounds.
