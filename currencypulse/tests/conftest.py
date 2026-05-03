"""Pytest fixtures for currencypulse."""

import os

import pytest


@pytest.fixture(autouse=True)
def _clear_cache():
    from currencypulse.core import fx as fx_module

    fx_module._cache.clear()
    yield
    fx_module._cache.clear()


@pytest.fixture(autouse=True)
def _clear_oxr_env(monkeypatch):
    """Drop OXR env so unit tests don't accidentally hit the real OXR provider."""
    monkeypatch.delenv("CURRENCYPULSE_OXR_APP_ID", raising=False)
    # Reset the Frankfurter currency set cache between tests.
    from currencypulse.core import providers as providers_module

    providers_module._FRANKFURTER_SUPPORTED = None
    yield


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_LIVE") == "1":
        return
    skip_marker = pytest.mark.skip(reason="set RUN_LIVE=1 to run live-API tests")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_marker)
