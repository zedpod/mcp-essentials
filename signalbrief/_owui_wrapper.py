"""OWUI Tools wrapper for signalbrief."""

from pydantic import BaseModel, Field

from signalbrief.core import collect, list_sources, to_markdown  # noqa: F401


class Tools:
    class Valves(BaseModel):
        DEFAULT_LANGUAGE: str = Field(
            default="en",
            description="Output language. 'en' or 'tr'.",
        )
        DEFAULT_HOURS: int = Field(default=24, description="Default recency window (hours).")
        DEFAULT_MIN_SCORE: int = Field(default=2, description="Drop items below this score.")
        DEFAULT_MAX_PER_SOURCE: int = Field(default=10, description="Cap items kept per source.")

    def __init__(self):
        self.valves = self.Valves()
        self.citation = False

    def _lang(self, language: str | None) -> str:
        return (language or self.valves.DEFAULT_LANGUAGE or "en").strip()

    def collect(
        self,
        topics: list[str] | None = None,
        sources: list[dict] | None = None,
        hours: int | None = None,
        max_per_source: int | None = None,
        min_score: int | None = None,
        language: str | None = None,
    ) -> str:
        """Collect a scored news brief from RSS/Atom feeds."""
        lang = self._lang(language)
        result = collect(
            topics=topics,
            sources=sources,
            hours=hours if hours is not None else self.valves.DEFAULT_HOURS,
            max_per_source=max_per_source
            if max_per_source is not None
            else self.valves.DEFAULT_MAX_PER_SOURCE,
            min_score=min_score if min_score is not None else self.valves.DEFAULT_MIN_SCORE,
            language=lang,
        )
        return to_markdown(result, lang=lang)

    def list_sources(self, language: str | None = None) -> str:
        """Show the built-in default RSS/Atom source catalog."""
        lang = self._lang(language)
        return to_markdown(list_sources(language=lang), lang=lang)
