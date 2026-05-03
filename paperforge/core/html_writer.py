"""HTML rendering — minimal, dependency-free; produces a clean readable page."""

import html


def _escape_block(md: str) -> str:
    """Very small markdown→HTML — handles headings, bullet lists, paragraphs, and bold/italic.

    For full-featured rendering, install `markdown` and use `_with_markdown_lib` below.
    """
    out_lines: list[str] = []
    in_list = False
    for raw_line in md.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            if in_list:
                out_lines.append("</ul>")
                in_list = False
            out_lines.append("")
            continue
        # Headings
        m = 0
        while m < len(line) and line[m] == "#":
            m += 1
        if m and m <= 6 and line[m : m + 1] == " ":
            if in_list:
                out_lines.append("</ul>")
                in_list = False
            out_lines.append(f"<h{m}>{html.escape(line[m + 1 :].strip())}</h{m}>")
            continue
        # Bullets
        if line.lstrip().startswith(("- ", "* ")):
            if not in_list:
                out_lines.append("<ul>")
                in_list = True
            text = line.lstrip()[2:]
            out_lines.append(f"<li>{_inline(text)}</li>")
            continue
        # Blockquote
        if line.startswith(">"):
            if in_list:
                out_lines.append("</ul>")
                in_list = False
            out_lines.append(f"<blockquote>{_inline(line[1:].strip())}</blockquote>")
            continue
        # Horizontal rule
        if line.strip() == "---":
            if in_list:
                out_lines.append("</ul>")
                in_list = False
            out_lines.append("<hr>")
            continue
        # Plain paragraph
        if in_list:
            out_lines.append("</ul>")
            in_list = False
        out_lines.append(f"<p>{_inline(line)}</p>")

    if in_list:
        out_lines.append("</ul>")
    return "\n".join(out_lines)


def _inline(text: str) -> str:
    """Inline markdown: **bold**, *italic*, `code`, [link](url)."""
    import re

    s = html.escape(text)
    s = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\w)\*([^\*]+)\*(?!\w)", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>',
        s,
    )
    return s


_HTML_TEMPLATE = """<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      max-width: 760px; margin: 40px auto; padding: 0 20px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #1d1d1f; line-height: 1.6;
    }}
    h1 {{ font-size: 32px; margin: 0 0 8px; }}
    h2 {{ font-size: 22px; margin: 28px 0 8px; border-bottom: 1px solid #e5e5e7; padding-bottom: 6px; }}
    h3 {{ font-size: 17px; margin: 20px 0 6px; }}
    h4 {{ font-size: 15px; margin: 16px 0 4px; }}
    blockquote {{ border-left: 3px solid #ffb084; margin: 8px 0 14px; padding: 4px 12px; color: #444; background: #fff8f3; border-radius: 0 6px 6px 0; }}
    code {{ background: #f4f4f5; padding: 1px 4px; border-radius: 4px; font-family: ui-monospace, "Cascadia Code", Menlo, monospace; }}
    a {{ color: #d4651a; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    hr {{ border: 0; border-top: 1px solid #e5e5e7; margin: 28px 0; }}
    .pf-meta {{ color: #6e6e73; font-size: 13px; margin-bottom: 16px; }}
    ul {{ padding-left: 22px; }}
    li {{ margin: 4px 0; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def render_html(
    markdown_source: str, *, title: str, language: str = "en", meta_line: str | None = None
) -> str:
    # Strip the YAML frontmatter; HTML doesn't need it.
    lines = markdown_source.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines = lines[i + 1 :]
                break
    body_md = "\n".join(lines)
    body_html = _escape_block(body_md)
    if meta_line:
        body_html = f'<p class="pf-meta">{html.escape(meta_line)}</p>\n' + body_html
    return _HTML_TEMPLATE.format(
        lang=html.escape(language), title=html.escape(title), body=body_html
    )
