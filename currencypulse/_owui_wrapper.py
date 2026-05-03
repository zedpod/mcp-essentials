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
        Foreign-exchange rate from a multi-source provider chain.
        :param base: Base currency code (e.g. USD).
        :param quote: Quote currency code (e.g. EUR).
        :param on: Optional YYYY-MM-DD date; default latest.
        :param language: en/tr.
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
        :param amount: Non-negative finite number.
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
        Latest rates from `base` against multiple quote currencies.
        :param base: Base code; default valve DEFAULT_BASE.
        :param symbols: List of quote codes; None uses a sensible global set.
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
        Daily rates between two dates (range capped at 366 days).
        """
        lang = self._lang(language)
        result = timeseries(base, quote, start, end, language=lang)
        return to_markdown(result, lang=lang)
