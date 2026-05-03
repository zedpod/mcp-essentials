"""Public API: create_document. Validates input, renders markdown, writes the requested format."""

import os
import re
from datetime import datetime, timezone
from pathlib import Path

from .docx_writer import write_docx
from .html_writer import render_html
from .i18n import normalize_lang, t
from .md_writer import render_markdown
from .pdf_writer import write_pdf
from .types import (
    Decision,
    DocumentArtifact,
    DocumentFormat,
    ErrorInfo,
    Result,
    Section,
)


def default_output_dir() -> Path:
    """Resolve the default output directory.

    Order: PAPERFORGE_OUTPUT_DIR env → ~/Documents/orzed-mcp/paperforge → ./paperforge-out.
    """
    env = os.getenv("PAPERFORGE_OUTPUT_DIR")
    if env:
        return Path(env).expanduser().resolve()
    home = Path.home()
    documents = home / "Documents"
    if documents.is_dir():
        return (documents / "orzed-mcp" / "paperforge").resolve()
    return Path.cwd() / "paperforge-out"


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug.strip("-") or "document"


def _err(code: str, lang: str, en_key: str, *, hint_key: str | None = None) -> ErrorInfo:
    return ErrorInfo(
        code=code,
        message_en=t(en_key, "en"),
        message_tr=t(en_key, "tr"),
        hint=t(hint_key, lang) if hint_key else None,
    )


_SUMMARY_MAX_CHARS = 280
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _has_content(section: Section) -> bool:
    if section.content.strip():
        return True
    return any(_has_content(child) for child in section.children)


def _derive_summary(sections: list[Section]) -> str:
    """Pull the first 1-2 sentences (or up to ~280 chars) from the first section with content."""
    for section in sections:
        text = section.content.strip()
        if not text:
            for child in section.children:
                text = child.content.strip()
                if text:
                    break
        if not text:
            continue
        sentences = [s for s in _SENTENCE_SPLIT.split(text) if s.strip()]
        picked = " ".join(sentences[:2]).strip() or text
        if len(picked) > _SUMMARY_MAX_CHARS:
            cut = picked[: _SUMMARY_MAX_CHARS - 3].rsplit(" ", 1)[0]
            picked = cut + "..."
        return picked
    return ""


def create_document(
    *,
    title: str,
    summary: str | None = None,
    sections: list[Section] | list[dict] | None = None,
    body: str | None = None,
    format: DocumentFormat = "md",
    project: str | None = None,
    decisions: list[Decision] | list[dict] | None = None,
    open_questions: list[str] | None = None,
    next_steps: list[str] | None = None,
    tags: list[str] | None = None,
    source: str | None = None,
    output_dir: str | Path | None = None,
    filename: str | None = None,
    language: str = "en",
) -> Result[DocumentArtifact]:
    """Build and write a document.

    `title` is mandatory. Provide either:
      - `sections`: an ordered list of {heading, content, children?} for structured docs, or
      - `body`: a single chunk of markdown prose for the simplest case (wrapped as one section).
    `summary` is optional; when omitted, the tool derives a 1-2 sentence summary from
    the first section that has content. Genuinely empty input (no sections, no body)
    is rejected with INVALID_INPUT - the tool will not fabricate content from nothing.
    """
    lang = normalize_lang(language)

    if not title or not title.strip():
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.empty_title"))

    section_models: list[Section] = []
    if sections:
        section_models = [Section.model_validate(s) for s in sections]
    elif body and body.strip():
        section_models = [Section(heading=title.strip(), content=body.strip())]

    if not section_models or not any(_has_content(s) for s in section_models):
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.no_content"))

    summary_clean = (summary or "").strip()
    if not summary_clean:
        summary_clean = _derive_summary(section_models)
    if not summary_clean:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.empty_summary"))
    summary = summary_clean

    decision_models = [Decision.model_validate(d) for d in (decisions or [])]
    open_q = [q.strip() for q in (open_questions or []) if q and q.strip()]
    steps = [s.strip() for s in (next_steps or []) if s and s.strip()]
    tag_list = [tag.strip() for tag in (tags or []) if tag and tag.strip()]

    if format not in ("md", "html", "docx", "pdf"):
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_format"))

    created = datetime.now(timezone.utc).replace(microsecond=0)
    md_source = render_markdown(
        title=title,
        summary=summary,
        sections=section_models,
        project=project,
        decisions=decision_models,
        open_questions=open_q,
        next_steps=steps,
        tags=tag_list,
        source=source,
        language=lang,
        created=created,
    )

    out_dir = Path(output_dir).expanduser().resolve() if output_dir else default_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    base = filename or f"{created.strftime('%Y%m%d-%H%M%S')}-{_slugify(title)}"
    target = out_dir / f"{base}.{format}"

    try:
        if format == "md":
            target.write_text(md_source, encoding="utf-8")
        elif format == "html":
            html_str = render_html(
                md_source,
                title=title,
                language=lang,
                meta_line=(f"{project} · {created.isoformat()}" if project else created.isoformat()),
            )
            target.write_text(html_str, encoding="utf-8")
        elif format == "docx":
            ok = write_docx(md_source, output_path=target, title=title)
            if not ok:
                return Result(
                    ok=False,
                    error=_err(
                        "UNSUPPORTED",
                        lang,
                        "error.docx_missing",
                        hint_key="hint.install_docx",
                    ),
                    meta={"format": format},
                )
        elif format == "pdf":
            ok = write_pdf(
                md_source,
                output_path=target,
                title=title,
                language=lang,
                meta_line=(f"{project} · {created.isoformat()}" if project else created.isoformat()),
            )
            if not ok:
                return Result(
                    ok=False,
                    error=_err(
                        "UNSUPPORTED",
                        lang,
                        "error.pdf_missing",
                        hint_key="hint.install_pdf",
                    ),
                    meta={"format": format},
                )
    except OSError as exc:
        return Result(
            ok=False,
            error=_err("INTERNAL", lang, "error.write_failed"),
            meta={"detail": str(exc)},
        )

    artifact = DocumentArtifact(
        title=title,
        format=format,
        file_path=str(target),
        byte_length=target.stat().st_size,
        sections_count=len(section_models),
        decisions_count=len(decision_models),
        open_questions_count=len(open_q),
        next_steps_count=len(steps),
        preview_md=md_source,
    )
    return Result(
        ok=True,
        data=artifact,
        meta={
            "output_dir": str(out_dir),
            "filename": target.name,
            "created": created.isoformat(),
        },
    )
