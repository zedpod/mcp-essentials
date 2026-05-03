# askuser

> Interactive question prompts for LLM agents. Modern overlay UX, dual delivery: Open WebUI overlay **or** localhost browser page (MCP).

Part of [mcp-essentials](../README.md).

## Modes

- **`single`** — pick one option; clicking confirms instantly.
- **`multi`** — pick zero or more options; explicit Confirm button (with optional `min_select`/`max_select`).
- **`free_text`** — textarea only; user types anything.

The `allow_custom` flag adds a free-text input *alongside* options. Keyboard nav: `1`–`9` for first nine, arrows + Enter to select, `Esc` to skip, `Tab` cycles within the modal (focus trap). Search filter auto-shows for >10 options. `prefers-reduced-motion` honored. Mobile: full-screen sheet under 640px.

## Install — Open WebUI

Paste [`./owui.py`](./owui.py) into Admin → Tools. Configure the `ACCENT_COLOR` Valve if you want a different brand color (default Claude orange `#E8713A`).

## Install — Claude Desktop / Cursor / Cline

```json
{
  "mcpServers": {
    "askuser": {
      "command": "python",
      "args": ["-m", "askuser"],
      "cwd": "/absolute/path/to/mcp-essentials",
      "env": { "PYTHONPATH": "/absolute/path/to/mcp-essentials" }
    }
  }
}
```

When `ask_user_question` is called, the MCP server starts an ephemeral localhost web server, generates a one-time CSRF token, opens your default browser to `http://127.0.0.1:<random-port>/?t=<token>`, and waits for the answer. The server shuts itself down as soon as the user submits, cancels, or the timeout fires.

If the host has no display (headless server, `DISPLAY` unset on Linux), the tool returns `UNSUPPORTED` instead of hanging. Run from a desktop session, or use the OWUI bundle.

## Tool

`ask_user_question(prompt, options?, mode, allow_custom, required, min_select?, max_select?, timeout_s, language)` → `Result[Answer]`.

`Answer.type` is one of `select`, `custom`, `skip`, `timeout`, `cancelled`. `indices` and `values` carry the picked options; `custom_text` carries free-text input. `elapsed_ms` is the round-trip duration.

## Security

- localhost binds only to `127.0.0.1` — never `0.0.0.0`.
- A fresh CSRF token is required on the `POST /answer` request via the `X-Token` header.
- Server lifetime is bounded by `timeout_s` (≤ 1800 sec). State is in-memory only.

## License

Apache 2.0.

---

*Part of mcp-essentials by [Orzed](https://orzed.com).*
