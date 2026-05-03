"""Markdown rendering for signalbrief."""

from .i18n import t
from .types import NewsBrief, Result, SourceCatalog


def to_markdown(result: Result, lang: str = "en") -> str:
    if not result.ok or result.data is None:
        if result.error is None:
            return f"**Error**: unknown failure (lang={lang})"
        msg = result.error.message_tr if lang == "tr" else result.error.message_en
        body = f"**Error** ({result.error.code}): {msg}"
        if result.error.hint:
            body += f"\n\n_Hint: {result.error.hint}_"
        return body

    data = result.data
    if isinstance(data, NewsBrief):
        return _render_brief(data, lang)
    if isinstance(data, SourceCatalog):
        return _render_catalog(data, lang)
    return f"**Result**: {data}"


def _render_brief(brief: NewsBrief, lang: str) -> str:
    parts: list[str] = [
        f"# {t('title', lang)}",
        "",
        f"**{t('label.window', lang)}**: `{brief.hours_back}` {t('label.hours_back', lang)}",
        f"**{t('label.sources', lang)}**: {len(brief.sources_used)}  •  "
        f"**{t('label.keywords', lang)}**: "
        f"{', '.join(f'`{k}`' for k in brief.keywords[:8])}"
        + (" …" if len(brief.keywords) > 8 else ""),
    ]
    if not brief.items:
        parts += ["", f"_{t('label.no_items', lang)}_"]
    else:
        parts.append("")
        for item in brief.items:
            line = f"- **[{item.title}]({item.link or '#'})** · _{item.source}_ · score `{item.score}`"
            if item.matched_keywords:
                line += " · " + ", ".join(f"`{k}`" for k in item.matched_keywords)
            parts.append(line)
            if item.summary:
                snippet = item.summary[:200] + ("…" if len(item.summary) > 200 else "")
                parts.append(f"  {snippet}")

    if brief.failed_sources:
        parts += [
            "",
            f"**{t('label.failed', lang)}**: " + ", ".join(
                f"`{f.name}` ({f.error})" for f in brief.failed_sources[:6]
            ),
        ]
    parts += ["", f"_{t('note.brief', lang)}_"]
    return "\n".join(parts)


def _render_catalog(cat: SourceCatalog, lang: str) -> str:
    parts = [f"# {t('title', lang)} — {t('label.sources', lang)}", ""]
    for src in cat.sources:
        suffix = f" · `{src.language}`" if src.language else ""
        parts.append(f"- **{src.name}** — `{src.url}`{suffix}")
    return "\n".join(parts)
