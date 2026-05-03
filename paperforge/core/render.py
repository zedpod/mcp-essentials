"""OWUI-side markdown rendering for paperforge Result types."""

from .i18n import t
from .types import DocumentArtifact, Result


def to_markdown(result: Result[DocumentArtifact], lang: str = "en") -> str:
    if not result.ok or result.data is None:
        if result.error is None:
            return f"**Error**: unknown failure (lang={lang})"
        msg = result.error.message_tr if lang == "tr" else result.error.message_en
        body = f"**Error** ({result.error.code}): {msg}"
        if result.error.hint:
            body += f"\n\n_Hint: {result.error.hint}_"
        return body

    a = result.data
    parts = [
        f"# {t('title', lang)} - `{a.format}`",
        "",
        f"**{a.title}**",
        "",
        f"- **{t('label.file_path', lang)}**: `{a.file_path}`",
        f"- **{t('label.size', lang)}**: `{a.byte_length}` bytes",
        f"- **{t('label.sections', lang)}**: {a.sections_count}  •  "
        f"**{t('label.decisions', lang)}**: {a.decisions_count}  •  "
        f"**{t('label.questions', lang)}**: {a.open_questions_count}  •  "
        f"**{t('label.steps', lang)}**: {a.next_steps_count}",
        "",
        "---",
        "",
        a.preview_md,
    ]
    return "\n".join(parts)
