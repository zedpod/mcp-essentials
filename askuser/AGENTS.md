# AGENTS.md — askuser

> Read with [`../AGENTS.md`](../AGENTS.md). Total-rewrite tool — drag-rank from the legacy version was deferred to a follow-up.

## Public surface
- `ask_user_question(prompt, options=None, mode="single", allow_custom=True, required=False, min_select=None, max_select=None, timeout_s=300, *, language)` → `Result[Answer]`

## Architecture
- `core/types.py` — Pydantic `Question`, `Option`, `Answer`, `Result`.
- `core/validate.py` — pure validation. **No silent overrides** (the legacy `allow_multiple` valve that quietly overrode `mode` is gone).
- `core/overlay.py` — single source of truth for the overlay UI. Exposes:
    - `build_overlay_js(question, mode='owui')` — IIFE returning a Promise.
    - `build_owui_overlay_call(question)` — same IIFE plus the inline `<style>` injection helper for OWUI's `__event_call__` runtime.
    - `build_localhost_html(question, csrf_token)` — full HTML page for the MCP localhost flow.
- `server.py` — FastMCP server that boots an aiohttp app, opens the user's browser, awaits the POST `/answer`, returns `Result[Answer]`.
- `_owui_wrapper.py` — async OWUI wrapper. Awaits OWUI's `__event_call__` and parses the resolved Promise into an `Answer`.

## Edge cases
- **No display** (`DISPLAY` unset on Linux) → MCP returns `UNSUPPORTED` with a `hint.set_display`. Don't try to open a browser blindly.
- **CSRF**: tokens are generated per-call with `secrets.token_urlsafe(32)` and required on `POST /answer`. Mismatch → 403.
- **Same overlay** runs in both modes: only the bootstrap differs (Promise resolve vs `fetch('/answer')`).
- **`required=True`** hides the Skip button; `Esc` triggers a shake animation instead of resolving.
- **`prefers-reduced-motion: reduce`** disables scale/fade transitions globally via `@media`.

## Killed legacy behaviour
- `allow_multiple` valve overriding `mode` — gone. Conflicts → `INVALID_INPUT`.
- Numeric overflow shortcuts past 26 options (`27, 28, …`) — replaced by the search box.
- 700-line vanilla JS overlay — replaced with ~200 lines, modernized.
- Drag-to-rank mode — deferred.

## Tests
- `tests/test_core.py` — validation, overlay JS shape (config payload round-trips), HTML page composition, render() round-trip.
- `tests/test_owui.py` — bundle smoke + fake `__event_call__` round-trip.
- `tests/test_server.py` — MCP smoke. Live browser flow is manual (`tests/test_integration.py` is a placeholder).

## Future
- Add a `rank` mode (drag-to-reorder).
- Keyboard chord `1-0` for first ten + `Shift-1..0` for 11–20 in long lists.
- Pluggable themes (light/dark/system).
