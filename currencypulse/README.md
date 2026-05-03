# currencypulse

> Multi-source FX rates, conversion, and time-series. Provider chain falls through automatically.

Part of [mcp-essentials](../README.md). Runs as both an Open WebUI Tool and a real MCP server.

## What it does

Four MCP tools, each returning a `Result[T]`:

| Tool | Returns |
|---|---|
| `rate(base, quote, on?)` | Single rate, latest or historical |
| `convert(amount, base, quote, on?)` | Amount conversion + rate detail |
| `snapshot(base, symbols?)` | Latest rates for many quote currencies |
| `timeseries(base, quote, start, end)` | Daily rates over a range (≤ 366 days) |

Provider chain (first that supports the pair wins):

1. **Frankfurter** (ECB-backed) - covers ~30 majors including TRY
2. **exchangerate.host** - wider ISO 4217 coverage
3. **OpenExchangeRates** - only when `CURRENCYPULSE_OXR_APP_ID` env is set
4. **TCMB** - Turkish central bank, TRY-anchored

The picked provider name shows up in `data.source` and `meta.source` so the LLM (and humans) know where the number came from.

## Install - Open WebUI

1. Open OWUI → **Admin Panel → Tools → "+ New tool"**.
2. Copy the entire contents of [`./owui.py`](./owui.py) into the editor.
3. Description field (optional override - bilingual triggers already live in the docstrings inside `owui.py`, so EN or TR natural-language calls both work):
   ```text
   FX rates, currency conversion, multi-quote snapshot, and historical time-series. Multi-source provider chain (Frankfurter, exchangerate.host, OXR, TCMB).

   Use when the user asks for:
   - the rate between two currencies
   - converting an amount between currencies
   - one base currency against many quotes
   - daily rates over a date range

   Do NOT use for: cryptocurrency, stock prices, commodity prices, NAV.
   ```
4. Click **Save**. Configure Valves (`DEFAULT_LANGUAGE`, `DEFAULT_BASE`, timeout). No env vars required for the free providers; set `CURRENCYPULSE_OXR_APP_ID` if you want OpenExchangeRates fallback coverage.

## Install - Claude Desktop / Cursor / Cline

```json
{
  "mcpServers": {
    "currencypulse": {
      "command": "python",
      "args": ["-m", "currencypulse"],
      "cwd": "/absolute/path/to/mcp-essentials",
      "env": {
        "PYTHONPATH": "/absolute/path/to/mcp-essentials",
        "CURRENCYPULSE_OXR_APP_ID": "optional-oxr-key"
      }
    }
  }
}
```

## Examples

```json
{ "name": "rate", "arguments": { "base": "USD", "quote": "EUR" } }
```

```json
{ "name": "convert", "arguments": { "amount": 100, "base": "USD", "quote": "TRY" } }
```

```json
{ "name": "timeseries",
  "arguments": { "base": "EUR", "quote": "USD", "start": "2025-01-01", "end": "2025-03-31" } }
```

## Errors

| Code | When |
|---|---|
| `INVALID_INPUT` | Unknown currency code, malformed date, range > 366 days, negative/non-finite amount |
| `UNSUPPORTED` | Crypto codes (BTC, ETH, …) - not handled by this tool |
| `NOT_FOUND` | No provider could fulfil the pair |
| `UPSTREAM_ERROR` | All providers failed network / 5xx |

Every error carries `message_en`, `message_tr`, and an optional `hint`.

## Numbers and locale

Rates come back as plain `float`s in the structured payload. The OWUI markdown renderer formats them per `language` (en: `1,234.5678`; tr: `1.234,5678`). MCP clients receive raw numbers and format on the consumer side.

## Environment variables

| Var | Required? | Effect |
|---|---|---|
| `CURRENCYPULSE_OXR_APP_ID` | No | Enables OpenExchangeRates fallback |

See [`./.env.example`](./.env.example).

## Development

```bash
pip install -r requirements.txt
pytest currencypulse/tests
RUN_LIVE=1 pytest currencypulse/tests -m live
python tools/bundle_owui.py currencypulse           # regenerate owui.py
python tools/bundle_owui.py currencypulse --check   # CI: fail on drift
```

Tool-specific contributor guide: [./AGENTS.md](./AGENTS.md).

## License

Apache 2.0 - see [../LICENSE](../LICENSE).

---

*Part of mcp-essentials by [Orzed](https://orzed.com).*
