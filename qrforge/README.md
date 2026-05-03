# qrforge

> QR codes for arbitrary text, URLs, Wi-Fi credentials, and vCards. Local rendering by default.

Part of [mcp-essentials](../README.md). Runs as both an Open WebUI Tool and a real MCP server (Claude Desktop, Cursor, Cline, Continue).

## What it does

Four MCP tools, each returning a `Result[QrImage]` envelope:

| Tool | Encodes | Remote fallback allowed? |
|---|---|---|
| `qr_text` | Any text or arbitrary payload | Optional (opt-in via valve / arg) |
| `qr_url` | An HTTP(S) URL (rejects schemeless) | Optional |
| `qr_wifi` | Wi-Fi credentials (`WIFI:` payload) | **No** - credentials never leave the host |
| `qr_vcard` | Contact details (vCard 3.0) | **No** - contact data never leaves the host |

The `data` field of a successful result carries either `data_b64` (base64-encoded PNG bytes for local rendering) or `remote_url` (a hyperlink to api.qrserver.com when remote fallback is opted into). The OWUI wrapper renders the same data as inline markdown.

## Install - Open WebUI

1. Open OWUI → **Admin Panel → Tools → "+ New tool"**.
2. Copy the entire contents of [`./owui.py`](./owui.py) and paste into the editor.
3. Description field (optional override - the docstrings inside `owui.py` already carry bilingual EN/TR triggers, so plain-language calls in either language work):
   ```text
   Generate QR codes (PNG) for arbitrary text, URLs, Wi-Fi credentials, or vCard contacts.

   Use when the user asks for:
   - QR code for a text or URL
   - QR card with contact info (vCard)
   - Wi-Fi QR for guests

   Do NOT use for: scanning an existing QR (this generates only), payment QR codes, or image enhancement.
   ```
4. Click **Save**.
5. Configure Valves:
   - `DEFAULT_LANGUAGE` - `en` or `tr`
   - `DEFAULT_SIZE`, `DEFAULT_BORDER`, `DEFAULT_EC_LEVEL`
   - `USE_REMOTE_FALLBACK` - leave **off** unless you accept payloads reaching api.qrserver.com when the local `qrcode` library is unavailable

If your OWUI runtime lacks the `qrcode` library, install it:

```bash
docker exec -it open-webui pip install "qrcode[pil]"
docker restart open-webui
```

## Install - Claude Desktop / Cursor / Cline

```json
{
  "mcpServers": {
    "qrforge": {
      "command": "python",
      "args": ["-m", "qrforge"],
      "cwd": "/absolute/path/to/mcp-essentials",
      "env": { "PYTHONPATH": "/absolute/path/to/mcp-essentials" }
    }
  }
}
```

Restart your client. The four tools become available with full JSON-Schema autocomplete.

## Examples

**OWUI prompt** (after enabling the tool):

> "Generate a Wi-Fi QR for SSID `OrzedGuest`, password `welcome2025`, WPA2."

The tool replies with a markdown block including the embedded PNG.

**MCP call** (from any MCP client):

```json
{
  "name": "qr_url",
  "arguments": { "url": "https://orzed.com", "size": 256, "ec_level": "Q" }
}
```

Returns:

```json
{
  "ok": true,
  "data": {
    "format": "png",
    "source": "local",
    "data_b64": "iVBORw0KGgo...",
    "byte_length": 5821,
    "pixel_size": 256,
    "border": 4,
    "ec_level": "Q",
    "payload_kind": "url",
    "payload_preview": "https://orzed.com"
  },
  "meta": { "source": "local" }
}
```

## Parameters

All four tools accept (in addition to their type-specific arguments):

| Param | Default | Range | Notes |
|---|---|---|---|
| `size` | 512 | 64–4096 | Pixel edge length |
| `border` | 4 | 0–16 | Quiet-zone width in modules |
| `ec_level` | `M` | `L` / `M` / `Q` / `H` | Higher is more robust but denser |
| `language` | `en` | `en` / `tr` | Output messages; unknown codes fall back to `en` |

`qr_text` and `qr_url` additionally take `use_remote_fallback: bool` (MCP) or honor the `USE_REMOTE_FALLBACK` valve (OWUI).

## Errors

Errors come back as `Result(ok=False, error=ErrorInfo(...))` with `code` ∈ {`INVALID_INPUT`, `UNSUPPORTED`, `INTERNAL`}. Every error carries `message_en`, `message_tr`, and an optional `hint` describing how to recover.

| Code | When |
|---|---|
| `INVALID_INPUT` | Empty payload, unrecognized EC level, size/border out of range, malformed URL/email/phone, payload exceeds QR capacity |
| `UNSUPPORTED` | Local `qrcode` library missing AND remote fallback unavailable (always for Wi-Fi/vCard) |
| `INTERNAL` | Unexpected exception - file an issue |

## Environment variables

None - qrforge is dependency-free at runtime aside from `qrcode[pil]` (optional). No API keys, no `.env`.

## Development

```bash
pip install -r ../requirements-dev.txt
pip install -r requirements.txt
pytest qrforge/tests          # mocked unit + smoke tests
RUN_LIVE=1 pytest qrforge/tests -m live
```

The OWUI bundle (`owui/main.py`) is generated. Edit `core/` and `owui/_wrapper.py`, then regenerate:

```bash
python tools/bundle_owui.py qrforge          # write
python tools/bundle_owui.py qrforge --check  # CI: fail on drift
```

Tool-specific contributor guide: [./AGENTS.md](./AGENTS.md).

## License

Apache 2.0 - see [../LICENSE](../LICENSE).

---

*Part of mcp-essentials by [Orzed](https://orzed.com).*
