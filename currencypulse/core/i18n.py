"""Per-tool string table for currencypulse."""

from typing import Final

STRINGS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "title.rate": "Rate",
        "title.convert": "Conversion",
        "title.snapshot": "FX Snapshot",
        "title.timeseries": "Time Series",
        "label.base": "Base",
        "label.quote": "Quote",
        "label.amount": "Amount",
        "label.rate": "Rate",
        "label.converted": "Converted",
        "label.on_date": "Date",
        "label.source": "Source",
        "label.no_data": "No data points.",
        "error.invalid_currency": "Unknown currency code: {code}.",
        "error.same_currency": "Base and quote currencies are the same.",
        "error.crypto_not_supported": "Cryptocurrency codes are not supported by this tool.",
        "error.no_provider": "No provider could fulfil the request for {base}/{quote}.",
        "error.invalid_amount": "Amount must be a finite, non-negative number.",
        "error.invalid_date": "Invalid date. Use YYYY-MM-DD or leave blank for the latest.",
        "error.start_after_end": "start date is after end date.",
        "error.range_too_large": "Date range exceeds 366 days.",
        "error.network": "Could not reach any FX provider.",
        "hint.try_different_pair": "Try a major pair (USD, EUR, GBP, JPY) and check the date.",
        "hint.set_oxr_key": "Set FLIGHTHUNTER_OXR_APP_ID for broader currency support.",  # cross-tool fallback hint not used
        "hint.set_oxr_app_id": "Set CURRENCYPULSE_OXR_APP_ID env var for OXR fallback coverage.",
        "note.rate": "Rates are indicative; do not use as a settlement quote.",
    },
    "tr": {
        "title.rate": "Kur",
        "title.convert": "Dönüşüm",
        "title.snapshot": "Kur Tablosu",
        "title.timeseries": "Zaman Serisi",
        "label.base": "Baz",
        "label.quote": "Karşı",
        "label.amount": "Miktar",
        "label.rate": "Kur",
        "label.converted": "Dönüşmüş",
        "label.on_date": "Tarih",
        "label.source": "Kaynak",
        "label.no_data": "Veri noktası yok.",
        "error.invalid_currency": "Bilinmeyen para kodu: {code}.",
        "error.same_currency": "Baz ve karşı para aynı.",
        "error.crypto_not_supported": "Kripto kodları bu araçta desteklenmiyor.",
        "error.no_provider": "{base}/{quote} için hiçbir sağlayıcı veri sunamadı.",
        "error.invalid_amount": "Miktar sonlu ve negatif olmayan bir sayı olmalı.",
        "error.invalid_date": "Geçersiz tarih. YYYY-MM-DD biçimi kullanın veya boş bırakın.",
        "error.start_after_end": "Başlangıç tarihi bitiş tarihinden büyük.",
        "error.range_too_large": "Tarih aralığı 366 günü aşıyor.",
        "error.network": "Hiçbir FX sağlayıcısına ulaşılamadı.",
        "hint.try_different_pair": "Ana paritelere (USD, EUR, GBP, JPY) ve tarihe bakın.",
        "hint.set_oxr_key": "Geniş kapsama için FLIGHTHUNTER_OXR_APP_ID girin.",
        "hint.set_oxr_app_id": "OXR fallback kapsaması için CURRENCYPULSE_OXR_APP_ID env değişkenini ayarlayın.",
        "note.rate": "Kurlar gösterge niteliğindedir; takas işlemine esas alınamaz.",
    },
}

SUPPORTED: Final[tuple[str, ...]] = ("en", "tr")
DEFAULT: Final[str] = "en"


def normalize_lang(lang: str | None) -> str:
    if not lang:
        return DEFAULT
    base = lang.lower().split("-")[0]
    return base if base in SUPPORTED else DEFAULT


def t(key: str, lang: str = DEFAULT, **kwargs: object) -> str:
    lang = normalize_lang(lang)
    table = STRINGS.get(lang) or STRINGS[DEFAULT]
    template = table.get(key) or STRINGS[DEFAULT].get(key) or key
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template
