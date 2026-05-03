# mcp-essentials

> Practical, dual-mode AI tools - same code runs as Open WebUI Tools **and** as real MCP servers.
> Open source by [Orzed](https://orzed.com).

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-stdio-7C3AED)](https://modelcontextprotocol.io/)
[![tests: pytest](https://img.shields.io/badge/tests-pytest-success)](https://docs.pytest.org/)
[![by Orzed](https://img.shields.io/badge/by-Orzed-E8713A)](https://orzed.com)

Plug them into your LLM. Two delivery modes from a single codebase:

- **Open WebUI** - paste `<tool>/owui.py` into Admin → Tools, configure Valves, done.
- **Claude Desktop / Cursor / Cline / Continue** - add a one-liner to `claude_desktop_config.json`. Each tool runs as `python -m <tool>` over MCP stdio.

Every tool is i18n-aware (English default, Turkish included), returns structured `Result` objects to MCP clients and rendered markdown to OWUI, retries network calls with backoff, and ships with tests.

### How a tool is laid out

```
<tool>/
├── owui.py            ← paste THIS into Open WebUI Admin → Tools
├── server.py          ← FastMCP server definition (the MCP brain)
├── __main__.py        ← so `python -m <tool>` runs the MCP server
├── core/              ← pure logic (the source of truth - all tools edit here)
├── tests/             ← unit + smoke tests
├── _owui_meta.py      ← bundler input (don't edit unless you know what you're doing)
├── _owui_wrapper.py   ← bundler input
├── README.md
├── AGENTS.md
└── requirements.txt
```

`owui.py` is **generated** from `core/` + `_owui_wrapper.py` by `tools/bundle_owui.py`. CI runs `make check-bundle` and fails if it drifts. Edit `core/`, run `make bundle`, commit both.

---

## Tools

| Tool | Does | OWUI | MCP | Docs |
|---|---|:---:|:---:|---|
| **qrforge** | QR codes for arbitrary text, URLs, Wi-Fi, vCards | ✓ | ✓ | [./qrforge/](./qrforge/README.md) |
| **currencypulse** | Multi-source FX quotes, conversion, time-series, historical | ✓ | ✓ | [./currencypulse/](./currencypulse/README.md) |
| **pagesignal** | URL → SEO + AI-answer-readiness audit | ✓ | ✓ | [./pagesignal/](./pagesignal/README.md) |
| **tubescript** | YouTube transcript extraction with format export | ✓ | ✓ | [./tubescript/](./tubescript/README.md) |
| **sitepulse** | DNS, RDAP, SSL, HTTP health snapshot | ✓ | ✓ | [./sitepulse/](./sitepulse/README.md) |
| **signalbrief** | Multi-feed news brief with deduping and scoring | ✓ | ✓ | [./signalbrief/](./signalbrief/README.md) |
| **flighthunter** | Flight search via SerpAPI (Google Flights), flexible-date | ✓ | ✓ | [./flighthunter/](./flighthunter/README.md) |
| **tripweather** | Open-Meteo geocoding + travel forecast | ✓ | ✓ | [./tripweather/](./tripweather/README.md) |
| **askuser** | Interactive multiple-choice prompts (overlay or browser) | ✓ | ✓ | [./askuser/](./askuser/README.md) |
| **paperforge** | Synthesize a conversation into a flowing md/html/docx/pdf document | ✓ | ✓ | [./paperforge/](./paperforge/README.md) |

> Status: all ten tools share the same dual-mode layout. Each one ships with respx-mocked tests, an `owui.py` bundle, and a `python -m <tool>` MCP server entry-point.

---

## Quick start - Open WebUI

1. In Open WebUI, go to **Admin Panel → Tools → "+ New tool"**.
2. Open the tool's `owui.py` (e.g. [`./qrforge/owui.py`](./qrforge/owui.py)). Copy the entire file.
3. Paste into the OWUI tool editor.
4. **Description field**: the metadata block at the top of `owui.py` populates it automatically. If you want to override it, every tool's per-tool README (`<tool>/README.md`) ships a paste-ready text block under "Install - Open WebUI". Bilingual EN/TR call triggers already live inside the docstrings of `owui.py`, so plain-language calls in either language work without touching this field.
5. Click **Save**.
6. Configure Valves (defaults are sensible - most users only set `DEFAULT_LANGUAGE` and `TIMEOUT_SECONDS`).
7. In a chat, open the **Controls → Tools** panel and toggle the tool on for your model.

Example prompt once `qrforge` is enabled:

> "Generate a Wi-Fi QR code for SSID `OrzedGuest`, password `welcome2025`, WPA2."

---

## Quick start - Claude Desktop, Cursor, Cline, Continue

Edit your MCP config:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Cursor**: Settings → MCP → Add server (same JSON shape)
- **Cline (VS Code)**: Cline panel → MCP Servers → Add server (same JSON)

```json
{
  "mcpServers": {
    "qrforge": {
      "command": "python",
      "args": ["-m", "qrforge"],
      "cwd": "/absolute/path/to/mcp-essentials",
      "env": { "PYTHONPATH": "/absolute/path/to/mcp-essentials" }
    },
    "tripweather": {
      "command": "python",
      "args": ["-m", "tripweather"],
      "cwd": "/absolute/path/to/mcp-essentials",
      "env": { "PYTHONPATH": "/absolute/path/to/mcp-essentials" }
    }
  }
}
```

Restart the client. The tools appear in the MCP indicator. Each tool exposes a JSON Schema MCP clients use for autocomplete and validation.

For tools that need API keys (`flighthunter` requires SerpAPI; `currencypulse`, `signalbrief`, `tubescript` have optional knobs), add them under `env`:

```json
"flighthunter": {
  "command": "python",
  "args": ["-m", "flighthunter"],
  "cwd": "/absolute/path/to/mcp-essentials",
  "env": {
    "PYTHONPATH": "/absolute/path/to/mcp-essentials",
    "FLIGHTHUNTER_SERPAPI_KEY": "your-serpapi-key"
  }
}
```

See each tool's `.env.example` for the full set of environment variables it consumes.

---

## Development

```bash
git clone https://github.com/orzed/mcp-essentials
cd mcp-essentials

python -m venv .venv && source .venv/bin/activate
make install-dev          # pytest, ruff, respx, mcp[cli], httpx
make install-tools        # runtime deps for all tools

make test                 # mocked unit + integration; coverage core/ ≥ 90%
make test-live            # real API calls (RUN_LIVE=1); nightly use only
make lint                 # ruff
make check-bundle         # ensures owui/main.py is up-to-date with core/
```

Adding a new tool? Read [AGENTS.md](AGENTS.md), copy `_template/`, fill in.

Browser-based MCP clients and remote-MCP setups will work too; consult your client's MCP docs for stdio command launch.

---

## Project ethos

Tools that an LLM can call **and** an engineer can read in one sitting. We aggressively reject:

- silent fallbacks ("I'll just use this hardcoded city")
- locale leakage ("why is my output Turkish?")
- god-tools with 12 optional parameters and unclear interactions
- substring keyword matches that fire on `ai → "brain"`
- personalization sneaking into shared output

Every refactor in this repo replaced one of those.

---

## License

Apache 2.0 - see [LICENSE](LICENSE).

---

*Made with care by [Orzed](https://orzed.com). We open-source small tools we wish existed. PRs, issues, and stories are welcome.*
