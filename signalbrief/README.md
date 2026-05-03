# signalbrief

> Multi-feed RSS/Atom news brief. Token-level keyword matching (no `"ai" → "brain"` collisions), recency boost, deduping.

Part of [mcp-essentials](../README.md).

## Tools

- `collect(topics?, sources?, hours, max_per_source, min_score, language)` → `Result[NewsBrief]`
- `list_sources(language)` → `Result[SourceCatalog]`

The default keyword set covers AI/ML/business; the default source list covers en + tr major outlets, deduped (the legacy duplicates are gone).

## Install — Open WebUI

Paste [`./owui.py`](./owui.py) into Admin → Tools.

## Install — Claude Desktop / Cursor / Cline

```json
{
  "mcpServers": {
    "signalbrief": {
      "command": "python",
      "args": ["-m", "signalbrief"],
      "cwd": "/absolute/path/to/mcp-essentials",
      "env": { "PYTHONPATH": "/absolute/path/to/mcp-essentials" }
    }
  }
}
```

## License

Apache 2.0.

---

*Part of mcp-essentials by [Orzed](https://orzed.com).*
