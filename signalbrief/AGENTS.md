# AGENTS.md — signalbrief

> Read with [`../AGENTS.md`](../AGENTS.md).

## Public surface
- `collect(topics, sources, hours, max_per_source, min_score, *, language)` → `Result[NewsBrief]`
- `list_sources(*, language)` → `Result[SourceCatalog]`

## Architecture
- `core/sources.py` — default source list + boost map. Editable.
- `core/feed.py` — stdlib XML RSS/Atom parser; charset-normalizer fallback for encoding.
- `core/tokens.py` — Unicode-aware whole-token + multi-word phrase matching. Substring matching is forbidden (legacy `"ai" in "brain"` bug).
- `core/brief.py` — orchestration with ThreadPoolExecutor (max 8 workers). Dedupes by `link → guid → title`.

## Edge cases
- **Personalization removed**: zero references to specific names/companies in tool output (legacy bug).
- **Encoding**: declared charset → charset-normalizer best guess → utf-8 with `errors="replace"`. Never silently drops items.
- **Future-dated `pubDate`** entries are accepted (some feeds publish embargoed pieces).
- **Keyword scoring**: title hit = 5 pts, body hit = 1 pt, recency 12h/24h/72h = 3/2/1 pts, source boost configurable.

## Tests
- `tests/test_core.py` — tokenization (including the canonical anti-substring assertion), aggregation, deduping, failed-source recording.
- `tests/test_owui.py`, `tests/test_server.py` — bundle/MCP smoke.
- `tests/test_integration.py` — `RUN_LIVE=1`.
