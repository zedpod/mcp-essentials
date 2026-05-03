"""OWUI Tools wrapper for currencypulse — concatenated by tools/bundle_owui.py.

The wrapper avoids importing from `currencypulse.core` directly: when this file
is concatenated into `owui.py`, the intra-package imports are stripped and the
core symbols (`rate`, `convert`, `snapshot`, `timeseries`, `to_markdown`) resolve
to the inlined module-level callables. We rename them inside `Tools` methods to
avoid shadowing.
"""

from pydantic import BaseModel, Field

# Resolved at runtime to either the inlined core symbols (in the bundle) or via
# this synthetic re-export when running from the package tree.
from currencypulse.core import (  # noqa: F401 — kept for IDE/dev runs
    convert,
    rate,
    snapshot,
    timeseries,
    to_markdown,
)


class Tools:
    class Valves(BaseModel):
        DEFAULT_LANGUAGE: str = Field(
            default="en",
            description="Output language. 'en' or 'tr'. Unknown codes fall back to 'en'.",
        )
        DEFAULT_BASE: str = Field(
            default="USD",
            description="Default base currency for snapshot() when caller omits it.",
        )
        DEFAULT_TIMEOUT_SECONDS: int = Field(
            default=10,
            description="HTTP timeout per provider attempt (clamped 2-20).",
        )

    def __init__(self):
        self.valves = self.Valves()
        self.citation = False

    def _lang(self, language: str | None) -> str:
        return (language or self.valves.DEFAULT_LANGUAGE or "en").strip()

    def rate(self, base: str, quote: str, on: str | None = None, language: str | None = None) -> str:
        """
        FX rate (latest or historical) for two ISO 4217 codes.

        Use when: "USD/EUR kuru" / "1 dolar kaç euro". Skip if the user gave
        an amount (use convert), wants many quotes at once (snapshot), or asked
        about crypto / stocks (out of scope).
        """
        lang = self._lang(language)
        result = rate(base, quote, on=on, language=lang)
        return to_markdown(result, lang=lang)

    def convert(
        self,
        amount: float,
        base: str,
        quote: str,
        on: str | None = None,
        language: str | None = None,
    ) -> str:
        """
        Convert an amount between two currencies.

        Use when: "100 USD kaç EUR" / "convert 50 GBP to TRY". Skip if no
        amount was given (use rate). Crypto not supported.
        """
        lang = self._lang(language)
        result = convert(amount, base, quote, on=on, language=lang)
        return to_markdown(result, lang=lang)

    def snapshot(
        self,
        base: str | None = None,
        symbols: list[str] | None = None,
        language: str | None = None,
    ) -> str:
        """
        Latest rates from one base to many quote currencies in one call.

        Use when: "USD against major currencies" / "USD'nin tüm büyük
        paritelere kuru". Skip for single pair (use rate) or historical
        comparison (use timeseries).
        """
        lang = self._lang(language)
        result = snapshot(base or self.valves.DEFAULT_BASE, symbols=symbols, language=lang)
        return to_markdown(result, lang=lang)

    def timeseries(
        self,
        base: str,
        quote: str,
        start: str,
        end: str,
        language: str | None = None,
    ) -> str:
        """
        Daily rates for a pair over a date range (range capped at 366 days).

        Use when: "EUR/USD past 30 days" / "son 30 gün USD/TRY". Skip for a
        single date (use rate with `on`). Range over a year - ask the user
        to narrow before calling.
        """
        lang = self._lang(language)
        result = timeseries(base, quote, start, end, language=lang)
        return to_markdown(result, lang=lang)
