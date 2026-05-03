"""flighthunter server smoke."""

import json

import pytest


@pytest.fixture
def mcp_server():
    from flighthunter.server import mcp
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
    assert {t.name for t in tools} == {"search_flights"}


async def test_invalid_iata_via_mcp(mcp_server):
    result = await mcp_server.call_tool(
        "search_flights",
        {"origin": "XX", "destination": "LHR", "departure_date": "2025-09-01"},
    )
    p = _payload(result)
    assert p["ok"] is False
    assert p["error"]["code"] == "INVALID_INPUT"
