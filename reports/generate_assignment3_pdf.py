#!/usr/bin/env python3
"""Generate Assignment 3 Phase II Technical Report PDF using reportlab."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import KeepTogether
import json
from pathlib import Path

OUTPUT = Path(__file__).parent / "Assignment3_Phase2_Report_Iradukunda.pdf"

doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=letter,
    rightMargin=1*inch, leftMargin=1*inch,
    topMargin=1*inch, bottomMargin=1*inch
)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle('Title', parent=styles['Title'],
    fontSize=16, spaceAfter=6, textColor=colors.HexColor('#1a1a2e'))
subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
    fontSize=11, spaceAfter=12, textColor=colors.HexColor('#444444'),
    alignment=TA_CENTER)
h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
    fontSize=13, spaceBefore=14, spaceAfter=4,
    textColor=colors.HexColor('#1a1a2e'), borderPad=2)
h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
    fontSize=11, spaceBefore=8, spaceAfter=3,
    textColor=colors.HexColor('#333366'))
body_style = ParagraphStyle('Body', parent=styles['Normal'],
    fontSize=10, spaceAfter=6, leading=14, alignment=TA_JUSTIFY)
code_style = ParagraphStyle('Code', parent=styles['Code'],
    fontSize=9, spaceAfter=4, leading=12,
    backColor=colors.HexColor('#f5f5f5'), leftIndent=12, rightIndent=12,
    borderPad=4)
caption_style = ParagraphStyle('Caption', parent=styles['Normal'],
    fontSize=9, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=8)
bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
    fontSize=10, spaceAfter=3, leading=13, leftIndent=18,
    bulletIndent=6, alignment=TA_JUSTIFY)
finding_style = ParagraphStyle('Finding', parent=styles['Normal'],
    fontSize=10, spaceAfter=5, leading=13, leftIndent=12,
    backColor=colors.HexColor('#e8f4f8'), borderPad=6, borderWidth=1,
    borderColor=colors.HexColor('#2196F3'), borderRadius=2)
abstract_style = ParagraphStyle('Abstract', parent=styles['Normal'],
    fontSize=10, spaceAfter=8, leading=13, leftIndent=24, rightIndent=24,
    backColor=colors.HexColor('#f9f9f9'), borderPad=8, alignment=TA_JUSTIFY)

def h(text, style=h1_style):
    return Paragraph(text, style)

def p(text, style=body_style):
    return Paragraph(text, style)

def b(text):
    return Paragraph(f"• {text}", bullet_style)

def sp(n=6):
    return Spacer(1, n)

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc'))

# ── Table helpers ─────────────────────────────────────────────────────────────
def make_table(data, col_widths, header_bg=colors.HexColor('#1a1a2e')):
    t = Table(data, colWidths=col_widths)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f7fa')]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])
    t.setStyle(style)
    return t

# ══════════════════════════════════════════════════════════════════════════════
# Load results
# ══════════════════════════════════════════════════════════════════════════════
results_file = Path(__file__).parent.parent / 'results' / 'audit' / 'phase2_adaptive_router.json'
with open(results_file) as f:
    results = json.load(f)

baselines = results['baselines']
pareto = results['pareto_optimal']
sweep = results['router_sweep']
ood = results['ood_detection']

# ══════════════════════════════════════════════════════════════════════════════
# Build document
# ══════════════════════════════════════════════════════════════════════════════
story = []

# ── Title ─────────────────────────────────────────────────────────────────────
story += [
    sp(12),
    Paragraph("Assignment 3: Methodological Extension &amp; Prototype Implementation (Phase II)", title_style),
    Paragraph("Vocabulary-Coverage Gating for Out-of-Distribution Detection<br/>"
              "<font size=11>Rwanda NCSA Compliance Auditor — Methodological Extension</font>",
              subtitle_style),
    Paragraph("Moise Iradukunda Ingabire<br/>"
              "Carnegie Mellon University Africa | Engineering Research Project",
              ParagraphStyle('auth', parent=styles['Normal'], fontSize=10,
                             alignment=TA_CENTER, textColor=colors.grey, spaceAfter=4)),
    Paragraph(f"Submission Date: March 20, 2026",
              ParagraphStyle('date', parent=styles['Normal'], fontSize=9,
                             alignment=TA_CENTER, textColor=colors.grey, spaceAfter=16)),
    hr(), sp(8),
]

# ── Abstract ──────────────────────────────────────────────────────────────────
story += [
    Paragraph("<b>Abstract</b>", ParagraphStyle('abshead', parent=styles['Normal'],
        fontSize=10, fontName='Helvetica-Bold', spaceAfter=4)),
    Paragraph(
        "Phase I of the Rwanda NCSA Compliance Auditor employed a fixed dual-path routing strategy: "
        "static regex rules forwarded structured logs to XGBoost, while ambiguous cases were escalated "
        "to a cloud-based LLM. This report presents Phase II — a non-trivial algorithmic extension that "
        "replaces static routing with <b>Vocabulary-Coverage Gating</b>, an out-of-distribution (OOD) "
        "detection mechanism exploiting TF-IDF's intrinsic property of producing zero-vectors for "
        "vocabulary-absent inputs. Phase II identifies a previously undetected silent failure mode: "
        "XGBoost's TF-IDF vocabulary was built exclusively from synthetic compliance events, producing "
        "zero vocabulary overlap with all real-world log formats, causing systematic high-confidence "
        "wrong predictions. The Phase II router computes ν(l) = |words(l) ∩ V| / |words(l)| before "
        "inference and routes to LLM whenever ν(l) &lt; θ. On a 50-sample mixed evaluation dataset "
        "(20 in-domain SSH + 30 OOD logs), Phase II achieves <b>90.0% overall accuracy</b> — a "
        "<b>+24.0 percentage-point improvement</b> over Phase I's fixed router (66.0%), with perfect "
        "OOD recall (1.00) at θ = 0.05.",
        abstract_style),
    sp(12),
]

# ── Section 1: Introduction ───────────────────────────────────────────────────
story += [
    h("1. Introduction and Motivation"),
    h("1.1 Phase I Architecture Recap", h2_style),
    p("Phase I implemented a seven-engine microservices pipeline where Engine 3 (XGBoost Classifier) "
      "handled evidence-to-control mapping using a hybrid TF-IDF + temporal feature representation "
      "(30 features: 25 TF-IDF n-grams + 5 numeric temporal). The routing strategy was <b>static</b>: "
      "regex patterns matching known log formats forwarded logs to XGBoost; non-matching logs were "
      "escalated to the LLM semantic path via Model Context Protocol (MCP)."),

    h("1.2 The Silent Failure Problem (New Finding)", h2_style),
    Paragraph(
        "⚠ <b>Key Finding</b>: XGBoost's TF-IDF vectorizer was fitted on synthetic compliance events "
        "containing vocabulary drawn entirely from compliance terminology (e.g., 'rwncsa', 'compliance "
        "check passed', 'control policy updated', 'audit log'). When processing any real-world log — "
        "SSH authentication, macOS system services, HTTP/API access — the TF-IDF vector is identically "
        "<b>zero</b>, because no log word appears in the 25-token training vocabulary (ν(l) = 0.00 for "
        "all 50 evaluation samples).",
        finding_style),
    sp(4),
    p("The consequence is severe: XGBoost defaults to its majority class prior (<i>compliant</i>) with "
      "maximum logit confidence (p ≈ 0), producing wrong predictions with perfect apparent certainty. "
      "The Phase I static router cannot detect this because it makes routing decisions on format matching, "
      "not on the quality of the XGBoost feature vector. This is a <b>silent failure</b> — the system "
      "appears to function normally while producing systematically incorrect compliance decisions."),

    h("1.3 Scope: Phase II within the Assignment 2 Extension Plan", h2_style),
    p("Assignment 2 proposed a full dataset and architectural extension comprising four components: "
      "(1) a 311,839-log cross-domain dataset spanning SSH, Windows Event, syslog, and cloud audit formats; "
      "(2) a Common Event Format (CEF) normalization layer for format-agnostic ingestion; "
      "(3) a cross-framework compliance adapter supporting NIST 800-53, ISO 27001, and Rwanda NCSA; "
      "and (4) optional on-premise LLM integration for data-sovereignty-constrained deployments. "
      "<b>Phase II implements the OOD detection mechanism</b> — the immediate algorithmic priority "
      "identified in A2's architecture plan — as a scoped prototype. CEF normalization, the "
      "cross-framework adapter, and on-premise LLM integration are deferred to the full thesis "
      "implementation, where the complete 311,839-log dataset will enable rigorous re-evaluation "
      "of routing accuracy under realistic cross-domain conditions."),

    h("1.4 Phase II Contribution", h2_style),
    p("We propose <b>Vocabulary-Coverage Gating</b>: a lightweight OOD detection mechanism that inspects "
      "vocabulary coverage before XGBoost inference. This extends Phase I in four concrete ways:"),
]
for item in [
    "<b>Algorithmic novelty</b>: replaces static regex routing with a computed OOD signal derived from TF-IDF theory",
    "<b>Silent failure prevention</b>: catches zero-vector collapse before it propagates to compliance decisions",
    "<b>Automatic format adaptation</b>: routing adapts to any log format without rule updates",
    "<b>Interpretability</b>: ν(l) ∈ [0,1] is human-readable and auditable",
]:
    story.append(b(item))
story += [
    sp(6),
    Paragraph(
        "<b>Connection to Research Hypothesis H1 (Assignment 1)</b>: The extended literature review "
        "formulated Hypothesis H1: <i>\"An LLM-augmented hybrid system will achieve ≥85% compliance "
        "detection accuracy across ≥3 distinct real-world log formats.\"</i> Phase I's GPT-4o-mini "
        "zero-shot evaluation (83.3% across 3 log types — SSH 80%, macOS 90%, HTTP/API 80%) "
        "<b>partially tests H1</b>: the ≥3-format criterion is satisfied, but the 83.3% overall "
        "accuracy falls 1.7pp below the 85% threshold, with SSH and HTTP/API individually below target. "
        "Phase II addresses the root cause of this gap — XGBoost's vocabulary mismatch forcing "
        "over-reliance on the LLM — but full H1 validation requires the expanded dataset proposed in "
        "Assignment 2.",
        finding_style),
    sp(8),
]

# ── Section 2: Architecture Comparison ───────────────────────────────────────
story += [
    h("2. Architecture: Phase I vs. Phase II"),
]

arch_data = [
    ["Property", "Phase I (Fixed Router)", "Phase II (Vocab-Coverage Gate)"],
    ["Routing signal", "Regex format match", "Vocabulary coverage ν(l)"],
    ["OOD detection", "None", "ν(l) < θ triggers LLM fallback"],
    ["Adapts to new formats", "No (rule update required)", "Yes (automatic)"],
    ["Overhead", "<1ms (regex match)", "<0.1ms (set intersection)"],
    ["Silent failure prevention", "No", "Yes"],
    ["Interpretability", "Low (opaque regex)", "High (ν ∈ [0,1])"],
    ["Training data dependency", "None", "Requires vocabulary V from TF-IDF fit"],
]
story += [
    make_table(arch_data, [1.5*inch, 2.2*inch, 2.8*inch]),
    Paragraph("Table 1: Architectural comparison between Phase I and Phase II routing strategies.",
              caption_style),
    sp(8),
]

# Phase II Architecture description (text diagram)
story += [
    h("2.1 Phase II Router Logic", h2_style),
    Paragraph(
        "<b>Phase I Flow:</b>  Log Input → [Regex Match?] → YES: XGBoost → Decision | NO: LLM → Decision<br/><br/>"
        "<b>Phase II Flow:</b>  Log Input → [Compute ν(l)] → [ν(l) ≥ θ?] → YES: XGBoost → Decision | NO: LLM (OOD) → Decision",
        ParagraphStyle('flow', parent=styles['Normal'], fontSize=10, spaceAfter=6,
                       leading=16, leftIndent=12, backColor=colors.HexColor('#f0f4ff'),
                       borderPad=8)),
    p("The Phase II router inserts a vocabulary coverage computation step between log ingestion and "
      "inference. This step costs &lt;0.1ms (a Python set intersection) and provides a principled "
      "basis for routing that Phase I's format-matching approach cannot provide."),
    sp(8),
]

# ── Section 3: Algorithm ──────────────────────────────────────────────────────
story += [
    h("3. Algorithm"),
    h("3.1 Vocabulary Coverage Score", h2_style),
    p("Let V be the TF-IDF vocabulary fitted during XGBoost training. For a log entry l, define:"),
    Paragraph("ν(l) = |{ w : w ∈ words(l) } ∩ V| / |words(l)|",
              ParagraphStyle('eq', parent=styles['Normal'], fontSize=11,
                             alignment=TA_CENTER, spaceBefore=4, spaceAfter=4,
                             fontName='Courier-Bold')),
    p("where words(l) is the whitespace-tokenised word set of l. ν(l) = 0 indicates that no word in l "
      "appears in the training vocabulary — a necessary condition for zero-vector collapse."),

    h("3.2 Routing Rule", h2_style),
    Paragraph("route(l) = XGBoost   if ν(l) ≥ θ<br/>route(l) = LLM        if ν(l) &lt; θ",
              ParagraphStyle('eq2', parent=styles['Normal'], fontSize=10,
                             alignment=TA_CENTER, spaceBefore=4, spaceAfter=4,
                             fontName='Courier', leading=16)),

    h("3.3 Training Vocabulary (Root Cause)", h2_style),
    p("The Phase I TF-IDF vocabulary (|V| = 25 tokens, word n-grams 1–2) was fitted on synthetic "
      "compliance audit events. The full vocabulary:"),
    Paragraph(
        "rwncsa | compliance | check | passed | compliance check | check compliance | "
        "check passed | verification | status | compliant | compliance verification | "
        "verification rwncsa | status compliant | control | policy | updated | executed | "
        "successfully | control rwncsa | policy updated | executed successfully | "
        "detected | audit | log | audit log",
        code_style),
    p("No real-world log format (SSH, syslog, macOS launchctl, HTTP/Apache) contains any of these tokens. "
      "This confirms that the zero-vector failure is structural, not incidental."),
    sp(8),
]

# ── Section 4: Evaluation ─────────────────────────────────────────────────────
story += [
    h("4. Evaluation"),
    h("4.1 Dataset ($n=50$)", h2_style),
    p("The evaluation uses a mixed dataset of 50 log samples across two sets:"),
]
for item in [
    "<b>Set A (n=20)</b>: SSH authentication log entries in SecRepo/syslog format — the XGBoost training format. Ground truth: rule-based (\"Accepted\" → compliant; \"Failed\"/\"Invalid\" → non-compliant). These are nominally in-domain but exhibit ν(l)=0.00 due to vocabulary mismatch.",
    "<b>Set B (n=30)</b>: OOD logs from Phase I multi-log evaluation — 10 SSH (SecRepo format), 10 macOS system/service logs, 10 HTTP/API access logs. Ground truth: GPT-4o-mini evaluation (Phase I results, verified against domain-specific rules).",
]:
    story.append(b(item))
story.append(sp(6))

# Vocab coverage table
story += [
    h("4.2 Vocabulary Coverage Analysis", h2_style),
]
vcov_data = [
    ["Log Type", "n", "Mean ν(l)", "Min ν(l)", "Max ν(l)"],
    ["SSH — Set A (nominal in-domain)", "20", "0.000", "0.000", "0.000"],
    ["SSH Authentication — Set B", "10", "0.000", "0.000", "0.000"],
    ["macOS System/Service — Set B", "10", "0.000", "0.000", "0.000"],
    ["HTTP/API Access — Set B", "10", "0.000", "0.000", "0.000"],
    ["ALL SAMPLES", "50", "0.000", "0.000", "0.000"],
]
story += [
    make_table(vcov_data, [2.6*inch, 0.4*inch, 1.0*inch, 1.0*inch, 1.0*inch]),
    Paragraph("Table 2: Vocabulary coverage ν(l) by log type. Zero coverage across all samples "
              "confirms TF-IDF vocabulary incompatibility with real-world log formats.",
              caption_style),
    sp(6),
]

# Baseline table
story += [
    h("4.3 Baseline Comparisons", h2_style),
]
bl = baselines
xgb_A = bl['xgboost_only']['accuracy_set_a']
xgb_B = bl['xgboost_only']['accuracy_set_b']
xgb_all = bl['xgboost_only']['accuracy_overall']
llm_A = bl['llm_only']['accuracy_set_a']
llm_B = bl['llm_only']['accuracy_set_b']
llm_all = bl['llm_only']['accuracy_overall']
p1_acc = bl['phase1_fixed_router']['accuracy']
p1_llm = bl['phase1_fixed_router']['llm_rate']
p1_cost = bl['phase1_fixed_router']['cost_per_10k']
p2_acc = pareto['accuracy']
p2_llm = pareto['llm_call_rate']
p2_cost = pareto['cost_per_10k']

baseline_data = [
    ["Approach", "Set A (SSH)", "Set B (OOD)", "Overall", "Cost/10K"],
    ["XGBoost only", f"{xgb_A}%", f"{xgb_B}%", f"{xgb_all}%", "$0.001"],
    ["LLM only (GPT-4o-mini)", f"{llm_A}%", f"{llm_B}%", f"{llm_all}%", "$0.150"],
    ["Phase I (fixed router)†", f"{xgb_A}%†", f"{llm_B}%", f"{p1_acc}%", f"${p1_cost}"],
    [f"Phase II (vocab-cov, θ=0.01)", "100.0%", f"{llm_B}%", f"{p2_acc}%", f"${p2_cost}"],
]
t = make_table(baseline_data, [2.0*inch, 1.0*inch, 1.0*inch, 0.9*inch, 0.9*inch])
# Highlight Phase II row
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#e8f5e9')),
    ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
    ('TEXTCOLOR', (0, 4), (-1, 4), colors.HexColor('#1b5e20')),
]))
story += [
    t,
    Paragraph("Table 3: Accuracy and cost comparison across routing strategies (n=50). "
              "† Phase I routes Set A to XGBoost (format match succeeds but vocabulary fails → 40.0% accuracy).",
              caption_style),
    sp(6),
]

# Threshold sweep
story += [
    h("4.4 Threshold Sweep", h2_style),
]
sweep_data = [["θ", "Accuracy", "LLM Rate", "Cost/10K", "LLM Calls"]]
for r in sweep:
    sweep_data.append([
        f"{r['threshold']:.2f}",
        f"{r['accuracy']:.1f}%",
        f"{r['llm_call_rate']:.1f}%",
        f"${r['cost_per_10k']:.4f}",
        f"{r['llm_calls']}/50"
    ])
story += [
    make_table(sweep_data, [0.7*inch, 1.0*inch, 1.0*inch, 1.1*inch, 1.0*inch]),
    Paragraph("Table 4: Phase II vocabulary-coverage router threshold sweep. "
              "Any θ > 0.00 correctly routes all 50 samples to LLM (since ν=0.00 for all), "
              "achieving 90.0% accuracy vs. 66.0% for Phase I.",
              caption_style),
    sp(8),
]

# OOD detection
story += [
    h("4.5 OOD Detection Quality (θ = 0.05)", h2_style),
]
ood_data = [
    ["Metric", "Value", "Interpretation"],
    ["OOD Recall", f"{ood['recall']:.2f}", "All 30 OOD logs correctly flagged (zero missed)"],
    ["OOD Precision", f"{ood['precision']:.2f}", "60% of LLM-routed logs are genuinely OOD"],
    ["F1 Score", f"{ood['f1']:.2f}", "Conservative gate: prefers LLM coverage"],
    ["True Positives (TP)", str(ood['tp']), "OOD logs correctly sent to LLM"],
    ["False Positives (FP)", str(ood['fp']), "In-domain SSH logs also sent to LLM (correct: vocab mismatch)"],
    ["False Negatives (FN)", str(ood['fn']), "OOD logs incorrectly kept in XGBoost (zero)"],
    ["True Negatives (TN)", str(ood['tn']), "In-domain logs kept in XGBoost (zero: all are OOD)"],
]
story += [
    make_table(ood_data, [1.6*inch, 0.8*inch, 4.0*inch]),
    Paragraph("Table 5: OOD detection performance at θ=0.05. Perfect recall ensures no OOD log "
              "is processed by the zero-vector XGBoost path.",
              caption_style),
    sp(8),
]

# ── Section 5: Key Findings ───────────────────────────────────────────────────
story += [
    h("5. Key Findings"),
    Paragraph("<b>Finding 1 — Root Cause of Phase I Zero-Shot Failure</b>: XGBoost's TF-IDF vocabulary "
              "(|V|=25, synthetic compliance events only) has zero overlap with any real-world log format. "
              "This is structural, not incidental. Zero vocabulary overlap → zero feature vector → maximum "
              "false confidence → systematic misclassification.", finding_style),
    sp(4),
    Paragraph("<b>Finding 2 — Phase I Static Router Misroutes In-Domain Logs</b>: The Phase I router "
              "correctly matched SSH log format via regex but incorrectly assumed that format-matching "
              "implies in-distribution features. Phase II reveals that SSH logs are also OOD with respect "
              "to the TF-IDF vocabulary, reducing Phase I's Set A accuracy to 40.0%.", finding_style),
    sp(4),
    Paragraph("<b>Finding 3 — Vocabulary Coverage is a Perfect OOD Signal Here</b>: ν(l)=0.00 for all "
              "50 samples (OOD recall = 1.00 at any θ > 0). The gate is conservative (FP=20, all in-domain "
              "SSH also flagged) but correct: those logs would have been misclassified by XGBoost anyway.",
              finding_style),
    sp(4),
    Paragraph("<b>Finding 4 — +24pp Accuracy Improvement</b>: Phase II achieves 90.0% overall accuracy "
              "vs. 66.0% for Phase I on the mixed 50-sample evaluation, by routing all logs — including "
              "nominally in-domain SSH — to LLM when vocabulary coverage is zero.", finding_style),
    sp(4),
    Paragraph("<b>Finding 5 — Empirical Validation of Domain-Shift Prediction</b>: Deka et al. (2023) "
              "predicted that ML classifiers trained on domain-specific corpora would exhibit systematic "
              "accuracy degradation when applied to cross-domain log data — a phenomenon they attributed "
              "to feature-space mismatch rather than model capacity. Phase II's vocabulary-coverage "
              "analysis provides direct empirical support for this prediction: the TF-IDF feature space, "
              "fitted exclusively on synthetic NCSA compliance events, produces zero-vector representations "
              "for all real-world log formats regardless of log complexity. This confirms that the "
              "domain-shift failure is structural (vocabulary-level) rather than incidental, exactly as "
              "Deka et al. anticipated for domain-mismatched deployment contexts.",
              finding_style),
    sp(8),
]

# ── Section 6: Design Choices ─────────────────────────────────────────────────
story += [
    h("6. Design Choices and Justification"),
    h("Why vocabulary coverage, not entropy or confidence thresholds?", h2_style),
    p("XGBoost's output probabilities are poorly calibrated on OOD inputs. Zero-vector features produce "
      "near-zero logits corresponding to p ≈ 0 (maximum false confidence for class 0). Entropy and "
      "probability-based thresholds therefore fail catastrophically: a high-confidence wrong prediction "
      "is indistinguishable from a high-confidence correct one. Vocabulary coverage is computed before "
      "inference and is independent of the model's output — it cannot be fooled by the model's own "
      "overconfidence."),

    h("Why not retrain XGBoost on real-world logs?", h2_style),
    p("Retraining would fix the vocabulary mismatch but requires labeled real-world logs — a "
      "resource-intensive process. The Phase II router achieves the correct outcome (route OOD to LLM) "
      "without new training data, preserving the training investment and enabling zero-shot deployment "
      "to new log formats. Future work should rebuild the vocabulary from real-world logs."),

    h("Cost vs. Accuracy Tradeoff", h2_style),
    p(f"At the optimal operating point (θ=0.01), Phase II routes all 50 samples to LLM (cost: $0.1500/10K). "
      f"This is higher than Phase I's blended cost ($0.0904/10K) but delivers +24pp accuracy. "
      "For mandatory NCSA compliance auditing, accuracy is non-negotiable — incorrect compliance "
      "determinations carry institutional and legal implications that far exceed the $0.06/10K cost delta."),
    sp(8),
]

# ── Section 7: Limitations ────────────────────────────────────────────────────
story += [
    h("7. Limitations"),
]
for item in [
    "<b>Sample size</b>: n=50 is small. The zero vocabulary coverage finding is deterministic, but accuracy numbers would benefit from larger evaluation sets.",
    "<b>Phase I baseline approximation</b>: Phase I SSH accuracy is taken as XGBoost-only (40.0%). In practice, Phase I's rule-based system may augment SSH processing with additional heuristics.",
    "<b>Full LLM dependency at optimal θ</b>: All 50 evaluation samples route to LLM (cost = $0.15/10K). Rebuilding the TF-IDF vocabulary from real-world logs would enable the router to correctly leverage XGBoost where genuinely in-distribution.",
    "<b>Necessary but not sufficient</b>: High vocabulary coverage does not guarantee in-distribution semantics. A log could contain training vocabulary tokens while describing an entirely different compliance context.",
    "<b>LLM accuracy ceiling</b>: The LLM achieves 83.3% on OOD logs. The Phase II router cannot improve LLM accuracy — only ensure the best available classifier is used for each input.",
]:
    story.append(b(item))
story.append(sp(8))

# ── Section 8: Conclusion ─────────────────────────────────────────────────────
story += [
    h("8. Conclusion"),
    p("This report presents Phase II of the Rwanda NCSA Compliance Auditor: a vocabulary-coverage "
      "gating mechanism that replaces Phase I's static regex routing with a principled OOD detection "
      "algorithm. Phase II identifies and resolves a previously undetected silent failure mode: "
      "XGBoost's TF-IDF vocabulary, built from synthetic compliance events, has zero overlap with all "
      "real-world log formats, causing systematic high-confidence wrong predictions that the Phase I "
      "router cannot detect."),
    p(f"The Phase II router achieves 90.0% overall accuracy on a 50-sample mixed evaluation dataset — "
      f"a +24.0 percentage-point improvement over Phase I's 66.0% — with perfect OOD recall (1.00). "
      "The extension is computationally negligible (&lt;0.1ms), requires no additional training data, "
      "and is clearly differentiated from Phase I in both mechanism and evaluation outcome."),
    p("Connecting to the theoretical model from Phase I: the detection rate D_k is not only "
      "log-type-dependent (as Phase I showed) but feature-representation-dependent. A model can "
      "produce maximum confidence while providing zero meaningful signal — and only OOD-aware routing "
      "prevents this from propagating to compliance decisions that inform NCSA audit outcomes."),
    p("This Phase II prototype is a scoped implementation of the architectural extension proposed in "
      "Assignment 2. The full extension — CEF normalization, cross-framework compliance adapter, and "
      "on-premise LLM integration evaluated on the 311,839-log cross-domain dataset — remains the "
      "thesis deliverable. Phase II establishes that OOD-aware routing is both necessary (silent failure "
      "confirmed) and sufficient for the immediate deployment context, providing a validated "
      "architectural building block for that larger system. Full H1 validation (≥85% across ≥3 log "
      "formats) requires the complete dataset and re-evaluation planned for the thesis phase."),
    sp(12),
    hr(), sp(6),
    Paragraph("Submitted for: Assignment 3 — Methodological Extension &amp; Prototype Implementation (Phase II)<br/>"
              "Engineering Research Project | Carnegie Mellon University Africa | March 2026",
              ParagraphStyle('footer', parent=styles['Normal'], fontSize=9,
                             textColor=colors.grey, alignment=TA_CENTER)),
]

doc.build(story)
print(f"PDF generated: {OUTPUT}")
print(f"File size: {OUTPUT.stat().st_size / 1024:.1f} KB")
