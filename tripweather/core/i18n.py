"""tripweather i18n strings."""

from typing import Final

STRINGS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "title.geocode": "Locations matching “{query}”",
        "title.forecast": "Forecast",
        "label.coords": "Coordinates",
        "label.timezone": "Timezone",
        "label.units": "Units",
        "label.population": "Population",
        "label.elevation": "Elevation",
        "label.score": "Score",
        "label.no_candidates": "No matching locations.",
        "label.no_days": "No forecast days returned.",
        "label.disambiguation": (
            "Multiple equally-confident matches; passing latitude/longitude is "
            "the deterministic fix."
        ),
        "header.day": "Day",
        "header.weather": "Weather",
        "header.temp": "Temp (°{unit})",
        "header.precip": "Precip",
        "header.wind": "Wind",
        "header.humidity": "Humidity",
        "error.empty_query": "Query cannot be empty.",
        "error.invalid_coords": (
            "Latitude must be in [-90, 90], longitude in [-180, 180]."
        ),
        "error.invalid_days": "days must be 1-16.",
        "error.invalid_units": "units must be 'metric' or 'imperial'.",
        "error.invalid_date": "start_date must be YYYY-MM-DD.",
        "error.network": "Open-Meteo did not respond.",
        "error.no_results": "Geocoding returned no results.",
        "hint.use_coords": "Pass `latitude` and `longitude` directly to skip geocoding.",
        "note.forecast": "Forecast data: Open-Meteo (CC-BY 4.0).",
    },
    "tr": {
        "title.geocode": "“{query}” için konumlar",
        "title.forecast": "Tahmin",
        "label.coords": "Koordinatlar",
        "label.timezone": "Saat dilimi",
        "label.units": "Birim",
        "label.population": "Nüfus",
        "label.elevation": "Rakım",
        "label.score": "Skor",
        "label.no_candidates": "Eşleşen konum yok.",
        "label.no_days": "Tahmin günü döndürülmedi.",
        "label.disambiguation": (
            "Eşit güvenilirlikte birden fazla eşleşme; lat/lon vermek belirleyici."
        ),
        "header.day": "Gün",
        "header.weather": "Hava",
        "header.temp": "Sıcaklık (°{unit})",
        "header.precip": "Yağış",
        "header.wind": "Rüzgar",
        "header.humidity": "Nem",
        "error.empty_query": "Sorgu boş olamaz.",
        "error.invalid_coords": "Enlem [-90, 90], boylam [-180, 180] aralığında olmalı.",
        "error.invalid_days": "days 1-16 aralığında olmalı.",
        "error.invalid_units": "units 'metric' veya 'imperial' olmalı.",
        "error.invalid_date": "start_date YYYY-MM-DD biçiminde olmalı.",
        "error.network": "Open-Meteo yanıt vermedi.",
        "error.no_results": "Geocoding hiç sonuç döndürmedi.",
        "hint.use_coords": "Geocoding atlamak için latitude/longitude doğrudan verin.",
        "note.forecast": "Tahmin verisi: Open-Meteo (CC-BY 4.0).",
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
