"""tripweather pytest fixtures."""

import os

import pytest


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_LIVE") == "1":
        return
    skip = pytest.mark.skip(reason="set RUN_LIVE=1 to run live-API tests")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)


GEOCODE_RESPONSE = {
    "results": [
        {
            "name": "Istanbul",
            "country_code": "TR",
            "country": "Turkey",
            "admin1": "Istanbul",
            "latitude": 41.0138,
            "longitude": 28.9497,
            "timezone": "Europe/Istanbul",
            "population": 14804116,
            "elevation": 39.0,
            "ranking_score": 90.0,
        },
        {
            "name": "Istanbul",
            "country_code": "US",
            "country": "United States",
            "admin1": "Texas",
            "latitude": 33.0,
            "longitude": -97.0,
            "timezone": "America/Chicago",
            "population": 50,
            "elevation": 200,
            "ranking_score": 30.0,
        },
    ],
    "generationtime_ms": 0.5,
}

FORECAST_RESPONSE = {
    "latitude": 41.0138,
    "longitude": 28.9497,
    "timezone": "Europe/Istanbul",
    "daily": {
        "time": ["2025-09-01", "2025-09-02", "2025-09-03"],
        "weather_code": [2, 61, 0],
        "temperature_2m_max": [28.0, 24.5, 27.0],
        "temperature_2m_min": [21.0, 19.0, 20.0],
        "precipitation_sum": [0.0, 5.5, 0.0],
        "precipitation_probability_max": [10, 80, 0],
        "wind_speed_10m_max": [14.0, 22.0, 12.0],
        "uv_index_max": [7.0, 5.0, 7.5],
        "sunrise": ["2025-09-01T06:30", "2025-09-02T06:31", "2025-09-03T06:32"],
        "sunset": ["2025-09-01T19:31", "2025-09-02T19:29", "2025-09-03T19:28"],
    },
}

GEOCODE_EMPTY = {"generationtime_ms": 0.5}

GEOCODE_AMBIGUOUS = {
    "results": [
        {"name": "Springfield", "country_code": "US", "country": "United States",
         "latitude": 42.1, "longitude": -72.6, "ranking_score": 80.0,
         "admin1": "Massachusetts"},
        {"name": "Springfield", "country_code": "US", "country": "United States",
         "latitude": 39.8, "longitude": -89.6, "ranking_score": 80.0,
         "admin1": "Illinois"},
    ]
}
