"""flighthunter live tests — RUN_LIVE=1.

Be deliberate: each call burns one SerpAPI search credit.
"""

import os

import pytest

from flighthunter.core import search_flights

pytestmark = pytest.mark.live


def test_live_basic_round_trip():
    """Single live call. SerpAPI credits are paid; do not multiply this."""
    if not os.getenv("FLIGHTHUNTER_SERPAPI_KEY"):
        pytest.skip("FLIGHTHUNTER_SERPAPI_KEY not set")
    r = search_flights(
        "IST",
        "LHR",
        "2026-09-01",
        return_date="2026-09-08",
        adults=1,
        currency="USD",
    )
    # Either we got results or SerpAPI returned a credible error — both shapes are valid.
    assert r.ok or (r.error and r.error.code in ("UPSTREAM_ERROR", "RATE_LIMITED"))
    if r.ok:
        assert r.data and r.data.options
