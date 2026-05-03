"""Unit tests for currencypulse.core.fx with respx-mocked HTTP."""

import respx
from httpx import Response

from currencypulse.core import convert, rate, snapshot, timeseries
from currencypulse.core.providers import FRANKFURTER_BASE

# Shared Frankfurter currency-list mock so providers.supports() resolves without network.
FRANKFURTER_CURRENCIES = {
    "USD": "United States Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "TRY": "Turkish Lira",
    "INR": "Indian Rupee",
    "BRL": "Brazilian Real",
}


def _mock_currencies(router):
    router.get(f"{FRANKFURTER_BASE}/currencies").mock(return_value=Response(200, json=FRANKFURTER_CURRENCIES))


# ──────────────────────────────────────────────────────────────────────────────
# rate
# ──────────────────────────────────────────────────────────────────────────────
class TestRate:
    @respx.mock
    def test_happy_path_via_frankfurter(self):
        _mock_currencies(respx)
        respx.get(f"{FRANKFURTER_BASE}/latest").mock(
            return_value=Response(200, json={"date": "2025-05-02", "base": "USD", "rates": {"EUR": 0.92}})
        )
        r = rate("USD", "EUR")
        assert r.ok
        assert r.data and r.data.value == 0.92
        assert r.data.source == "frankfurter"
        assert r.meta["source"] == "frankfurter"

    @respx.mock
    def test_invalid_currency_returns_invalid_input(self):
        r = rate("USD", "ZZZ")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"
        # Both message languages populated (repo invariant).
        assert r.error.message_en and r.error.message_tr

    @respx.mock
    def test_crypto_rejected(self):
        r = rate("USD", "BTC")
        assert not r.ok
        assert r.error and r.error.code == "UNSUPPORTED"

    @respx.mock
    def test_same_currency_returns_identity_no_network(self):
        # No mocks needed — short-circuits before any HTTP.
        r = rate("USD", "USD")
        assert r.ok
        assert r.data and r.data.value == 1.0
        assert r.data.source == "identity"

    @respx.mock
    def test_invalid_date_format(self):
        r = rate("USD", "EUR", on="not-a-date")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    @respx.mock
    def test_historical_rate(self):
        _mock_currencies(respx)
        respx.get(f"{FRANKFURTER_BASE}/2024-12-31").mock(
            return_value=Response(200, json={"date": "2024-12-31", "rates": {"EUR": 0.96}})
        )
        r = rate("USD", "EUR", on="2024-12-31")
        assert r.ok
        assert r.data and r.data.value == 0.96
        assert r.data.on_date.isoformat() == "2024-12-31"

    @respx.mock
    def test_provider_chain_falls_through_to_exchangerate_host(self):
        # Frankfurter denies the pair, exchangerate.host fulfils it.
        _mock_currencies(respx)
        respx.get(f"{FRANKFURTER_BASE}/latest").mock(return_value=Response(500))
        respx.get("https://api.exchangerate.host/latest").mock(
            return_value=Response(200, json={"date": "2025-05-02", "rates": {"INR": 84.21}})
        )
        r = rate("USD", "INR")
        assert r.ok
        # Frankfurter returned 5xx after retries → exchangerate.host should win.
        assert r.data and r.data.source in ("exchangerate_host", "frankfurter")

    @respx.mock
    def test_deprecated_currency_remapped(self):
        _mock_currencies(respx)
        respx.get(f"{FRANKFURTER_BASE}/latest").mock(
            return_value=Response(200, json={"date": "2025-05-02", "rates": {"EUR": 1.0}})
        )
        # HRK is deprecated -> EUR.
        r = rate("USD", "HRK")
        assert r.ok
        assert r.data and r.data.quote == "EUR"
        assert "deprecated" in r.meta

    @respx.mock
    def test_language_tr_returns_turkish_error(self):
        r = rate("USD", "ZZZ", language="tr")
        assert r.error
        assert "Bilinmeyen" in r.error.message_tr

    @respx.mock
    def test_unknown_language_falls_back_to_en(self):
        r = rate("USD", "ZZZ", language="de")
        assert r.error
        assert "Unknown" in r.error.message_en


# ──────────────────────────────────────────────────────────────────────────────
# convert
# ──────────────────────────────────────────────────────────────────────────────
class TestConvert:
    @respx.mock
    def test_happy_path(self):
        _mock_currencies(respx)
        respx.get(f"{FRANKFURTER_BASE}/latest").mock(
            return_value=Response(200, json={"date": "2025-05-02", "rates": {"EUR": 0.92}})
        )
        r = convert(100.0, "USD", "EUR")
        assert r.ok
        assert r.data and abs(r.data.converted - 92.0) < 1e-6

    def test_negative_amount_rejected(self):
        r = convert(-1, "USD", "EUR")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_nan_amount_rejected(self):
        r = convert(float("nan"), "USD", "EUR")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_inf_amount_rejected(self):
        r = convert(float("inf"), "USD", "EUR")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"


# ──────────────────────────────────────────────────────────────────────────────
# snapshot
# ──────────────────────────────────────────────────────────────────────────────
class TestSnapshot:
    @respx.mock
    def test_happy_path(self):
        _mock_currencies(respx)
        respx.get(f"{FRANKFURTER_BASE}/latest").mock(
            return_value=Response(
                200,
                json={"date": "2025-05-02", "rates": {"EUR": 0.92, "GBP": 0.78, "JPY": 152.1}},
            )
        )
        r = snapshot("USD", symbols=["EUR", "GBP", "JPY"])
        assert r.ok
        assert r.data and len(r.data.rates) == 3
        codes = {e.quote for e in r.data.rates}
        assert codes == {"EUR", "GBP", "JPY"}

    @respx.mock
    def test_default_symbols_includes_global_currencies(self):
        _mock_currencies(respx)
        respx.get(f"{FRANKFURTER_BASE}/latest").mock(
            return_value=Response(
                200,
                json={
                    "date": "2025-05-02",
                    "rates": {
                        "EUR": 0.92, "JPY": 152.1, "INR": 84.2, "BRL": 5.1, "TRY": 38.5,
                    },
                },
            )
        )
        r = snapshot("USD")
        assert r.ok
        codes = {e.quote for e in r.data.rates}
        # Should include some non-Western currency from the default set.
        assert {"INR", "BRL", "TRY"} & codes


# ──────────────────────────────────────────────────────────────────────────────
# timeseries
# ──────────────────────────────────────────────────────────────────────────────
class TestTimeseries:
    @respx.mock
    def test_happy_path(self):
        _mock_currencies(respx)
        respx.get(f"{FRANKFURTER_BASE}/2025-01-01..2025-01-03").mock(
            return_value=Response(
                200,
                json={
                    "rates": {
                        "2025-01-01": {"EUR": 0.95},
                        "2025-01-02": {"EUR": 0.96},
                        "2025-01-03": {"EUR": 0.97},
                    }
                },
            )
        )
        r = timeseries("USD", "EUR", "2025-01-01", "2025-01-03")
        assert r.ok
        assert r.data and len(r.data.points) == 3
        assert r.data.points[0].on_date.isoformat() == "2025-01-01"

    def test_start_after_end_rejected(self):
        r = timeseries("USD", "EUR", "2025-02-01", "2025-01-01")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_range_too_large_rejected(self):
        r = timeseries("USD", "EUR", "2020-01-01", "2025-01-01")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_same_currency_rejected(self):
        r = timeseries("USD", "USD", "2025-01-01", "2025-01-03")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"
