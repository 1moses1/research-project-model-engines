"""
Generate live_audit_dashboard.png — a publication-quality compliance dashboard
matching the thesis Chapter 4 live audit results (AUDIT-20260320-205239).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Arc
import matplotlib.gridspec as gridspec
import numpy as np

# ── Audit data from thesis Chapter 4 ──────────────────────────────────────────
AUDIT_ID   = "AUDIT-20260320-205239"
AUDIT_DATE = "March 20, 2026  |  20:52:39"
HOSTNAME   = "cmu-africa-workstation.local"
OS         = "macOS 26.3.1"
DURATION   = "0.77 s"
OVERALL    = 75.0

FAMILIES = [
    ("Access Control",          "AC", 35, 28,  80.0),
    ("Audit & Accountability",  "AU", 22, 17,  77.3),
    ("Config. Management",      "CM", 12, 10,  83.3),
    ("Identification & Auth.",  "IA", 10,  7,  70.0),
    ("Sys. & Comms. Prot.",     "SC", 15, 10,  66.7),
    ("Sys. & Info Integrity",   "SI",  2,  0,   0.0),
]

TOP_FINDINGS = [
    ("SI-3", "Malicious Code Protection",
     "Fileless shell detection rate 20% — below 85% threshold",     "PARTIAL",   "#e67e22"),
    ("SI-10","Information Input Validation",
     "WAF XSS bypass rate 32% — non-compliant despite WAF present", "NON-COMPLIANT","#e74c3c"),
    ("SC-8", "Transmission Confidentiality",
     "TLS 1.0/1.1 still active on internal services",               "PARTIAL",   "#e67e22"),
    ("IA-2", "Identification & Authentication",
     "MFA not enforced for local user accounts",                    "PARTIAL",   "#e67e22"),
    ("AC-7", "Account Management",
     "7 accounts inactive > 90 days; de-provisioning overdue",      "PARTIAL",   "#e67e22"),
]

# ── Colour palette ─────────────────────────────────────────────────────────────
C_BG      = "#1a2332"   # dark navy background
C_CARD    = "#243447"   # card background
C_BORDER  = "#2e4060"   # card border
C_GREEN   = "#27ae60"
C_AMBER   = "#e67e22"
C_RED     = "#e74c3c"
C_TEXT    = "#ecf0f1"
C_SUBTEXT = "#95a5a6"
C_ACCENT  = "#3498db"
C_HEADER  = "#1a2332"

def score_color(score):
    if score >= 80: return C_GREEN
    if score >= 60: return C_AMBER
    return C_RED

def draw_gauge(ax, score, label="", size=1.0):
    """Draw a semicircular gauge."""
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.4, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")

    # Background arc
    theta1, theta2 = 0, 180
    arc_bg = Arc((0, 0), 2*size, 2*size, angle=0,
                 theta1=theta1, theta2=theta2,
                 color="#2e4060", lw=14*size, zorder=1)
    ax.add_patch(arc_bg)

    # Score arc
    arc_score = Arc((0, 0), 2*size, 2*size, angle=0,
                    theta1=theta1, theta2=theta1 + (score/100)*180,
                    color=score_color(score), lw=14*size, zorder=2)
    ax.add_patch(arc_score)

    # Score text
    ax.text(0, 0.15, f"{score:.0f}%", ha="center", va="center",
            fontsize=28*size, fontweight="bold", color=C_TEXT,
            fontfamily="monospace")
    ax.text(0, -0.25, label, ha="center", va="center",
            fontsize=9*size, color=C_SUBTEXT)

def draw_bar(ax, score, label, total, compliant, ypos, height=0.5):
    """Draw a horizontal compliance bar."""
    ax.barh(ypos, 100, height=height, color="#2e4060", zorder=1)
    ax.barh(ypos, score, height=height, color=score_color(score), zorder=2)
    ax.text(-1, ypos, label, va="center", ha="right",
            fontsize=8, color=C_TEXT, fontweight="bold")
    ax.text(101, ypos, f"{score:.0f}%  ({compliant}/{total})",
            va="center", ha="left", fontsize=7.5, color=score_color(score))

# ── Figure layout ──────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 10), facecolor=C_BG)
gs  = gridspec.GridSpec(3, 3, figure=fig,
                        left=0.03, right=0.97,
                        top=0.90, bottom=0.04,
                        hspace=0.55, wspace=0.35)

# ── Header bar ─────────────────────────────────────────────────────────────────
header_ax = fig.add_axes([0, 0.91, 1, 0.09], facecolor="#0d1b2a")
header_ax.axis("off")
header_ax.text(0.02, 0.60, "Rwanda NCSA Compliance Auditor",
               transform=header_ax.transAxes, fontsize=15, fontweight="bold",
               color=C_ACCENT, va="center")
header_ax.text(0.02, 0.20, "AI-Augmented Compliance Dashboard  |  Engine 5 — Web UI",
               transform=header_ax.transAxes, fontsize=9, color=C_SUBTEXT, va="center")
header_ax.text(0.98, 0.60, f"Audit ID: {AUDIT_ID}",
               transform=header_ax.transAxes, fontsize=9,
               color=C_TEXT, va="center", ha="right", fontfamily="monospace")
header_ax.text(0.98, 0.20, f"{AUDIT_DATE}  |  {HOSTNAME}  ({OS})",
               transform=header_ax.transAxes, fontsize=8,
               color=C_SUBTEXT, va="center", ha="right")

# ── Panel 1: Overall gauge (top-left) ──────────────────────────────────────────
gauge_ax = fig.add_subplot(gs[0, 0], facecolor=C_CARD)
for spine in gauge_ax.spines.values():
    spine.set_edgecolor(C_BORDER)
draw_gauge(gauge_ax, OVERALL, "Overall Compliance Score")
gauge_ax.text(0.5, 0.95, "COMPLIANCE POSTURE", transform=gauge_ax.transAxes,
              ha="center", va="top", fontsize=8, color=C_SUBTEXT, fontweight="bold")

# Stat badges below gauge
stats = [("96", "Controls Audited"), ("72", "Compliant"), ("24", "Partial / Non-Comp.")]
for i, (val, lbl) in enumerate(stats):
    xpos = 0.15 + i * 0.35
    gauge_ax.text(xpos, -0.30, val, transform=gauge_ax.transAxes,
                  ha="center", fontsize=14, fontweight="bold",
                  color=[C_TEXT, C_GREEN, C_AMBER][i])
    gauge_ax.text(xpos, -0.42, lbl, transform=gauge_ax.transAxes,
                  ha="center", fontsize=6.5, color=C_SUBTEXT)

# ── Panel 2: Metadata card (top-centre) ────────────────────────────────────────
meta_ax = fig.add_subplot(gs[0, 1], facecolor=C_CARD)
for spine in meta_ax.spines.values():
    spine.set_edgecolor(C_BORDER)
meta_ax.axis("off")
meta_ax.text(0.5, 0.95, "AUDIT METADATA", transform=meta_ax.transAxes,
             ha="center", va="top", fontsize=8, color=C_SUBTEXT, fontweight="bold")

rows = [
    ("Audit ID",   AUDIT_ID),
    ("Timestamp",  "2026-03-20  20:52:39"),
    ("Host",       HOSTNAME),
    ("OS",         OS),
    ("Duration",   DURATION),
    ("Framework",  "NCSA MCS 2023 (NIST SP 800-53)"),
    ("Controls",   "96 / 143 automated"),
    ("Parsers",    "60 evidence parsers"),
]
for i, (key, val) in enumerate(rows):
    y = 0.83 - i * 0.104
    meta_ax.text(0.04, y, key + ":", transform=meta_ax.transAxes,
                 fontsize=7.5, color=C_SUBTEXT, va="center")
    meta_ax.text(0.42, y, val, transform=meta_ax.transAxes,
                 fontsize=7.5, color=C_TEXT, va="center",
                 fontfamily="monospace" if key in ("Audit ID", "Timestamp") else "sans-serif")

# ── Panel 3: Mini gauges per family (top-right) ────────────────────────────────
mini_gs = gridspec.GridSpecFromSubplotSpec(2, 3, subplot_spec=gs[0, 2],
                                           hspace=0.6, wspace=0.5)
for idx, (name, code, total, comp, score) in enumerate(FAMILIES):
    r, c = divmod(idx, 3)
    ax = fig.add_subplot(mini_gs[r, c], facecolor=C_CARD)
    for sp in ax.spines.values():
        sp.set_edgecolor(C_BORDER)
    draw_gauge(ax, score, f"{code}  {comp}/{total}", size=0.65)

# ── Panel 4: Family bar chart (middle-left + centre) ──────────────────────────
bar_ax = fig.add_subplot(gs[1, :2], facecolor=C_CARD)
for spine in bar_ax.spines.values():
    spine.set_edgecolor(C_BORDER)
bar_ax.set_facecolor(C_CARD)
bar_ax.text(0.5, 1.04, "CONTROL FAMILY COMPLIANCE BREAKDOWN",
            transform=bar_ax.transAxes, ha="center", fontsize=8,
            color=C_SUBTEXT, fontweight="bold")

bar_ax.set_xlim(-45, 115)
bar_ax.set_ylim(-0.5, len(FAMILIES) - 0.5)
bar_ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
for sp in ["top", "right", "left", "bottom"]:
    bar_ax.spines[sp].set_visible(False)

for i, (name, code, total, comp, score) in enumerate(reversed(FAMILIES)):
    draw_bar(bar_ax, score, f"{code} — {name}", total, comp, i)

# Threshold line at 85%
bar_ax.axvline(85, color=C_SUBTEXT, lw=0.8, ls="--", alpha=0.6)
bar_ax.text(85.5, len(FAMILIES) - 0.3, "NCSA 85% threshold",
            fontsize=6.5, color=C_SUBTEXT, va="top")

# ── Panel 5: C(k) effectiveness scores (middle-right) ─────────────────────────
eff_ax = fig.add_subplot(gs[1, 2], facecolor=C_CARD)
for spine in eff_ax.spines.values():
    spine.set_edgecolor(C_BORDER)
eff_ax.set_facecolor(C_CARD)
eff_ax.text(0.5, 1.04, "C(k) EFFECTIVENESS SCORES",
            transform=eff_ax.transAxes, ha="center", fontsize=8,
            color=C_SUBTEXT, fontweight="bold")

ck_data = [
    ("SI-3",  0.395, "Malware Prot."),
    ("SI-10", 0.746, "Input Valid."),
    ("SC-8",  0.612, "TLS Config."),
    ("IA-2",  0.680, "MFA Status"),
    ("AC-17", 0.820, "Remote Access"),
    ("CM-6",  0.910, "Config Mgmt."),
]
eff_ax.set_xlim(0, 1.0)
eff_ax.set_ylim(-0.5, len(ck_data) - 0.5)
eff_ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
for sp in ["top", "right", "left", "bottom"]:
    eff_ax.spines[sp].set_visible(False)

for i, (ctrl, score, label) in enumerate(reversed(ck_data)):
    eff_ax.barh(i, 1.0, height=0.4, color="#2e4060", zorder=1)
    eff_ax.barh(i, score, height=0.4, color=score_color(score * 100), zorder=2)
    eff_ax.text(-0.02, i, f"{ctrl}", va="center", ha="right",
                fontsize=7.5, color=C_TEXT, fontweight="bold")
    eff_ax.text(score + 0.02, i, f"{score:.3f}",
                va="center", ha="left", fontsize=7, color=score_color(score * 100))

eff_ax.axvline(0.85, color=C_SUBTEXT, lw=0.8, ls="--", alpha=0.6)
eff_ax.text(0.855, len(ck_data) - 0.3, "0.85", fontsize=6.5,
            color=C_SUBTEXT, va="top")

# ── Panel 6: Top findings (bottom row, full width) ─────────────────────────────
find_ax = fig.add_subplot(gs[2, :], facecolor=C_CARD)
for spine in find_ax.spines.values():
    spine.set_edgecolor(C_BORDER)
find_ax.axis("off")
find_ax.text(0.5, 0.97, "TOP FINDINGS & REMEDIATION PRIORITY",
             transform=find_ax.transAxes, ha="center", va="top",
             fontsize=8, color=C_SUBTEXT, fontweight="bold")

col_w = 1.0 / len(TOP_FINDINGS)
for i, (ctrl, name, detail, status, col) in enumerate(TOP_FINDINGS):
    xc = (i + 0.5) * col_w
    # Badge
    find_ax.text(xc, 0.78, ctrl, transform=find_ax.transAxes,
                 ha="center", va="center", fontsize=11, fontweight="bold",
                 color=col, bbox=dict(boxstyle="round,pad=0.2", facecolor=C_BG,
                                      edgecolor=col, lw=1.5))
    find_ax.text(xc, 0.58, name, transform=find_ax.transAxes,
                 ha="center", va="center", fontsize=7.5, color=C_TEXT,
                 fontweight="bold", wrap=True)
    find_ax.text(xc, 0.35, detail, transform=find_ax.transAxes,
                 ha="center", va="center", fontsize=6.5, color=C_SUBTEXT,
                 wrap=True, multialignment="center",
                 linespacing=1.4)
    # Status pill
    find_ax.text(xc, 0.10, status, transform=find_ax.transAxes,
                 ha="center", va="center", fontsize=6.5, fontweight="bold",
                 color=C_BG,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor=col, edgecolor="none"))

# Dividers
for i in range(1, len(TOP_FINDINGS)):
    find_ax.plot([i * col_w, i * col_w], [0, 1], color=C_BORDER, lw=0.8,
                 transform=find_ax.transAxes, clip_on=False)

# ── Footer ──────────────────────────────────────────────────────────────────────
fig.text(0.02, 0.01,
         "Rwanda NCSA Compliance Auditor v1.0  |  CMU Africa  |  "
         "C(k) = αD_k + βV_k + γR_k  (α=0.5, β=0.3, γ=0.2)  |  "
         "Audit completed in 0.77 s  |  Kubernetes deployment: 2.0 CPU / 2.66 GB RAM",
         fontsize=6.5, color=C_SUBTEXT, va="bottom")

fig.text(0.98, 0.01,
         f"Generated: {AUDIT_DATE}",
         fontsize=6.5, color=C_SUBTEXT, va="bottom", ha="right")

# ── Save ───────────────────────────────────────────────────────────────────────
output = "live_audit_dashboard.png"
plt.savefig(output, dpi=180, bbox_inches="tight", facecolor=C_BG)
print(f"Saved: {output}")
plt.close()
