"""OWUI Tools wrapper for tripweather."""

from pydantic import BaseModel, Field

from tripweather.core import forecast, forecast_by_query, geocode, to_markdown  # noqa: F401


class Tools:
    class Valves(BaseModel):
        DEFAULT_LANGUAGE: str = Field(
            default="en",
            description="Output language. 'en' or 'tr'.",
        )
        DEFAULT_UNITS: str = Field(
            default="metric",
            description="'metric' (°C, km/h, mm) or 'imperial' (°F, mph, in).",
        )
        DEFAULT_DAYS: int = Field(default=3, description="Default forecast horizon (1-16).")

    def __init__(self):
        self.valves = self.Valves()
        self.citation = False

    def _lang(self, language: str | None) -> str:
        return (language or self.valves.DEFAULT_LANGUAGE or "en").strip()

    def geocode(
        self,
        query: str,
        country: str | None = None,
        max_results: int = 5,
        language: str | None = None,
    ) -> str:
        """Look up geographic candidates."""
        lang = self._lang(language)
        return to_markdown(
            geocode(query, country=country, max_results=max_results, language=lang),
            lang=lang,
        )

    def forecast(
        self,
        latitude: float,
        longitude: float,
        start_date: str | None = None,
        days: int | None = None,
        units: str | None = None,
        language: str | None = None,
    ) -> str:
        """Forecast for explicit coordinates."""
        lang = self._lang(language)
        return to_markdown(
            forecast(
                latitude,
                longitude,
                start_date=start_date,
                days=days if days is not None else self.valves.DEFAULT_DAYS,
                units=(units or self.valves.DEFAULT_UNITS),
                language=lang,
            ),
            lang=lang,
        )

    def forecast_by_query(
        self,
        query: str,
        country: str | None = None,
        start_date: str | None = None,
        days: int | None = None,
        units: str | None = None,
        language: str | None = None,
    ) -> str:
        """Geocode → forecast in one call. Sets a disambiguation warning on tie."""
        lang = self._lang(language)
        return to_markdown(
            forecast_by_query(
                query,
                country=country,
                start_date=start_date,
                days=days if days is not None else self.valves.DEFAULT_DAYS,
                units=(units or self.valves.DEFAULT_UNITS),
                language=lang,
            ),
            lang=lang,
        )
