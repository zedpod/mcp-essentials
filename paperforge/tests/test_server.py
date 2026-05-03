"""paperforge server smoke."""

import json

import pytest


@pytest.fixture
def mcp_server():
    from paperforge.server import mcp
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
    assert {t.name for t in tools} == {"create_document"}


async def test_invalid_input_via_mcp(mcp_server, tmp_output):
    result = await mcp_server.call_tool(
        "create_document",
        {"title": "", "summary": "x", "sections": [{"heading": "h"}]},
    )
    p = _payload(result)
    assert p["ok"] is False
    assert p["error"]["code"] == "INVALID_INPUT"


async def test_happy_path_via_mcp(mcp_server, tmp_output, sample_payload):
    args = dict(sample_payload)
    args["format"] = "md"
    result = await mcp_server.call_tool("create_document", args)
    p = _payload(result)
    assert p["ok"] is True
    assert p["data"]["file_path"].endswith(".md")
    assert p["data"]["sections_count"] == 2
