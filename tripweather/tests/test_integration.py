"""tripweather live tests."""

import pytest

from tripweather.core import forecast_by_query

pytestmark = pytest.mark.live


def test_live_istanbul_forecast():
    r = forecast_by_query("Istanbul", country="TR", days=2)
    assert r.ok or (r.error and r.error.code in ("NETWORK_TIMEOUT", "UPSTREAM_ERROR"))
