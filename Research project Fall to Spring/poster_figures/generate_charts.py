"""
Poster chart generator for CMU Africa Research Showcase 2026
Run with: python3 generate_charts.py
Outputs 5 PNG files in the same directory.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ── CMU colour palette ────────────────────────────────────────────────────────
CMU_RED    = '#C41230'
CMU_DARK   = '#1A1A1A'
CMU_GREY   = '#6D6E71'
CMU_LIGHT  = '#F2F2F2'
ACCENT_1   = '#2D6A9F'   # blue
ACCENT_2   = '#E87722'   # orange
ACCENT_3   = '#4DAF4A'   # green
WARN       = '#FF4444'   # red-warning

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
})

# ═══════════════════════════════════════════════════════════════════════════════
# CHART 1 — Generalization Gap
# ═══════════════════════════════════════════════════════════════════════════════
def chart1_generalization_gap():
    fig, ax = plt.subplots(figsize=(7, 4.5))

    stages   = ['XGBoost\nSynthetic\n(in-dist)', 'XGBoost\nZero-Shot\n(real logs)', 'XGBoost\n5% Fine-Tune', 'GPT-4o-mini\nZero-Shot', 'Llama-3.2-3B\nZero-Shot\n(CPU-only)']
    values   = [99.99, 7.98, 99.88, 93.5, 84.0]
    colors   = [ACCENT_3, WARN, ACCENT_3, ACCENT_1, ACCENT_2]

    bars = ax.bar(stages, values, color=colors, width=0.55, zorder=3, edgecolor='white', linewidth=0.8)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                f'{val}%', ha='center', va='bottom', fontsize=11, fontweight='bold',
                color=CMU_DARK)

    # annotate the gap
    ax.annotate('', xy=(1, 7.98), xytext=(0, 99.99),
                arrowprops=dict(arrowstyle='<->', color=WARN, lw=2))
    ax.text(0.5, 54, '92-point\ngap', ha='center', fontsize=10, color=WARN,
            fontweight='bold')

    ax.set_ylim(0, 115)
    ax.set_ylabel('F1 / Accuracy (%)', fontsize=12, color=CMU_DARK)
    ax.set_title('Generalization Gap & How We Bridge It', fontsize=14,
                 fontweight='bold', color=CMU_RED, pad=12)
    ax.axhline(y=65, color=CMU_GREY, linestyle='--', linewidth=1, alpha=0.5, zorder=2)
    ax.text(4.55, 66.5, 'Target\n65%', fontsize=8, color=CMU_GREY)
    ax.tick_params(axis='x', labelsize=9)
    ax.tick_params(axis='y', labelsize=10)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)

    legend_patches = [
        mpatches.Patch(color=ACCENT_3, label='XGBoost'),
        mpatches.Patch(color=WARN,     label='Zero-shot collapse'),
        mpatches.Patch(color=ACCENT_1, label='GPT-4o-mini (cloud)'),
        mpatches.Patch(color=ACCENT_2, label='Llama-3.2-3B (CPU)'),
    ]
    ax.legend(handles=legend_patches, fontsize=9, loc='lower right',
              framealpha=0.85)

    plt.tight_layout()
    path = os.path.join(OUT, 'chart1_generalization_gap.png')
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'  ✓ {path}')


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 2 — LLM accuracy by log type (grouped bar)
# ═══════════════════════════════════════════════════════════════════════════════
def chart2_llm_by_log_type():
    fig, ax = plt.subplots(figsize=(8, 5))

    log_types = ['SSH Auth', 'macOS\nSystem', 'HTTP/API\nAccess', 'Windows\nEvents']
    gpt   = [84.0, 92.0, 98.0, 100.0]
    llama = [82.0, 90.0, 64.0, 100.0]

    x = np.arange(len(log_types))
    w = 0.35

    b1 = ax.bar(x - w/2, gpt,   w, label='GPT-4o-mini (cloud)', color=ACCENT_1,
                zorder=3, edgecolor='white')
    b2 = ax.bar(x + w/2, llama, w, label='Llama-3.2-3B (CPU-only)', color=ACCENT_2,
                zorder=3, edgecolor='white')

    for bar in list(b1) + list(b2):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
                f'{bar.get_height():.0f}%', ha='center', va='bottom',
                fontsize=10, fontweight='bold', color=CMU_DARK)

    # highlight the HTTP gap — arrow points from Llama HTTP bar upward
    ax.annotate('29.5pp gap\n(HTTP logs)', xy=(2 + w/2, 64), xytext=(2 + w/2 - 0.55, 50),
                fontsize=9.5, color=WARN, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=WARN, lw=1.8))

    ax.set_xticks(x)
    ax.set_xticklabels(log_types, fontsize=11)
    ax.set_ylim(0, 122)
    ax.set_ylabel('Zero-Shot Accuracy (%)', fontsize=12, color=CMU_DARK)
    ax.set_title('LLM Zero-Shot Accuracy by Log Type\n(n = 50 per type, 200 total)',
                 fontsize=13, fontweight='bold', color=CMU_RED, pad=10)
    ax.axhline(y=93.5, color=CMU_GREY, linestyle='--', linewidth=1, alpha=0.5, zorder=2)
    ax.text(0.01, 95, 'GPT-4o-mini overall: 93.5%', fontsize=8.5, color=CMU_GREY,
            transform=ax.get_yaxis_transform())
    ax.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
    ax.legend(fontsize=10, loc='lower right', framealpha=0.85)

    plt.tight_layout()
    path = os.path.join(OUT, 'chart2_llm_log_types.png')
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'  ✓ {path}')


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 3 — Adversarial validation (checkbox vs effectiveness)
# ═══════════════════════════════════════════════════════════════════════════════
def chart3_adversarial():
    fig, ax = plt.subplots(figsize=(7.5, 5))

    controls   = ['SI-3\n(Malware Protection)', 'SI-10\n(Input Validation)']
    checkbox   = [100, 100]
    effective  = [20, 68]

    x = np.arange(len(controls))
    w = 0.32

    b1 = ax.bar(x - w/2, checkbox,  w, label='Checkbox audit: ✓ PASS',
                color=CMU_GREY, alpha=0.55, zorder=3, edgecolor='white', hatch='//')
    b2 = ax.bar(x + w/2, effective, w, label='Actual effectiveness',
                color=WARN, zorder=3, edgecolor='white')

    for bar, val in zip(b2, effective):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                f'{val}%', ha='center', va='bottom', fontsize=13,
                fontweight='bold', color=WARN)

    for bar in b1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                '100% ✓', ha='center', va='bottom', fontsize=11,
                fontweight='bold', color=CMU_GREY)

    # clean inside-bar annotations
    ax.text(x[0] + w/2, 10, 'Fileless shell\nevaded EDR\n4/5 times', ha='center',
            fontsize=9, color='white', fontweight='bold')
    ax.text(x[1] + w/2, 10, '32% XSS\nbypassed\nWAF', ha='center',
            fontsize=9, color='white', fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(controls, fontsize=12)
    ax.set_ylim(0, 130)
    ax.set_ylabel('Score (%)', fontsize=12, color=CMU_DARK)
    ax.set_title('Checkbox Compliance vs. Actual Effectiveness\n(Adversarial Testing)',
                 fontsize=13, fontweight='bold', color=CMU_RED, pad=12)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
    ax.legend(fontsize=11, loc='upper right', framealpha=0.85)

    plt.tight_layout()
    path = os.path.join(OUT, 'chart3_adversarial.png')
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'  ✓ {path}')


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Cost & resource comparison (ranges from real-world pricing)
# Qualys: $16–21/ep/mo × 100 endpoints → $1,660–$2,080/mo (UnderDefense 2025)
# BERT/GPU: AWS g4dn–p3 GPU cloud inference → $1,000–$5,000/mo (AWS ML Blog 2025)
# AWS Config: $35–$300/mo consumption-based (AWS official pricing)
# Wazuh: $0 licensing; TCO with labor ~$2,500–$8,000/mo (footnoted)
# This Work: $50/mo (measured)
# ═══════════════════════════════════════════════════════════════════════════════
def chart4_cost_comparison():
    fig, ax = plt.subplots(figsize=(10, 6.5))

    systems  = ['Qualys/\nTenable\n(100 ep)', 'BERT-based\nML (GPU)', 'AWS\nConfig', 'Wazuh\n(no ML)†', 'This Work\n(Hybrid)‡']
    cost_mid = [1870,  3000, 167,  0,  57]
    cost_lo  = [1660,  1000,  35,  0,  50]
    cost_hi  = [2080,  5000, 300,  0,  65]
    colors   = [CMU_GREY, CMU_GREY, CMU_GREY, ACCENT_3, CMU_RED]
    range_labels = [r'\$1,660–\$2,080/mo', r'\$1,000–\$5,000/mo', r'\$35–\$300/mo', 'Free\n(licensing)', r'\$50–\$65/mo']

    x = np.arange(len(systems))

    # Draw bars at midpoint
    bars = ax.bar(x, cost_mid, color=colors, width=0.55, zorder=3,
                  edgecolor='white', linewidth=0.8)

    # Error bars showing real-world range
    yerr_lo = [m - lo for m, lo in zip(cost_mid, cost_lo)]
    yerr_hi = [hi - m  for m, hi in zip(cost_mid, cost_hi)]
    ax.errorbar(x, cost_mid, yerr=[yerr_lo, yerr_hi], fmt='none',
                ecolor=CMU_DARK, elinewidth=2.0, capsize=7, zorder=5)

    # Range labels above each bar — minimum y so short bars don't overlap x-ticks
    MIN_Y = 600
    for i, (label, hi) in enumerate(zip(range_labels, cost_hi)):
        ypos = max(hi + 130, MIN_Y)
        ax.text(i, ypos, label, ha='center', va='bottom',
                fontsize=9.5, fontweight='bold', color=CMU_DARK)

    ax.set_xticks(x)
    ax.set_xticklabels(systems, fontsize=10.5)
    ax.set_ylim(0, 6800)
    ax.set_ylabel('Estimated Monthly Cost (USD)', fontsize=12, color=CMU_DARK)
    ax.set_title('Deployment Cost Comparison\n(100-endpoint deployment; licensing + infrastructure costs)',
                 fontsize=12, fontweight='bold', color=CMU_RED, pad=12)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)

    # Arrow annotation from This Work to Qualys
    ax.annotate('~33–42×\ncheaper\nthan Qualys', xy=(0, 1870), xytext=(1.6, 3600),
                fontsize=10, color=CMU_RED, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=CMU_RED, lw=2.0,
                                connectionstyle='arc3,rad=-0.25'))

    # Resource note inside This Work bar
    ax.text(4, 220, '2 CPU · 2.66 GB RAM', ha='center', fontsize=8.5,
            color='white', fontweight='bold')

    # Footnote
    ax.text(0.5, -0.11,
            r'† Wazuh: free licensing; TCO with labor/infra = \$2,500–\$8,000/mo   '
            r'‡ This Work: \$50/mo cloud VM + ~\$0.15/10K logs LLM API (variable)   '
            'Error bars = published price range',
            ha='center', fontsize=7.5, color=CMU_GREY, transform=ax.transAxes, style='italic')

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.16)
    path = os.path.join(OUT, 'chart4_cost_comparison.png')
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'  ✓ {path}')


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 5 — Compliance effectiveness model (radar / gauge)
# ═══════════════════════════════════════════════════════════════════════════════
def chart5_effectiveness_model():
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.5))
    fig.suptitle('Effectiveness Model:  C(k) = α · Detection + β · Coverage + γ · Evasion Resistance',
                 fontsize=12, color=CMU_DARK, fontweight='bold', y=1.02)

    # --- LEFT: SI-3 horizontal bar breakdown ---
    ax = axes[0]
    components = ['Evasion Resistance (R)', 'Log Coverage (V)', 'Detection Rate (D)']
    vals       = [0.014, 1.00, 0.20]
    colors_bar = [WARN, ACCENT_3, WARN]

    bars = ax.barh(components, vals, color=colors_bar, height=0.45, zorder=3,
                   edgecolor='white')
    for bar, v in zip(bars, vals):
        ax.text(v + 0.02, bar.get_y() + bar.get_height()/2,
                f'{v:.3f}', va='center', fontsize=12, fontweight='bold', color=CMU_DARK)

    ax.set_xlim(0, 1.25)
    ax.set_xlabel('Score (0 = worst → 1 = best)', fontsize=11, color=CMU_DARK)
    ax.set_title('SI-3 Component Scores\n(Malware Protection)', fontsize=12,
                 fontweight='bold', color=CMU_RED, pad=10)
    ax.axvline(x=1.0, color=CMU_GREY, linestyle='--', alpha=0.5, linewidth=1.2)
    ax.xaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
    ax.tick_params(axis='y', labelsize=12)

    score = 0.5*0.20 + 0.3*1.00 + 0.2*0.014
    ax.text(0.5, -0.85, f'→  C(SI-3) = {score:.3f}   vs.   Checkbox = 1.0',
            ha='center', fontsize=10, color=WARN, fontweight='bold', style='italic',
            transform=ax.get_xaxis_transform())

    # --- RIGHT: grouped bar before/after ---
    ax2 = axes[1]
    methods = ['Checkbox Audit', 'This Work C(k)']
    # C(SI-10): D=0.68 (34/50 blocked), V=1.0 (WAF logs covered), R=0.68 (1-0.32 bypass)
    # C(SI-10) = 0.5(0.68) + 0.3(1.0) + 0.2(0.68) = 0.340 + 0.300 + 0.136 = 0.776
    si10_ck = round(0.5*0.68 + 0.3*1.0 + 0.2*0.68, 3)
    si3_scores  = [1.0, round(score, 3)]
    si10_scores = [1.0, si10_ck]

    x = np.arange(2)
    w = 0.28
    bars_si3  = ax2.bar(x - w/2, si3_scores,  w, label='SI-3 (Malware)',
                        color=[CMU_GREY, WARN], zorder=3, edgecolor='white')
    bars_si10 = ax2.bar(x + w/2, si10_scores, w, label='SI-10 (Input Val.)',
                        color=[CMU_GREY, ACCENT_1], zorder=3, edgecolor='white')

    for bar, val, col in zip(list(bars_si3) + list(bars_si10),
                              si3_scores + si10_scores,
                              [CMU_GREY, WARN, CMU_GREY, ACCENT_1]):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.025,
                 f'{val:.2f}', ha='center', va='bottom',
                 fontsize=12, fontweight='bold', color=col)

    ax2.set_xticks(x)
    ax2.set_xticklabels(methods, fontsize=11)
    ax2.set_ylim(0, 1.45)
    ax2.set_ylabel('Compliance Score (0–1)', fontsize=11, color=CMU_DARK)
    ax2.set_title('Score: Checkbox vs. Effectiveness Model', fontsize=12,
                  fontweight='bold', color=CMU_RED, pad=10)
    ax2.legend(fontsize=10, loc='upper right', framealpha=0.9)
    ax2.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)

    plt.tight_layout()
    path = os.path.join(OUT, 'chart5_effectiveness_model.png')
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'  ✓ {path}')


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('Generating poster charts...')
    chart1_generalization_gap()
    chart2_llm_by_log_type()
    chart3_adversarial()
    chart4_cost_comparison()
    chart5_effectiveness_model()
    print('\nAll 5 charts saved to poster_figures/')
