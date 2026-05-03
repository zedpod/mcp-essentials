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
        """Look up geographic candidates for a place name.

        Use when: "where is Springfield" / "Cambridge'in koordinatları". Skip
        if the user wants weather (forecast_by_query) or already has lat/lon
        (forecast). Reverse geocoding (lat/lon -> name) is not supported.
        """
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
        """Daily forecast for explicit lat/lon (Open-Meteo).

        Use when: user already has coordinates, or you geocoded first and now
        have a chosen candidate. Skip if the user gave a place name (use
        forecast_by_query instead). Past dates not supported (forecast only).
        """
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
        """Geocode + forecast in one call. The default for plain-language requests.

        Use when: "İstanbul hava durumu" / "weather in Tokyo next 5 days" /
        "yarın Paris'te yağmur var mı". Skip if the user gave lat/lon (use
        forecast). Climate / historical weather and past dates are out of scope.
        Sets meta.disambiguation_warning=True when two equally-scored candidates
        exist so the LLM can ask which city.
        """
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
