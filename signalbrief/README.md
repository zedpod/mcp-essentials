# signalbrief

> Multi-feed RSS/Atom news brief. Token-level keyword matching (no `"ai" → "brain"` collisions), recency boost, deduping.

Part of [mcp-essentials](../README.md).

## Tools

- `collect(topics?, sources?, hours, max_per_source, min_score, language)` → `Result[NewsBrief]`
- `list_sources(language)` → `Result[SourceCatalog]`

The default keyword set covers AI/ML/business; the default source list covers en + tr major outlets, deduped (the legacy duplicates are gone).

## Install - Open WebUI

1. Paste [`./owui.py`](./owui.py) into Admin → Tools.
2. Description field (optional - docstrings already carry bilingual EN/TR triggers):
   ```text
   Aggregate, dedupe, and score recent news items from curated RSS / Atom feeds.

   Use when the user asks for:
   - a news brief on a topic (AI, tech, business, etc.)
   - recent headlines across multiple outlets
   - what happened in <topic> over the last day / week

   Do NOT use for: summarizing a specific article URL (use pagesignal or read it inline), generic Web search, real-time alerts, stock prices, or sports scores.
   ```
3. Configure Valves (`DEFAULT_LANGUAGE`, `DEFAULT_HOURS`, `DEFAULT_MIN_SCORE`, `DEFAULT_MAX_PER_SOURCE`).

## Install - Claude Desktop / Cursor / Cline

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
