# AGENTS.md — pagesignal

> Read this plus [`../AGENTS.md`](../AGENTS.md) before changing pagesignal.

## Tool identity
SEO + AI-answer audit for a single URL. Stable. Owned by Orzed, LLC.

## Public surface
- `audit_page(url, target_keywords=None, *, language="en", timeout_seconds=10.0)` → `Result[PageAudit]`

## Architecture
- `core/parse.py` — single-pass `html.parser` walker → `PageDocument`. No external HTML parser.
- `core/lexicons.py` — multi-language question-word sets (en/tr/de/es/fr/it/pt/ar).
- `core/audit.py` — orchestration: fetch → parse → derive issues → assemble `PageAudit`.
- `core/render.py` — markdown view for OWUI.
- `core/http.py` — same retry/backoff pattern as the other tools (httpx-based).

## Edge cases
- **Non-HTML content** → `UNSUPPORTED` (PDF/image/JSON/etc.). Don't try to parse arbitrary bytes.
- **JS-heavy pages** flagged via heuristic: `word_count < 50` while `bytes(html) > 4_000`. False positives possible on highly minified static pages — fine for an advisory issue.
- **Question detection**: looks for `?`/`؟` or a leading question word in the detected language. The `<html lang>` attribute drives detection; falls back to caller's `language`.
- **Schema types** are extracted from JSON-LD `<script>` blocks; both string and array `@type` forms are handled. Other structured-data formats (microdata, RDFa) are intentionally ignored.
- **Word count** uses Unicode `\w+` — works for Latin, Cyrillic, CJK, Arabic. **Do not** add a hand-rolled regex with character ranges (legacy bug).
- **`noindex`** is surfaced as an `error` severity. Site owners almost always want to see this.

## i18n
All user-visible strings (issues, error messages, labels) live in `core/i18n.py`. Both `en` and `tr` keys mandatory; the repo-level test enforces parity.

## Tests
- `tests/test_core_audit.py` — happy path + edge cases, respx-mocked HTML.
- `tests/test_owui.py`, `tests/test_server.py` — bundle/MCP smoke.
- `tests/test_integration.py` — `@pytest.mark.live`, only with `RUN_LIVE=1`.

## How to add a new check
1. Add an issue key (en+tr) in `core/i18n.py`.
2. Compute the signal in `core/audit.py` and append `_make_issue(...)` with proper severity.
3. If the signal needs new structured fields, extend `core/types.py` + render.
4. Add a test exercising the trigger.
5. `python tools/bundle_owui.py pagesignal && pytest pagesignal/tests`.
