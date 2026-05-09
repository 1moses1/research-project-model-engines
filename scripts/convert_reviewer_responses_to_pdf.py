"""
Convert reviewer response markdown files to formatted PDFs.
Uses reportlab Platypus for professional layout.
"""

import re
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors

# ── Colour palette ────────────────────────────────────────────────────────────
C_DARK       = HexColor("#1a2a3a")   # dark navy for headings
C_ACCENT     = HexColor("#2c5f8a")   # steel blue for reviewer comment boxes
C_RESPONSE   = HexColor("#1d6b3f")   # dark green for response boxes
C_BOX_COMMENT = HexColor("#e8f0f7")  # light blue fill
C_BOX_RESP   = HexColor("#e8f5ee")   # light green fill
C_BORDER     = HexColor("#b0c4d8")   # border colour for comment box
C_BORDER_R   = HexColor("#7ab893")   # border colour for response box
C_META_BG    = HexColor("#f5f5f5")   # light grey for metadata table
C_TABLE_HDR  = HexColor("#2c5f8a")   # table header background
C_TABLE_ROW  = HexColor("#f0f4f8")   # alternating table row
C_RULE       = HexColor("#cccccc")   # horizontal rule

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm


def build_styles():
    base = getSampleStyleSheet()

    def ps(name, **kwargs):
        return ParagraphStyle(name, **kwargs)

    styles = {
        "title": ps("DocTitle",
            fontName="Helvetica-Bold", fontSize=17, textColor=C_DARK,
            spaceAfter=4, leading=22, alignment=TA_LEFT),
        "subtitle": ps("DocSubtitle",
            fontName="Helvetica", fontSize=11, textColor=C_ACCENT,
            spaceAfter=2, leading=15, alignment=TA_LEFT),
        "meta_label": ps("MetaLabel",
            fontName="Helvetica-Bold", fontSize=9, textColor=C_DARK,
            leading=13),
        "meta_value": ps("MetaValue",
            fontName="Helvetica", fontSize=9, textColor=HexColor("#333333"),
            leading=13),
        "section_h1": ps("SecH1",
            fontName="Helvetica-Bold", fontSize=13, textColor=C_DARK,
            spaceBefore=14, spaceAfter=4, leading=17,
            borderPad=0),
        "section_h2": ps("SecH2",
            fontName="Helvetica-Bold", fontSize=11, textColor=C_ACCENT,
            spaceBefore=10, spaceAfter=3, leading=15),
        "comment_label": ps("CommentLabel",
            fontName="Helvetica-Bold", fontSize=10, textColor=C_ACCENT,
            leading=14),
        "comment_body": ps("CommentBody",
            fontName="Helvetica-Oblique", fontSize=9.5, textColor=HexColor("#222222"),
            leading=14, alignment=TA_JUSTIFY, spaceAfter=2),
        "response_label": ps("ResponseLabel",
            fontName="Helvetica-Bold", fontSize=10, textColor=C_RESPONSE,
            leading=14),
        "response_body": ps("ResponseBody",
            fontName="Helvetica", fontSize=9.5, textColor=HexColor("#111111"),
            leading=14, alignment=TA_JUSTIFY, spaceAfter=2),
        "bullet": ps("Bullet",
            fontName="Helvetica", fontSize=9.5, textColor=HexColor("#111111"),
            leading=14, leftIndent=18, firstLineIndent=-10, spaceAfter=1),
        "sub_bullet": ps("SubBullet",
            fontName="Helvetica", fontSize=9, textColor=HexColor("#222222"),
            leading=13, leftIndent=34, firstLineIndent=-10, spaceAfter=1),
        "code": ps("Code",
            fontName="Courier", fontSize=8.5, textColor=HexColor("#333333"),
            leading=12, leftIndent=12),
        "normal": ps("NormalText",
            fontName="Helvetica", fontSize=9.5, textColor=HexColor("#111111"),
            leading=14, alignment=TA_JUSTIFY, spaceAfter=2),
        "table_hdr": ps("TableHdr",
            fontName="Helvetica-Bold", fontSize=8.5, textColor=white,
            leading=12, alignment=TA_CENTER),
        "table_cell": ps("TableCell",
            fontName="Helvetica", fontSize=8.5, textColor=C_DARK,
            leading=12, alignment=TA_LEFT),
        "table_cell_c": ps("TableCellC",
            fontName="Helvetica", fontSize=8.5, textColor=C_DARK,
            leading=12, alignment=TA_CENTER),
    }
    return styles


# ── Math / inline text helpers ────────────────────────────────────────────────

def escape_xml(text):
    """Escape & < > for ReportLab XML-based paragraphs."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def convert_math(text):
    """
    Convert LaTeX inline math $...$ to ReportLab XML with proper
    <super>/<sub> tags and Unicode symbols.  Avoids combining Unicode
    characters (e.g. U+0302 combining circumflex) which Helvetica
    cannot render — uses ReportLab superscript markup instead.
    """
    # Named replacements applied before regex passes.
    # \hat{p} → p<super>^</super>  (NOT p̂ which uses a combining char)
    named = {
        r"\hat{p}":   "p<super>^</super>",
        r"\hat{n}":   "n<super>^</super>",
        r"\hat{x}":   "x<super>^</super>",
        r"\alpha":    "α", r"\beta":    "β",  r"\gamma":   "γ",
        r"\delta":    "δ", r"\epsilon": "ε",  r"\zeta":    "ζ",
        r"\eta":      "η", r"\theta":   "θ",  r"\lambda":  "λ",
        r"\mu":       "μ", r"\xi":      "ξ",  r"\pi":      "π",
        r"\rho":      "ρ", r"\sigma":   "σ",  r"\tau":     "τ",
        r"\phi":      "φ", r"\chi":     "χ",  r"\psi":     "ψ",
        r"\omega":    "ω",
        r"\geq":      "≥", r"\leq":     "≤",  r"\neq":     "≠",
        r"\pm":       "±", r"\cdot":    "·",  r"\times":   "×",
        r"\div":      "÷", r"\in":      "∈",  r"\notin":   "∉",
        r"\subset":   "⊂", r"\cup":     "∪",  r"\cap":     "∩",
        r"\infty":    "∞", r"\rightarrow": "→",
        r"\leftarrow": "←", r"\Rightarrow": "⇒",
        r"\text{compliant}":     "compliant",
        r"\text{non-compliant}": "non-compliant",
        r"\text{NIST}":          "NIST",
        r"\text{presence}":      "presence",
        r"\text{binary}":        "binary",
        r"\text{satisfied}":     "satisfied",
        r"\text{other than satisfied}": "other than satisfied",
        r"\{":  "{",  r"\}":  "}",   # literal LaTeX braces
        r"\|":  "|",  r"\,":  " ",   # spacing / delimiter
        r"_{SI\text{-}3}":       "<sub>SI-3</sub>",
        r"_{SI\text{-}10}":      "<sub>SI-10</sub>",
    }

    def replace_math(m):
        expr = m.group(1)

        # 1. Named substitutions (longest first to avoid partial matches)
        for k, v in sorted(named.items(), key=lambda x: -len(x[0])):
            expr = expr.replace(k, v)

        # 2. \frac{a}{b}  →  a/b
        expr = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', expr)

        # 3. \sqrt{inner}  →  √(inner)   — apply before sub/super so inner
        #    is still intact when we process it
        def sqrt_repl(sm):
            inner = sm.group(1)
            # recursively process the inner expression for sub/super
            inner = re.sub(r'\^\{([^}]+)\}', r'<super>\1</super>', inner)
            inner = re.sub(r'\^([a-zA-Z0-9])',  r'<super>\1</super>', inner)
            inner = re.sub(r'_\{([^}]+)\}',  r'<sub>\1</sub>', inner)
            inner = re.sub(r'_([a-zA-Z0-9])', r'<sub>\1</sub>', inner)
            return f"√({inner})"
        expr = re.sub(r'\\sqrt\{([^}]+)\}', sqrt_repl, expr)

        # 4. Superscripts ^{...} or ^x  →  <super>...</super>
        expr = re.sub(r'\^\{([^}]+)\}', r'<super>\1</super>', expr)
        expr = re.sub(r'\^([a-zA-Z0-9])',  r'<super>\1</super>', expr)

        # 5. Subscripts _{...} or _x  →  <sub>...</sub>
        expr = re.sub(r'_\{([^}]+)\}',  r'<sub>\1</sub>', expr)
        expr = re.sub(r'_([a-zA-Z0-9])', r'<sub>\1</sub>', expr)

        # 6. Strip \textbf, \text, \mathrm, \mathit wrappers
        for cmd in [r'\\mathbf', r'\\textbf', r'\\text', r'\\mathrm', r'\\mathit']:
            expr = re.sub(cmd + r'\{([^}]+)\}', r'\1', expr)

        # 7. Remove any remaining unknown backslash-commands
        expr = re.sub(r'\\[a-zA-Z]+', '', expr)

        return expr

    text = re.sub(r'\$\$(.+?)\$\$', replace_math, text, flags=re.DOTALL)
    text = re.sub(r'\$(.+?)\$',     replace_math, text)
    return text


def md_inline_to_rl(text, style_bold="b", style_italic="i"):
    """Convert inline markdown (**bold**, *italic*, `code`) to ReportLab XML tags."""
    text = escape_xml(text)
    text = convert_math(text)
    # Bold italic ***...***
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Bold **...**
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic *...*
    text = re.sub(r'\*([^*\n]+?)\*', r'<i>\1</i>', text)
    # Code `...`
    text = re.sub(r'`([^`]+)`', r'<font name="Courier" size="8.5">\1</font>', text)
    return text


# ── Markdown → flowable list ──────────────────────────────────────────────────

def parse_md_to_flowables(md_text, styles, doc_width):
    """Parse the full markdown and return a list of Platypus flowables."""
    lines = md_text.splitlines()
    flowables = []
    i = 0
    n = len(lines)

    # State for the response-block accumulator
    in_comment_block = False
    in_response_block = False
    comment_lines = []
    response_lines = []

    def flush_comment():
        nonlocal comment_lines
        if comment_lines:
            _emit_comment_box(comment_lines, flowables, styles, doc_width)
            comment_lines = []

    def flush_response():
        nonlocal response_lines
        if response_lines:
            _emit_response_box(response_lines, flowables, styles, doc_width)
            response_lines = []

    # Track whether we've stripped the first H1 title (the "Reviewer N" heading)
    stripped_title = False
    title_stripped_text = None  # keep the non-reviewer part for the document header

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # ── Detect "## Comment N" or "> Response N:" blocks ──────────────────
        comment_match = re.match(
            r'^#{1,3}\s+(Comment\s+\w+|Comment\s+R|Comment\s+S)\s*[-—–]?\s*(.*)',
            stripped, re.IGNORECASE
        )
        response_start = re.match(r'^>\s*\*\*Response\s*\w+', stripped, re.IGNORECASE)
        response_start2 = re.match(r'^>\s*\*\*Response\s+\w+', stripped, re.IGNORECASE)

        # ── H1 title (strip "Reviewer N —" prefix) ───────────────────────────
        if stripped.startswith("# ") and not stripped_title:
            stripped_title = True
            # Skip — title is built from metadata below
            i += 1
            continue

        # ── H2 / H3 section headings ──────────────────────────────────────────
        if re.match(r'^#{2,3}\s+', stripped):
            flush_comment()
            flush_response()
            heading_text = re.sub(r'^#{2,3}\s+', '', stripped)
            # "Comment N" headings get special treatment below
            if re.match(r'^Comment\s+', heading_text, re.IGNORECASE):
                # Handled as comment block below; don't emit generic heading
                pass
            else:
                h_style = styles["section_h1"] if stripped.startswith("## ") else styles["section_h2"]
                flowables.append(Spacer(1, 6))
                flowables.append(Paragraph(md_inline_to_rl(heading_text), h_style))
                flowables.append(HRFlowable(width="100%", thickness=0.5, color=C_RULE, spaceAfter=4))
            i += 1
            continue

        # ── Metadata table block (| Criterion | Rating |) ────────────────────
        if stripped.startswith("|") and not in_comment_block and not in_response_block:
            flush_comment()
            flush_response()
            table_lines = []
            while i < n and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            flowables.append(_build_md_table(table_lines, styles))
            flowables.append(Spacer(1, 6))
            continue

        # ── Blockquote lines ("> ...") → response accumulator ────────────────
        if stripped.startswith(">"):
            flush_comment()
            in_response_block = True
            bq_content = re.sub(r'^>\s?', '', line)
            response_lines.append(bq_content)
            i += 1
            # Collect continuation blockquote lines
            while i < n and (lines[i].strip().startswith(">") or
                              (response_lines and lines[i].strip() == "")):
                if lines[i].strip() == "":
                    response_lines.append("")
                else:
                    response_lines.append(re.sub(r'^>\s?', '', lines[i]))
                i += 1
            flush_response()
            in_response_block = False
            continue

        # ── "**Comment N**" style bold comment headers ───────────────────────
        if re.match(r'^\*\*Comment\s+\w+', stripped):
            flush_comment()
            flush_response()
            # Start collecting comment block
            in_comment_block = True
            comment_lines.append(line)
            i += 1
            continue

        # ── H3 "### Comment N" ────────────────────────────────────────────────
        if re.match(r'^##+ Comment\s+', stripped, re.IGNORECASE):
            flush_comment()
            flush_response()
            in_comment_block = True
            comment_lines.append(re.sub(r'^##+ ', '', line))
            i += 1
            continue

        # ── Horizontal rule ───────────────────────────────────────────────────
        if re.match(r'^[-*]{3,}$', stripped):
            flush_comment()
            flush_response()
            flowables.append(Spacer(1, 4))
            flowables.append(HRFlowable(width="100%", thickness=1, color=C_RULE))
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # ── If we're accumulating a comment block ─────────────────────────────
        if in_comment_block:
            # Stop if we hit a blockquote (response) or a new "---"
            if stripped.startswith(">") or re.match(r'^[-*]{3,}$', stripped):
                flush_comment()
                in_comment_block = False
                continue  # don't advance i, re-process this line
            comment_lines.append(line)
            i += 1
            continue

        # ── Bullet list items ─────────────────────────────────────────────────
        if re.match(r'^[-*]\s+', stripped):
            flush_comment()
            flush_response()
            bullet_text = re.sub(r'^[-*]\s+', '', stripped)
            flowables.append(Paragraph("• " + md_inline_to_rl(bullet_text), styles["bullet"]))
            i += 1
            continue

        # ── Numbered list ─────────────────────────────────────────────────────
        num_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if num_match:
            flush_comment()
            flush_response()
            num = num_match.group(1)
            rest = num_match.group(2)
            flowables.append(Paragraph(f"{num}. {md_inline_to_rl(rest)}", styles["bullet"]))
            i += 1
            continue

        # ── Blank lines ───────────────────────────────────────────────────────
        if stripped == "":
            flush_comment()
            flush_response()
            in_comment_block = False
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # ── Normal paragraph ──────────────────────────────────────────────────
        flush_comment()
        flush_response()
        flowables.append(Paragraph(md_inline_to_rl(stripped), styles["normal"]))
        i += 1

    flush_comment()
    flush_response()
    return flowables


# ── Box renderers ─────────────────────────────────────────────────────────────

def _parse_block_lines(lines, styles, is_response=False):
    """Parse a list of text lines into Paragraph/Spacer flowables."""
    out = []
    body_style = styles["response_body"] if is_response else styles["comment_body"]
    bullet_style = styles["bullet"]

    for line in lines:
        s = line.strip()
        if s == "":
            out.append(Spacer(1, 3))
            continue
        # Table rows inside a block
        if s.startswith("|"):
            # collect consecutive table lines — handled below by caller
            out.append(Paragraph(md_inline_to_rl(s), body_style))
            continue
        if re.match(r'^[-*]\s+', s):
            text = re.sub(r'^[-*]\s+', '', s)
            out.append(Paragraph("• " + md_inline_to_rl(text), bullet_style))
            continue
        num_match = re.match(r'^(\d+)\.\s+(.*)', s)
        if num_match:
            out.append(Paragraph(f"{num_match.group(1)}. {md_inline_to_rl(num_match.group(2))}", bullet_style))
            continue
        # Italic note (*Required Revision:*)
        if s.startswith("*") and s.endswith("*"):
            out.append(Paragraph(md_inline_to_rl(s), body_style))
            continue
        out.append(Paragraph(md_inline_to_rl(s), body_style))
    return out


def _emit_comment_box(comment_lines, flowables, styles, doc_width):
    """Render a tinted comment box."""
    if not comment_lines:
        return

    # First line is the comment label
    label_line = comment_lines[0].strip()
    # Strip markdown heading chars
    label_line = re.sub(r'^#{1,3}\s*', '', label_line)
    # Bold label
    label_para = Paragraph(md_inline_to_rl(label_line), styles["comment_label"])

    body_paras = _parse_block_lines(comment_lines[1:], styles, is_response=False)
    inner = [label_para, Spacer(1, 4)] + body_paras

    # Check if there's a markdown table to render nicely
    table_lines = []
    new_inner = []
    collecting_table = False
    raw_lines = comment_lines[1:]
    j = 0
    while j < len(raw_lines):
        ls = raw_lines[j].strip()
        if ls.startswith("|"):
            table_lines.append(ls)
            collecting_table = True
        else:
            if collecting_table:
                new_inner.append(_build_md_table(table_lines, styles, inner_width=doc_width - 2.4*cm))
                table_lines = []
                collecting_table = False
            new_inner.append(raw_lines[j])
        j += 1
    if table_lines:
        new_inner.append(_build_md_table(table_lines, styles, inner_width=doc_width - 2.4*cm))

    if any(isinstance(x, str) for x in new_inner):
        # re-render: mix of strings and flowables
        inner = [label_para, Spacer(1, 4)]
        for item in new_inner:
            if isinstance(item, str):
                s = item.strip()
                if s == "":
                    inner.append(Spacer(1, 3))
                elif re.match(r'^[-*]\s+', s):
                    inner.append(Paragraph("• " + md_inline_to_rl(re.sub(r'^[-*]\s+', '', s)), styles["bullet"]))
                else:
                    inner.append(Paragraph(md_inline_to_rl(s) if s else " ", styles["comment_body"]))
            else:
                inner.append(item)
    else:
        inner = [label_para, Spacer(1, 4)] + [x for x in new_inner]

    pad = 8
    data = [[inner]]
    t = Table(data, colWidths=[doc_width - 0.2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), C_BOX_COMMENT),
        ("BOX",        (0,0), (-1,-1), 1.2, C_BORDER),
        ("LEFTPADDING",  (0,0), (-1,-1), pad),
        ("RIGHTPADDING", (0,0), (-1,-1), pad),
        ("TOPPADDING",   (0,0), (-1,-1), pad),
        ("BOTTOMPADDING",(0,0), (-1,-1), pad),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    flowables.append(KeepTogether([t, Spacer(1, 4)]))


def _emit_response_box(response_lines, flowables, styles, doc_width):
    """Render a tinted response box."""
    if not response_lines:
        return
    # First line might be the "Response N:" label
    first = response_lines[0].strip()
    has_label = bool(re.match(r'^\*\*Response\s*\w+', first))

    if has_label:
        label_para = Paragraph(md_inline_to_rl(first), styles["response_label"])
        rest_lines = response_lines[1:]
    else:
        label_para = Paragraph("<b>Author Response:</b>", styles["response_label"])
        rest_lines = response_lines

    # Check for inline tables
    inner = [label_para, Spacer(1, 4)]
    j = 0
    tbl_buf = []
    text_buf = []
    while j < len(rest_lines):
        ls = rest_lines[j].strip()
        if ls.startswith("|"):
            if text_buf:
                inner += _parse_block_lines(text_buf, styles, is_response=True)
                text_buf = []
            tbl_buf.append(ls)
        else:
            if tbl_buf:
                inner.append(_build_md_table(tbl_buf, styles, inner_width=doc_width - 2.4*cm))
                tbl_buf = []
            text_buf.append(rest_lines[j])
        j += 1
    if tbl_buf:
        inner.append(_build_md_table(tbl_buf, styles, inner_width=doc_width - 2.4*cm))
    if text_buf:
        inner += _parse_block_lines(text_buf, styles, is_response=True)

    pad = 8
    data = [[inner]]
    t = Table(data, colWidths=[doc_width - 0.2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), C_BOX_RESP),
        ("BOX",        (0,0), (-1,-1), 1.2, C_BORDER_R),
        ("LEFTPADDING",  (0,0), (-1,-1), pad),
        ("RIGHTPADDING", (0,0), (-1,-1), pad),
        ("TOPPADDING",   (0,0), (-1,-1), pad),
        ("BOTTOMPADDING",(0,0), (-1,-1), pad),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    flowables.append(KeepTogether([t, Spacer(1, 6)]))


def _build_md_table(table_lines, styles, inner_width=None):
    """Build a ReportLab Table from markdown pipe-table lines."""
    if inner_width is None:
        inner_width = A4[0] - 2 * MARGIN

    rows = []
    for line in table_lines:
        # Skip separator rows (---|---| etc.)
        if re.match(r'^\|[-:| ]+\|$', line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)

    if not rows:
        return Spacer(1, 2)

    max_cols = max(len(r) for r in rows)
    # Pad short rows
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    col_w = inner_width / max_cols

    formatted = []
    for ridx, row in enumerate(rows):
        style = styles["table_hdr"] if ridx == 0 else styles["table_cell"]
        formatted.append([Paragraph(md_inline_to_rl(c), style) for c in row])

    t = Table(formatted, colWidths=[col_w] * max_cols, repeatRows=1)

    ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_TABLE_HDR),
        ("TEXTCOLOR",  (0, 0), (-1, 0), white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#bbbbbb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, C_TABLE_ROW]),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ])
    t.setStyle(ts)
    return t


# ── Header / metadata block ───────────────────────────────────────────────────

def build_header_block(md_text, styles, doc_width):
    """Extract manuscript metadata and build a styled header."""
    lines = md_text.splitlines()
    meta = {}
    for line in lines:
        for key in ["Manuscript ID", "Journal", "Review submitted", "Recommendation"]:
            m = re.match(r'\*\*' + key + r'\*\*[:\s]+(.*)', line.strip())
            if m:
                meta[key] = m.group(1).strip()

    flowables = []

    # Title bar
    title_para = Paragraph(
        "Author Response to Reviewers",
        styles["title"]
    )
    subtitle_para = Paragraph(
        "AI-Augmented Compliance Auditing for Cloud Systems: A Hybrid ML–LLM Approach",
        styles["subtitle"]
    )
    flowables.append(title_para)
    flowables.append(subtitle_para)
    flowables.append(Spacer(1, 8))
    flowables.append(HRFlowable(width="100%", thickness=2, color=C_ACCENT, spaceAfter=8))

    # Metadata table
    rows = []
    for k, v in meta.items():
        rows.append([
            Paragraph(k + ":", styles["meta_label"]),
            Paragraph(v, styles["meta_value"]),
        ])
    if rows:
        t = Table(rows, colWidths=[4.5*cm, doc_width - 4.5*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), C_META_BG),
            ("BOX",  (0,0), (-1,-1), 0.5, C_RULE),
            ("GRID", (0,0), (-1,-1), 0.3, C_RULE),
            ("TOPPADDING",    (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
            ("RIGHTPADDING",  (0,0), (-1,-1), 6),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        flowables.append(t)
        flowables.append(Spacer(1, 12))

    return flowables


# ── Page template with footer ─────────────────────────────────────────────────

def make_page_template(canvas, doc):
    canvas.saveState()
    # Footer rule + text
    canvas.setStrokeColor(C_RULE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 1.5*cm, PAGE_W - MARGIN, 1.5*cm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(HexColor("#777777"))
    canvas.drawString(MARGIN, 1.1*cm,
        "futureinternet-4270373 | Future Internet (MDPI) | Major Revision — May 2026")
    canvas.drawRightString(PAGE_W - MARGIN, 1.1*cm, f"Page {doc.page}")
    canvas.restoreState()


# ── Main conversion routine ───────────────────────────────────────────────────

def convert(md_path, pdf_path, reviewer_label):
    with open(md_path, "r") as f:
        md_text = f.read()

    styles = build_styles()
    doc_width = PAGE_W - 2 * MARGIN

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=2.2*cm, bottomMargin=2.2*cm,
        title=f"Author Response — {reviewer_label}",
        author="Moise Iradukunda Ingabire; Jema David Ndibwile",
        subject="futureinternet-4270373 Major Revision",
    )

    story = []

    # Header metadata block
    story += build_header_block(md_text, styles, doc_width)

    # Reviewer label sub-heading (from file name, not from inside content)
    story.append(Paragraph(
        f"<b>Responses to {reviewer_label}</b>",
        ParagraphStyle("RevLabel",
            fontName="Helvetica-Bold", fontSize=12,
            textColor=C_DARK, spaceBefore=4, spaceAfter=6, leading=16)
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_ACCENT, spaceAfter=8))

    # Body
    story += parse_md_to_flowables(md_text, styles, doc_width)

    doc.build(story, onFirstPage=make_page_template, onLaterPages=make_page_template)
    print(f"  ✓ {pdf_path}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    base = "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine/Research project Fall to Spring"

    files = [
        ("reviewer1_comments.md", "reviewer_response_1.pdf", "Reviewer 1"),
        ("reviewer2_comments.md", "reviewer_response_2.pdf", "Reviewer 2"),
        ("reviewer3_comments.md", "reviewer_response_3.pdf", "Reviewer 3"),
    ]

    for md_name, pdf_name, label in files:
        md_path  = os.path.join(base, md_name)
        pdf_path = os.path.join(base, pdf_name)
        print(f"Converting {md_name} → {pdf_name} ...")
        convert(md_path, pdf_path, label)

    print("\nDone. PDFs saved to:")
    for _, pdf_name, _ in files:
        print(f"  {os.path.join(base, pdf_name)}")
