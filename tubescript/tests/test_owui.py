"""Smoke tests for the generated tubescript owui.py bundle."""

import importlib.util
import sys
from pathlib import Path

import pytest

OWUI_BUNDLE = Path(__file__).resolve().parent.parent / "owui.py"


@pytest.fixture(scope="module")
def bundled_module():
    spec = importlib.util.spec_from_file_location("tubescript_owui_bundle", OWUI_BUNDLE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["tubescript_owui_bundle"] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop("tubescript_owui_bundle", None)
        raise
    yield module
    sys.modules.pop("tubescript_owui_bundle", None)


def test_tools_class_present(bundled_module):
    tools = bundled_module.Tools()
    assert callable(tools.list_transcripts)
    assert callable(tools.get_transcript)


def test_invalid_id_renders_error(bundled_module):
    tools = bundled_module.Tools()
    out = tools.get_transcript("not-a-url-or-id")
    assert "Error" in out and "INVALID_INPUT" in out
