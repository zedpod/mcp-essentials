"""OWUI Tools wrapper for tubescript."""

from pydantic import BaseModel, Field

from tubescript.core import get_transcript, list_transcripts, to_markdown  # noqa: F401


class Tools:
    class Valves(BaseModel):
        DEFAULT_LANGUAGE: str = Field(
            default="en",
            description="Output language. 'en' or 'tr'.",
        )
        DEFAULT_PREFER_LANG: str = Field(
            default="en,tr",
            description="Comma-separated preferred transcript languages, in order.",
        )
        MAX_CHARS: int = Field(
            default=0,
            description="Hard cap on transcript output. 0 disables truncation.",
        )

    def __init__(self):
        self.valves = self.Valves()
        self.citation = False

    def _lang(self, language: str | None) -> str:
        return (language or self.valves.DEFAULT_LANGUAGE or "en").strip()

    def _prefer(self, prefer_lang: list[str] | None) -> list[str]:
        if prefer_lang:
            return prefer_lang
        return [x.strip() for x in (self.valves.DEFAULT_PREFER_LANG or "en").split(",") if x.strip()]

    def list_transcripts(self, url_or_id: str, language: str | None = None) -> str:
        """List available transcript tracks for a YouTube video."""
        lang = self._lang(language)
        result = list_transcripts(url_or_id, language=lang)
        return to_markdown(result, lang=lang)

    def get_transcript(
        self,
        url_or_id: str,
        prefer_lang: list[str] | None = None,
        translate_to: str | None = None,
        format: str = "text",
        max_chars: int | None = None,
        language: str | None = None,
    ) -> str:
        """Fetch a YouTube transcript in text/srt/vtt/json."""
        lang = self._lang(language)
        cap = max_chars if max_chars is not None else (self.valves.MAX_CHARS or None)
        result = get_transcript(
            url_or_id,
            prefer_lang=self._prefer(prefer_lang),
            translate_to=translate_to,
            format=format,
            max_chars=cap,
            language=lang,
        )
        return to_markdown(result, lang=lang)
