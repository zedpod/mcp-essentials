# pagesignal

> URL → SEO + AI-answer-readiness audit, no third-party services required.

Part of [mcp-essentials](../README.md). Dual-mode: Open WebUI Tool **and** real MCP server.

## What it does

One MCP tool, `audit_page(url, target_keywords?, language)`, returning a structured `PageAudit`:

- **meta_tags** — title, description, canonical, robots, Open Graph, Twitter cards, lang, charset
- **headings** — H1/H2/H3 counts and text, skipped-level detection
- **readability** — word/sentence count, average sentence length, detected language
- **geo_signals** — JSON-LD schema types (FAQPage, HowTo, Article, Question), question-style headings (lexicons in en/tr/de/es/fr/it/pt/ar), keyword hit counts
- **performance** — bytes, response time, status, redirect count
- **issues** — prioritized list with severity (`info`/`warning`/`error`), code, and i18n messages

Uses stdlib `html.parser` (no external soup dep). Honors `noindex`. Detects JS-heavy pages heuristically.

## Install — Open WebUI

Paste [`./owui.py`](./owui.py) into Admin → Tools. Configure Valves (`DEFAULT_LANGUAGE`, `TIMEOUT_SECONDS`, `USER_AGENT`).

## Install — Claude Desktop / Cursor / Cline

```json
{
  "mcpServers": {
    "pagesignal": {
      "command": "python",
      "args": ["-m", "pagesignal"],
      "cwd": "/absolute/path/to/mcp-essentials",
      "env": { "PYTHONPATH": "/absolute/path/to/mcp-essentials" }
    }
  }
}
```

## Example MCP call

```json
{
  "name": "audit_page",
  "arguments": {
    "url": "https://example.com/landing",
    "target_keywords": ["seo", "audit"],
    "language": "en"
  }
}
```

## Errors

| Code | When |
|---|---|
| `INVALID_INPUT` | Missing/malformed URL |
| `UNSUPPORTED` | Non-HTML content type (PDF, image, JSON, …) |
| `NETWORK_TIMEOUT` / `UPSTREAM_ERROR` | Fetch failed after retries |
| `PARSE_ERROR` | HTML parse blew up (rare) |

## Environment variables

None.

## Development

```bash
pip install -r requirements.txt
pytest pagesignal/tests
RUN_LIVE=1 pytest pagesignal/tests -m live
python tools/bundle_owui.py pagesignal
```

Tool-specific notes: [./AGENTS.md](./AGENTS.md).

## License

Apache 2.0 — see [../LICENSE](../LICENSE).

---

*Part of mcp-essentials by [Orzed](https://orzed.com).*
