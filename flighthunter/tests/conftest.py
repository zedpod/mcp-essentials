"""flighthunter pytest fixtures."""

import os

import pytest


@pytest.fixture(autouse=True)
def _ensure_test_key(monkeypatch, request):
    """Fake SerpAPI key for unit tests.

    Skipped for tests marked `live` so the real env-supplied key passes through.
    """
    if "live" in request.keywords:
        return
    monkeypatch.setenv("FLIGHTHUNTER_SERPAPI_KEY", "test-key-do-not-use")


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_LIVE") == "1":
        return
    skip = pytest.mark.skip(reason="set RUN_LIVE=1 to run live-API tests")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)


# A trimmed SerpAPI Google Flights response fixture.
SAMPLE_RESPONSE = {
    "search_metadata": {
        "google_flights_url": "https://www.google.com/flights?source=flightsearch",
        "credits_left": 175,
    },
    "best_flights": [
        {
            "price": 187,
            "price_currency": "USD",
            "total_duration": 215,
            "type": "best",
            "booking_token": "tok-1",
            "flights": [
                {
                    "airline": "Turkish Airlines",
                    "flight_number": "TK1981",
                    "duration": 215,
                    "travel_class": "Economy",
                    "airplane": "Boeing 737-800",
                    "departure_airport": {"id": "IST", "time": "2025-09-01 09:00"},
                    "arrival_airport": {"id": "LHR", "time": "2025-09-01 11:35"},
                }
            ],
            "layovers": [],
        }
    ],
    "other_flights": [
        {
            "price": 245,
            "price_currency": "USD",
            "total_duration": 380,
            "type": "other",
            "flights": [
                {
                    "airline": "Pegasus",
                    "flight_number": "PC1185",
                    "duration": 175,
                    "departure_airport": {"id": "SAW", "time": "2025-09-01 06:00"},
                    "arrival_airport": {"id": "AMS", "time": "2025-09-01 08:30"},
                },
                {
                    "airline": "EasyJet",
                    "flight_number": "U21234",
                    "duration": 90,
                    "departure_airport": {"id": "AMS", "time": "2025-09-01 10:00"},
                    "arrival_airport": {"id": "LHR", "time": "2025-09-01 10:30"},
                },
            ],
            "layovers": [{"id": "AMS", "duration": 90}],
        }
    ],
    "price_insights": {
        "lowest_price": 187,
        "typical_price_range": [200, 320],
        "price_level": "low",
    },
}


SERPAPI_ERROR = {"error": "Your account has run out of searches."}
