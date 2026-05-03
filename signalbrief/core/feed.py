"""Lightweight RSS/Atom parser using stdlib xml.etree.

Returns dicts with title, link, summary, published (datetime), guid.
"""

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx

NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "media": "http://search.yahoo.com/mrss/",
}

HTML_TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def _strip_html(text: str | None) -> str:
    if not text:
        return ""
    return WS_RE.sub(" ", HTML_TAG_RE.sub(" ", text)).strip()


def _parse_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    raw = raw.strip()
    try:
        dt = parsedate_to_datetime(raw)
        if dt and dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _findtext(element, *paths) -> str | None:
    for path in paths:
        value = element.findtext(path, namespaces=NAMESPACES)
        if value:
            return value.strip()
    return None


def _find(element, *paths):
    for path in paths:
        e = element.find(path, namespaces=NAMESPACES)
        if e is not None:
            return e
    return None


def parse_feed(content: str) -> list[dict]:
    """Parse an RSS 2.0 or Atom 1.0 feed. Returns a list of item dicts."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return []

    out: list[dict] = []
    items = root.findall(".//item") or root.findall(".//atom:entry", NAMESPACES)
    for item in items:
        title = _findtext(item, "title", "atom:title")
        link = _findtext(item, "link", "atom:link")
        if not link:
            link_e = _find(item, "atom:link")
            if link_e is not None:
                link = link_e.attrib.get("href")
        summary = _strip_html(
            _findtext(item, "description", "summary", "atom:summary", "content:encoded")
        )
        published = _parse_date(
            _findtext(item, "pubDate", "atom:published", "atom:updated", "dc:date")
        )
        guid = _findtext(item, "guid", "atom:id") or link
        if not title and not link:
            continue
        out.append(
            {
                "title": (title or "").strip(),
                "link": (link or "").strip() or None,
                "summary": summary or None,
                "published": published,
                "guid": (guid or "").strip(),
            }
        )
    return out


def fetch_feed_text(client: httpx.Client, url: str) -> str:
    """Fetch a URL and decode using declared charset → charset-normalizer fallback."""
    r = client.get(url)
    r.raise_for_status()
    raw = r.content or b""
    declared = r.encoding
    if declared:
        try:
            return raw.decode(declared, errors="replace")
        except (LookupError, UnicodeDecodeError):
            pass
    try:
        from charset_normalizer import from_bytes

        result = from_bytes(raw).best()
        if result:
            return str(result)
    except Exception:
        pass
    return raw.decode("utf-8", errors="replace")
