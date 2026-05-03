"""In-process FastMCP smoke tests for currencypulse.server."""

import json

import pytest
import respx
from httpx import Response


@pytest.fixture
def mcp_server():
    from currencypulse.server import mcp

    return mcp


def _payload(result) -> dict:
    if isinstance(result, tuple) and len(result) == 2:
        content, structured = result
        if structured is not None:
            return structured
        result = content
    if isinstance(result, list) and result:
        text = getattr(result[0], "text", None) or str(result[0])
        return json.loads(text)
    raise AssertionError(f"unexpected: {type(result).__name__}")


async def test_lists_all_tools(mcp_server):
    tools = await mcp_server.list_tools()
    names = {t.name for t in tools}
    assert names == {"rate", "convert", "snapshot", "timeseries"}


async def test_descriptions_present(mcp_server):
    for tool in await mcp_server.list_tools():
        assert tool.description
        assert tool.inputSchema


@respx.mock
async def test_rate_call(mcp_server):
    respx.get("https://api.frankfurter.dev/v1/currencies").mock(
        return_value=Response(200, json={"USD": "x", "EUR": "y"})
    )
    respx.get("https://api.frankfurter.dev/v1/latest").mock(
        return_value=Response(200, json={"date": "2025-05-02", "rates": {"EUR": 0.92}})
    )
    result = await mcp_server.call_tool("rate", {"base": "USD", "quote": "EUR"})
    p = _payload(result)
    assert p["ok"] is True
    assert p["data"]["value"] == 0.92


async def test_invalid_currency_via_mcp(mcp_server):
    result = await mcp_server.call_tool("rate", {"base": "USD", "quote": "ZZZ"})
    p = _payload(result)
    assert p["ok"] is False
    assert p["error"]["code"] == "INVALID_INPUT"
