"""flighthunter MCP server. Run: python -m flighthunter"""

from mcp.server.fastmcp import FastMCP

from flighthunter.core import search_flights as core_search

mcp = FastMCP("orzed-flighthunter")


@mcp.tool()
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    cabin_class: str = "economy",
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    currency: str = "USD",
    language: str = "en",
) -> dict:
    """Search Google Flights via SerpAPI.

    When to use:
      - "find flights IST to LHR Sep 1"   / "İstanbul Londra uçuş bul 1 eylül"
      - "compare ticket prices X -> Y"
      - "round trip JFK to NRT next month"

    When NOT to use:
      - User gave only city names without airports - ask them for IATA codes
        (or specific airport names) before calling
      - Train / bus / ferry / car-rental searches - flights only
      - Hotels or vacation packages - not supported
      - Generic travel advice without dates - chat answer, no tool

    Requires the `FLIGHTHUNTER_SERPAPI_KEY` env var. Each call costs 1 SerpAPI credit.

    Args:
        origin: 3-letter IATA code (e.g. IST, LHR, JFK).
        destination: 3-letter IATA code.
        departure_date: YYYY-MM-DD.
        return_date: Optional YYYY-MM-DD; omit for one-way.
        cabin_class: economy / premium_economy / business / first.
        adults / children / infants: total ≤ 9; children < adults.
        currency: ISO 4217, default USD.
        language: en/tr.

    Returns:
        Result envelope; `data.search_url` deep-links the same query on Google Flights.
    """
    return core_search(
        origin,
        destination,
        departure_date,
        return_date=return_date,
        cabin_class=cabin_class,
        adults=adults,
        children=children,
        infants=infants,
        currency=currency,
        language=language,
    ).model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
