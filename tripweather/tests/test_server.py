"""tripweather server smoke."""

import json

import pytest


@pytest.fixture
def mcp_server():
    from tripweather.server import mcp
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


async def test_three_tools_registered(mcp_server):
    tools = await mcp_server.list_tools()
    names = {t.name for t in tools}
    assert names == {"geocode", "forecast", "forecast_by_query"}


async def test_invalid_coords_via_mcp(mcp_server):
    result = await mcp_server.call_tool("forecast", {"latitude": 91, "longitude": 0})
    p = _payload(result)
    assert p["ok"] is False
    assert p["error"]["code"] == "INVALID_INPUT"
