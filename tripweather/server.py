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
    """Look up geographic candidates for a place name (Open-Meteo geocoding).

    When to use:
      - "where is Springfield"        / "İstanbul nerede"
      - "coordinates of Cambridge"    / "Cambridge'in koordinatları"
      - User wants to disambiguate same-name cities before forecasting

    When NOT to use:
      - User wants the weather - call `forecast_by_query` directly
      - User already has lat/lon - jump to `forecast`
      - Reverse geocoding (lat/lon -> name) - not supported

    Args:
        query: Free-form place name.
        country: Optional ISO 3166-1 alpha-2 filter (e.g. "TR", "US").
        max_results: 1-25.
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
    """Daily weather forecast for explicit lat/lon (Open-Meteo).

    When to use:
      - User already has coordinates: "weather at 41.01, 28.97"
      - You called `geocode` first and now have a chosen candidate

    When NOT to use:
      - User gave a place name - prefer `forecast_by_query` (one call)
      - Climate / historical analysis - this is short-term forecast (1-16 days)
      - Past dates - Open-Meteo's forecast endpoint is forward-looking only

    Args:
        latitude: -90 to 90.
        longitude: -180 to 180.
        start_date: Optional YYYY-MM-DD; otherwise today plus `days`.
        days: 1-16.
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
    """Convenience: geocode + forecast in one call. The default for plain-language requests.

    When to use:
      - "İstanbul hava durumu"            / "Istanbul weather"
      - "weather in Tokyo next 5 days"    / "Tokyo'da gelecek 5 gün hava nasıl"
      - "will it rain in Paris tomorrow"  / "yarın Paris'te yağmur var mı"
      - Any natural-language request that names a place

    When NOT to use:
      - User already gave lat/lon - use `forecast` directly (skips geocoding)
      - Climate trends / historical weather - this is short-term forecast only
      - Multi-city trip planning - call this once per city
      - Past dates - not supported

    Sets `meta.disambiguation_warning=True` when two candidates have nearly
    identical scores (e.g., multiple Springfields), so the LLM can ask which one.

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
