"""flighthunter i18n strings."""

from typing import Final

STRINGS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "title": "FlightHunter",
        "label.route": "Route",
        "label.dates": "Dates",
        "label.trip_type": "Trip type",
        "label.cabin": "Cabin",
        "label.passengers": "Passengers",
        "label.cheapest": "Cheapest options",
        "label.price_insight": "Price insight",
        "label.no_results": "No flights found.",
        "label.stops": "stops",
        "label.nonstop": "nonstop",
        "label.via": "via",
        "label.adults": "adults",
        "label.children": "children",
        "label.infants": "infants",
        "label.book": "Book on Google Flights",
        "trip.round_trip": "round trip",
        "trip.one_way": "one way",
        "trip.multi_city": "multi-city",
        "cabin.economy": "Economy",
        "cabin.premium_economy": "Premium Economy",
        "cabin.business": "Business",
        "cabin.first": "First",
        "level.low": "below typical",
        "level.typical": "typical",
        "level.high": "above typical",
        "error.missing_api_key": (
            "FLIGHTHUNTER_SERPAPI_KEY environment variable is not set. "
            "Sign up at https://serpapi.com to get one."
        ),
        "error.invalid_iata": "Origin and destination must be 3-letter IATA codes (e.g., IST, LHR).",
        "error.same_origin_destination": "Origin and destination cannot be the same.",
        "error.invalid_date": "Date must be YYYY-MM-DD.",
        "error.return_before_departure": "Return date is before departure date.",
        "error.invalid_passengers": "Total passengers must be 1 to 9; children must be < adults.",
        "error.invalid_cabin": "Cabin class must be economy, premium_economy, business, or first.",
        "error.upstream": "SerpAPI returned an error.",
        "hint.set_key": (
            "Add `FLIGHTHUNTER_SERPAPI_KEY` to your env (Open WebUI Valves or "
            "claude_desktop_config.json env block)."
        ),
        "hint.try_other_dates": "Try a different date or a major airport hub.",
        "note.search": "Prices are SerpAPI snapshots; book directly with the airline for fare guarantees.",
    },
    "tr": {
        "title": "FlightHunter",
        "label.route": "Rota",
        "label.dates": "Tarihler",
        "label.trip_type": "Tip",
        "label.cabin": "Sınıf",
        "label.passengers": "Yolcular",
        "label.cheapest": "En ucuz seçenekler",
        "label.price_insight": "Fiyat seviyesi",
        "label.no_results": "Uçuş bulunamadı.",
        "label.stops": "aktarma",
        "label.nonstop": "aktarmasız",
        "label.via": "üzerinden",
        "label.adults": "yetişkin",
        "label.children": "çocuk",
        "label.infants": "bebek",
        "label.book": "Google Flights'ta Rezerve Et",
        "trip.round_trip": "gidiş-dönüş",
        "trip.one_way": "tek yön",
        "trip.multi_city": "çoklu şehir",
        "cabin.economy": "Ekonomi",
        "cabin.premium_economy": "Premium Ekonomi",
        "cabin.business": "Business",
        "cabin.first": "First",
        "level.low": "tipik altı",
        "level.typical": "tipik",
        "level.high": "tipik üstü",
        "error.missing_api_key": (
            "FLIGHTHUNTER_SERPAPI_KEY env değişkeni ayarlı değil. "
            "https://serpapi.com adresinden ücretsiz alabilirsiniz."
        ),
        "error.invalid_iata": "Origin ve destination 3 harfli IATA kodu olmalı (örn. IST, LHR).",
        "error.same_origin_destination": "Origin ve destination aynı olamaz.",
        "error.invalid_date": "Tarih YYYY-MM-DD formatında olmalı.",
        "error.return_before_departure": "Dönüş tarihi gidişten önce.",
        "error.invalid_passengers": "Yolcu toplamı 1-9; çocuk sayısı yetişkin sayısından az olmalı.",
        "error.invalid_cabin": "Sınıf: economy, premium_economy, business veya first.",
        "error.upstream": "SerpAPI bir hata döndürdü.",
        "hint.set_key": (
            "FLIGHTHUNTER_SERPAPI_KEY'i env'e ekleyin (OWUI Valves veya "
            "claude_desktop_config.json env bloğu)."
        ),
        "hint.try_other_dates": "Farklı bir tarih veya ana havalimanı deneyin.",
        "note.search": (
            "Fiyatlar SerpAPI anlık görüntüsüdür; kesin tarife için havayolu sitesinden rezerve edin."
        ),
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
