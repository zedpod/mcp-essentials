"""OWUI Tools wrapper for pagesignal."""

from pydantic import BaseModel, Field

from pagesignal.core import audit_page, to_markdown  # noqa: F401


class Tools:
    class Valves(BaseModel):
        DEFAULT_LANGUAGE: str = Field(
            default="en",
            description="Output language. 'en' or 'tr'. Unknown codes fall back to 'en'.",
        )
        TIMEOUT_SECONDS: float = Field(
            default=10.0,
            description="HTTP timeout (seconds).",
        )
        USER_AGENT: str = Field(
            default="orzed-pagesignal/1.0 (+https://orzed.com)",
            description="User-Agent sent to the audited site.",
        )

    def __init__(self):
        self.valves = self.Valves()
        self.citation = False

    def _lang(self, language: str | None) -> str:
        return (language or self.valves.DEFAULT_LANGUAGE or "en").strip()

    def audit_page(
        self,
        url: str,
        target_keywords: list[str] | None = None,
        language: str | None = None,
    ) -> str:
        """
        Audit a URL: SEO + AI-answer-readiness signals.

        Use when: "audit this page" / "şu sayfayı analiz et" / "SEO check on X".
        Skip for: page-content summarization (read it inline), DNS / SSL / domain
        registration (use sitepulse), generic SEO advice (no tool needed).
        """
        lang = self._lang(language)
        result = audit_page(
            url,
            target_keywords=target_keywords,
            language=lang,
            timeout_seconds=self.valves.TIMEOUT_SECONDS,
            user_agent=self.valves.USER_AGENT,
        )
        return to_markdown(result, lang=lang)
