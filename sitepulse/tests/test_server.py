"""sitepulse server smoke."""

import json

import pytest


@pytest.fixture
def mcp_server():
    from sitepulse.server import mcp
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


async def test_inspect_registered(mcp_server):
    tools = await mcp_server.list_tools()
    assert {t.name for t in tools} == {"inspect"}


async def test_invalid_input_via_mcp(mcp_server):
    result = await mcp_server.call_tool("inspect", {"domain": ""})
    p = _payload(result)
    assert p["ok"] is False
    assert p["error"]["code"] == "INVALID_INPUT"
