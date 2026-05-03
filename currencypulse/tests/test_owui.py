"""Smoke tests for the generated OWUI bundle."""

import importlib.util
import sys
from pathlib import Path

import pytest
import respx
from httpx import Response

OWUI_BUNDLE = Path(__file__).resolve().parent.parent / "owui.py"


@pytest.fixture(scope="module")
def bundled_module():
    spec = importlib.util.spec_from_file_location("currencypulse_owui_bundle", OWUI_BUNDLE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["currencypulse_owui_bundle"] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop("currencypulse_owui_bundle", None)
        raise
    yield module
    sys.modules.pop("currencypulse_owui_bundle", None)


def test_tools_class_exposes_expected_methods(bundled_module):
    tools = bundled_module.Tools()
    for name in ("rate", "convert", "snapshot", "timeseries"):
        assert callable(getattr(tools, name))


@respx.mock
def test_rate_returns_markdown(bundled_module):
    respx.get("https://api.frankfurter.dev/v1/currencies").mock(
        return_value=Response(200, json={"USD": "x", "EUR": "y"})
    )
    respx.get("https://api.frankfurter.dev/v1/latest").mock(
        return_value=Response(200, json={"date": "2025-05-02", "rates": {"EUR": 0.92}})
    )
    tools = bundled_module.Tools()
    out = tools.rate("USD", "EUR")
    assert "Rate" in out
    assert "0.9200" in out or "0.92" in out


def test_invalid_currency_renders_error(bundled_module):
    tools = bundled_module.Tools()
    out = tools.rate("USD", "ZZZ")
    assert "Error" in out
    assert "INVALID_INPUT" in out


def test_default_language_valve_honored(bundled_module):
    tools = bundled_module.Tools()
    tools.valves.DEFAULT_LANGUAGE = "tr"
    out = tools.rate("USD", "ZZZ")
    assert "Bilinmeyen" in out
