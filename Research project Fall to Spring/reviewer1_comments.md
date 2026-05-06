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

> Response 1: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 2
**Cost estimates (e.g. $50/month total deployment and $0.15/10K logs) are very vague and need clearer explanation: HW type, is storage included, is maintenance included, etc.**

> Response 2: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 3
**Authors should pay attention to terminology. Terms like "compliance auditor", "classifier", "decision engine", "routing engine" are a little bit blended. Authors should distinguish components and roles more clearly.**

> Response 3: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 4
**Metric inconsistency. Different metrics are used throughout the paper (F1, Accuracy, MAcro-F1, …) without consistently specifying whether multilabel macro/micro/subset metrics are used.**

> Response 4: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 5
**Extremely high values for some performance metrics which look unrealistic. Usually these unrealistic values are tied with problems in the data set or problems with methodology. The authors partially acknowledge this issue, but stronger validation is needed.**

> Response 5: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 6
**Heavy reliance on synthetic data. This fact significantly limits external validity. Real-life enterprise logs are noisy, inconsistent, incomplete, and adversarially messy. Need much stronger validation on real production datasets.**

> Response 6: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 7
**The scope of the study is too broad. The authors should choose narrower scope in order to increase the impact of the paper.**

> Response 7: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 8
**Some claims made by the authors are too strong. E.g. "first methodologies", "proves insufficiency", "fundamental constraint" or "strictly more expressive" should be used only if they can be formally demonstrated.**

> Response 8: [PLACEHOLDER — to be completed after manuscript revision]

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

> Response 9: [PLACEHOLDER — to be completed after manuscript revision]

---

## Comment 10
**Comparing GPT-4o-mini and Llama with only 50 samples/type is too small for strong conclusions. Prompt wording and parsing procedures should be fully disclosed.**

> Response 10: [PLACEHOLDER — to be completed after manuscript revision]

---
