"""OWUI Tools wrapper for sitepulse."""

from pydantic import BaseModel, Field

from sitepulse.core import inspect, to_markdown  # noqa: F401


class Tools:
    class Valves(BaseModel):
        DEFAULT_LANGUAGE: str = Field(
            default="en",
            description="Output language. 'en' or 'tr'.",
        )
        TIMEOUT_SECONDS: float = Field(
            default=6.0,
            description="Per-check timeout. The whole inspect runs checks in parallel.",
        )

    def __init__(self):
        self.valves = self.Valves()
        self.citation = False

    def _lang(self, language: str | None) -> str:
        return (language or self.valves.DEFAULT_LANGUAGE or "en").strip()

    def inspect(
        self,
        domain: str,
        checks: list[str] | None = None,
        language: str | None = None,
    ) -> str:
        """
        Snapshot a domain: DNS, RDAP, TLS, HTTP/HTTPS.

        Use when: "DNS records of X" / "SSL sertifikası" / "kim kayıt ettirmiş"
        / "https çalışıyor mu". Skip for page content audits (pagesignal),
        WHOIS history, port scans, or general connectivity questions.
        """
        lang = self._lang(language)
        result = inspect(
            domain,
            checks=checks,
            language=lang,
            timeout_seconds=self.valves.TIMEOUT_SECONDS,
        )
        return to_markdown(result, lang=lang)
