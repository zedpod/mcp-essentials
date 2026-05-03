"""Pure formatting helpers for transcripts: text/srt/vtt/json."""

import json as json_module


def _ts(seconds: float, sep: str = ",") -> str:
    """SRT-style HH:MM:SS,mmm (sep=',') or VTT-style HH:MM:SS.mmm (sep='.')."""
    if seconds is None or seconds < 0:
        seconds = 0.0
    total_ms = int(round(seconds * 1000))
    h, rem = divmod(total_ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def format_transcript(entries: list[dict], fmt: str) -> str:
    """Render the entry list to text/srt/vtt/json.

    `entries` items: {start, duration, text}.
    """
    if fmt == "text":
        return "\n".join(e["text"] for e in entries if e.get("text")).strip()

    if fmt == "json":
        return json_module.dumps(entries, ensure_ascii=False, indent=2)

    if fmt == "srt":
        out = []
        for i, e in enumerate(entries, start=1):
            start = float(e.get("start", 0.0))
            dur = float(e.get("duration", 0.0))
            text = (e.get("text") or "").strip()
            if not text:
                continue
            out.append(str(i))
            out.append(f"{_ts(start, ',')} --> {_ts(start + dur, ',')}")
            out.append(text)
            out.append("")
        return "\n".join(out).strip()

    if fmt == "vtt":
        out = ["WEBVTT", ""]
        for e in entries:
            start = float(e.get("start", 0.0))
            dur = float(e.get("duration", 0.0))
            text = (e.get("text") or "").strip()
            if not text:
                continue
            out.append(f"{_ts(start, '.')} --> {_ts(start + dur, '.')}")
            out.append(text)
            out.append("")
        return "\n".join(out).strip()

    raise ValueError(f"unknown format: {fmt}")


def truncate_at_word_boundary(text: str, max_chars: int) -> tuple[str, bool]:
    """Cut text at the last whitespace ≤ max_chars. Returns (truncated_text, was_truncated)."""
    if max_chars is None or max_chars <= 0 or len(text) <= max_chars:
        return text, False
    cut = text[:max_chars]
    last_space = max(cut.rfind(" "), cut.rfind("\n"))
    if last_space > 0:
        cut = cut[:last_space]
    return cut.rstrip() + "\n…(truncated)", True
