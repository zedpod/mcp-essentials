"""Smoke tests for the FastMCP server. Uses an in-process client (no subprocess)."""

import json

import pytest


@pytest.fixture
def mcp_server():
    from qrforge.server import mcp

    return mcp


def _payload_from_call_result(result) -> dict:
    """Tolerate both old (list[TextContent]) and new ((content, structured)) APIs."""
    if isinstance(result, tuple) and len(result) == 2:
        content, structured = result
        if structured is not None:
            return structured
        result = content
    if isinstance(result, list) and result:
        first = result[0]
        text = getattr(first, "text", None) or str(first)
        return json.loads(text)
    raise AssertionError(f"unexpected call_tool return shape: {type(result).__name__}")


async def test_server_lists_expected_tools(mcp_server) -> None:
    tools = await mcp_server.list_tools()
    names = {t.name for t in tools}
    assert names == {"qr_text", "qr_url", "qr_wifi", "qr_vcard"}


async def test_server_descriptions_present(mcp_server) -> None:
    tools = await mcp_server.list_tools()
    for tool in tools:
        assert tool.description, f"{tool.name} has no description (LLM needs it)"
        assert tool.inputSchema, f"{tool.name} has no input schema"


async def test_qr_text_via_call_tool(mcp_server) -> None:
    result = await mcp_server.call_tool("qr_text", {"text": "hello mcp", "size": 128})
    payload = _payload_from_call_result(result)
    assert payload["ok"] is True
    assert payload["data"]["source"] == "local"


async def test_qr_url_rejects_schemeless(mcp_server) -> None:
    result = await mcp_server.call_tool("qr_url", {"url": "orzed.com"})
    payload = _payload_from_call_result(result)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "INVALID_INPUT"


async def test_qr_wifi_returns_local_payload(mcp_server) -> None:
    result = await mcp_server.call_tool(
        "qr_wifi",
        {"ssid": "OrzedGuest", "password": "welcome2025", "encryption": "WPA"},
    )
    payload = _payload_from_call_result(result)
    assert payload["ok"] is True
    assert payload["data"]["payload_kind"] == "wifi"
    assert "WIFI:T:WPA" in payload["data"]["payload_preview"]


async def test_input_schema_documents_language(mcp_server) -> None:
    tools = await mcp_server.list_tools()
    qr_text_tool = next(t for t in tools if t.name == "qr_text")
    schema = qr_text_tool.inputSchema
    properties = schema.get("properties", {})
    assert "language" in properties
    assert "ec_level" in properties
