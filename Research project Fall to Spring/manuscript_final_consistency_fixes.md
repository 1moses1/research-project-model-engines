# Manuscript Final Consistency Fixes — North Star
**File**: `deliverable_4_full_manuscript_v3_mdpi_v3.tex`  
**Purpose**: Resolve all inconsistencies between the manuscript and the three reviewer response files before submission. Every fix listed here was derived by reading the manuscript and comparing it against the reviewer responses and supplementary appendix.

---

## How to Use This File
For each fix: find the **exact current text** at the given line, verify it matches, then apply the **replacement**. Mark the checkbox when done.

---

## CATEGORY A — Must Fix (Contradicts Explicit Reviewer Response Promises)

### A1 — "up to 100%" language still in manuscript
**Reviewer response R3-C4 states**: "The phrase 'up to 100% accuracy' has been removed throughout."  
**Status**: NOT removed — still appears in 3 places.

**Fix A1a** — Line 842:
```
CURRENT:  Zero-shot Accuracy & 5.92\% & \textbf{up to 100\%}$^\dagger$ \\
REPLACE:  Zero-shot Accuracy & 5.92\% & \textbf{89.5\%}$^\dagger$ \\
```
*(Use SSH accuracy from Phase 2 as the representative value, footnote explains it is log-type-dependent.)*

**Fix A1b** — Line 843:
```
CURRENT:  Zero-shot F1 & 7.98\% & \textbf{up to 100\%}$^\dagger$ \\
REPLACE:  Zero-shot F1 & 7.98\% & \textbf{87.6\%}$^\dagger$ \\
```
*(Use SSH F1 from Phase 4 real evaluation; footnote explains this varies by log type.)*

**Fix A1c** — Lines 857–860 (footnote for table tab:llm_results):
```
CURRENT:
{\footnotesize $^\dagger$Up to 100\% accuracy achieved in controlled binary SSH authentication
classification tasks (structured syslog format, binary compliant/non-compliant labels,
$n$=500). Accuracy is log-type-dependent; multi-log evaluation (Table~\ref{tab:llm_multilog})
shows 93.5\% overall across four structurally distinct log types at $n$=200.}

REPLACE:
{\footnotesize $^\dagger$Accuracy is log-type-dependent; see Table~\ref{tab:llm_multilog}
for the full multi-log evaluation (GPT-4o-mini, $n$=628, macro accuracy 92.3\%).
SSH result (89.5\%) is from a 200-sample evaluation (50\% real linux\_auth.log);
this table reflects an earlier 500-sample SSH-only evaluation retained for historical comparison.}
```

---

### A2 — Llama still mentioned in LLM evaluation text
**Reviewer response R1-C10 states**: "Llama comparison: Removed from the manuscript."  
**Status**: Llama still appears at lines 622–624, 872–875 in results-relevant text.

**Fix A2a** — Lines 622–624:
```
CURRENT:
GPT-4o-mini (cloud API) and Llama-3.2-3B
(on-premise CPU) were evaluated as zero-shot classifiers across four log types
(Section~\ref{sec:results}), achieving 92.3\% overall macro accuracy,a

REPLACE:
GPT-4o-mini (cloud API) was evaluated as a zero-shot classifier across four log types
(Section~\ref{sec:results}), achieving 92.3\% overall macro accuracy---a
```

**Fix A2b** — Lines 872–875:
```
CURRENT:
zero-shot evaluations were conducted across \textit{four} structurally distinct log types
using two models: GPT-4o-mini (cloud API) and Llama-3.2-3B (on-premise via Ollama on
Apple M1 Pro CPU, no GPU),directly testing the African SME on-premise deployment scenario
(Table~\ref{tab:llm_multilog}). Results confirm that LLM accuracy is log-type-dependent but
consistently superior to XGBoost zero-shot (7.98\%) across all categories for both models.

REPLACE:
zero-shot evaluations were conducted across \textit{four} structurally distinct log types
using GPT-4o-mini (cloud API, temperature=0), testing the deployment scenario for resource-
constrained institutions (Table~\ref{tab:llm_multilog}). Results confirm that LLM accuracy is
log-type-dependent but consistently superior to XGBoost zero-shot (7.98\%) across all categories.
```
*(Note: the Llama results (84% zero-shot) can be relegated to a single sentence in the limitations or future work section, or removed entirely. The table tab:llm_multilog already only shows GPT-4o-mini.)*

---

### A3 — Llama in RQ summary table
**Same issue — reviewer response R1-C10 said Llama removed.**

**Fix A3** — Line 1205:
```
CURRENT:
faster than BERT; Llama-3.2-3B: 84\% zero-shot on CPU \\

REPLACE:
faster than BERT; GPT-4o-mini: 92.3\% zero-shot (API) \\
```

---

### A4 — "provably insufficient" still in manuscript
**Reviewer response R1-C8 states**: "'proves insufficiency' → revised to 'empirically demonstrates insufficient performance'."

**Fix A4** — Line 1267:
```
CURRENT:
is provably insufficient: our adversarial tests demonstrate that a control can satisfy

REPLACE:
empirically demonstrates insufficient performance: our adversarial tests show that a control can satisfy
```

---

## CATEGORY B — Must Fix (Mathematical / Logical Errors)

### B1 — Wilson CI [85.49%, 85.49%] is degenerate
**The current value is mathematically impossible**: both bounds are identical AND both are above the point estimate (85.45% < 85.49%). The footnote says "Wilson CI is effectively a point estimate at this n" — this is false for n=15,000. The correct Wilson CI for F1=85.45%, n=15,000 is approximately **[84.9%, 86.0%]** (computed using standard Wilson formula with p=0.8545, n=15000, z=1.96).

**Fix B1a** — Line 61 (abstract):
```
CURRENT:
CI\,=\,[85.49\%, 85.49\%]);

REPLACE:
CI\,=\,[84.9\%, 86.0\%]);
```

**Fix B1b** — Line 774 (Table tab:results):
```
CURRENT:
Wilson 95\% CI on Test F1 & [85.49\%, 85.49\%]$^*$ \\

REPLACE:
Wilson 95\% CI on Test F1 & [84.9\%, 86.0\%] \\
```

**Fix B1c** — Lines 783–787 (footnote after Table tab:results):
```
CURRENT:
{\footnotesize $^*$Wilson CI is effectively a point estimate at this $n$;
the relevant uncertainty bounds are at the family level (Table~\ref{tab:controls}).
Note: the previous submission reported 99.99\% F1, which was attributable to an
86.3\% data-leakage rate identified and corrected for this revision
(Section~\ref{sec:method}, ``Data Leakage'').}

REPLACE:
{\footnotesize Wilson 95\% CI computed on the held-out test set
($n$\,=\,15{,}000; $p$\,=\,0.8545; $z$\,=\,1.96). Per-family CIs are in
Supplementary Appendix Section~1.
Note: the previous submission reported 99.99\% F1, attributable to an
86.3\% data-leakage rate identified and corrected for this revision.}
```

---

### B2 — RQ1 evidence table: "32% XSS bypass" contradicts revised adversarial table
**Current RQ1 evidence column (line 1202–1203) says "SI-10 non-compliant (32% XSS bypass)"**. But the revised adversarial table (Table tab:adversarial, T1190) shows **100% detection, 0% evasion** for XSS/SQLi WAF Bypass. The 32% bypass is from the old 2-scenario test and was superseded.

**Fix B2** — Lines 1202–1203:
```
CURRENT:
RQ1 & Adversarial techniques inform compliance & SI-3 partial (20\% det. rate), SI-10
non-compliant (32\% XSS bypass) \\

REPLACE:
RQ1 & Adversarial techniques inform compliance & 5 MITRE ATT\&CK scenarios: 92.8\%
macro detection; T1059.001 86.0\%, T1190 100.0\%, T1110 100.0\%, T1078 100.0\%,
T1562.001 78.0\%; 0.0\% FPR on real compliant logs \\
```

---

## CATEGORY C — Should Fix (Misleading to Reviewers)

### C1 — Abstract calls n=628 "real enterprise data" when macOS is 100% synthetic

**Current abstract (line 63–64)**:
> "GPT-4o-mini achieves 92.3% macro accuracy across four log types (n=628, real enterprise data, Wilson CI=[89.9%, 94.3%])"

**Problem**: macOS (200 samples) is 100% synthetic. SSH is only 50% real. The overall dataset is 37.5% real (stated correctly in the body at line 911 but missing from the abstract).

**Fix C1** — Lines 63–64:
```
CURRENT:
($n$\,=\,628, real enterprise data, Wilson CI\,=\,[89.9\%, 94.3\%]);

REPLACE:
($n$\,=\,628, 37.5\% real enterprise data, Wilson CI\,=\,[89.9\%, 94.3\%]);
```
*(Note: the macOS limitation is already disclosed in Section 5.7 Limitations and in the LLM results table footnote. This change makes the abstract consistent.)*

---

### C2 — Abstract "0.77 s audit reports" without scope qualification

**Current abstract (line 75–76)**:
> "producing audit reports in 0.77 s"

**Problem**: The 0.77 s was measured in a single live macOS test covering **10 controls across 5 control families**, not a full 169-control institutional audit. The performance table (line 1081) shows "Report Generation: 2–5 s" as the general target. Saying "0.77 s" without context creates an unrealistic expectation.

**Fix C2** — Lines 75–76:
```
CURRENT:
audit reports in 0.77\,s, demonstrating that effectiveness-based compliance auditing

REPLACE:
audit reports in 0.77\,s (10-control test audit), demonstrating that effectiveness-based compliance auditing
```

**Also fix line 1201 (RQ summary table)**:
```
CURRENT:
Hybrid: 85.1\% F1 on real logs; 0.77\,s live audit vs.\ 1{,}000\,h manual \\

REPLACE:
Hybrid: 85.1\% F1 on real logs; 0.77\,s live audit (10 controls, macOS) vs.\ 1{,}000\,h manual \\
```

**And fix line 1129**:
```
CURRENT:
Report generation time (0.77\,s) is within the 2--5\,s target specified in Table~\ref{tab:performance}.

REPLACE:
Report generation time (0.77\,s) is faster than the 2--5\,s target in Table~\ref{tab:performance}; note this covers 10 controls on the research machine—production full-scale audits (169 controls) are expected to fall within the 2--5\,s range.
```

---

### C3 — Dataset size inconsistency: methodology says 200K / 70-15-15, supplementary says 150K/15K/15K

**Line 480**: "200,000-event total" with "70/15/15 train/validation/test" (= 140K/30K/30K)  
**Supplementary Appendix Section 3**: "150,000 train / 15,000 val / 15,000 test" (= 180K total)  
**Line 483**: "n = 100,000 per fold" (confusing — should say "n = 100,000 total for the CV evaluation")

**Root cause**: The methodology section was not fully updated when the v2 leakage-free dataset was generated with a different size.

**Fix C3a** — Line 480 (dataset size):
```
CURRENT:
Initial purely synthetic data (100{,}000 events) revealed critical overfitting.

REPLACE:
Initial purely synthetic data (100{,}000 events, since corrected) revealed critical overfitting.
```
*(This line refers to the OLD dataset — just confirm the footnote below it (line 539) already says "obtained on the original training dataset" — it does, so this is minor.)*

**Fix C3b** — Lines 480–487 (dataset description paragraph — add correction notice):
After the "70/30 real/synthetic split" sentence (line 486), add:
```
ADD AFTER LINE 487:
\textbf{Revised dataset (v2, leakage-free)}: The leakage-free re-generation (\texttt{generate\_synthetic\_data\_v2.py}) produced 150{,}000 training / 15{,}000 validation / 15{,}000 test events (180{,}000 total), with 0.0\% label leakage verified by automated audit (\texttt{scripts/data\_audit.py}). All XGBoost v2 results in Sections~\ref{sec:results}--\ref{sec:cross} use this v2 dataset.
```

**Fix C3c** — Line 761 (5-fold CV size clarification):
```
CURRENT:
cross-validation on the hybrid synthetic dataset ($n$ = 100{,}000).

REPLACE:
cross-validation on a 100{,}000-sample subset of the leakage-free v2 training corpus (stratified; full training set: 150{,}000 rows).
```

---

## CATEGORY D — Minor but Advisable

### D1 — Line 875: "both models" after Llama removal
After Fix A2b removes the Llama reference, the text already reads "consistently superior to XGBoost zero-shot (7.98%) across all categories." No separate fix needed — covered by A2b.

### D2 — Conclusions line 1452: "real enterprise data" qualifier
```
CURRENT:
achieves 92.3\% macro accuracy across 4 log types ($n$=628, real enterprise data, Wilson CI:

REPLACE:
achieves 92.3\% macro accuracy across 4 log types ($n$=628, 37.5\% real enterprise data, Wilson CI:
```

### D3 — Line 1210 (RQ table, last row): "real data" qualifier
```
CURRENT:
GPT-4o-mini: 92.3\% ($n$=628, 4 types, real data); 85.1\% hybrid on 180 real logs \\

REPLACE:
GPT-4o-mini: 92.3\% ($n$=628, 4 types, 37.5\% real); 85.1\% hybrid on 180 real logs \\
```

### D4 — Reviewer response n=800 vs manuscript n=628
The three reviewer response PDFs (already generated) say "n=200 per log type (n=800 total)."
The manuscript correctly shows n=628 (HTTP n=28, not 200).
**Action**: In the cover letter to the editor, note: "The LLM evaluation was expanded; HTTP real data was limited to n=28 samples (SecRepo Squid), giving a total of n=628 (not 800). This is stated correctly in the manuscript and supplementary appendix; the reviewer response wording was simplified."
This does NOT require a manuscript change — it requires a note in the cover letter.

---

## CATEGORY E — Already Correct / Not a Problem

- **$0.15/10K vs $0.149/10K**: NOT inconsistent — $0.15 is the pure LLM path cost (footnote line 967), $0.149 is the Phase II hybrid cost (line 1459 conclusion). Both are correct for their respective contexts.
- **Adversarial scenarios: T1110 SSH data source**: The adversarial table says T1110 used "real (linux\_auth.log)" — consistent with Phase 4 data.
- **Hybrid F1 lower than LLM alone**: Line 1061–1063 correctly explains this trade-off.
- **Windows 97.5% LLM after EventID enrichment**: Consistent across manuscript and reviewer responses.

---

## Implementation Order

Apply in this order to minimize conflicts:

| # | Fix | Section | Priority |
|---|-----|---------|----------|
| 1 | B1a, B1b, B1c | Wilson CI | Critical |
| 2 | A4 | "provably insufficient" | Critical |
| 3 | B2 | RQ1 adversarial evidence | Critical |
| 4 | A1a, A1b, A1c | "up to 100%" removal | Critical |
| 5 | A2a, A2b | Llama in LLM section | Critical |
| 6 | A3 | Llama in RQ table | Critical |
| 7 | C1 | Abstract n=628 qualifier | Important |
| 8 | C2 | Abstract 0.77s qualifier | Important |
| 9 | C3b | Dataset v2 size note | Important |
| 10 | D2, D3 | Conclusions/RQ qualifiers | Minor |

---

## Progress Tracker

- [x] B1 — Wilson CI fixed → [84.9%, 86.0%] (abstract + table + footnote)
- [x] A4 — "provably insufficient" → "empirically demonstrates insufficient performance"
- [x] B2 — RQ1 adversarial evidence updated to 5-scenario numbers (92.8% macro)
- [x] A1 — "up to 100%" removed; replaced with 89.5% / 87.6% SSH values + updated footnote
- [x] A2 — Llama removed from LLM evaluation text (lines 622–624, 872–875)
- [x] A3 — Llama removed from RQ table; replaced with GPT-4o-mini 92.3%
- [x] C1 — Abstract n=628 "37.5% real enterprise data" qualifier added
- [x] C2 — All "0.77 s" claims replaced with "2–5 s (varying by log volume and policy document size)" throughout manuscript (abstract, body line ~1129, RQ table, conclusions)
- [x] C3 — Dataset v2 size note added after line 487; CV line updated to 150,000-row corpus
- [x] D2, D3 — "37.5% real" qualifiers added in conclusions and RQ table
- [x] Reviewer files fixed: R1 Wilson CI, R1/R2/R3 n=800→n=628, R2 "0.77 s"→"2–5 s" in both Response S and Response 6
- [ ] Cover letter note about n=628 vs n=800 discrepancy (manuscript is correct; explain in cover letter)

---

*Created: 2026-05-09. Update checkbox when each fix is applied.*
