"""Audit a page: fetch + parse + classify into PageAudit + Issues."""

import time

from .http import NetworkTimeout, RateLimited, UpstreamError, build_client, get_with_retry
from .i18n import normalize_lang, t
from .lexicons import is_question
from .parse import PageDocument, parse_jsonld_types, sentence_count, word_count
from .types import (
    ErrorInfo,
    GeoSignals,
    HeadingsInfo,
    Issue,
    MetaTags,
    PageAudit,
    Performance,
    Readability,
    Result,
)

DEFAULT_USER_AGENT = "orzed-pagesignal/1.0 (+https://orzed.com)"
LARGE_RESPONSE_KB = 1024
SLOW_RESPONSE_MS = 1500


def _err(code: str, lang: str, en_key: str, *, fmt: dict | None = None,
         hint_key: str | None = None) -> ErrorInfo:
    fmt = fmt or {}
    return ErrorInfo(
        code=code,
        message_en=t(en_key, "en", **fmt),
        message_tr=t(en_key, "tr", **fmt),
        hint=t(hint_key, lang, **fmt) if hint_key else None,
    )


def _make_issue(severity: str, code: str, lang: str, en_key: str,
                 fmt: dict | None = None) -> Issue:
    fmt = fmt or {}
    return Issue(
        severity=severity,  # type: ignore[arg-type]
        code=code,
        message_en=t(en_key, "en", **fmt),
        message_tr=t(en_key, "tr", **fmt),
    )


def _detect_skipped_levels(sequence: list[str]) -> list[str]:
    """Return a list of "h1->h3" style strings for any heading that skipped a level."""
    skips: list[str] = []
    last_level = 0
    for h in sequence:
        level = int(h[1])
        if last_level and level - last_level > 1:
            skips.append(f"{['h0','h1','h2','h3'][last_level]}->{h}")
        last_level = level
    return skips


def _detect_language_hint(html_lang: str | None) -> str | None:
    if not html_lang:
        return None
    return html_lang.lower().split("-")[0][:5]


def audit_page(
    url: str,
    target_keywords: list[str] | None = None,
    *,
    language: str = "en",
    timeout_seconds: float = 10.0,
    user_agent: str = DEFAULT_USER_AGENT,
    client=None,
) -> Result[PageAudit]:
    lang = normalize_lang(language)

    if not url or not isinstance(url, str):
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.url_required"))
    cleaned = url.strip()
    if not (cleaned.startswith("http://") or cleaned.startswith("https://")):
        return Result(
            ok=False,
            error=_err(
                "INVALID_INPUT",
                lang,
                "error.invalid_url",
                hint_key="hint.try_https",
            ),
        )

    own_client = client is None
    if client is None:
        client = build_client(timeout=timeout_seconds, user_agent=user_agent)

    started = time.monotonic()
    try:
        try:
            response = get_with_retry(client, cleaned)
        except (NetworkTimeout, RateLimited, UpstreamError) as exc:
            upstream = getattr(exc, "status", None)
            return Result(
                ok=False,
                error=_err(
                    "UPSTREAM_ERROR" if isinstance(exc, UpstreamError) else "NETWORK_TIMEOUT",
                    lang,
                    "error.unreachable",
                    fmt={"detail": str(exc)},
                ),
                meta={"upstream_status": upstream} if upstream else {},
            )
        elapsed_ms = int((time.monotonic() - started) * 1000)

        content_type = (response.headers.get("Content-Type") or "").lower()
        if content_type and "html" not in content_type and "xml" not in content_type:
            return Result(
                ok=False,
                error=_err(
                    "UNSUPPORTED",
                    lang,
                    "error.unsupported_content_type",
                    fmt={"ct": content_type},
                ),
            )

        body_bytes = response.content or b""
        try:
            text = body_bytes.decode(response.encoding or "utf-8", errors="replace")
        except (LookupError, AttributeError):
            text = body_bytes.decode("utf-8", errors="replace")
    finally:
        if own_client:
            client.close()

    doc = PageDocument()
    try:
        doc.feed(text)
    except Exception as exc:  # html.parser is permissive; this is rare
        return Result(
            ok=False,
            error=_err("PARSE_ERROR", lang, "error.unreachable", fmt={"detail": str(exc)}),
        )

    issues: list[Issue] = []

    # ── Meta tags ────────────────────────────────────────────────────────
    title = doc.title or ""
    description = doc.meta_description or ""
    meta = MetaTags(
        title=title or None,
        title_length=len(title),
        description=description or None,
        description_length=len(description),
        canonical=doc.canonical,
        robots=doc.robots,
        og_title=doc.og_title,
        og_description=doc.og_description,
        og_image=doc.og_image,
        twitter_card=doc.twitter_card,
        lang=doc.html_lang,
        charset=doc.charset,
    )
    if not title:
        issues.append(_make_issue("error", "empty_title", lang, "issue.empty_title"))
    elif len(title) < 30:
        issues.append(_make_issue("warning", "title_too_short", lang, "issue.title_too_short"))
    elif len(title) > 65:
        issues.append(_make_issue("warning", "title_too_long", lang, "issue.title_too_long"))
    if not description:
        issues.append(_make_issue("warning", "empty_description", lang, "issue.empty_description"))
    elif len(description) < 70:
        issues.append(
            _make_issue("info", "description_too_short", lang, "issue.description_too_short")
        )
    elif len(description) > 160:
        issues.append(
            _make_issue("warning", "description_too_long", lang, "issue.description_too_long")
        )
    if not doc.canonical:
        issues.append(_make_issue("info", "no_canonical", lang, "issue.no_canonical"))
    if not (doc.og_title or doc.og_description):
        issues.append(_make_issue("info", "no_open_graph", lang, "issue.no_open_graph"))
    if not doc.html_lang:
        issues.append(_make_issue("info", "no_lang", lang, "issue.no_lang"))
    if doc.robots and "noindex" in doc.robots.lower():
        issues.append(_make_issue("error", "noindex", lang, "issue.noindex"))

    # ── Headings ─────────────────────────────────────────────────────────
    skipped = _detect_skipped_levels(doc.heading_sequence)
    headings = HeadingsInfo(
        h1_count=len(doc.h1),
        h1_texts=doc.h1[:5],
        h2_count=len(doc.h2),
        h2_texts=doc.h2[:10],
        h3_count=len(doc.h3),
        skipped_levels=skipped,
    )
    if len(doc.h1) == 0:
        issues.append(_make_issue("warning", "no_h1", lang, "issue.no_h1"))
    elif len(doc.h1) > 1:
        issues.append(_make_issue("warning", "multiple_h1", lang, "issue.multiple_h1"))
    if skipped:
        issues.append(
            _make_issue(
                "info",
                "skipped_heading_levels",
                lang,
                "issue.skipped_heading_levels",
                fmt={"levels": ", ".join(skipped)},
            )
        )

    # ── Readability ──────────────────────────────────────────────────────
    body_text = doc.body_text
    wc = word_count(body_text)
    sc = sentence_count(body_text)
    avg = (wc / sc) if sc else 0.0
    detected_lang = _detect_language_hint(doc.html_lang) or lang
    readability = Readability(
        word_count=wc,
        sentence_count=sc,
        avg_sentence_length=round(avg, 1),
        detected_language=detected_lang,
    )
    # Heuristic: very short body text on a non-trivial page suggests JS rendering.
    if wc < 50 and len(body_bytes) > 4_000:
        issues.append(
            _make_issue("warning", "javascript_heavy", lang, "issue.javascript_heavy")
        )

    # ── GEO signals ──────────────────────────────────────────────────────
    schema_types = parse_jsonld_types(doc.jsonld_blobs)
    schema_lower = {t.lower() for t in schema_types}
    detection_lang = detected_lang if detected_lang in ("en", "tr", "de", "es", "fr", "it", "pt", "ar") else "en"
    question_headings = [h for h in (*doc.h1, *doc.h2, *doc.h3) if is_question(h, detection_lang)]
    keywords_found: dict[str, int] = {}
    if target_keywords:
        haystack = (title + " " + description + " " + body_text).lower()
        for kw in target_keywords:
            if not kw:
                continue
            keywords_found[kw] = haystack.count(kw.lower())
    geo = GeoSignals(
        has_faq_schema="faqpage" in schema_lower,
        has_question_schema="question" in schema_lower,
        has_howto_schema="howto" in schema_lower,
        has_article_schema="article" in schema_lower or "newsarticle" in schema_lower,
        schema_types=schema_types,
        question_headings=question_headings[:8],
        answers_first_mode=bool(question_headings),
        keywords_found=keywords_found,
    )
    if not schema_types:
        issues.append(_make_issue("info", "no_schema", lang, "issue.no_schema"))

    # ── Performance ──────────────────────────────────────────────────────
    perf = Performance(
        bytes_total=len(body_bytes),
        bytes_html=len(body_bytes),
        response_time_ms=elapsed_ms,
        redirect_count=len(response.history),
        final_url=str(response.url),
        status_code=response.status_code,
    )
    if len(body_bytes) > LARGE_RESPONSE_KB * 1024:
        issues.append(
            _make_issue(
                "info",
                "large_response",
                lang,
                "issue.large_response",
                fmt={"kb": LARGE_RESPONSE_KB},
            )
        )
    if elapsed_ms > SLOW_RESPONSE_MS:
        issues.append(
            _make_issue(
                "info",
                "slow_response",
                lang,
                "issue.slow_response",
                fmt={"ms": elapsed_ms},
            )
        )

    audit = PageAudit(
        url=cleaned,
        final_url=str(response.url),
        meta_tags=meta,
        headings=headings,
        readability=readability,
        geo_signals=geo,
        performance=perf,
        issues=issues,
    )
    return Result(ok=True, data=audit, meta={"final_url": str(response.url)})
