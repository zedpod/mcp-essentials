"""OWUI Tools wrapper for flighthunter."""

import os

from pydantic import BaseModel, Field

from flighthunter.core import search_flights, to_markdown  # noqa: F401


class Tools:
    class Valves(BaseModel):
        DEFAULT_LANGUAGE: str = Field(
            default="en", description="Output language. 'en' or 'tr'."
        )
        DEFAULT_CURRENCY: str = Field(
            default="USD", description="ISO 4217 currency code for displayed prices."
        )
        SERPAPI_API_KEY: str = Field(
            default="",
            description=(
                "SerpAPI key. If blank, the tool falls back to the "
                "FLIGHTHUNTER_SERPAPI_KEY environment variable."
            ),
        )

    def __init__(self):
        self.valves = self.Valves()
        self.citation = False

    def _lang(self, language: str | None) -> str:
        return (language or self.valves.DEFAULT_LANGUAGE or "en").strip()

    def _api_key(self) -> str | None:
        return self.valves.SERPAPI_API_KEY or os.getenv("FLIGHTHUNTER_SERPAPI_KEY") or None

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: str | None = None,
        cabin_class: str = "economy",
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
        currency: str | None = None,
        language: str | None = None,
    ) -> str:
        """
        Search flights via SerpAPI Google Flights.

        :param origin: 3-letter IATA airport code.
        :param destination: 3-letter IATA airport code.
        :param departure_date: YYYY-MM-DD.
        :param return_date: Optional YYYY-MM-DD; omit for one-way.
        """
        lang = self._lang(language)
        result = search_flights(
            origin,
            destination,
            departure_date,
            return_date=return_date,
            cabin_class=cabin_class,
            adults=adults,
            children=children,
            infants=infants,
            currency=currency or self.valves.DEFAULT_CURRENCY,
            language=lang,
            api_key=self._api_key(),
        )
        return to_markdown(result, lang=lang)
