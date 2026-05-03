"""Smoke tests for the generated pagesignal owui.py bundle."""

import importlib.util
import sys
from pathlib import Path

import pytest
import respx
from httpx import Response

from pagesignal.tests.conftest import SAMPLE_HTML

OWUI_BUNDLE = Path(__file__).resolve().parent.parent / "owui.py"


@pytest.fixture(scope="module")
def bundled_module():
    spec = importlib.util.spec_from_file_location("pagesignal_owui_bundle", OWUI_BUNDLE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["pagesignal_owui_bundle"] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop("pagesignal_owui_bundle", None)
        raise
    yield module
    sys.modules.pop("pagesignal_owui_bundle", None)


def test_tools_class_present(bundled_module):
    tools = bundled_module.Tools()
    assert callable(tools.audit_page)


@respx.mock
def test_audit_page_renders_markdown(bundled_module):
    respx.get("https://example.com/hosting").mock(
        return_value=Response(200, text=SAMPLE_HTML, headers={"content-type": "text/html"})
    )
    tools = bundled_module.Tools()
    out = tools.audit_page("https://example.com/hosting")
    assert "PageSignal" in out
    assert "Headings" in out


def test_invalid_url_renders_error(bundled_module):
    tools = bundled_module.Tools()
    out = tools.audit_page("not-a-url")
    assert "Error" in out and "INVALID_INPUT" in out
