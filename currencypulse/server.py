"""currencypulse MCP server (stdio).

Run with:
    python -m currencypulse
"""

from mcp.server.fastmcp import FastMCP

from currencypulse.core import convert as core_convert
from currencypulse.core import rate as core_rate
from currencypulse.core import snapshot as core_snapshot
from currencypulse.core import timeseries as core_timeseries

mcp = FastMCP("orzed-currencypulse")


@mcp.tool()
def rate(base: str, quote: str, on: str = "", language: str = "en") -> dict:
    """Look up a foreign-exchange rate from a chained provider list.

    Args:
        base: Base currency ISO 4217 code (e.g., "USD").
        quote: Quote currency ISO 4217 code (e.g., "EUR").
        on: Optional date in YYYY-MM-DD. Empty string returns latest.
        language: Output language for messages, "en" or "tr".

    Returns:
        Result envelope. `data` is `{base, quote, value, on_date, source}`.
    """
    return core_rate(base, quote, on=on or None, language=language).model_dump(mode="json")


@mcp.tool()
def convert(
    amount: float, base: str, quote: str, on: str = "", language: str = "en"
) -> dict:
    """Convert an amount between two currencies.

    Args:
        amount: Non-negative finite number to convert.
        base: Base currency code.
        quote: Quote currency code.
        on: Optional YYYY-MM-DD date. Empty for latest.
        language: en/tr.
    """
    return core_convert(
        amount, base, quote, on=on or None, language=language
    ).model_dump(mode="json")


@mcp.tool()
def snapshot(base: str, symbols: list[str] | None = None, language: str = "en") -> dict:
    """Latest rate snapshot from `base` to multiple quote currencies.

    Args:
        base: Base currency ISO 4217 code.
        symbols: List of quote codes. None uses a global default set.
        language: en/tr.
    """
    return core_snapshot(base, symbols=symbols, language=language).model_dump(mode="json")


@mcp.tool()
def timeseries(
    base: str, quote: str, start: str, end: str, language: str = "en"
) -> dict:
    """Daily exchange-rate time series for a pair over a date range.

    Args:
        base: Base currency code.
        quote: Quote currency code.
        start: Inclusive start date YYYY-MM-DD.
        end: Inclusive end date YYYY-MM-DD. Range capped at 366 days.
        language: en/tr.
    """
    return core_timeseries(base, quote, start, end, language=language).model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
