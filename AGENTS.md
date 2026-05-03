# AGENTS.md — orzed/mcp-essentials

> Master guide for AI agents and humans contributing to this repo.
> If you change one tool, **read only that tool's `AGENTS.md`** (linked below) plus this file. Don't load all of them — the per-tool guides exist precisely so the master file stays small.

## Mission

Ship small, dual-mode tools that solve concrete jobs and are pleasant to read. Each tool runs two ways:

1. As an **Open WebUI Tool** — a single paste-able `<tool>/owui/main.py` users drop into OWUI Admin.
2. As a real **MCP server** (FastMCP / stdio) — `python -m <tool>.mcp` for Claude Desktop, Cursor, Cline, Continue, and any other MCP client.

Optimize for clarity over cleverness. The same LLM that calls these tools also reads them when something breaks; make both jobs easy.

## Architecture (read once)

Every tool lives in its own folder with this flat-as-possible structure:

```
<tool>/
├── owui.py            # GENERATED single-file Open WebUI Tool. Paste into OWUI Admin.
├── server.py          # FastMCP server definition (the MCP brain — small, calls core.*).
├── __main__.py        # Lets `python -m <tool>` start the MCP server over stdio.
├── core/              # Pure logic. Returns Pydantic Result[T]. No I/O at import time.
│   ├── __init__.py    # Re-exports + __bundle_order__ list driving the OWUI bundler.
│   ├── types.py       # Pydantic: Result, ErrorInfo, Input/Output models.
│   ├── i18n.py        # STRINGS = {"en": {...}, "tr": {...}} + t() helper.
│   ├── http.py        # build_client + get_json_with_retry (sync) and async variant.
│   ├── render.py      # to_markdown(result, lang) — used by the OWUI wrapper.
│   └── <feature>.py   # One file per logical sub-domain.
├── tests/
│   ├── conftest.py
│   ├── test_core_*.py # Unit tests for pure logic; respx-mocked HTTP. Coverage ≥90%.
│   ├── test_owui.py   # Smoke: load the generated owui.py, exercise its Tools class.
│   ├── test_server.py # Smoke: in-process FastMCP client of server.py.
│   ├── test_integration.py  # @pytest.mark.live, RUN_LIVE=1 only.
│   └── golden/        # Expected markdown outputs (optional).
├── static/            # askuser only — overlay HTML/CSS/JS shared with localhost MCP UI.
├── _owui_meta.py      # Bundler input: TITLE/DESCRIPTION/AUTHOR/VERSION/...
├── _owui_wrapper.py   # Bundler input: the `class Tools:` shell that delegates to core.
├── .env.example       # Only when the tool consumes env vars.
├── requirements.txt   # Runtime deps, slim.
├── README.md          # End-user documentation.
└── AGENTS.md          # Tool-specific agent guide.
```

`owui.py` is **generated** by `tools/bundle_owui.py` from `core/` (in `__bundle_order__`) plus `_owui_wrapper.py`, with the OWUI metadata header from `_owui_meta.py`. Hand-edit anywhere except `owui.py`; run `make bundle`; commit both.

The root holds `tools/bundle_owui.py`, `tests/test_repo.py`, the master `AGENTS.md`, and (eventually) `_template/` for adding new tools.

## Universal Rules

These apply to every tool. The repo-level test suite enforces several of them.

1. **`language: str = "en"` is a mandatory parameter on every public function.** Valves and env vars are *defaults only*; the per-call argument always wins. `core/` code never reads `self.valves.LANGUAGE` — that is the OWUI wrapper's job, and the wrapper passes `language=` explicitly.
2. **Return `Result[T]`. Never raise across the public boundary.** Inside `core/` you may raise freely; catch at the seam and convert to `Result(ok=False, error=ErrorInfo(...))`.
3. **`ErrorInfo` always carries `code` (machine-readable enum), `message_en`, `message_tr`, and an optional `hint`** explaining recovery. `message_tr` cannot be empty — repo tests fail if it is.
4. **HTTP goes through `core/http.py`** built on `httpx`. Default timeout 10s, max 20s. Retry idempotent GETs three times on 408/429/5xx with jittered exponential backoff. Honor `Retry-After`.
5. **No silent fallbacks.** A hardcoded city list, a remote API substituting for a local generator, a default symbol set that excludes whole continents — all of these ship as explicit, surfaced behavior. Provider switches show up in `meta.source`. Remote rendering of sensitive payloads requires explicit opt-in plus a `meta.warning`.
6. **No silent override of caller intent.** If two parameters conflict, return `INVALID_INPUT` with a `hint`. The original `askuser` valve `allow_multiple` overrode `mode` silently — that is the canonical anti-pattern this rule kills.
7. **No personalization in tool output.** Names, companies, in-jokes — they do not belong in tool responses. They belong in the caller's prompt.
8. **Locale-independent parsing.** Don't `strptime` month names. Use `cryptography` for cert dates. Format numbers in `render.py` based on `language`, never on `LC_NUMERIC`.
9. **Token-based keyword matching only.** Substring matching ("ai" in "brain") is forbidden. Use Unicode word boundaries or exact quoted-phrase matching.
10. **No `print()` in MCP mode.** Stdio is the protocol channel. Loggers go to stderr.
11. **`owui/main.py` is generated.** Edit `core/`, run `make bundle`. CI runs `make check-bundle` and fails on drift.
12. **Resources are closed.** `with httpx.Client(...)`, `with io.BytesIO() as buf:`, `try/finally` for aiohttp runners. No exceptions.

## Per-tool guidance index

When you change one tool, load *only* the relevant `AGENTS.md` plus this file. Each per-tool guide is ~80–150 lines.

| Tool | Status | Per-tool guide |
|---|---|---|
| askuser | refactored ✓ | [./askuser/AGENTS.md](./askuser/AGENTS.md) |
| currencypulse | refactored ✓ | [./currencypulse/AGENTS.md](./currencypulse/AGENTS.md) |
| flighthunter | refactored ✓ | [./flighthunter/AGENTS.md](./flighthunter/AGENTS.md) |
| pagesignal | refactored ✓ | [./pagesignal/AGENTS.md](./pagesignal/AGENTS.md) |
| paperforge | refactored ✓ | [./paperforge/AGENTS.md](./paperforge/AGENTS.md) |
| qrforge | refactored ✓ | [./qrforge/AGENTS.md](./qrforge/AGENTS.md) |
| signalbrief | refactored ✓ | [./signalbrief/AGENTS.md](./signalbrief/AGENTS.md) |
| sitepulse | refactored ✓ | [./sitepulse/AGENTS.md](./sitepulse/AGENTS.md) |
| tripweather | refactored ✓ | [./tripweather/AGENTS.md](./tripweather/AGENTS.md) |
| tubescript | refactored ✓ | [./tubescript/AGENTS.md](./tubescript/AGENTS.md) |

"Legacy" tools still ship as the original single-file Open WebUI Tool. They do not yet conform to the universal rules above. Refactor them in the order shown.

## Adding a new tool

1. `cp -r _template/ <newtool>/`
2. Define inputs and outputs as Pydantic models in `core/types.py`. Wrap public functions to return `Result[YourOutput]`.
3. Add `en` and `tr` keys to `core/i18n.py`. The repo test enforces parity.
4. Implement pure logic in `core/<feature>.py`. Export from `core/__init__.py`.
5. Write `tests/test_core_*.py` with respx-mocked HTTP. Add live tests behind `@pytest.mark.live`.
6. Wire the OWUI side: edit `owui/main.py.template` if templated, then `make bundle` to produce `owui/main.py`.
7. Wire the MCP side: register `@mcp.tool()` wrappers in `mcp/server.py` that call `core` and return `.model_dump(mode="json")`.
8. Write `<newtool>/README.md` and `<newtool>/AGENTS.md` from the templates.
9. Add a row to the table above and to the root README.
10. `make test && make check-bundle && make lint` must be green.

## Testing & CI

- `make test` — mocked unit + integration. Run on every PR.
- `make test-live` — `RUN_LIVE=1` real APIs. Nightly cron only.
- `make check-bundle` — fails if any `<tool>/owui/main.py` drifts from `core/`. Required to merge.
- `tests/test_repo.py` — repo-level invariants: each tool has the required files; `STRINGS["en"]` and `STRINGS["tr"]` carry identical key sets; each `mcp/server.py` exports a `FastMCP` instance.

## Release

PyPI is optional. Per-tool semver: tags `<tool>-vX.Y.Z`. Each tool can release independently. The packaging hook lives in each tool's `pyproject.toml` once it lands.

## Secret handling

- Production OWUI: pass via Valves in the OWUI Admin panel.
- Production MCP: pass via the `env` block in `claude_desktop_config.json` (or the equivalent for your MCP client).
- Local dev / tests: `.env` files, never committed (see `.gitignore`).
- `core/` reads via `os.getenv("ORZED_<TOOL>_<KEY>")`. **No `load_dotenv()` calls in production code.** Tests opt in.
- Never log secret values. If a fallback path leaks data to a third-party API, surface it in `meta.warning` and require opt-in.

## Branding

`Orzed` and `orzed.com` appear in (a) one badge in the root README, (b) one subtitle line, (c) one footer line, and (d) per-tool README footers. Nowhere else. Tool output, error messages, MCP tool descriptions, and `core/` code are brand-neutral. No marketing copy in code.
