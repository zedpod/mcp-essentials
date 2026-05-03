"""Pure URL/ID extraction for YouTube."""

import re
import urllib.parse

_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
_PATTERNS = [
    re.compile(r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/|/live/)([A-Za-z0-9_-]{11})"),
]


def extract_video_id(input_str: str) -> str | None:
    """Return the 11-char YouTube ID from a URL or raw ID. None on failure."""
    if not input_str:
        return None
    raw = input_str.strip()
    if _ID_RE.match(raw):
        return raw
    if "://" not in raw:
        # Try common short forms first.
        m = _PATTERNS[0].search(raw)
        if m:
            return m.group(1)
        return None
    try:
        parsed = urllib.parse.urlparse(raw)
    except ValueError:
        return None
    host = (parsed.netloc or "").lower()
    if "youtube.com" in host or "youtu.be" in host or "youtube-nocookie.com" in host:
        # /watch?v=ID
        qs = urllib.parse.parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            cand = qs["v"][0]
            if _ID_RE.match(cand):
                return cand
        m = _PATTERNS[0].search(raw)
        if m:
            return m.group(1)
    return None
