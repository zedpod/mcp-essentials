"""OWUI Tools wrapper for askuser.

OWUI injects `__event_call__` and `__event_emitter__` as keyword arguments to
async tool methods. We pass the overlay JS through `__event_call__` and parse
the resolved Promise value as our Answer.
"""

import json
from typing import Any

from pydantic import BaseModel, Field

from askuser.core import (
    Option,
    Question,
    t,
    to_markdown,
    validate_question,
)
from askuser.core.overlay import build_owui_overlay_call
from askuser.core.types import Answer, ErrorInfo, Result  # noqa: F401


class Tools:
    class Valves(BaseModel):
        DEFAULT_LANGUAGE: str = Field(
            default="en",
            description="Output language. 'en' or 'tr'.",
        )
        ACCENT_COLOR: str = Field(
            default="#E8713A",
            description="Hex color used for selected/confirm buttons.",
        )

    def __init__(self):
        self.valves = self.Valves()
        self.citation = False

    def _lang(self, language):
        return (language or self.valves.DEFAULT_LANGUAGE or "en").strip()

    async def ask_user_question(
        self,
        prompt: str,
        options: list[dict] | None = None,
        mode: str = "single",
        allow_custom: bool = True,
        required: bool = False,
        min_select: int | None = None,
        max_select: int | None = None,
        timeout_s: float = 300.0,
        language: str | None = None,
        __event_call__=None,
        **_unused: Any,
    ) -> str:
        """
        Ask the user an interactive question (single, multi, or free-text).

        :param prompt: Question text.
        :param options: List of {label, description?, value?}.
        :param mode: 'single' | 'multi' | 'free_text'.
        :param allow_custom: Show a free-text input below options.
        :param required: Hide the Skip button.
        :param min_select / max_select: Constraints for multi mode.
        :param timeout_s: Auto-resolve to `timeout` after N seconds.
        :param language: 'en' or 'tr'.
        """
        lang = self._lang(language)
        opt_models = [Option(**o) for o in (options or [])]
        question = Question(
            prompt=prompt,
            options=opt_models,
            mode=mode,
            allow_custom=allow_custom,
            required=required,
            min_select=min_select,
            max_select=max_select,
            timeout_s=timeout_s,
            accent=self.valves.ACCENT_COLOR,
        )
        err = validate_question(question, language=lang)
        if err is not None:
            return to_markdown(Result(ok=False, error=err), lang=lang)

        if __event_call__ is None:
            return to_markdown(
                Result(
                    ok=False,
                    error=ErrorInfo(
                        code="UNSUPPORTED",
                        message_en="OWUI __event_call__ channel not available.",
                        message_tr="OWUI __event_call__ kanalı kullanılamıyor.",
                    ),
                ),
                lang=lang,
            )

        js = build_owui_overlay_call(question, language=lang)
        try:
            payload = await __event_call__({"type": "execute", "data": {"code": js}})
        except Exception as exc:
            return to_markdown(
                Result(
                    ok=False,
                    error=ErrorInfo(
                        code="INTERNAL",
                        message_en=f"event_call failed: {exc.__class__.__name__}",
                        message_tr=f"event_call hatası: {exc.__class__.__name__}",
                    ),
                ),
                lang=lang,
            )

        # OWUI may pass the resolved Promise value as a JSON string or raw dict.
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except (TypeError, ValueError):
                return f"**{t('label.user_typed', lang)}**: {payload}"
        if not isinstance(payload, dict):
            return to_markdown(
                Result(
                    ok=True,
                    data=Answer(type="skip"),
                ),
                lang=lang,
            )

        ans = Answer(
            type=payload.get("type", "skip"),
            indices=payload.get("indices") or [],
            values=payload.get("values") or [],
            custom_text=payload.get("custom_text"),
            elapsed_ms=int(payload.get("elapsed_ms", 0)),
        )
        return to_markdown(Result(ok=True, data=ans), lang=lang)
