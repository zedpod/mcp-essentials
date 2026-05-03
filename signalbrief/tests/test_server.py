"""signalbrief server smoke."""

import json

import pytest


@pytest.fixture
def mcp_server():
    from signalbrief.server import mcp
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


async def test_tools_registered(mcp_server):
    tools = await mcp_server.list_tools()
    names = {t.name for t in tools}
    assert names == {"collect", "list_sources"}


async def test_invalid_hours_via_mcp(mcp_server):
    result = await mcp_server.call_tool("collect", {"topics": ["x"], "hours": 0})
    p = _payload(result)
    assert p["ok"] is False
    assert p["error"]["code"] == "INVALID_INPUT"


async def test_list_sources_via_mcp(mcp_server):
    result = await mcp_server.call_tool("list_sources", {})
    p = _payload(result)
    assert p["ok"] is True
    assert p["data"]["sources"]
