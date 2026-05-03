"""signalbrief live tests."""

import pytest

from signalbrief.core import list_sources

pytestmark = pytest.mark.live


def test_live_list_sources():
    r = list_sources()
    assert r.ok
    assert r.data and r.data.sources
