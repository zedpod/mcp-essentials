"""askuser server smoke. Validates that the MCP tool wires through.

We don't actually open a browser in CI - we just exercise the validation path.
"""

import json

import pytest


@pytest.fixture
def mcp_server():
    from askuser.server import mcp
    return mcp


def _payload(result):
    if isinstance(result, tuple) and len(result) == 2:
        c, s = result
        if s is not None:
            return s
        result = c
    if isinstance(result, list) and result:
        text = getattr(result[0], "text", None) or str(result[0])
        return json.loads(text)
    raise AssertionError(f"unexpected: {type(result).__name__}")


async def test_tool_registered(mcp_server):
    tools = await mcp_server.list_tools()
    assert {t.name for t in tools} == {"ask_user_question"}


async def test_invalid_input_via_mcp(mcp_server):
    result = await mcp_server.call_tool(
        "ask_user_question",
        {"prompt": "", "options": []},
    )
    p = _payload(result)
    assert p["ok"] is False
    assert p["error"]["code"] == "INVALID_INPUT"


async def test_no_display_returns_unsupported(mcp_server, monkeypatch):
    # Force the no-display detector to True regardless of environment.
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.setattr("os.name", "posix", raising=False)
    result = await mcp_server.call_tool(
        "ask_user_question",
        {"prompt": "Pick", "options": [{"label": "x"}], "mode": "single"},
    )
    p = _payload(result)
    assert p["ok"] is False
    assert p["error"]["code"] in ("UNSUPPORTED", "INVALID_INPUT")
