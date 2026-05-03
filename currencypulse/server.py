"""currencypulse MCP server (stdio). Run: python -m currencypulse"""

from mcp.server.fastmcp import FastMCP

from currencypulse.core import convert as core_convert
from currencypulse.core import rate as core_rate
from currencypulse.core import snapshot as core_snapshot
from currencypulse.core import timeseries as core_timeseries

mcp = FastMCP("orzed-currencypulse")


@mcp.tool()
def rate(base: str, quote: str, on: str = "", language: str = "en") -> dict:
    """Look up a foreign-exchange rate (latest or historical).

    When to use:
      - "USD/EUR rate"                 / "USD EUR kuru"
      - "1 dolar kaç euro"             / "what's a dollar in euros"
      - "EUR/TRY on 2024-12-31"        / "31 aralık'ta euro kuru"
      - User wants the rate itself, no amount conversion

    When NOT to use:
      - User asks "convert 100 USD to EUR" - use `convert` (it returns rate + total)
      - Crypto (BTC, ETH) - this tool covers ISO 4217 fiat only
      - Stock prices, commodity prices, NAV - out of scope

    Args:
        base: ISO 4217 base code (e.g., USD).
        quote: ISO 4217 quote code (e.g., EUR).
        on: Optional YYYY-MM-DD. Empty returns latest.
        language: en/tr.
    """
    return core_rate(base, quote, on=on or None, language=language).model_dump(mode="json")


@mcp.tool()
def convert(
    amount: float, base: str, quote: str, on: str = "", language: str = "en"
) -> dict:
    """Convert an amount between two currencies.

    When to use:
      - "100 USD kaç EUR"              / "convert 100 USD to EUR"
      - "50 sterlin kaç lira"          / "what's 50 GBP in TRY"
      - "1500 TRY in dollars yesterday" - pass `on` for the historical rate

    When NOT to use:
      - User just asks the rate without an amount - use `rate`
      - Multi-currency snapshot - use `snapshot`
      - Crypto - not supported

    Args:
        amount: Non-negative finite number.
        base, quote, on, language: see `rate`.
    """
    return core_convert(
        amount, base, quote, on=on or None, language=language
    ).model_dump(mode="json")


@mcp.tool()
def snapshot(base: str, symbols: list[str] | None = None, language: str = "en") -> dict:
    """Latest rates from one base to many quote currencies in a single call.

    When to use:
      - "USD'nin tüm büyük paritelere kuru"  / "USD against major currencies"
      - "show me TRY against the world today" / "TRY karşısı tüm kurlar"
      - User wants a table view, not a single pair

    When NOT to use:
      - Single pair only - `rate` is cheaper and more direct
      - Historical comparison - use `timeseries`

    Args:
        base: ISO 4217 base code.
        symbols: List of quote codes. None uses a sensible global default
            (USD, EUR, GBP, JPY, CHF, CAD, AUD, CNY, INR, BRL, ...).
        language: en/tr.
    """
    return core_snapshot(base, symbols=symbols, language=language).model_dump(mode="json")


@mcp.tool()
def timeseries(
    base: str, quote: str, start: str, end: str, language: str = "en"
) -> dict:
    """Daily rates for a pair over a date range (capped at 366 days).

    When to use:
      - "EUR/USD past 30 days"         / "son 30 gün EUR/USD"
      - "TRY trend over last quarter"  / "son çeyrekte TRY/USD"
      - User wants a series, not a single point

    When NOT to use:
      - Single date - use `rate` with `on=YYYY-MM-DD`
      - Range over a year - the tool caps at 366 days; ask the user to narrow
      - Multi-currency view - use `snapshot`

    Args:
        base, quote: ISO 4217 codes.
        start, end: Inclusive YYYY-MM-DD dates.
        language: en/tr.
    """
    return core_timeseries(base, quote, start, end, language=language).model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
