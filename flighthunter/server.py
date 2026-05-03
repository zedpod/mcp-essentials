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

    Args:
        origin: 3-letter IATA airport code (e.g. IST, LHR, JFK).
        destination: 3-letter IATA airport code.
        departure_date: YYYY-MM-DD.
        return_date: Optional YYYY-MM-DD. Empty/None for one-way.
        cabin_class: economy / premium_economy / business / first.
        adults / children / infants: passenger counts; total ≤ 9; children < adults.
        currency: ISO 4217 currency code for prices (default USD).
        language: en/tr.

    Returns:
        Result envelope. `data` is a `FlightSearch` with options sorted by price.
        `data.search_url` opens the same query on Google Flights.

    Requires `FLIGHTHUNTER_SERPAPI_KEY` env var.
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
