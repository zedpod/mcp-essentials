"""Public API: collect() + list_sources()."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import httpx

from .feed import fetch_feed_text, parse_feed
from .i18n import normalize_lang, t
from .sources import (
    DEFAULT_KEYWORDS,
    DEFAULT_SOURCES,
    boost_for,
    dedupe_sources,
)
from .tokens import keyword_matches, tokenize
from .types import (
    ErrorInfo,
    NewsBrief,
    NewsItem,
    Result,
    SourceCatalog,
    SourceFailure,
    SourceInfo,
)


def _err(code: str, lang: str, en_key: str, *, hint_key: str | None = None) -> ErrorInfo:
    return ErrorInfo(
        code=code,
        message_en=t(en_key, "en"),
        message_tr=t(en_key, "tr"),
        hint=t(hint_key, lang) if hint_key else None,
    )


def _resolve_sources(custom: list[dict] | None) -> list[dict]:
    if custom:
        cleaned = [s for s in custom if isinstance(s, dict) and s.get("url")]
        return dedupe_sources(cleaned)
    return dedupe_sources(DEFAULT_SOURCES)


def _resolve_keywords(custom: list[str] | None) -> list[str]:
    if custom:
        return [k.strip() for k in custom if k and k.strip()]
    return list(DEFAULT_KEYWORDS)


def _score(item: dict, source_name: str, keyword_tokens: dict[str, list[str]]) -> tuple[int, list[str]]:
    title = item.get("title") or ""
    summary = item.get("summary") or ""
    haystack_title = tokenize(title)
    haystack_full = tokenize(title + " " + summary)
    score = 0
    matched: list[str] = []
    for kw, kw_toks in keyword_tokens.items():
        if not kw_toks:
            continue
        title_hits = keyword_matches(haystack_title, kw)
        body_hits = keyword_matches(haystack_full, kw) - title_hits
        local = title_hits * 5 + body_hits
        if local > 0:
            score += local
            matched.append(kw)

    pub = item.get("published")
    if isinstance(pub, datetime):
        now = datetime.now(timezone.utc)
        try:
            age = now - pub
            if age <= timedelta(hours=12):
                score += 3
            elif age <= timedelta(hours=24):
                score += 2
            elif age <= timedelta(hours=72):
                score += 1
        except TypeError:
            pass

    score += boost_for(source_name)
    return score, matched


def _fetch_one(client: httpx.Client, source: dict) -> tuple[dict, list[dict] | None, str | None]:
    try:
        text = fetch_feed_text(client, source["url"])
        items = parse_feed(text)
        return source, items, None
    except Exception as exc:
        return source, None, f"{type(exc).__name__}: {exc}"


def list_sources(*, language: str = "en") -> Result[SourceCatalog]:
    catalog = SourceCatalog(
        sources=[
            SourceInfo(
                name=str(src["name"]),
                url=str(src["url"]),
                language=src.get("language"),
            )
            for src in dedupe_sources(DEFAULT_SOURCES)
        ]
    )
    return Result(ok=True, data=catalog, meta={"count": len(catalog.sources)})


def collect(
    topics: list[str] | None = None,
    sources: list[dict] | None = None,
    hours: int = 24,
    max_per_source: int = 10,
    min_score: int = 2,
    *,
    language: str = "en",
    client=None,
) -> Result[NewsBrief]:
    lang = normalize_lang(language)
    if hours < 1 or hours > 336:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_hours"))

    keywords = _resolve_keywords(topics)
    feeds = _resolve_sources(sources)
    if not keywords:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.empty_keywords"))
    if not feeds:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.empty_sources"))

    keyword_tokens = {kw: tokenize(kw) for kw in keywords}
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    own_client = client is None
    if client is None:
        client = httpx.Client(
            timeout=8.0,
            follow_redirects=True,
            headers={"User-Agent": "orzed-signalbrief/1.0"},
        )

    aggregate: list[NewsItem] = []
    failures: list[SourceFailure] = []
    sources_used: list[str] = []
    seen_keys: set[str] = set()

    try:
        with ThreadPoolExecutor(max_workers=min(8, len(feeds))) as pool:
            futures = [pool.submit(_fetch_one, client, src) for src in feeds]
            for fut in futures:
                src, items, error = fut.result()
                src_name = str(src.get("name") or src.get("url"))
                if error:
                    failures.append(
                        SourceFailure(
                            name=src_name,
                            url=str(src.get("url") or ""),
                            error=error,
                        )
                    )
                    continue
                sources_used.append(src_name)
                items_for_source = 0
                for raw in items or []:
                    pub = raw.get("published")
                    if isinstance(pub, datetime) and pub < cutoff:
                        continue
                    key = (raw.get("link") or raw.get("guid") or raw.get("title") or "").strip().lower()
                    if not key or key in seen_keys:
                        continue
                    seen_keys.add(key)
                    score, matched = _score(raw, src_name, keyword_tokens)
                    if score < min_score:
                        continue
                    aggregate.append(
                        NewsItem(
                            title=raw.get("title") or "(untitled)",
                            link=raw.get("link"),
                            summary=raw.get("summary"),
                            source=src_name,
                            published=pub if isinstance(pub, datetime) else None,
                            score=score,
                            matched_keywords=matched,
                        )
                    )
                    items_for_source += 1
                    if items_for_source >= max_per_source:
                        break
    finally:
        if own_client:
            client.close()

    aggregate.sort(key=lambda n: (-n.score, n.title))
    brief = NewsBrief(
        items=aggregate,
        sources_used=sources_used,
        failed_sources=failures,
        keywords=keywords,
        hours_back=hours,
    )
    return Result(
        ok=True,
        data=brief,
        meta={
            "item_count": len(aggregate),
            "sources_ok": len(sources_used),
            "sources_failed": len(failures),
        },
    )
