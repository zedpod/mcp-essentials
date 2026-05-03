# AGENTS.md — tubescript

> Read with [`../AGENTS.md`](../AGENTS.md). YouTube transcript MCP tool.

## Public surface
- `list_transcripts(url_or_id, *, language)` → `Result[TranscriptList]`
- `get_transcript(url_or_id, prefer_lang=None, translate_to=None, format="text", max_chars=None, *, language)` → `Result[Transcript]`

## Architecture
- `core/extract.py` — pure URL/ID extraction (raw 11-char IDs, watch URLs, youtu.be, shorts, live, embed, nocookie).
- `core/format.py` — pure formatters (text/srt/vtt/json) + word-boundary truncation.
- `core/transcript.py` — wraps `youtube-transcript-api`. Tests inject a `FakeApi` via the `api=` kwarg, no network.
- Errors classified from the third-party exception class name (`TranscriptsDisabled`, `VideoUnavailable`, etc.) so we don't depend on importing every exception type.

## Edge cases
- **Shorts / live / embed / nocookie URLs**: all parsed by `extract_video_id`.
- **Age-gated / region-blocked / private**: surfaced as `UNSUPPORTED` with a clear message.
- **Translation**: chained via `chosen.translate(target)`. If YouTube doesn't support the pair, returns `UNSUPPORTED` with a hint to call `list_transcripts` first.
- **Truncation**: word-boundary cut, never mid-word. `max_chars=0` or `None` disables it.

## Tests
- `tests/test_core_extract.py` — pure logic (no network, no library mock).
- `tests/test_core_transcript.py` — `FakeApi` exercising happy + every error path.
- `tests/test_owui.py` / `tests/test_server.py` — bundle/MCP smoke.
- `tests/test_integration.py` — `RUN_LIVE=1` with a stable test video ID.

## Env vars
- `TUBESCRIPT_MAX_TRANSCRIPT_CHARS` — optional, advisory cap (currently honored only via OWUI valve).
