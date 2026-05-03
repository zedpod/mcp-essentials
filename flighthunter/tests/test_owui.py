"""flighthunter owui.py smoke."""

import importlib.util
import sys
from pathlib import Path

import pytest

OWUI_BUNDLE = Path(__file__).resolve().parent.parent / "owui.py"


@pytest.fixture(scope="module")
def bundled_module():
    spec = importlib.util.spec_from_file_location("flighthunter_owui_bundle", OWUI_BUNDLE)
    module = importlib.util.module_from_spec(spec)
    sys.modules["flighthunter_owui_bundle"] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop("flighthunter_owui_bundle", None)
        raise
    yield module
    sys.modules.pop("flighthunter_owui_bundle", None)


def test_tools_present(bundled_module):
    tools = bundled_module.Tools()
    assert callable(tools.search_flights)


def test_invalid_iata_renders_error(bundled_module):
    tools = bundled_module.Tools()
    out = tools.search_flights("XX", "LHR", "2025-09-01")
    assert "Error" in out and "INVALID_INPUT" in out
