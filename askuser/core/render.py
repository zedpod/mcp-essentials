"""Markdown rendering for askuser Result types."""

from .i18n import t
from .types import Answer, Question, Result


def to_markdown(result: Result[Answer], lang: str = "en", question: Question | None = None) -> str:
    if not result.ok or result.data is None:
        if result.error is None:
            return f"**Error**: unknown failure (lang={lang})"
        msg = result.error.message_tr if lang == "tr" else result.error.message_en
        body = f"**Error** ({result.error.code}): {msg}"
        if result.error.hint:
            body += f"\n\n_Hint: {result.error.hint}_"
        return body

    a = result.data
    if a.type == "skip":
        return f"_{t('label.no_answer', lang)}_"
    if a.type == "cancelled":
        return f"_{t('label.cancelled', lang)}_"
    if a.type == "timeout":
        return f"_{t('label.timeout', lang)}_"
    if a.type == "custom":
        return f"**{t('label.user_typed', lang)}**: {a.custom_text}"
    if a.type == "select":
        items = ", ".join(f"`{v}`" for v in a.values)
        return f"**{t('label.user_selected', lang)}**: {items}"
    return str(a)
