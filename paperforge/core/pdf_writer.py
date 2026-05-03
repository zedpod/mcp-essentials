"""PDF rendering — HTML → PDF via weasyprint when available."""

from pathlib import Path

from .html_writer import render_html


def write_pdf(
    markdown_source: str,
    *,
    output_path: Path,
    title: str,
    language: str = "en",
    meta_line: str | None = None,
) -> bool:
    try:
        import weasyprint
    except ImportError:
        return False
    except Exception:
        return False

    html_doc = render_html(
        markdown_source, title=title, language=language, meta_line=meta_line
    )
    try:
        weasyprint.HTML(string=html_doc).write_pdf(str(output_path))
        return True
    except Exception:
        return False
