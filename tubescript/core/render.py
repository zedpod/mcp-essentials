"""Markdown rendering for tubescript Result types."""

from .i18n import t
from .types import Result, Transcript, TranscriptList


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
    if isinstance(data, TranscriptList):
        return _render_list(data, lang)
    if isinstance(data, Transcript):
        return _render_transcript(data, lang)
    return f"**Result**: {data}"


def _render_list(tl: TranscriptList, lang: str) -> str:
    lines = [
        f"# {t('title.list', lang)}",
        "",
        f"- **{t('label.video_id', lang)}**: `{tl.video_id}`",
        f"- **{t('label.tracks', lang)}**: {len(tl.tracks)}",
        "",
        "| Code | Language | Auto | Translatable |",
        "|---|---|:---:|:---:|",
    ]
    for tr in tl.tracks:
        lines.append(
            f"| `{tr.language_code}` | {tr.language} | "
            f"{'✓' if tr.is_generated else '—'} | {'✓' if tr.is_translatable else '—'} |"
        )
    return "\n".join(lines)


def _render_transcript(tr: Transcript, lang: str) -> str:
    parts = [
        f"# {t('title.transcript', lang)}",
        "",
        f"- **{t('label.video_id', lang)}**: `{tr.video_id}`",
        f"- **{t('label.language', lang)}**: `{tr.language_code}`"
        f"{' (auto)' if tr.is_generated else ''}",
        f"- **{t('label.format', lang)}**: `{tr.format}`",
        f"- **{t('label.chars', lang)}**: {tr.char_count}"
        + (f"  •  **{t('label.entries', lang)}**: {len(tr.entries)}" if tr.entries else ""),
    ]
    if tr.translated_to:
        parts.append(f"- **{t('label.translated_to', lang)}**: `{tr.translated_to}`")
    if tr.truncated:
        parts.append(f"\n_{t('note.truncated', lang)}_")
    parts.append("")
    parts.append("```" + (tr.format if tr.format != "text" else ""))
    parts.append(tr.text)
    parts.append("```")
    return "\n".join(parts)
