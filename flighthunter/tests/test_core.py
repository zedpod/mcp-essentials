"""flighthunter unit tests."""

import respx
from httpx import Response

from flighthunter.core import search_flights
from flighthunter.tests.conftest import SAMPLE_RESPONSE, SERPAPI_ERROR

SERPAPI = "https://serpapi.com/search"


class TestValidation:
    def test_invalid_iata_origin(self):
        r = search_flights("XX", "LHR", "2025-09-01")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_invalid_iata_destination(self):
        r = search_flights("IST", "12345", "2025-09-01")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_same_endpoints_rejected(self):
        r = search_flights("IST", "IST", "2025-09-01")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_invalid_date(self):
        r = search_flights("IST", "LHR", "tomorrow")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_return_before_departure(self):
        r = search_flights("IST", "LHR", "2025-09-10", return_date="2025-09-01")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_invalid_cabin(self):
        r = search_flights("IST", "LHR", "2025-09-01", cabin_class="luxury")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_too_many_passengers(self):
        r = search_flights("IST", "LHR", "2025-09-01", adults=5, children=5)
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_children_more_than_adults(self):
        r = search_flights("IST", "LHR", "2025-09-01", adults=1, children=3)
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_missing_api_key(self, monkeypatch):
        monkeypatch.delenv("FLIGHTHUNTER_SERPAPI_KEY", raising=False)
        monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
        r = search_flights("IST", "LHR", "2025-09-01")
        assert not r.ok
        assert r.error and r.error.code == "MISSING_API_KEY"
        assert r.error.hint  # tells the caller how to recover


class TestSearch:
    @respx.mock
    def test_happy_path(self):
        respx.get(SERPAPI).mock(return_value=Response(200, json=SAMPLE_RESPONSE))
        r = search_flights("IST", "LHR", "2025-09-01")
        assert r.ok
        assert r.data is not None
        assert r.data.origin == "IST"
        assert r.data.destination == "LHR"
        assert len(r.data.options) == 2
        # Best flights come first.
        assert r.data.options[0].type == "best"
        assert r.data.options[0].price == 187
        # Multi-leg option is parsed correctly.
        multi = r.data.options[1]
        assert multi.stops == 1
        assert multi.layover_airports == ["AMS"]
        assert len(multi.legs) == 2
        # Price insight surfaced.
        assert r.data.price_insight and r.data.price_insight.lowest == 187
        # Search URL deep-link present.
        assert r.data.search_url and "google.com/flights" in r.data.search_url

    @respx.mock
    def test_one_way(self):
        respx.get(SERPAPI).mock(return_value=Response(200, json=SAMPLE_RESPONSE))
        r = search_flights("IST", "LHR", "2025-09-01")  # no return date
        assert r.ok
        assert r.data and r.data.trip_type == "one_way"
        assert r.data.return_date is None

    @respx.mock
    def test_round_trip(self):
        respx.get(SERPAPI).mock(return_value=Response(200, json=SAMPLE_RESPONSE))
        r = search_flights("IST", "LHR", "2025-09-01", return_date="2025-09-08")
        assert r.ok
        assert r.data and r.data.trip_type == "round_trip"
        assert r.data.return_date is not None

    @respx.mock
    def test_serpapi_error_surfaces_upstream(self):
        respx.get(SERPAPI).mock(return_value=Response(200, json=SERPAPI_ERROR))
        r = search_flights("IST", "LHR", "2025-09-01")
        assert not r.ok
        assert r.error and r.error.code == "UPSTREAM_ERROR"
        assert "serpapi_error" in r.meta

    @respx.mock
    def test_429_returns_rate_limited(self):
        respx.get(SERPAPI).mock(return_value=Response(429, text="rate-limited"))
        r = search_flights("IST", "LHR", "2025-09-01")
        assert not r.ok
        assert r.error and r.error.code == "RATE_LIMITED"


class TestI18n:
    def test_tr_message(self, monkeypatch):
        monkeypatch.delenv("FLIGHTHUNTER_SERPAPI_KEY", raising=False)
        monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
        r = search_flights("IST", "LHR", "2025-09-01", language="tr")
        assert r.error and "FLIGHTHUNTER_SERPAPI_KEY" in r.error.message_tr
