"""HTML parser using stdlib html.parser — no soup dependency."""

import json
import re
from html.parser import HTMLParser

WORD_RE = re.compile(r"\w+", re.UNICODE)
SENTENCE_SPLIT_RE = re.compile(r"[.!?؟]+")
WHITESPACE_RE = re.compile(r"\s+")


class PageDocument(HTMLParser):
    """Single-pass HTML walker that collects everything pagesignal needs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self._in_title = False

        self.meta_description: str | None = None
        self.canonical: str | None = None
        self.robots: str | None = None
        self.og_title: str | None = None
        self.og_description: str | None = None
        self.og_image: str | None = None
        self.twitter_card: str | None = None
        self.html_lang: str | None = None
        self.charset: str | None = None

        self.h1: list[str] = []
        self.h2: list[str] = []
        self.h3: list[str] = []
        self._heading_stack: list[tuple[str, list[str]]] = []
        self.heading_sequence: list[str] = []  # h1, h2, ...

        self.body_text_parts: list[str] = []
        self._in_body = False
        self._suppress_depth = 0  # script/style nesting

        self.jsonld_blobs: list[str] = []
        self._in_jsonld = False
        self._current_jsonld: list[str] = []

    # ── boilerplate handlers ─────────────────────────────────────────────
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attr_dict = {k.lower(): v for k, v in attrs}

        if tag == "html":
            self.html_lang = attr_dict.get("lang") or self.html_lang
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            self._handle_meta(attr_dict)
        elif tag == "link" and attr_dict.get("rel", "").lower() == "canonical":
            self.canonical = attr_dict.get("href") or self.canonical
        elif tag in ("h1", "h2", "h3"):
            self._heading_stack.append((tag, []))
            self.heading_sequence.append(tag)
        elif tag == "body":
            self._in_body = True
        elif tag in ("script", "style", "noscript"):
            self._suppress_depth += 1
            if tag == "script" and (attr_dict.get("type") or "").lower() == "application/ld+json":
                self._in_jsonld = True
                self._current_jsonld = []

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3") and self._heading_stack:
            level, parts = self._heading_stack.pop()
            text = WHITESPACE_RE.sub(" ", "".join(parts)).strip()
            if level == "h1":
                self.h1.append(text)
            elif level == "h2":
                self.h2.append(text)
            elif level == "h3":
                self.h3.append(text)
        elif tag in ("script", "style", "noscript"):
            self._suppress_depth = max(0, self._suppress_depth - 1)
            if self._in_jsonld:
                self.jsonld_blobs.append("".join(self._current_jsonld))
                self._in_jsonld = False
                self._current_jsonld = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._heading_stack:
            self._heading_stack[-1][1].append(data)
        if self._in_jsonld:
            self._current_jsonld.append(data)
        if self._in_body and self._suppress_depth == 0:
            self.body_text_parts.append(data)

    # ── meta detail ──────────────────────────────────────────────────────
    def _handle_meta(self, attrs: dict[str, str]) -> None:
        name = (attrs.get("name") or "").lower()
        prop = (attrs.get("property") or "").lower()
        content = attrs.get("content") or ""
        charset = attrs.get("charset")
        if charset and self.charset is None:
            self.charset = charset
        if not content:
            return
        if name == "description":
            self.meta_description = content
        elif name == "robots":
            self.robots = content
        elif prop == "og:title":
            self.og_title = content
        elif prop == "og:description":
            self.og_description = content
        elif prop == "og:image":
            self.og_image = content
        elif name == "twitter:card":
            self.twitter_card = content

    # ── derived ──────────────────────────────────────────────────────────
    @property
    def title(self) -> str | None:
        text = WHITESPACE_RE.sub(" ", "".join(self.title_parts)).strip()
        return text or None

    @property
    def body_text(self) -> str:
        return WHITESPACE_RE.sub(" ", "".join(self.body_text_parts)).strip()


def parse_jsonld_types(blobs: list[str]) -> list[str]:
    out: list[str] = []
    for blob in blobs:
        try:
            data = json.loads(blob)
        except (json.JSONDecodeError, ValueError):
            continue

        def visit(obj):
            if isinstance(obj, dict):
                t = obj.get("@type")
                if isinstance(t, str):
                    out.append(t)
                elif isinstance(t, list):
                    out.extend(x for x in t if isinstance(x, str))
                for v in obj.values():
                    visit(v)
            elif isinstance(obj, list):
                for v in obj:
                    visit(v)

        visit(data)
    # Stable, deduped, lowercase hint preserved.
    seen: set[str] = set()
    dedup: list[str] = []
    for t in out:
        if t.lower() in seen:
            continue
        seen.add(t.lower())
        dedup.append(t)
    return dedup


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def sentence_count(text: str) -> int:
    parts = [p.strip() for p in SENTENCE_SPLIT_RE.split(text) if p.strip()]
    return max(1, len(parts)) if text.strip() else 0
