"""askuser owui.py smoke."""

import importlib.util
import sys
from pathlib import Path

import pytest

OWUI_BUNDLE = Path(__file__).resolve().parent.parent / "owui.py"


@pytest.fixture(scope="module")
def bundled_module():
    spec = importlib.util.spec_from_file_location("askuser_owui_bundle", OWUI_BUNDLE)
    module = importlib.util.module_from_spec(spec)
    sys.modules["askuser_owui_bundle"] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop("askuser_owui_bundle", None)
        raise
    yield module
    sys.modules.pop("askuser_owui_bundle", None)


def test_tools_class_present(bundled_module):
    tools = bundled_module.Tools()
    assert callable(tools.ask_user_question)


async def test_invalid_question_renders_error(bundled_module):
    tools = bundled_module.Tools()
    out = await tools.ask_user_question(prompt="", options=[], __event_call__=lambda *a, **kw: {})
    assert "Error" in out and "INVALID_INPUT" in out


async def test_no_event_call_returns_unsupported(bundled_module):
    tools = bundled_module.Tools()
    out = await tools.ask_user_question(prompt="hi", options=[{"label": "x"}])
    assert "UNSUPPORTED" in out


async def test_event_call_returns_select(bundled_module):
    tools = bundled_module.Tools()

    async def fake_event_call(_payload):
        # OWUI returns the resolved Promise value as a JSON string by convention.
        return '{"type":"select","indices":[1],"values":["Beta"],"elapsed_ms":150}'

    out = await tools.ask_user_question(
        prompt="Pick one",
        options=[{"label": "Alpha"}, {"label": "Beta"}],
        mode="single",
        __event_call__=fake_event_call,
    )
    assert "Beta" in out
