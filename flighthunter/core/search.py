"""Public search_flights function — wraps SerpAPI Google Flights engine."""

import os
import re
from collections.abc import Iterable
from datetime import date as Date

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
    FlightLeg,
    FlightOption,
    FlightSearch,
    PriceInsight,
    Result,
)

SERPAPI_ENDPOINT = "https://serpapi.com/search"
IATA_RE = re.compile(r"^[A-Za-z]{3}$")

# SerpAPI travel_class mapping: 1=economy, 2=premium_economy, 3=business, 4=first.
_CABIN_TO_CODE = {"economy": "1", "premium_economy": "2", "business": "3", "first": "4"}
_TRIP_TO_CODE = {"round_trip": "1", "one_way": "2", "multi_city": "3"}


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


def _flatten_options(
    group: Iterable[dict], category: str, fallback_currency: str | None = None
) -> list[FlightOption]:
    out: list[FlightOption] = []
    for item in group or []:
        flights = item.get("flights") or []
        legs = []
        for f in flights:
            legs.append(
                FlightLeg(
                    airline=f.get("airline"),
                    flight_number=f.get("flight_number"),
                    departure_airport=(f.get("departure_airport") or {}).get("id"),
                    arrival_airport=(f.get("arrival_airport") or {}).get("id"),
                    departure_time=(f.get("departure_airport") or {}).get("time"),
                    arrival_time=(f.get("arrival_airport") or {}).get("time"),
                    duration_minutes=f.get("duration"),
                    travel_class=f.get("travel_class"),
                    aircraft=f.get("airplane"),
                )
            )
        layovers = item.get("layovers") or []
        layover_airports = [layover.get("id") for layover in layovers if layover.get("id")]
        out.append(
            FlightOption(
                price=item.get("price"),
                currency=item.get("price_currency") or item.get("currency") or fallback_currency,
                total_duration_minutes=item.get("total_duration"),
                stops=len(layovers),
                layover_airports=[la for la in layover_airports if la],
                legs=legs,
                booking_token=item.get("booking_token"),
                type=category,
            )
        )
    return out


def search_flights(
    origin: str,
    destination: str,
    departure_date: str | Date,
    return_date: str | Date | None = None,
    *,
    cabin_class: str = "economy",
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    currency: str = "USD",
    language: str = "en",
    api_key: str | None = None,
    client=None,
) -> Result[FlightSearch]:
    lang = normalize_lang(language)

    # ── Inputs ────────────────────────────────────────────────────────────
    if not origin or not IATA_RE.match(origin or "") or not destination or not IATA_RE.match(destination or ""):
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_iata"))
    origin = origin.upper()
    destination = destination.upper()
    if origin == destination:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.same_origin_destination"))
    cabin = (cabin_class or "economy").lower()
    if cabin not in _CABIN_TO_CODE:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_cabin"))
    if adults < 1 or adults + children + infants > 9 or children > adults:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_passengers"))

    departure, derr = _parse_date(departure_date, lang)
    if derr or departure is None:
        return Result(ok=False, error=derr or _err("INVALID_INPUT", lang, "error.invalid_date"))
    return_d, derr = _parse_date(return_date, lang)
    if derr:
        return Result(ok=False, error=derr)
    if return_d and return_d < departure:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.return_before_departure"))

    trip_type = "round_trip" if return_d else "one_way"

    key = api_key or os.getenv("FLIGHTHUNTER_SERPAPI_KEY") or os.getenv("SERPAPI_API_KEY")
    if not key:
        return Result(
            ok=False,
            error=_err("MISSING_API_KEY", lang, "error.missing_api_key", hint_key="hint.set_key"),
        )

    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": departure.isoformat(),
        "type": _TRIP_TO_CODE[trip_type],
        "travel_class": _CABIN_TO_CODE[cabin],
        "adults": str(adults),
        "currency": currency.upper(),
        "hl": lang,
        "gl": "us" if lang == "en" else lang,
        "api_key": key,
    }
    if children:
        params["children"] = str(children)
    if infants:
        params["infants_in_seat"] = str(infants)
    if return_d:
        params["return_date"] = return_d.isoformat()

    own_client = client is None
    if client is None:
        client = build_client()
    try:
        try:
            payload = get_json_with_retry(client, SERPAPI_ENDPOINT, params=params)
        except (NetworkTimeout, RateLimited, UpstreamError) as exc:
            return Result(
                ok=False,
                error=_err(
                    "RATE_LIMITED" if isinstance(exc, RateLimited) else "UPSTREAM_ERROR",
                    lang,
                    "error.upstream",
                    hint_key="hint.try_other_dates",
                ),
                meta={"upstream": "serpapi"},
            )

        if "error" in payload:
            return Result(
                ok=False,
                error=_err(
                    "UPSTREAM_ERROR",
                    lang,
                    "error.upstream",
                    hint_key="hint.try_other_dates",
                ),
                meta={"serpapi_error": str(payload.get("error"))[:200]},
            )

        best = payload.get("best_flights") or []
        other = payload.get("other_flights") or []
        currency_code = (payload.get("search_parameters") or {}).get("currency") or currency.upper()
        options = (
            _flatten_options(best, "best", fallback_currency=currency_code)
            + _flatten_options(other, "other", fallback_currency=currency_code)
        )

        insight_raw = payload.get("price_insights") or {}
        typical = insight_raw.get("typical_price_range") or [None, None]
        insight = PriceInsight(
            lowest=insight_raw.get("lowest_price"),
            typical_low=typical[0] if isinstance(typical, list) and len(typical) >= 1 else None,
            typical_high=typical[1] if isinstance(typical, list) and len(typical) >= 2 else None,
            price_level=insight_raw.get("price_level"),
        )

        search = FlightSearch(
            origin=origin,
            destination=destination,
            departure_date=departure,
            return_date=return_d,
            trip_type=trip_type,  # type: ignore[arg-type]
            cabin_class=cabin,  # type: ignore[arg-type]
            adults=adults,
            children=children,
            infants=infants,
            currency=currency.upper(),
            options=options,
            price_insight=insight,
            search_url=(payload.get("search_metadata") or {}).get("google_flights_url"),
        )
        return Result(
            ok=True,
            data=search,
            meta={
                "option_count": len(options),
                "best_count": len(best),
                "credits_left": (payload.get("search_metadata") or {}).get("credits_left"),
            },
        )
    finally:
        if own_client:
            client.close()
