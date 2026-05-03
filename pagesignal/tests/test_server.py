"""In-process FastMCP smoke tests for pagesignal.server."""

import json

import pytest
import respx
from httpx import Response

from pagesignal.tests.conftest import SAMPLE_HTML


@pytest.fixture
def mcp_server():
    from pagesignal.server import mcp

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


async def test_tool_registered(mcp_server):
    tools = await mcp_server.list_tools()
    assert {t.name for t in tools} == {"audit_page"}


@respx.mock
async def test_audit_page_via_mcp(mcp_server):
    respx.get("https://example.com/hosting").mock(
        return_value=Response(200, text=SAMPLE_HTML, headers={"content-type": "text/html"})
    )
    result = await mcp_server.call_tool("audit_page", {"url": "https://example.com/hosting"})
    p = _payload(result)
    assert p["ok"] is True
    assert p["data"]["meta_tags"]["title"]
    assert p["data"]["geo_signals"]["has_faq_schema"] is True


async def test_invalid_url_via_mcp(mcp_server):
    result = await mcp_server.call_tool("audit_page", {"url": "not-a-url"})
    p = _payload(result)
    assert p["ok"] is False
    assert p["error"]["code"] == "INVALID_INPUT"
