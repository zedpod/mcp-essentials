"""Live integration tests for pagesignal - gated by RUN_LIVE=1."""

import pytest

from pagesignal.core import audit_page

pytestmark = pytest.mark.live


def test_live_orzed_dot_com():
    r = audit_page("https://orzed.com")
    assert r.ok or (r.error and r.error.code in ("UPSTREAM_ERROR", "NETWORK_TIMEOUT"))
