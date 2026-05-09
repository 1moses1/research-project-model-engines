"""
Compile supplementary_appendix.tex → supplementary_appendix.pdf
via LaTeX → HTML → WeasyPrint (no LaTeX installation required).
"""

import re, os

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@400;600;700&family=Source+Code+Pro:wght@400;600&display=swap');

@page {
    size: A4;
    margin: 2.2cm 2.4cm 2.4cm 2.4cm;
    @bottom-center {
        content: "futureinternet-4270373 · Supplementary Appendix · May 2026  —  page " counter(page);
        font-family: 'Source Sans 3', sans-serif;
        font-size: 8pt;
        color: #888;
    }
}

body {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 10.5pt;
    line-height: 1.55;
    color: #111;
}

/* ── Cover header ─────────────────────────────────────────────── */
.doc-title   { font-family:'Source Sans 3',sans-serif; font-size:18pt;
               font-weight:700; color:#1a2a3a; margin:0 0 4pt 0; }
.doc-subtitle{ font-family:'Source Sans 3',sans-serif; font-size:11pt;
               color:#2c5f8a; margin:0 0 2pt 0; }
.doc-authors { font-family:'Source Sans 3',sans-serif; font-size:9.5pt;
               color:#555; margin:0 0 12pt 0; }
.header-rule { border:none; border-top:2.5pt solid #2c5f8a; margin:10pt 0 14pt 0; }

/* ── TOC ──────────────────────────────────────────────────────── */
.toc { background:#f5f8fc; border:1pt solid #ccd9e8; padding:10pt 14pt;
       margin-bottom:18pt; }
.toc-title { font-family:'Source Sans 3',sans-serif; font-weight:700;
             font-size:10pt; color:#1a2a3a; margin-bottom:6pt; }
.toc ul  { margin:0; padding-left:16pt; }
.toc li  { margin:2pt 0; font-size:9.5pt; color:#2c5f8a; }
.toc a   { color:#2c5f8a; text-decoration:none; }

/* ── Section headings ─────────────────────────────────────────── */
h1 { font-family:'Source Sans 3',sans-serif; font-size:14pt; font-weight:700;
     color:#1a2a3a; margin:22pt 0 6pt 0; border-bottom:1.5pt solid #2c5f8a;
     padding-bottom:3pt; page-break-after:avoid; }
h2 { font-family:'Source Sans 3',sans-serif; font-size:12pt; font-weight:700;
     color:#2c5f8a; margin:16pt 0 5pt 0; page-break-after:avoid; }
h3 { font-family:'Source Sans 3',sans-serif; font-size:10.5pt; font-weight:600;
     color:#1a2a3a; margin:12pt 0 4pt 0; page-break-after:avoid; }

/* ── Tables ───────────────────────────────────────────────────── */
.table-wrap  { margin:12pt 0; page-break-inside:avoid; }
.table-caption { font-family:'Source Sans 3',sans-serif; font-size:9pt;
                 font-weight:600; color:#333; margin-bottom:5pt; }
.table-num   { color:#2c5f8a; }
table { border-collapse:collapse; width:100%; font-size:9pt; }
thead tr { background:#2c5f8a; color:#fff; }
thead th { padding:5pt 6pt; text-align:left; font-weight:600;
           border:0.4pt solid #1a4a6a; }
tbody tr:nth-child(even)  { background:#f0f4f8; }
tbody tr:nth-child(odd)   { background:#fff; }
td { padding:4pt 6pt; border:0.4pt solid #ccc; vertical-align:top; }
td.center, th.center { text-align:center; }
td.right { text-align:right; }
.table-note { font-size:8.5pt; color:#444; margin-top:5pt; font-style:italic; }

/* ── Lists ────────────────────────────────────────────────────── */
ul, ol { margin:4pt 0 6pt 0; padding-left:20pt; }
li { margin:2pt 0; }

/* ── Paragraphs ───────────────────────────────────────────────── */
p { margin:4pt 0 7pt 0; text-align:justify; }
.noindent { text-indent:0; }

/* ── Verbatim / code ──────────────────────────────────────────── */
pre  { background:#f4f4f4; border:0.8pt solid #ddd; padding:8pt 10pt;
       font-family:'Source Code Pro',Courier,monospace; font-size:8.2pt;
       line-height:1.45; white-space:pre-wrap; margin:8pt 0;
       border-left:3pt solid #2c5f8a; }
code { font-family:'Source Code Pro',Courier,monospace; font-size:8.5pt;
       background:#f0f0f0; padding:0pt 2pt; border-radius:2pt; }

/* ── Math ─────────────────────────────────────────────────────── */
.math-block { font-family:'Source Serif 4',serif; font-style:italic;
              text-align:center; margin:8pt 0; font-size:10.5pt; }
sup { font-size:7pt; vertical-align:super; line-height:0; }
sub { font-size:7pt; vertical-align:sub;   line-height:0; }

/* ── Footnotes ─────────────────────────────────────────────────── */
.footnote { font-size:8.2pt; color:#555; border-top:0.5pt solid #ccc;
            margin-top:10pt; padding-top:4pt; }

/* ── Misc ──────────────────────────────────────────────────────── */
hr   { border:none; border-top:0.5pt solid #ccc; margin:10pt 0; }
.bold { font-weight:700; }
.ital { font-style:italic; }
a    { color:#2c5f8a; }
"""

# ── LaTeX → HTML helpers ──────────────────────────────────────────────────────

def escape_html(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

MATH_SYMS = {
    r"\alpha":"α", r"\beta":"β", r"\gamma":"γ", r"\delta":"δ",
    r"\epsilon":"ε", r"\zeta":"ζ", r"\eta":"η", r"\theta":"θ",
    r"\lambda":"λ", r"\mu":"μ", r"\xi":"ξ", r"\pi":"π",
    r"\rho":"ρ", r"\sigma":"σ", r"\tau":"τ", r"\phi":"φ",
    r"\chi":"χ", r"\psi":"ψ", r"\omega":"ω",
    r"\Omega":"Ω", r"\Sigma":"Σ", r"\Pi":"Π", r"\Delta":"Δ",
    r"\geq":"≥", r"\leq":"≤", r"\neq":"≠", r"\approx":"≈",
    r"\pm":"±", r"\cdot":"·", r"\times":"×", r"\div":"÷",
    r"\in":"∈", r"\notin":"∉", r"\subset":"⊂", r"\cup":"∪",
    r"\cap":"∩", r"\infty":"∞", r"\rightarrow":"→", r"\leftarrow":"←",
    r"\Rightarrow":"⇒", r"\Leftarrow":"⇐", r"\leftrightarrow":"↔",
    r"\bar{x}": "x̄",
    r"\hat{p}": "p<sup>^</sup>",
    r"\hat{n}": "n<sup>^</sup>",
    r"\{":"{", r"\}":"}",
    r"\,": " ", r"\;": " ", r"\ ": " ",
    r"\ldots":"…", r"\cdots":"⋯",
    r"---": "—", r"--": "–",
}

def convert_math_inline(expr):
    """Convert LaTeX math expression to HTML."""
    # Named symbols (longest first)
    for k, v in sorted(MATH_SYMS.items(), key=lambda x: -len(x[0])):
        expr = expr.replace(k, v)
    # \text{...}
    expr = re.sub(r'\\(?:text|mathrm|mathit|mathbf|textbf|textit)\{([^}]*)\}', r'\1', expr)
    # \frac{a}{b}
    expr = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', expr)
    # \sqrt{...}
    def sqrt_r(m):
        inner = m.group(1)
        inner = re.sub(r'\^\{([^}]+)\}', r'<sup>\1</sup>', inner)
        inner = re.sub(r'\^([a-zA-Z0-9])', r'<sup>\1</sup>', inner)
        return f"√({inner})"
    expr = re.sub(r'\\sqrt\{([^}]+)\}', sqrt_r, expr)
    # Superscripts
    expr = re.sub(r'\^\{([^}]+)\}', r'<sup>\1</sup>', expr)
    expr = re.sub(r'\^([a-zA-Z0-9])', r'<sup>\1</sup>', expr)
    # Subscripts
    expr = re.sub(r'_\{([^}]+)\}', r'<sub>\1</sub>', expr)
    expr = re.sub(r'_([a-zA-Z0-9])', r'<sub>\1</sub>', expr)
    # Remaining unknown commands
    expr = re.sub(r'\\[a-zA-Z]+', '', expr)
    return expr

def math_to_html(text):
    """Replace $...$ and $$...$$ with HTML italic+math spans."""
    def repl_display(m):
        return f'<div class="math-block"><i>{convert_math_inline(m.group(1).strip())}</i></div>'
    def repl_inline(m):
        return f'<i>{convert_math_inline(m.group(1))}</i>'
    text = re.sub(r'\$\$(.+?)\$\$', repl_display, text, flags=re.DOTALL)
    text = re.sub(r'\$(.+?)\$',     repl_inline,  text)
    return text

def inline_fmt(text):
    """Handle inline LaTeX formatting → HTML."""
    text = escape_html(text)
    # Special chars
    text = text.replace("~", " ")          # non-breaking space
    text = text.replace("---", "—").replace("--", "–")
    text = text.replace("``", "“").replace("''", "”")
    text = text.replace("`",  "‘").replace("'",  "’")
    # Math
    text = math_to_html(text)
    # \textbf, \textit, \emph
    text = re.sub(r'\\textbf\{([^}]*)\}',  r'<strong>\1</strong>', text)
    text = re.sub(r'\\textit\{([^}]*)\}',  r'<em>\1</em>',         text)
    text = re.sub(r'\\emph\{([^}]*)\}',    r'<em>\1</em>',         text)
    text = re.sub(r'\\texttt\{([^}]*)\}',  r'<code>\1</code>',     text)
    text = re.sub(r'\\text\{([^}]*)\}',    r'\1',                  text)
    # \url{...}
    text = re.sub(r'\\url\{([^}]*)\}',
                  lambda m: f'<a href="{m.group(1)}">{escape_html(m.group(1))}</a>', text)
    text = re.sub(r'\\href\{([^}]*)\}\{([^}]*)\}', r'<a href="\1">\2</a>', text)
    # Spacing / layout commands that have no HTML equivalent
    for cmd in [r'\\noindent', r'\\vspace\*?\{[^}]*\}', r'\\hspace\*?\{[^}]*\}',
                r'\\medskip', r'\\bigskip', r'\\smallskip', r'\\par',
                r'\\newline', r'\\\\', r'\\centering', r'\\raggedright',
                r'\\label\{[^}]*\}', r'\\pagebreak', r'\\newpage',
                r'\\clearpage', r'\\setlength\{[^}]*\}\{[^}]*\}',
                r'\\addlinespace', r'\\toprule', r'\\midrule', r'\\bottomrule',
                r'\\multicolumn\{[^}]*\}\{[^}]*\}', r'\\multirow\{[^}]*\}\{[^}]*\}',
                r'\\caption\{[^}]*\}',   # already handled separately
                r'\\small', r'\\footnotesize', r'\\normalsize', r'\\large',
                r'\\Large', r'\\LARGE', r'\\huge', r'\\Huge',
                r'\\bf', r'\\it', r'\\rm', r'\\tt',
                r'\\[A-Za-z]+\*?']:
        text = re.sub(cmd, '', text)
    return text.strip()


# ── Table parser ──────────────────────────────────────────────────────────────

def parse_tabular(body, col_spec):
    """Convert tabular/longtable body text to an HTML <table>."""
    # Determine column alignments from spec like lrrrr or p{3cm}p{5cm}
    aligns = []
    for ch in col_spec:
        if ch == 'l' or ch.startswith('p'): aligns.append('left')
        elif ch == 'r': aligns.append('right')
        elif ch == 'c': aligns.append('center')

    # Strip decorative rules
    body = re.sub(r'\\(top|mid|bottom|h)rule', '', body)
    body = re.sub(r'\\addlinespace', '', body)
    body = re.sub(r'\\endfirsthead.*?(?=\\)', '', body, flags=re.DOTALL)
    body = re.sub(r'\\endhead.*?(?=\\)', '', body, flags=re.DOTALL)
    body = re.sub(r'\\endfoot.*?(?=\\)', '', body, flags=re.DOTALL)
    body = re.sub(r'\\endlastfoot', '', body)
    body = re.sub(r'\\multicolumn\{(\d+)\}\{[^}]*\}\{([^}]*)\}',
                  lambda m: (r'\1 ' * (int(m.group(1))-1)) + m.group(2), body)

    rows = []
    for raw_row in body.split(r'\\'):
        raw_row = raw_row.strip()
        if not raw_row or raw_row.startswith('%'):
            continue
        cells = raw_row.split('&')
        rows.append([inline_fmt(c.strip()) for c in cells])

    if not rows:
        return '<p><em>(empty table)</em></p>'

    html = ['<table>']
    # First non-empty row → header
    first = True
    for ridx, row in enumerate(rows):
        if not any(c.strip() for c in row):
            continue
        if first:
            html.append('<thead><tr>')
            for cidx, cell in enumerate(row):
                al = aligns[cidx] if cidx < len(aligns) else 'left'
                html.append(f'<th class="{al}">{cell}</th>')
            html.append('</tr></thead><tbody>')
            first = False
        else:
            html.append('<tr>')
            for cidx, cell in enumerate(row):
                al = aligns[cidx] if cidx < len(aligns) else 'left'
                html.append(f'<td class="{al}">{cell}</td>')
            html.append('</tr>')
    html.append('</tbody></table>')
    return '\n'.join(html)


# ── Environment parsers ───────────────────────────────────────────────────────

def parse_itemize(body, ordered=False):
    tag = 'ol' if ordered else 'ul'
    items = re.split(r'\\item\b', body)
    html = [f'<{tag}>']
    for item in items:
        item = item.strip()
        if not item:
            continue
        html.append(f'<li>{inline_fmt(item)}</li>')
    html.append(f'</{tag}>')
    return '\n'.join(html)


# ── Main LaTeX → HTML converter ───────────────────────────────────────────────

# Table counter for captions
_table_counter = [0]

def latex_to_html(tex):
    """Convert the full .tex file body to an HTML fragment."""
    # ── Strip preamble up to \begin{document} ────────────────────────────────
    doc_start = tex.find(r'\begin{document}')
    if doc_start != -1:
        tex = tex[doc_start + len(r'\begin{document}'):]
    doc_end = tex.find(r'\end{document}')
    if doc_end != -1:
        tex = tex[:doc_end]

    # ── Remove \maketitle, \tableofcontents (we build our own) ───────────────
    tex = re.sub(r'\\maketitle', '', tex)
    tex = re.sub(r'\\tableofcontents', '', tex)
    tex = re.sub(r'\\newpage', '', tex)

    # ── Collect section headings for TOC ─────────────────────────────────────
    toc_entries = []
    def register_heading(level, title, anchor):
        toc_entries.append((level, title, anchor))

    # ── Process verbatim blocks first (protect from other transforms) ─────────
    verbatim_store = {}
    def stash_verbatim(m):
        key = f"__VERBATIM_{len(verbatim_store)}__"
        verbatim_store[key] = f'<pre>{escape_html(m.group(1))}</pre>'
        return key
    tex = re.sub(r'\\begin\{verbatim\}(.*?)\\end\{verbatim\}',
                 stash_verbatim, tex, flags=re.DOTALL)

    # ── Process table/longtable environments ──────────────────────────────────
    table_store = {}
    def stash_table(m):
        env = m.group(1)       # 'table' or 'longtable'
        body = m.group(2)
        key = f"__TABLE_{len(table_store)}__"

        # Extract caption
        cap_m = re.search(r'\\caption\{(.*?)\}', body, re.DOTALL)
        cap_text = inline_fmt(cap_m.group(1)) if cap_m else ''
        _table_counter[0] += 1
        tnum = _table_counter[0]

        # Extract tabular spec and body
        tab_m = re.search(r'\\begin\{(?:tabular|longtable)\}\{([^}]*)\}(.*?)\\end\{(?:tabular|longtable)\}',
                          body, re.DOTALL)
        if tab_m:
            col_spec = tab_m.group(1)
            tab_body = tab_m.group(2)
            table_html = parse_tabular(tab_body, col_spec)
        else:
            # longtable has spec as first arg differently
            lt_m = re.search(r'\\begin\{longtable\}\{([^}]*)\}(.*?)\\end\{longtable\}',
                             body, re.DOTALL)
            if lt_m:
                table_html = parse_tabular(lt_m.group(2), lt_m.group(1))
            else:
                table_html = '<p><em>(table parse error)</em></p>'

        # Extract notes after the table environment
        note_m = re.search(r'\\end\{(?:tabular|longtable)\}(.*?)$', body, re.DOTALL)
        note_html = ''
        if note_m:
            note_raw = note_m.group(1).strip()
            note_raw = re.sub(r'\\end\{table\*?\}', '', note_raw)
            note_raw = re.sub(r'\\(centering|small|normalsize)', '', note_raw)
            if note_raw.strip():
                note_html = f'<div class="table-note">{inline_fmt(note_raw)}</div>'

        cap_html = f'<div class="table-caption"><span class="table-num">Table {tnum}.</span> {cap_text}</div>' if cap_text else ''
        table_store[key] = (
            f'<div class="table-wrap">{cap_html}{table_html}{note_html}</div>'
        )
        return key
    tex = re.sub(r'\\begin\{(table\*?|longtable)\}(.*?)\\end\{(?:table\*?|longtable)\}',
                 stash_table, tex, flags=re.DOTALL)

    # ── Process itemize / enumerate ───────────────────────────────────────────
    def proc_list(m):
        env = m.group(1)
        body = m.group(2)
        return parse_itemize(body, ordered=(env == 'enumerate'))
    tex = re.sub(r'\\begin\{(itemize|enumerate)\}(.*?)\\end\{(?:itemize|enumerate)\}',
                 proc_list, tex, flags=re.DOTALL)

    # ── Now split into lines and process headings / paragraphs ───────────────
    lines = tex.splitlines()
    html_parts = []
    para_buf = []
    sec_counter = [0, 0, 0]  # section, subsection, subsubsection

    def flush_para():
        text = ' '.join(para_buf).strip()
        para_buf.clear()
        if not text:
            return
        # Restore stashed verbatim/tables
        for k, v in verbatim_store.items():
            if k in text:
                text = text.replace(k, v)
        for k, v in table_store.items():
            if k in text:
                text = text.replace(k, v)
        # If it's already a block element, don't wrap in <p>
        if re.match(r'\s*<(div|table|pre|ul|ol|h[1-6]|hr)', text):
            html_parts.append(text)
        else:
            html_parts.append(f'<p class="noindent">{text}</p>')

    for line in lines:
        s = line.strip()

        # Section headings
        sec_m  = re.match(r'\\section\{(.*?)\}', s)
        sub_m  = re.match(r'\\subsection\{(.*?)\}', s)
        ssub_m = re.match(r'\\subsubsection\{(.*?)\}', s)

        if sec_m:
            flush_para()
            sec_counter[0] += 1; sec_counter[1] = 0; sec_counter[2] = 0
            num = sec_counter[0]
            title = inline_fmt(sec_m.group(1))
            anchor = f"sec-{num}"
            register_heading(1, title, anchor)
            html_parts.append(f'<h1 id="{anchor}">{num}. {title}</h1>')
        elif sub_m:
            flush_para()
            sec_counter[1] += 1; sec_counter[2] = 0
            num = f"{sec_counter[0]}.{sec_counter[1]}"
            title = inline_fmt(sub_m.group(1))
            anchor = f"sec-{num}"
            register_heading(2, title, anchor)
            html_parts.append(f'<h2 id="{anchor}">{num} {title}</h2>')
        elif ssub_m:
            flush_para()
            sec_counter[2] += 1
            title = inline_fmt(ssub_m.group(1))
            anchor = f"sec-{sec_counter[0]}-{sec_counter[1]}-{sec_counter[2]}"
            html_parts.append(f'<h3 id="{anchor}">{title}</h3>')
        elif s == '' and para_buf:
            flush_para()
        elif s.startswith('%'):
            pass  # LaTeX comment
        elif s in (r'\bigskip', r'\medskip', r'\smallskip'):
            flush_para()
        else:
            # Stashed tokens get passed through
            para_buf.append(s)

    flush_para()

    body_html = '\n'.join(html_parts)
    # Final inline formatting pass on anything not yet processed
    # (catches paragraphs that weren't in stash)
    def fmt_para(m):
        inner = m.group(1)
        if any(k in inner for k in list(verbatim_store) + list(table_store)):
            return m.group(0)  # already formatted
        return f'<p class="noindent">{inline_fmt(inner)}</p>'
    # Don't re-process block elements
    body_html = re.sub(r'<p class="noindent">((?:(?!</p>).)+)</p>',
                       lambda m: f'<p class="noindent">{inline_fmt(m.group(1))}</p>',
                       body_html)

    return body_html, toc_entries


def extract_preamble_info(tex):
    """Extract title, authors from LaTeX preamble."""
    title_m  = re.search(r'\\title\{(.*?)\}',  tex, re.DOTALL)
    author_m = re.search(r'\\author\{(.*?)\}', tex, re.DOTALL)
    title  = inline_fmt(title_m.group(1))  if title_m  else "Supplementary Appendix"
    author = inline_fmt(author_m.group(1)) if author_m else ""
    # Clean up \and
    author = re.sub(r'\\and', ' &amp; ', author)
    return title, author


def build_toc_html(toc_entries):
    if not toc_entries:
        return ''
    html = ['<div class="toc"><div class="toc-title">Contents</div><ul>']
    for level, title, anchor in toc_entries:
        indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * (level - 1)
        html.append(f'<li style="margin-left:{(level-1)*12}pt">'
                    f'{indent}<a href="#{anchor}">{title}</a></li>')
    html.append('</ul></div>')
    return '\n'.join(html)


def build_full_html(tex_path):
    with open(tex_path, 'r') as f:
        tex = f.read()

    title, author = extract_preamble_info(tex)
    body_html, toc = latex_to_html(tex)
    toc_html = build_toc_html(toc)

    # Strip raw \section labels that leaked through
    body_html = re.sub(r'\\label\{[^}]*\}', '', body_html)
    body_html = re.sub(r'\\ref\{[^}]*\}', '§', body_html)
    # Clean up double-escaped entities from inline_fmt running twice
    body_html = re.sub(r'&amp;amp;', '&amp;', body_html)
    body_html = re.sub(r'&amp;lt;',  '&lt;',  body_html)
    body_html = re.sub(r'&amp;gt;',  '&gt;',  body_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
<p class="doc-title">Supplementary Appendix</p>
<p class="doc-subtitle">AI-Augmented Compliance Auditing for Cloud Systems: A Hybrid ML–LLM Approach</p>
<p class="doc-authors">{author} · Carnegie Mellon University Africa<br>
<em>futureinternet-4270373 · Future Internet (MDPI) · Major Revision, May 2026</em></p>
<hr class="header-rule">
{toc_html}
{body_html}
</body>
</html>"""


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from weasyprint import HTML, CSS as WCSS

    base = "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine/Research project Fall to Spring"
    tex_path = os.path.join(base, "supplementary_appendix.tex")
    pdf_path = os.path.join(base, "supplementary_appendix.pdf")
    html_path = tex_path.replace(".tex", "_preview.html")

    print("Parsing LaTeX …")
    html = build_full_html(tex_path)

    # Save HTML for debugging if needed
    with open(html_path, 'w') as f:
        f.write(html)
    print(f"  HTML intermediate: {html_path}")

    print("Rendering PDF via WeasyPrint …")
    HTML(string=html, base_url=base).write_pdf(pdf_path)

    size_kb = os.path.getsize(pdf_path) // 1024
    print(f"  ✓ {pdf_path}  ({size_kb} KB)")
