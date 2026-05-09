"""
Generate reviewer response PDFs from .md files.
Produces clean A4 PDFs with proper Greek/math Unicode rendering.
"""

import os, re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

BASE = "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine/Research project Fall to Spring"

FILES = [
    ("reviewer1_comments.md", "reviewer_response_1.pdf", "Reviewer 1"),
    ("reviewer2_comments.md", "reviewer_response_2.pdf", "Reviewer 2"),
    ("reviewer3_comments.md", "reviewer_response_3.pdf", "Reviewer 3"),
]

# ── Colours ─────────────────────────────────────────────────────────────────
C_DARK    = colors.HexColor("#1a1a2e")
C_BLUE    = colors.HexColor("#1565c0")
C_BORDER  = colors.HexColor("#bdbdbd")
C_GREY    = colors.HexColor("#f5f5f5")
C_MATH_BG = colors.HexColor("#f3f0ff")   # lavender for math blocks
C_MATH_BD = colors.HexColor("#7c4dff")   # purple border for math

# ── LaTeX → Unicode math converter ──────────────────────────────────────────
GREEK = {
    r'\alpha':   'α',  r'\beta':    'β',  r'\gamma':   'γ',
    r'\delta':   'δ',  r'\epsilon': 'ε',  r'\zeta':    'ζ',
    r'\eta':     'η',  r'\theta':   'θ',  r'\iota':    'ι',
    r'\kappa':   'κ',  r'\lambda':  'λ',  r'\mu':      'μ',
    r'\nu':      'ν',  r'\xi':      'ξ',  r'\pi':      'π',
    r'\rho':     'ρ',  r'\sigma':   'σ',  r'\tau':     'τ',
    r'\upsilon': 'υ',  r'\phi':     'φ',  r'\chi':     'χ',
    r'\psi':     'ψ',  r'\omega':   'ω',
    r'\Gamma':   'Γ',  r'\Delta':   'Δ',  r'\Theta':   'Θ',
    r'\Lambda':  'Λ',  r'\Xi':      'Ξ',  r'\Pi':      'Π',
    r'\Sigma':   'Σ',  r'\Upsilon': 'Υ',  r'\Phi':     'Φ',
    r'\Psi':     'Ψ',  r'\Omega':   'Ω',
}

UNICODE_SUB = str.maketrans("0123456789aehijklmnoprstuvx",
                             "₀₁₂₃₄₅₆₇₈₉ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ")
UNICODE_SUP = str.maketrans("0123456789abcdefghijklmnoprstuvwxyz",
                             "⁰¹²³⁴⁵⁶⁷⁸⁹ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ")

def to_subscript(s):
    try:
        return s.translate(UNICODE_SUB)
    except Exception:
        return s

def to_superscript(s):
    try:
        return s.translate(UNICODE_SUP)
    except Exception:
        return s

def convert_math(expr):
    """Convert a LaTeX math expression (no surrounding $) to Unicode string."""
    s = expr

    # \text{...}  →  just the text
    s = re.sub(r'\\text\{([^}]*)\}', r'\1', s)

    # \textbf{...} → just the text
    s = re.sub(r'\\textbf\{([^}]*)\}', r'\1', s)

    # \mathbf{...} → just the text
    s = re.sub(r'\\mathbf\{([^}]*)\}', r'\1', s)

    # \mathrm{...} → just the text
    s = re.sub(r'\\mathrm\{([^}]*)\}', r'\1', s)

    # Greek letters (longest match first)
    for latex, uni in sorted(GREEK.items(), key=lambda x: -len(x[0])):
        s = s.replace(latex, uni)

    # Operators and symbols
    s = s.replace(r'\cdot', '·')
    s = s.replace(r'\times', '×')
    s = s.replace(r'\geq', '≥')
    s = s.replace(r'\leq', '≤')
    s = s.replace(r'\neq', '≠')
    s = s.replace(r'\approx', '≈')
    s = s.replace(r'\pm', '±')
    s = s.replace(r'\mp', '∓')
    s = s.replace(r'\in', '∈')
    s = s.replace(r'\notin', '∉')
    s = s.replace(r'\subset', '⊂')
    s = s.replace(r'\subseteq', '⊆')
    s = s.replace(r'\cup', '∪')
    s = s.replace(r'\cap', '∩')
    s = s.replace(r'\rightarrow', '→')
    s = s.replace(r'\leftarrow', '←')
    s = s.replace(r'\Rightarrow', '⇒')
    s = s.replace(r'\Leftarrow', '⇐')
    s = s.replace(r'\leftrightarrow', '↔')
    s = s.replace(r'\ldots', '…')
    s = s.replace(r'\cdots', '⋯')
    s = s.replace(r'\infty', '∞')
    s = s.replace(r'\sum', 'Σ')
    s = s.replace(r'\prod', 'Π')
    s = s.replace(r'\int', '∫')
    s = s.replace(r'\partial', '∂')
    s = s.replace(r'\nabla', '∇')
    s = s.replace(r'\forall', '∀')
    s = s.replace(r'\exists', '∃')
    s = s.replace(r'\neg', '¬')
    s = s.replace(r'\land', '∧')
    s = s.replace(r'\lor', '∨')
    s = s.replace(r'\hat', '')     # simplify
    s = s.replace(r'\bar', '')     # simplify
    s = s.replace(r'\tilde', '')   # simplify
    s = s.replace(r'\mathbb', '')
    s = s.replace(r'\mathcal', '')

    # \frac{a}{b}  →  a/b
    s = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'\1/\2', s)

    # Sub/superscripts with braces:  _{abc}  ^{abc}
    def apply_sub(m):
        inner = m.group(1)
        result = to_subscript(inner)
        return result if result != inner else ('_' + inner)

    def apply_sup(m):
        inner = m.group(1)
        result = to_superscript(inner)
        return result if result != inner else ('^' + inner)

    s = re.sub(r'_\{([^}]+)\}', apply_sub, s)
    s = re.sub(r'\^\{([^}]+)\}', apply_sup, s)

    # Single-char sub/superscripts:  _k  ^2
    s = re.sub(r'_([A-Za-z0-9])', lambda m: to_subscript(m.group(1)), s)
    s = re.sub(r'\^([A-Za-z0-9])', lambda m: to_superscript(m.group(1)), s)

    # Escaped braces and pipes
    s = s.replace(r'\{', '{').replace(r'\}', '}')
    s = s.replace(r'\|', '|')
    s = s.replace(r'\ ', ' ')

    # Strip leftover backslash-word commands
    s = re.sub(r'\\[a-zA-Z]+', '', s)

    return s.strip()


def render_inline_math(text):
    """Replace $...$ spans in text with Unicode-converted math, styled."""
    parts = re.split(r'\$([^$]+)\$', text)
    result = ''
    for idx, part in enumerate(parts):
        if idx % 2 == 0:
            # Normal text segment
            result += part
        else:
            # Math segment — convert and wrap in italic purple font
            uni = convert_math(part)
            uni_xml = uni.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            result += (
                f'<font color="#6a0dad" name="Helvetica-Oblique">'
                f'<b>{uni_xml}</b></font>'
            )
    return result


# ── Styles ───────────────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()
    S = {}

    S["title"] = ParagraphStyle(
        "title", parent=base["Title"],
        fontSize=16, textColor=C_DARK, spaceAfter=4,
        fontName="Helvetica-Bold", alignment=TA_CENTER,
    )
    S["subtitle"] = ParagraphStyle(
        "subtitle", parent=base["Normal"],
        fontSize=10, textColor=C_BLUE, spaceAfter=12,
        fontName="Helvetica", alignment=TA_CENTER,
    )
    S["h2"] = ParagraphStyle(
        "h2", parent=base["Heading2"],
        fontSize=13, textColor=C_BLUE, spaceBefore=14, spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    S["h3"] = ParagraphStyle(
        "h3", parent=base["Heading3"],
        fontSize=11, textColor=C_DARK, spaceBefore=8, spaceAfter=3,
        fontName="Helvetica-Bold",
    )
    S["body"] = ParagraphStyle(
        "body", parent=base["Normal"],
        fontSize=9.5, leading=14, spaceAfter=6,
        fontName="Helvetica", alignment=TA_JUSTIFY,
    )
    S["reviewer_comment"] = ParagraphStyle(
        "reviewer_comment", parent=base["Normal"],
        fontSize=9.5, leading=14, spaceAfter=4,
        fontName="Helvetica-Oblique", textColor=colors.HexColor("#0d47a1"),
        leftIndent=10, rightIndent=10,
    )
    S["response"] = ParagraphStyle(
        "response", parent=base["Normal"],
        fontSize=9.5, leading=14, spaceAfter=4,
        fontName="Helvetica", leftIndent=10, rightIndent=6,
        alignment=TA_JUSTIFY,
    )
    S["bullet"] = ParagraphStyle(
        "bullet", parent=base["Normal"],
        fontSize=9.5, leading=13, spaceAfter=3,
        fontName="Helvetica", leftIndent=22, firstLineIndent=-12,
    )
    S["resp_bullet"] = ParagraphStyle(
        "resp_bullet", parent=base["Normal"],
        fontSize=9.5, leading=13, spaceAfter=3,
        fontName="Helvetica", leftIndent=26, firstLineIndent=-12,
    )
    S["math_display"] = ParagraphStyle(
        "math_display", parent=base["Normal"],
        fontSize=11, leading=16, spaceAfter=4, spaceBefore=2,
        fontName="Helvetica-BoldOblique",
        textColor=colors.HexColor("#4a148c"),
        leftIndent=14, rightIndent=14,
        alignment=TA_CENTER,
    )
    S["table_header"] = ParagraphStyle(
        "table_header", parent=base["Normal"],
        fontSize=9, fontName="Helvetica-Bold", textColor=colors.white,
    )
    S["table_cell"] = ParagraphStyle(
        "table_cell", parent=base["Normal"],
        fontSize=9, fontName="Helvetica", leading=12,
    )
    return S


# ── XML escaping and inline formatting ───────────────────────────────────────
def xml_escape(text):
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text

def inline_fmt(text):
    """Apply inline markdown + math rendering to a text string."""
    # First handle math so $ isn't treated as currency
    text = render_inline_math(xml_escape(text))
    # Bold-italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic (single *)
    text = re.sub(r'\*([^*]+?)\*', r'<i>\1</i>', text)
    # Inline code (backtick) — already escaped
    text = re.sub(
        r'`([^`]+)`',
        r'<font name="Courier" size="8.5" color="#b71c1c">\1</font>',
        text
    )
    return text


# ── Table parsing ────────────────────────────────────────────────────────────
def parse_md_table(lines):
    rows = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Separator row
        if re.match(r'^[\|\-:\s]+$', line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows

def make_table(md_rows, styles):
    if not md_rows:
        return None
    col_count = max(len(r) for r in md_rows)
    page_w = A4[0] - 4.4 * cm
    col_w = page_w / col_count
    table_data = []
    for i, row in enumerate(md_rows):
        while len(row) < col_count:
            row.append("")
        if i == 0:
            cells = [Paragraph(xml_escape(c), styles["table_header"]) for c in row]
        else:
            cells = [Paragraph(inline_fmt(c), styles["table_cell"]) for c in row]
        table_data.append(cells)

    t = Table(table_data, colWidths=[col_w] * col_count, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  C_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, C_GREY]),
        ("GRID",          (0, 0), (-1, -1), 0.5, C_BORDER),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    return t


# ── Math display block ───────────────────────────────────────────────────────
def make_math_block(latex_expr, styles):
    """Render a standalone $...$ or display math as a highlighted box."""
    uni = convert_math(latex_expr)
    uni_xml = uni.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    p = Paragraph(uni_xml, styles["math_display"])
    t = Table([[p]], colWidths=[A4[0] - 4.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_MATH_BG),
        ("BOX",           (0, 0), (-1, -1), 1.2, C_MATH_BD),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    return t


# ── Response block parser ─────────────────────────────────────────────────────
def parse_response_block(lines, styles):
    flowables = []
    i = 0
    in_sub_table = False
    sub_table_lines = []

    def flush_sub_table():
        nonlocal sub_table_lines, in_sub_table
        rows = parse_md_table(sub_table_lines)
        t = make_table(rows, styles)
        if t:
            flowables.append(Spacer(1, 4))
            flowables.append(t)
            flowables.append(Spacer(1, 4))
        sub_table_lines = []
        in_sub_table = False

    while i < len(lines):
        line = lines[i]

        # Table detection
        if "|" in line:
            in_sub_table = True
            sub_table_lines.append(line)
            i += 1
            while i < len(lines) and "|" in lines[i]:
                sub_table_lines.append(lines[i])
                i += 1
            flush_sub_table()
            continue

        if in_sub_table:
            flush_sub_table()

        if line.strip() == "":
            flowables.append(Spacer(1, 3))
            i += 1
            continue

        # Standalone display math line  (e.g. "**Effectiveness function** $C(k) = ...$:")
        # If it contains an isolated large $...$ that looks like a formula definition, render it big
        standalone = re.match(r'^\s*\$([^$]+)\$\s*:?\s*$', line)
        if standalone:
            flowables.append(Spacer(1, 2))
            flowables.append(make_math_block(standalone.group(1), styles))
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # Bullet
        if line.startswith("- ") or line.startswith("* "):
            text = inline_fmt(line[2:].strip())
            flowables.append(Paragraph("  • " + text, styles["resp_bullet"]))
            i += 1
            continue

        # Numbered list
        m = re.match(r'^(\d+)\.\s+(.*)', line)
        if m:
            text = inline_fmt(m.group(2).strip())
            flowables.append(Paragraph(f"  {m.group(1)}.  {text}", styles["resp_bullet"]))
            i += 1
            continue

        # Normal response line
        text = inline_fmt(line.strip())
        if text:
            flowables.append(Paragraph(text, styles["response"]))
        i += 1

    if in_sub_table:
        flush_sub_table()

    return flowables


# ── Main document parser ─────────────────────────────────────────────────────
def md_to_flowables(md_text, styles):
    flowables = []
    lines = md_text.splitlines()
    i = 0
    in_response = False
    response_lines = []
    in_table = False
    table_lines = []

    def flush_response():
        nonlocal response_lines, in_response
        if response_lines:
            inner = parse_response_block(response_lines, styles)
            # Wrap response in a light green box
            if inner:
                box = Table([[inner]], colWidths=[A4[0] - 4.4 * cm])
                box.setStyle(TableStyle([
                    ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#f1f8e9")),
                    ("BOX",           (0, 0), (-1, -1), 0.8, colors.HexColor("#a5d6a7")),
                    ("TOPPADDING",    (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
                ]))
                flowables.append(box)
                flowables.append(Spacer(1, 5))
        response_lines = []
        in_response = False

    def flush_table():
        nonlocal table_lines, in_table
        rows = parse_md_table(table_lines)
        t = make_table(rows, styles)
        if t:
            flowables.append(t)
            flowables.append(Spacer(1, 6))
        table_lines = []
        in_table = False

    while i < len(lines):
        line = lines[i]

        # Table (outside response block)
        if "|" in line and not line.startswith(">"):
            if in_response:
                flush_response()
            in_table = True
            table_lines.append(line)
            i += 1
            while i < len(lines) and "|" in lines[i] and not lines[i].startswith(">"):
                table_lines.append(lines[i])
                i += 1
            flush_table()
            continue

        # Response block
        if line.startswith(">"):
            in_response = True
            response_lines.append(line[1:].lstrip())
            i += 1
            continue

        if in_response and line.strip() == "":
            # Peek ahead to see if response continues
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and lines[j].startswith(">"):
                response_lines.append("")
                i += 1
                continue
            else:
                flush_response()
                i += 1
                continue

        if in_response:
            flush_response()

        # HR
        if re.match(r'^---+$', line.strip()):
            flowables.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER,
                                         spaceAfter=8, spaceBefore=4))
            i += 1
            continue

        # H1
        if re.match(r'^# [^#]', line):
            flowables.append(Paragraph(xml_escape(line[2:].strip()), styles["title"]))
            i += 1
            continue

        # H2
        if line.startswith("## "):
            flowables.append(Paragraph(inline_fmt(line[3:].strip()), styles["h2"]))
            i += 1
            continue

        # H3
        if line.startswith("### "):
            flowables.append(Paragraph(inline_fmt(line[4:].strip()), styles["h3"]))
            i += 1
            continue

        # Blank line
        if line.strip() == "":
            flowables.append(Spacer(1, 5))
            i += 1
            continue

        # Reviewer comment (bold italic blue line)
        if line.startswith("**") and line.endswith("**") and "Response" not in line[:20]:
            text = inline_fmt(line.strip())
            flowables.append(Paragraph(text, styles["reviewer_comment"]))
            i += 1
            continue

        # Bullet
        if line.startswith("- ") or line.startswith("* "):
            flowables.append(Paragraph("• " + inline_fmt(line[2:].strip()),
                                        styles["bullet"]))
            i += 1
            continue

        # Numbered
        m = re.match(r'^(\d+)\.\s+(.*)', line)
        if m:
            flowables.append(Paragraph(f"{m.group(1)}. {inline_fmt(m.group(2))}",
                                        styles["bullet"]))
            i += 1
            continue

        # Default
        text = inline_fmt(line.strip())
        if text:
            flowables.append(Paragraph(text, styles["body"]))
        i += 1

    if in_response:
        flush_response()
    if in_table:
        flush_table()

    return flowables


# ── PDF builder ───────────────────────────────────────────────────────────────
def build_pdf(md_path, pdf_path, reviewer_label):
    styles = build_styles()

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
        title=f"Response to {reviewer_label} — futureinternet-4270373",
        author="Moise Iradukunda Ingabire",
    )

    story = []
    story.append(Paragraph("Author Response to Reviewers", styles["title"]))
    story.append(Paragraph(
        "AI-Augmented Compliance Auditing for Cloud Systems: A Hybrid ML–LLM Approach",
        styles["subtitle"],
    ))
    story.append(Paragraph(
        f"Manuscript ID: futureinternet-4270373 &nbsp;|&nbsp; "
        f"Journal: Future Internet (MDPI) &nbsp;|&nbsp; {reviewer_label}",
        styles["subtitle"],
    ))
    story.append(HRFlowable(width="100%", thickness=1.0, color=C_BLUE, spaceAfter=10))
    story.extend(md_to_flowables(md_text, styles))

    doc.build(story)
    print(f"  ✓  {os.path.basename(pdf_path)}")


def main():
    for _, pdf_name, _ in FILES:
        p = os.path.join(BASE, pdf_name)
        if os.path.exists(p):
            os.remove(p)
            print(f"  🗑  Deleted {pdf_name}")

    print("\nGenerating updated PDFs...")
    for md_name, pdf_name, label in FILES:
        build_pdf(os.path.join(BASE, md_name), os.path.join(BASE, pdf_name), label)

    print("\nDone. All three reviewer PDFs regenerated with proper math rendering.")


if __name__ == "__main__":
    main()
