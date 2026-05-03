"""forecast(lat, lon) and forecast_by_query(query) — Open-Meteo daily forecast."""

from datetime import date as Date
from datetime import timedelta

from .geocode import geocode
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
    ForecastDay,
    ForecastResult,
    Result,
)
from .wmo import label as wmo_label

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def _err(code: str, lang: str, en_key: str, *, hint_key: str | None = None) -> ErrorInfo:
    return ErrorInfo(
        code=code,
        message_en=t(en_key, "en"),
        message_tr=t(en_key, "tr"),
        hint=t(hint_key, lang) if hint_key else None,
    )


def _parse_date(value, lang: str) -> tuple[Date | None, ErrorInfo | None]:
    if value is None or value == "":
        return None, None
    if isinstance(value, Date):
        return value, None
    try:
        return Date.fromisoformat(str(value).strip()), None
    except ValueError:
        return None, _err("INVALID_INPUT", lang, "error.invalid_date")


def forecast(
    latitude: float,
    longitude: float,
    *,
    start_date: str | Date | None = None,
    days: int = 3,
    units: str = "metric",
    language: str = "en",
    client=None,
) -> Result[ForecastResult]:
    lang = normalize_lang(language)

    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_coords"))
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_coords"))
    if days < 1 or days > 16:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_days"))
    if units not in ("metric", "imperial"):
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_units"))

    start, derr = _parse_date(start_date, lang)
    if derr:
        return Result(ok=False, error=derr)

    own_client = client is None
    if client is None:
        client = build_client()
    daily = (
        "weather_code,temperature_2m_max,temperature_2m_min,"
        "precipitation_sum,precipitation_probability_max,wind_speed_10m_max,"
        "uv_index_max,sunrise,sunset"
    )
    params = {
        "latitude": str(lat),
        "longitude": str(lon),
        "daily": daily,
        "timezone": "auto",
        "temperature_unit": "fahrenheit" if units == "imperial" else "celsius",
        "wind_speed_unit": "mph" if units == "imperial" else "kmh",
        "precipitation_unit": "inch" if units == "imperial" else "mm",
    }
    if start:
        params["start_date"] = start.isoformat()
        params["end_date"] = (start + timedelta(days=days - 1)).isoformat()
    else:
        params["forecast_days"] = str(days)

    try:
        try:
            payload = get_json_with_retry(client, FORECAST_URL, params=params)
        except (NetworkTimeout, RateLimited, UpstreamError):
            return Result(
                ok=False,
                error=_err("UPSTREAM_ERROR", lang, "error.network"),
                meta={"upstream": "open-meteo"},
            )

        d = payload.get("daily") or {}
        dates = d.get("time") or []
        codes = d.get("weather_code") or []
        tmax = d.get("temperature_2m_max") or []
        tmin = d.get("temperature_2m_min") or []
        precip = d.get("precipitation_sum") or []
        precip_prob = d.get("precipitation_probability_max") or []
        wind = d.get("wind_speed_10m_max") or []
        uv = d.get("uv_index_max") or []
        sunrise = d.get("sunrise") or []
        sunset = d.get("sunset") or []

        out_days: list[ForecastDay] = []
        for i, ds in enumerate(dates):
            try:
                dt = Date.fromisoformat(ds)
            except ValueError:
                continue
            code = codes[i] if i < len(codes) else None
            out_days.append(
                ForecastDay(
                    date=dt,
                    weather_code=code,
                    weather_label=wmo_label(code, lang),
                    max_temp=tmax[i] if i < len(tmax) else None,
                    min_temp=tmin[i] if i < len(tmin) else None,
                    precipitation=precip[i] if i < len(precip) else None,
                    precipitation_probability=(
                        int(precip_prob[i]) if i < len(precip_prob) and precip_prob[i] is not None else None
                    ),
                    wind_speed=wind[i] if i < len(wind) else None,
                    humidity=None,
                    sunrise=sunrise[i] if i < len(sunrise) else None,
                    sunset=sunset[i] if i < len(sunset) else None,
                    uv_index=uv[i] if i < len(uv) else None,
                )
            )

        result = ForecastResult(
            latitude=lat,
            longitude=lon,
            timezone=payload.get("timezone"),
            units="metric" if units == "metric" else "imperial",
            days=out_days,
        )
        return Result(ok=True, data=result, meta={"count": len(out_days)})
    finally:
        if own_client:
            client.close()


def forecast_by_query(
    query: str,
    country: str | None = None,
    *,
    start_date: str | Date | None = None,
    days: int = 3,
    units: str = "metric",
    language: str = "en",
    client=None,
) -> Result[ForecastResult]:
    """Convenience: geocode → top candidate → forecast.

    Surfaces a `meta.disambiguation_warning` flag when multiple high-score
    matches exist so the LLM knows the choice was non-deterministic.
    """
    lang = normalize_lang(language)
    g = geocode(query, country=country, max_results=5, language=lang, client=client)
    if not g.ok or g.data is None:
        return Result(ok=False, error=g.error, meta=g.meta)

    candidates = g.data.candidates
    if not candidates:
        return Result(
            ok=False,
            error=_err("NOT_FOUND", lang, "error.no_results", hint_key="hint.use_coords"),
        )
    top = candidates[0]
    disambiguation = (
        len(candidates) > 1
        and abs((candidates[1].score or 0) - (top.score or 0)) < 1.0
    )

    res = forecast(
        top.latitude,
        top.longitude,
        start_date=start_date,
        days=days,
        units=units,
        language=lang,
        client=client,
    )
    if res.ok and res.data is not None:
        res.data.place_name = top.name
        res.data.country_code = top.country_code
        meta = dict(res.meta)
        meta["matched"] = {
            "name": top.name,
            "country": top.country_code,
            "score": top.score,
        }
        if disambiguation:
            meta["disambiguation_warning"] = True
            meta["hint"] = t("hint.use_coords", lang)
        return Result(ok=True, data=res.data, meta=meta)
    return res
