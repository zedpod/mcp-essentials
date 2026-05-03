"""geocode(query) — Open-Meteo geocoding without country bias or hardcoded fallbacks."""

from .http import (
    NetworkTimeout,
    RateLimited,
    UpstreamError,
    build_client,
    get_json_with_retry,
)
from .i18n import normalize_lang, t
from .types import (
    ErrorInfo,
    GeocodeCandidate,
    GeocodeResult,
    Result,
)

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def _err(code: str, lang: str, en_key: str, *, hint_key: str | None = None,
         fmt: dict | None = None) -> ErrorInfo:
    fmt = fmt or {}
    return ErrorInfo(
        code=code,
        message_en=t(en_key, "en", **fmt),
        message_tr=t(en_key, "tr", **fmt),
        hint=t(hint_key, lang, **fmt) if hint_key else None,
    )


def _to_candidate(raw: dict) -> GeocodeCandidate:
    return GeocodeCandidate(
        name=raw.get("name") or "",
        country_code=raw.get("country_code"),
        country=raw.get("country"),
        admin1=raw.get("admin1"),
        admin2=raw.get("admin2"),
        latitude=float(raw.get("latitude", 0.0)),
        longitude=float(raw.get("longitude", 0.0)),
        timezone=raw.get("timezone"),
        population=raw.get("population"),
        elevation=raw.get("elevation"),
        score=float(raw.get("ranking_score") or 0.0),
    )


def geocode(
    query: str,
    country: str | None = None,
    max_results: int = 5,
    *,
    language: str = "en",
    client=None,
) -> Result[GeocodeResult]:
    lang = normalize_lang(language)
    if not query or not query.strip():
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.empty_query"))

    own_client = client is None
    if client is None:
        client = build_client()
    params = {
        "name": query.strip(),
        "count": str(max(1, min(max_results, 25))),
        "language": lang,
        "format": "json",
    }
    if country and len(country) == 2:
        params["country_code"] = country.upper()

    try:
        try:
            payload = get_json_with_retry(client, GEOCODING_URL, params=params)
        except (NetworkTimeout, RateLimited, UpstreamError):
            return Result(
                ok=False,
                error=_err("UPSTREAM_ERROR", lang, "error.network"),
                meta={"upstream": "open-meteo"},
            )

        results = payload.get("results") or []
        if not results:
            return Result(
                ok=False,
                error=_err("NOT_FOUND", lang, "error.no_results"),
                meta={"query": query},
            )

        candidates = [_to_candidate(r) for r in results]
        # Open-Meteo's ranking_score is monotonic — keep its order; no country bias.
        return Result(
            ok=True,
            data=GeocodeResult(query=query, candidates=candidates),
            meta={"count": len(candidates)},
        )
    finally:
        if own_client:
            client.close()
