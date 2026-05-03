"""Frozen ISO 4217 currency codes used for input validation.

Generated from the ISO 4217 active-codes list (subset of ~160 fiat currencies).
Crypto codes (BTC/ETH/etc.) are intentionally excluded - this tool returns
UNSUPPORTED for them rather than guessing.
"""

from typing import Final

CURRENCIES: Final[frozenset[str]] = frozenset(
    {
        "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN",
        "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BRL",
        "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHF", "CLP", "CNY",
        "COP", "CRC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP",
        "ERN", "ETB", "EUR", "FJD", "FKP", "GBP", "GEL", "GHS", "GIP", "GMD",
        "GNF", "GTQ", "GYD", "HKD", "HNL", "HTG", "HUF", "IDR", "ILS", "INR",
        "IQD", "IRR", "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF",
        "KPW", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL",
        "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR",
        "MVR", "MWK", "MXN", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR",
        "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR",
        "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD",
        "SHP", "SLE", "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB",
        "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX",
        "USD", "UYU", "UZS", "VES", "VND", "VUV", "WST", "XAF", "XCD", "XOF",
        "XPF", "YER", "ZAR", "ZMW",
    }
)

# Common deprecated codes mapped to their successors. Returned via meta.note.
DEPRECATED_REPLACEMENTS: Final[dict[str, str]] = {
    "HRK": "EUR",
    "EEK": "EUR",
    "LTL": "EUR",
    "LVL": "EUR",
    "VEF": "VES",
    "MRO": "MRU",
    "STD": "STN",
    "BYR": "BYN",
    "CYP": "EUR",
    "MTL": "EUR",
    "SKK": "EUR",
    "SIT": "EUR",
    "TRL": "TRY",
}

CRYPTO_CODES: Final[frozenset[str]] = frozenset(
    {"BTC", "ETH", "USDT", "USDC", "BNB", "XRP", "ADA", "SOL", "DOGE", "TRX", "DOT"}
)

# Sensible default symbols list - broader than the legacy Western-only set,
# covers Asia, LATAM, MENA, Africa.
DEFAULT_SYMBOLS: Final[tuple[str, ...]] = (
    "USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD",
    "CNY", "INR", "BRL", "MXN", "ZAR", "AED", "SAR",
    "TRY", "RUB", "KRW", "SGD", "HKD", "THB",
)


def normalize_code(code: str) -> str:
    return (code or "").strip().upper()


def is_supported(code: str) -> bool:
    return normalize_code(code) in CURRENCIES


def is_crypto(code: str) -> bool:
    return normalize_code(code) in CRYPTO_CODES


def deprecated_replacement(code: str) -> str | None:
    return DEPRECATED_REPLACEMENTS.get(normalize_code(code))
