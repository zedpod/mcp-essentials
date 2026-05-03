"""tripweather MCP server. Run: python -m tripweather"""

from mcp.server.fastmcp import FastMCP

from tripweather.core import forecast as core_forecast
from tripweather.core import forecast_by_query as core_forecast_by_query
from tripweather.core import geocode as core_geocode

mcp = FastMCP("orzed-tripweather")


@mcp.tool()
def geocode(
    query: str,
    country: str | None = None,
    max_results: int = 5,
    language: str = "en",
) -> dict:
    """Look up geographic candidates for a place name.

    Args:
        query: Free-form place name.
        country: Optional ISO 3166-1 alpha-2 filter (e.g. "TR", "US").
        max_results: 1..25.
        language: en/tr.
    """
    return core_geocode(
        query, country=country, max_results=max_results, language=language
    ).model_dump(mode="json")


@mcp.tool()
def forecast(
    latitude: float,
    longitude: float,
    start_date: str | None = None,
    days: int = 3,
    units: str = "metric",
    language: str = "en",
) -> dict:
    """Daily weather forecast for explicit coordinates.

    Args:
        latitude: -90..90 decimal degrees.
        longitude: -180..180 decimal degrees.
        start_date: Optional YYYY-MM-DD; otherwise today + `days`.
        days: 1..16.
        units: "metric" (°C, km/h, mm) or "imperial" (°F, mph, in).
        language: en/tr.
    """
    return core_forecast(
        latitude, longitude,
        start_date=start_date,
        days=days,
        units=units,
        language=language,
    ).model_dump(mode="json")


@mcp.tool()
def forecast_by_query(
    query: str,
    country: str | None = None,
    start_date: str | None = None,
    days: int = 3,
    units: str = "metric",
    language: str = "en",
) -> dict:
    """Convenience: geocode → top candidate → forecast. Sets meta.disambiguation_warning when multiple equally-confident matches exist.

    Args:
        query: Free-form place name.
        country: Optional 2-letter ISO country filter.
        start_date, days, units, language: see `forecast`.
    """
    return core_forecast_by_query(
        query,
        country=country,
        start_date=start_date,
        days=days,
        units=units,
        language=language,
    ).model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
