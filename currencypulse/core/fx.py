"""Public FX functions: rate, convert, snapshot, timeseries.

All return Result[T]. Never raise across the public boundary.
"""

import math
import time
from collections.abc import Iterable
from datetime import date as Date

from .http import NetworkTimeout, RateLimited, UpstreamError, build_client
from .i18n import t
from .iso4217 import (
    DEFAULT_SYMBOLS,
    deprecated_replacement,
    is_crypto,
    is_supported,
    normalize_code,
)
from .providers import build_providers, env_oxr_app_id
from .types import (
    Conversion,
    ErrorInfo,
    Rate,
    Result,
    Snapshot,
    SnapshotEntry,
    TimeSeries,
    TimeSeriesPoint,
)

_CACHE_TTL_SECONDS = 300
_cache: dict[tuple, tuple[float, object]] = {}


def _err(
    code: str,
    lang: str,
    en_key: str,
    *,
    fmt: dict | None = None,
    hint_key: str | None = None,
    upstream: str | None = None,
) -> ErrorInfo:
    fmt = fmt or {}
    return ErrorInfo(
        code=code,
        message_en=t(en_key, "en", **fmt),
        message_tr=t(en_key, "tr", **fmt),
        hint=t(hint_key, lang, **fmt) if hint_key else None,
        upstream=upstream,
    )


def _validate_pair(base: str, quote: str, lang: str) -> ErrorInfo | None:
    base_n = normalize_code(base)
    quote_n = normalize_code(quote)
    if not base_n or not quote_n:
        return _err("INVALID_INPUT", lang, "error.invalid_currency", fmt={"code": ""})
    if is_crypto(base_n) or is_crypto(quote_n):
        return _err("UNSUPPORTED", lang, "error.crypto_not_supported")
    for c in (base_n, quote_n):
        if not is_supported(c) and deprecated_replacement(c) is None:
            return _err("INVALID_INPUT", lang, "error.invalid_currency", fmt={"code": c})
    return None


def _resolve_deprecated(code: str) -> tuple[str, str | None]:
    """Return (normalized_code, replacement_used_for_meta_or_None)."""
    n = normalize_code(code)
    if is_supported(n):
        return n, None
    rep = deprecated_replacement(n)
    if rep is not None:
        return rep, n
    return n, None


def _parse_date(raw: str | None, lang: str) -> tuple[Date | None, ErrorInfo | None]:
    if not raw:
        return None, None
    if isinstance(raw, Date):
        return raw, None
    try:
        return Date.fromisoformat(str(raw).strip()), None
    except ValueError:
        return None, _err("INVALID_INPUT", lang, "error.invalid_date")


def _cache_key(*parts: object) -> tuple:
    return parts


def _cache_get(key: tuple):
    item = _cache.get(key)
    if item is None:
        return None
    expires_at, value = item
    if time.time() > expires_at:
        _cache.pop(key, None)
        return None
    return value


def _cache_set(key: tuple, value: object) -> None:
    _cache[key] = (time.time() + _CACHE_TTL_SECONDS, value)


def _try_providers(
    providers: Iterable,
    method_name: str,
    base: str,
    quote: str | None,
    *args,
    **kwargs,
):
    """Run the named method across providers in order. Return (provider, value)."""
    last_exc: Exception | None = None
    for prov in providers:
        if hasattr(prov, "is_configured") and not prov.is_configured():
            continue
        if quote is not None and not prov.supports(base, quote):
            continue
        if quote is None and not prov.supports(base, base):  # snapshot uses base only
            continue
        try:
            value = getattr(prov, method_name)(*args, **kwargs)
            return prov, value
        except (NetworkTimeout, RateLimited, UpstreamError, ValueError) as exc:
            last_exc = exc
            continue
    return None, last_exc


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────
def rate(
    base: str,
    quote: str,
    on: str | Date | None = None,
    *,
    language: str = "en",
    client=None,
) -> Result[Rate]:
    err = _validate_pair(base, quote, language)
    if err:
        return Result(ok=False, error=err)
    base_n, base_dep = _resolve_deprecated(base)
    quote_n, quote_dep = _resolve_deprecated(quote)
    if base_n == quote_n:
        # Same currency - return 1.0 deterministically without hitting the network.
        on_date, derr = _parse_date(on, language)
        if derr:
            return Result(ok=False, error=derr)
        on_date = on_date or Date.today()
        meta: dict = {"source": "identity"}
        if base_dep or quote_dep:
            meta["deprecated"] = [c for c in (base_dep, quote_dep) if c]
        return Result(
            ok=True,
            data=Rate(
                base=base_n, quote=quote_n, value=1.0, on_date=on_date, source="identity"
            ),
            meta=meta,
        )

    on_date, derr = _parse_date(on, language)
    if derr:
        return Result(ok=False, error=derr)

    cache_key = _cache_key("rate", base_n, quote_n, on_date.isoformat() if on_date else "latest")
    cached = _cache_get(cache_key)
    if cached:
        rate_obj, source = cached
        return Result(ok=True, data=rate_obj, meta={"source": source, "cached": True})

    own_client = client is None
    if client is None:
        client = build_client()
    try:
        providers = build_providers(client, env_oxr_app_id())
        prov, value = _try_providers(providers, "rate", base_n, quote_n, base_n, quote_n, on_date)
        if prov is None:
            if isinstance(value, (NetworkTimeout, RateLimited, UpstreamError)):
                return Result(
                    ok=False,
                    error=_err("UPSTREAM_ERROR", language, "error.network", upstream="all"),
                )
            return Result(
                ok=False,
                error=_err(
                    "NOT_FOUND",
                    language,
                    "error.no_provider",
                    fmt={"base": base_n, "quote": quote_n},
                    hint_key="hint.set_oxr_app_id",
                ),
            )
        rate_obj = Rate(
            base=base_n,
            quote=quote_n,
            value=value["value"],
            on_date=value["on_date"],
            source=prov.name,
        )
        _cache_set(cache_key, (rate_obj, prov.name))
        meta: dict = {"source": prov.name}
        if base_dep or quote_dep:
            meta["deprecated"] = [c for c in (base_dep, quote_dep) if c]
        return Result(ok=True, data=rate_obj, meta=meta)
    finally:
        if own_client:
            client.close()


def convert(
    amount: float,
    base: str,
    quote: str,
    on: str | Date | None = None,
    *,
    language: str = "en",
    client=None,
) -> Result[Conversion]:
    if amount is None or not isinstance(amount, (int, float)) or math.isnan(float(amount)):
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.invalid_amount"))
    if float(amount) < 0 or math.isinf(float(amount)):
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.invalid_amount"))

    rate_result = rate(base, quote, on=on, language=language, client=client)
    if not rate_result.ok or rate_result.data is None:
        return Result(ok=False, error=rate_result.error, meta=rate_result.meta)
    r = rate_result.data
    return Result(
        ok=True,
        data=Conversion(
            base=r.base,
            quote=r.quote,
            amount=float(amount),
            rate=r.value,
            converted=float(amount) * r.value,
            on_date=r.on_date,
            source=r.source,
        ),
        meta=rate_result.meta,
    )


def snapshot(
    base: str,
    symbols: list[str] | None = None,
    *,
    language: str = "en",
    client=None,
) -> Result[Snapshot]:
    base_n = normalize_code(base)
    if not is_supported(base_n) and deprecated_replacement(base_n) is None:
        return Result(
            ok=False,
            error=_err("INVALID_INPUT", language, "error.invalid_currency", fmt={"code": base_n}),
        )
    base_n, base_dep = _resolve_deprecated(base_n)
    requested = [normalize_code(s) for s in (symbols or DEFAULT_SYMBOLS)]
    requested = [s for s in requested if s and is_supported(s)]
    if not requested:
        return Result(
            ok=False,
            error=_err("INVALID_INPUT", language, "error.invalid_currency", fmt={"code": ""}),
        )

    own_client = client is None
    if client is None:
        client = build_client()
    try:
        providers = build_providers(client, env_oxr_app_id())
        last_exc: Exception | None = None
        for prov in providers:
            if hasattr(prov, "is_configured") and not prov.is_configured():
                continue
            try:
                payload = prov.snapshot(base_n, requested)
            except (NetworkTimeout, RateLimited, UpstreamError, ValueError) as exc:
                last_exc = exc
                continue
            entries = [
                SnapshotEntry(quote=q, rate=v) for q, v in sorted(payload.get("rates", {}).items())
            ]
            if not entries:
                last_exc = ValueError("provider returned empty snapshot")
                continue
            snap = Snapshot(
                base=base_n,
                on_date=payload.get("on_date") or Date.today(),
                rates=entries,
                source=prov.name,
            )
            meta: dict = {"source": prov.name}
            if base_dep:
                meta["deprecated"] = [base_dep]
            return Result(ok=True, data=snap, meta=meta)
        if isinstance(last_exc, (NetworkTimeout, RateLimited, UpstreamError)):
            return Result(
                ok=False,
                error=_err("UPSTREAM_ERROR", language, "error.network", upstream="all"),
            )
        return Result(
            ok=False,
            error=_err(
                "NOT_FOUND",
                language,
                "error.no_provider",
                fmt={"base": base_n, "quote": ",".join(requested[:3]) + "..."},
            ),
        )
    finally:
        if own_client:
            client.close()


def timeseries(
    base: str,
    quote: str,
    start: str | Date,
    end: str | Date,
    *,
    language: str = "en",
    client=None,
) -> Result[TimeSeries]:
    err = _validate_pair(base, quote, language)
    if err:
        return Result(ok=False, error=err)
    base_n, _ = _resolve_deprecated(base)
    quote_n, _ = _resolve_deprecated(quote)
    if base_n == quote_n:
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.same_currency"))

    start_d, derr = _parse_date(start, language)
    if derr or start_d is None:
        return Result(ok=False, error=derr or _err("INVALID_INPUT", language, "error.invalid_date"))
    end_d, derr = _parse_date(end, language)
    if derr or end_d is None:
        return Result(ok=False, error=derr or _err("INVALID_INPUT", language, "error.invalid_date"))
    if start_d > end_d:
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.start_after_end"))
    if (end_d - start_d).days > 366:
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.range_too_large"))

    own_client = client is None
    if client is None:
        client = build_client()
    try:
        providers = build_providers(client, env_oxr_app_id())
        last_exc: Exception | None = None
        for prov in providers:
            if hasattr(prov, "is_configured") and not prov.is_configured():
                continue
            if not prov.supports(base_n, quote_n):
                continue
            try:
                points = prov.timeseries(base_n, quote_n, start_d, end_d)
            except (NetworkTimeout, RateLimited, UpstreamError, ValueError) as exc:
                last_exc = exc
                continue
            if not points:
                last_exc = ValueError("provider returned no points")
                continue
            ts = TimeSeries(
                base=base_n,
                quote=quote_n,
                start=start_d,
                end=end_d,
                points=[TimeSeriesPoint(on_date=p["on_date"], rate=p["rate"]) for p in points],
                source=prov.name,
            )
            return Result(ok=True, data=ts, meta={"source": prov.name})
        if isinstance(last_exc, (NetworkTimeout, RateLimited, UpstreamError)):
            return Result(
                ok=False,
                error=_err("UPSTREAM_ERROR", language, "error.network", upstream="all"),
            )
        return Result(
            ok=False,
            error=_err(
                "NOT_FOUND",
                language,
                "error.no_provider",
                fmt={"base": base_n, "quote": quote_n},
            ),
        )
    finally:
        if own_client:
            client.close()
