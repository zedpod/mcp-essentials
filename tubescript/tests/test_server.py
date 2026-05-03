"""tubescript server smoke tests."""

import json

import pytest


@pytest.fixture
def mcp_server():
    from tubescript.server import mcp
    return mcp


def _payload(result):
    if isinstance(result, tuple) and len(result) == 2:
        content, structured = result
        if structured is not None:
            return structured
        result = content
    if isinstance(result, list) and result:
        text = getattr(result[0], "text", None) or str(result[0])
        return json.loads(text)
    raise AssertionError(f"unexpected: {type(result).__name__}")


async def test_tools_registered(mcp_server):
    tools = await mcp_server.list_tools()
    names = {t.name for t in tools}
    assert names == {"list_transcripts", "get_transcript"}


async def test_invalid_input_via_mcp(mcp_server):
    result = await mcp_server.call_tool("get_transcript", {"url_or_id": "not-a-url"})
    p = _payload(result)
    assert p["ok"] is False
    assert p["error"]["code"] == "INVALID_INPUT"
