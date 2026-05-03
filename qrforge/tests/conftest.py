"""Pytest fixtures for qrforge."""

from __future__ import annotations

import os

import pytest


@pytest.fixture
def golden_dir(request) -> object:
    return request.path.parent / "golden"


@pytest.fixture
def tmp_env(monkeypatch):
    """Convenience for setting environment variables that auto-revert."""

    def _set(**kwargs: str) -> None:
        for k, v in kwargs.items():
            monkeypatch.setenv(k, v)

    return _set


def pytest_collection_modifyitems(config, items):  # noqa: D401 - pytest hook
    """Skip live tests unless RUN_LIVE=1 is set in the environment."""
    if os.getenv("RUN_LIVE") == "1":
        return
    skip_marker = pytest.mark.skip(reason="set RUN_LIVE=1 to run live-API tests")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_marker)
