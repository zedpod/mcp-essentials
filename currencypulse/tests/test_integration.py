"""Live currencypulse tests - gated by RUN_LIVE=1."""

import pytest

from currencypulse.core import rate

pytestmark = pytest.mark.live


def test_live_usd_eur_rate():
    r = rate("USD", "EUR")
    assert r.ok, r.error
    assert r.data and r.data.value > 0
