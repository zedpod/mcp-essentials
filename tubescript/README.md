# tubescript

> YouTube transcripts as text, SRT, VTT, or JSON. Auto-detects video ID from any URL variant.

Part of [mcp-essentials](../README.md).

## Tools

- `list_transcripts(url_or_id, language)` → all available tracks (auto + manual + translatable flags).
- `get_transcript(url_or_id, prefer_lang, translate_to, format, max_chars, language)` → the transcript itself.

`format`: `text` / `srt` / `vtt` / `json`. `max_chars` truncates at the nearest word boundary.

## Install — Open WebUI

Paste [`./owui.py`](./owui.py) into Admin → Tools.

## Install — Claude Desktop / Cursor / Cline

```json
{
  "mcpServers": {
    "tubescript": {
      "command": "python",
      "args": ["-m", "tubescript"],
      "cwd": "/absolute/path/to/mcp-essentials",
      "env": { "PYTHONPATH": "/absolute/path/to/mcp-essentials" }
    }
  }
}
```

## Errors

| Code | When |
|---|---|
| `INVALID_INPUT` | Empty or non-extractable URL/ID, unknown format |
| `NOT_FOUND` | None of `prefer_lang` are available |
| `UNSUPPORTED` | Transcripts disabled, age-gated, region-blocked, video unavailable |
| `UPSTREAM_ERROR` | YouTube returned an unexpected error |

## License

Apache 2.0 — see [../LICENSE](../LICENSE). Note: scraping YouTube transcripts is governed by YouTube ToS; use at your own risk.

---

*Part of mcp-essentials by [Orzed](https://orzed.com).*
