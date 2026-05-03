"""FX provider implementations and dispatch.

Provider chain (preferred order, first that supports the pair wins):
    1. Frankfurter         - ECB-backed; ~30 fiat currencies including EUR/USD/GBP/TRY etc.
    2. exchangerate.host   - wider coverage; free tier available
    3. OpenExchangeRates   - paid; only used when CURRENCYPULSE_OXR_APP_ID env set
    4. TCMB                - Turkish central bank; TRY-anchored only

Each provider exposes the same shape:
    - supports(base, quote, on_date) -> bool
    - rate(base, quote, on_date) -> dict {"value", "on_date"}
    - timeseries(base, quote, start, end) -> list[dict]
    - snapshot(base, symbols) -> {"on_date", "rates": {quote: rate}}
Raises NetworkTimeout / RateLimited / UpstreamError on transport failures, or
ValueError on per-provider unsupported pairs.
"""

import os
from datetime import date as Date
from xml.etree import ElementTree as ET

from .http import (
    NetworkTimeout,
    RateLimited,
    UpstreamError,
    get_json_with_retry,
    get_text_with_retry,
)
from .iso4217 import is_supported

FRANKFURTER_BASE = "https://api.frankfurter.dev/v1"
EXCHANGERATE_HOST_BASE = "https://api.exchangerate.host"
OXR_BASE = "https://openexchangerates.org/api"
TCMB_TODAY = "https://www.tcmb.gov.tr/kurlar/today.xml"
TCMB_HISTORY = "https://www.tcmb.gov.tr/kurlar/{ymd}.xml"  # ymd format YYYY/YYYYMM/YYYYMMDD

_FRANKFURTER_SUPPORTED: frozenset[str] | None = None


def _frankfurter_currencies(client) -> frozenset[str]:
    global _FRANKFURTER_SUPPORTED
    if _FRANKFURTER_SUPPORTED is not None:
        return _FRANKFURTER_SUPPORTED
    try:
        data = get_json_with_retry(client, f"{FRANKFURTER_BASE}/currencies", max_attempts=2)
        _FRANKFURTER_SUPPORTED = frozenset(data.keys())
    except Exception:
        # Conservative fallback based on Frankfurter's published list.
        _FRANKFURTER_SUPPORTED = frozenset(
            {
                "AUD", "BGN", "BRL", "CAD", "CHF", "CNY", "CZK", "DKK", "EUR", "GBP",
                "HKD", "HUF", "IDR", "ILS", "INR", "ISK", "JPY", "KRW", "MXN", "MYR",
                "NOK", "NZD", "PHP", "PLN", "RON", "SEK", "SGD", "THB", "TRY", "USD",
                "ZAR",
            }
        )
    return _FRANKFURTER_SUPPORTED


# ──────────────────────────────────────────────────────────────────────────────
# Frankfurter
# ──────────────────────────────────────────────────────────────────────────────
class FrankfurterProvider:
    name = "frankfurter"

    def __init__(self, client) -> None:
        self.client = client

    def supports(self, base: str, quote: str, on_date: Date | None = None) -> bool:
        cur = _frankfurter_currencies(self.client)
        return base in cur and quote in cur

    def rate(self, base: str, quote: str, on_date: Date | None = None) -> dict:
        path = on_date.isoformat() if on_date else "latest"
        url = f"{FRANKFURTER_BASE}/{path}"
        data = get_json_with_retry(self.client, url, params={"base": base, "symbols": quote})
        rates = data.get("rates") or {}
        if quote not in rates:
            raise ValueError(f"frankfurter: missing rate for {quote}")
        return {
            "value": float(rates[quote]),
            "on_date": Date.fromisoformat(data.get("date") or path),
        }

    def snapshot(self, base: str, symbols: list[str]) -> dict:
        url = f"{FRANKFURTER_BASE}/latest"
        data = get_json_with_retry(
            self.client, url, params={"base": base, "symbols": ",".join(symbols)}
        )
        return {
            "on_date": Date.fromisoformat(data.get("date")),
            "rates": {k: float(v) for k, v in (data.get("rates") or {}).items()},
        }

    def timeseries(self, base: str, quote: str, start: Date, end: Date) -> list[dict]:
        url = f"{FRANKFURTER_BASE}/{start.isoformat()}..{end.isoformat()}"
        data = get_json_with_retry(self.client, url, params={"base": base, "symbols": quote})
        out = []
        for d_str, rates in (data.get("rates") or {}).items():
            if quote in rates:
                out.append({"on_date": Date.fromisoformat(d_str), "rate": float(rates[quote])})
        return sorted(out, key=lambda p: p["on_date"])


# ──────────────────────────────────────────────────────────────────────────────
# exchangerate.host
# ──────────────────────────────────────────────────────────────────────────────
class ExchangerateHostProvider:
    name = "exchangerate_host"

    def __init__(self, client) -> None:
        self.client = client

    def supports(self, base: str, quote: str, on_date: Date | None = None) -> bool:
        # exchangerate.host claims most ISO 4217 codes; we let our list gate it.
        return is_supported(base) and is_supported(quote)

    def rate(self, base: str, quote: str, on_date: Date | None = None) -> dict:
        path = on_date.isoformat() if on_date else "latest"
        url = f"{EXCHANGERATE_HOST_BASE}/{path}"
        data = get_json_with_retry(
            self.client, url, params={"base": base, "symbols": quote}
        )
        rates = data.get("rates") or {}
        if quote not in rates:
            raise ValueError(f"exchangerate.host: missing rate for {quote}")
        return {
            "value": float(rates[quote]),
            "on_date": Date.fromisoformat(data.get("date") or path),
        }

    def snapshot(self, base: str, symbols: list[str]) -> dict:
        url = f"{EXCHANGERATE_HOST_BASE}/latest"
        data = get_json_with_retry(
            self.client, url, params={"base": base, "symbols": ",".join(symbols)}
        )
        return {
            "on_date": Date.fromisoformat(data.get("date") or Date.today().isoformat()),
            "rates": {k: float(v) for k, v in (data.get("rates") or {}).items()},
        }

    def timeseries(self, base: str, quote: str, start: Date, end: Date) -> list[dict]:
        url = f"{EXCHANGERATE_HOST_BASE}/timeseries"
        data = get_json_with_retry(
            self.client,
            url,
            params={
                "base": base,
                "symbols": quote,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
        )
        out = []
        for d_str, rates in (data.get("rates") or {}).items():
            if quote in rates:
                out.append({"on_date": Date.fromisoformat(d_str), "rate": float(rates[quote])})
        return sorted(out, key=lambda p: p["on_date"])


# ──────────────────────────────────────────────────────────────────────────────
# OpenExchangeRates (optional, requires APP_ID)
# ──────────────────────────────────────────────────────────────────────────────
class OXRProvider:
    name = "oxr"

    def __init__(self, client, app_id: str | None) -> None:
        self.client = client
        self.app_id = app_id

    def is_configured(self) -> bool:
        return bool(self.app_id)

    def supports(self, base: str, quote: str, on_date: Date | None = None) -> bool:
        return self.is_configured() and is_supported(base) and is_supported(quote)

    def _fetch(self, path: str, params: dict | None = None) -> dict:
        merged = dict(params or {})
        merged["app_id"] = self.app_id
        return get_json_with_retry(self.client, f"{OXR_BASE}/{path}", params=merged)

    def _convert_via_usd(self, base: str, quote: str, on_date: Date | None) -> dict:
        # OXR free tier requires USD as base; do cross via USD.
        path = (
            f"historical/{on_date.isoformat()}.json" if on_date else "latest.json"
        )
        data = self._fetch(path, {"symbols": ",".join({base, quote})})
        rates = data.get("rates") or {}
        if base not in rates or quote not in rates:
            raise ValueError(f"oxr: missing rate for {base} or {quote}")
        # USD->base = rates[base], USD->quote = rates[quote]; base->quote = quote/base
        value = float(rates[quote]) / float(rates[base])
        ts = data.get("timestamp")
        on = Date.fromtimestamp(ts) if ts else (on_date or Date.today())
        return {"value": value, "on_date": on}

    def rate(self, base: str, quote: str, on_date: Date | None = None) -> dict:
        return self._convert_via_usd(base, quote, on_date)

    def snapshot(self, base: str, symbols: list[str]) -> dict:
        data = self._fetch("latest.json", {"symbols": ",".join({base, *symbols})})
        rates = data.get("rates") or {}
        if base not in rates:
            raise ValueError(f"oxr: missing base rate for {base}")
        usd_to_base = float(rates[base])
        out = {}
        for sym in symbols:
            if sym in rates:
                out[sym] = float(rates[sym]) / usd_to_base
        ts = data.get("timestamp")
        on = Date.fromtimestamp(ts) if ts else Date.today()
        return {"on_date": on, "rates": out}

    def timeseries(self, base: str, quote: str, start: Date, end: Date) -> list[dict]:
        # OXR time-series is per-day; we don't fan out hundreds of calls. Caller falls back.
        raise ValueError("oxr: time-series not implemented (free tier rate-limit)")


# ──────────────────────────────────────────────────────────────────────────────
# TCMB (Turkish Central Bank, TRY-anchored)
# ──────────────────────────────────────────────────────────────────────────────
class TCMBProvider:
    name = "tcmb"

    def __init__(self, client) -> None:
        self.client = client

    def supports(self, base: str, quote: str, on_date: Date | None = None) -> bool:
        return base == "TRY" or quote == "TRY"

    def _fetch_xml(self, on_date: Date | None) -> dict[str, dict[str, float]]:
        if on_date is None:
            url = TCMB_TODAY
        else:
            ymd = on_date.strftime("%Y%m/%d%m%Y")  # https://www.tcmb.gov.tr/kurlar/202310/05102023.xml
            url = f"https://www.tcmb.gov.tr/kurlar/{ymd}.xml"
        text = get_text_with_retry(self.client, url, max_attempts=2)
        root = ET.fromstring(text)
        out: dict[str, dict[str, float]] = {}
        for cur in root.findall("Currency"):
            code = (cur.attrib.get("CurrencyCode") or "").upper()
            if not code:
                continue
            unit = float(cur.findtext("Unit") or "1")
            forex_buy = cur.findtext("ForexBuying") or ""
            forex_sell = cur.findtext("ForexSelling") or ""
            try:
                buy = float(forex_buy) / unit if forex_buy.strip() else None
                sell = float(forex_sell) / unit if forex_sell.strip() else None
            except ValueError:
                continue
            if buy is None and sell is None:
                continue
            mid = (buy + sell) / 2 if (buy and sell) else (buy or sell)
            out[code] = {"buy": buy or 0.0, "sell": sell or 0.0, "mid": mid or 0.0}
        return out

    def rate(self, base: str, quote: str, on_date: Date | None = None) -> dict:
        rates = self._fetch_xml(on_date)
        on = on_date or Date.today()
        if base == "TRY" and quote in rates:
            return {"value": 1.0 / rates[quote]["mid"], "on_date": on}
        if quote == "TRY" and base in rates:
            return {"value": rates[base]["mid"], "on_date": on}
        if base in rates and quote in rates:
            # Cross via TRY mid rates.
            return {"value": rates[base]["mid"] / rates[quote]["mid"], "on_date": on}
        raise ValueError(f"tcmb: missing rate for {base}->{quote}")

    def snapshot(self, base: str, symbols: list[str]) -> dict:
        rates = self._fetch_xml(None)
        on = Date.today()
        out = {}
        if base == "TRY":
            for sym in symbols:
                if sym == "TRY":
                    out["TRY"] = 1.0
                elif sym in rates:
                    out[sym] = 1.0 / rates[sym]["mid"]
        else:
            if base not in rates:
                raise ValueError(f"tcmb: snapshot base {base} unsupported")
            base_to_try = rates[base]["mid"]
            for sym in symbols:
                if sym == "TRY":
                    out["TRY"] = base_to_try
                elif sym in rates:
                    out[sym] = base_to_try / rates[sym]["mid"]
        return {"on_date": on, "rates": out}

    def timeseries(self, base: str, quote: str, start: Date, end: Date) -> list[dict]:
        # TCMB requires per-day fetches; not feasible at scale. Caller falls back.
        raise ValueError("tcmb: time-series not implemented")


# ──────────────────────────────────────────────────────────────────────────────
# Provider registry
# ──────────────────────────────────────────────────────────────────────────────
def build_providers(client, oxr_app_id: str | None = None) -> list:
    return [
        FrankfurterProvider(client),
        ExchangerateHostProvider(client),
        OXRProvider(client, oxr_app_id),
        TCMBProvider(client),
    ]


def env_oxr_app_id() -> str | None:
    return os.getenv("CURRENCYPULSE_OXR_APP_ID") or None


__all__ = [
    "FrankfurterProvider",
    "ExchangerateHostProvider",
    "OXRProvider",
    "TCMBProvider",
    "build_providers",
    "env_oxr_app_id",
    "NetworkTimeout",
    "RateLimited",
    "UpstreamError",
]
