"""tripweather unit tests."""

import respx
from httpx import Response

from tripweather.core import forecast, forecast_by_query, geocode
from tripweather.tests.conftest import (
    FORECAST_RESPONSE,
    GEOCODE_AMBIGUOUS,
    GEOCODE_EMPTY,
    GEOCODE_RESPONSE,
)

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORE_URL = "https://api.open-meteo.com/v1/forecast"


class TestGeocode:
    @respx.mock
    def test_happy_path_no_country_bias(self):
        respx.get(GEO_URL).mock(return_value=Response(200, json=GEOCODE_RESPONSE))
        r = geocode("Istanbul")
        assert r.ok
        # Order is preserved from Open-Meteo's own ranking_score; we don't add a TR bias.
        assert r.data and r.data.candidates[0].name == "Istanbul"
        assert r.data.candidates[0].country_code == "TR"
        assert len(r.data.candidates) == 2

    @respx.mock
    def test_empty_query_rejected(self):
        r = geocode("")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    @respx.mock
    def test_no_results(self):
        respx.get(GEO_URL).mock(return_value=Response(200, json=GEOCODE_EMPTY))
        r = geocode("Atlantis")
        assert not r.ok
        assert r.error and r.error.code == "NOT_FOUND"

    @respx.mock
    def test_country_filter_passes_through(self):
        respx.get(GEO_URL).mock(return_value=Response(200, json=GEOCODE_RESPONSE))
        r = geocode("Istanbul", country="TR")
        assert r.ok


class TestForecast:
    @respx.mock
    def test_happy_path(self):
        respx.get(FORE_URL).mock(return_value=Response(200, json=FORECAST_RESPONSE))
        r = forecast(41.0138, 28.9497, days=3)
        assert r.ok
        assert r.data and len(r.data.days) == 3
        assert r.data.timezone == "Europe/Istanbul"
        assert r.data.days[0].weather_label  # WMO label populated

    def test_invalid_coords_too_north(self):
        r = forecast(91.0, 0.0)
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_invalid_coords_too_west(self):
        r = forecast(0.0, -181.0)
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_invalid_days(self):
        r = forecast(41, 29, days=20)
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_invalid_units(self):
        r = forecast(41, 29, units="kelvin")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    @respx.mock
    def test_imperial_units_passed_through(self):
        called = {}

        def handler(request):
            called["params"] = dict(request.url.params)
            return Response(200, json=FORECAST_RESPONSE)

        respx.get(FORE_URL).mock(side_effect=handler)
        r = forecast(41.0, 29.0, units="imperial")
        assert r.ok
        assert r.data.units == "imperial"
        assert called["params"]["temperature_unit"] == "fahrenheit"
        assert called["params"]["wind_speed_unit"] == "mph"


class TestForecastByQuery:
    @respx.mock
    def test_happy_path(self):
        respx.get(GEO_URL).mock(return_value=Response(200, json=GEOCODE_RESPONSE))
        respx.get(FORE_URL).mock(return_value=Response(200, json=FORECAST_RESPONSE))
        r = forecast_by_query("Istanbul")
        assert r.ok
        assert r.data and r.data.place_name == "Istanbul"
        assert r.data.country_code == "TR"

    @respx.mock
    def test_disambiguation_warning_for_ties(self):
        respx.get(GEO_URL).mock(return_value=Response(200, json=GEOCODE_AMBIGUOUS))
        respx.get(FORE_URL).mock(return_value=Response(200, json=FORECAST_RESPONSE))
        r = forecast_by_query("Springfield")
        assert r.ok
        assert r.meta.get("disambiguation_warning") is True

    @respx.mock
    def test_geocode_failure_propagates(self):
        respx.get(GEO_URL).mock(return_value=Response(200, json=GEOCODE_EMPTY))
        r = forecast_by_query("Atlantis")
        assert not r.ok
        assert r.error and r.error.code == "NOT_FOUND"


class TestI18n:
    def test_tr_message(self):
        r = forecast(91.0, 0.0, language="tr")
        assert r.error and "Enlem" in r.error.message_tr
