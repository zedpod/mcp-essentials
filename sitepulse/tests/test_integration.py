"""sitepulse live tests."""

import pytest

from sitepulse.core import inspect

pytestmark = pytest.mark.live


def test_live_orzed_dot_com():
    r = inspect("orzed.com", checks=["dns"])
    assert r.ok
    assert r.data and r.data.dns is not None
