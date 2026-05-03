"""Pure validation for Question. No silent overrides - conflicting fields → INVALID_INPUT."""

from .i18n import normalize_lang, t
from .types import ErrorInfo, Question


def _err(en_key: str, lang: str) -> ErrorInfo:
    return ErrorInfo(
        code="INVALID_INPUT",
        message_en=t(en_key, "en"),
        message_tr=t(en_key, "tr"),
    )


def validate_question(q: Question, *, language: str = "en") -> ErrorInfo | None:
    lang = normalize_lang(language)
    if not q.prompt or not q.prompt.strip():
        return _err("error.empty_prompt", lang)
    if q.mode not in ("single", "multi", "free_text"):
        return _err("error.invalid_mode", lang)
    if q.mode in ("single", "multi") and not q.options:
        return _err("error.options_required", lang)
    if len(q.options) > 200:
        return _err("error.too_many_options", lang)
    if q.mode == "multi":
        if q.min_select is not None and q.max_select is not None:
            if q.min_select > q.max_select:
                return _err("error.min_max", lang)
        if q.min_select is not None and q.min_select > len(q.options):
            return _err("error.min_max", lang)
        if q.max_select is not None and q.max_select > len(q.options):
            return _err("error.min_max", lang)
    if q.timeout_s <= 0 or q.timeout_s > 1800:
        return _err("error.invalid_timeout", lang)
    return None
