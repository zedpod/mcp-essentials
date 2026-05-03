"""tripweather owui.py smoke."""

import importlib.util
import sys
from pathlib import Path

import pytest

OWUI_BUNDLE = Path(__file__).resolve().parent.parent / "owui.py"


@pytest.fixture(scope="module")
def bundled_module():
    spec = importlib.util.spec_from_file_location("tripweather_owui_bundle", OWUI_BUNDLE)
    module = importlib.util.module_from_spec(spec)
    sys.modules["tripweather_owui_bundle"] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop("tripweather_owui_bundle", None)
        raise
    yield module
    sys.modules.pop("tripweather_owui_bundle", None)


def test_tools_present(bundled_module):
    tools = bundled_module.Tools()
    for name in ("geocode", "forecast", "forecast_by_query"):
        assert callable(getattr(tools, name))


def test_invalid_coords_renders_error(bundled_module):
    tools = bundled_module.Tools()
    out = tools.forecast(91.0, 0.0)
    assert "Error" in out and "INVALID_INPUT" in out
