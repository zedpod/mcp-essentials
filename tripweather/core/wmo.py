"""WMO weather code → label table.

Open-Meteo uses the WMO weather code interpretation.
"""

WMO_LABELS: dict[int, dict[str, str]] = {
    0: {"en": "Clear sky", "tr": "Açık"},
    1: {"en": "Mainly clear", "tr": "Çoğunlukla açık"},
    2: {"en": "Partly cloudy", "tr": "Parçalı bulutlu"},
    3: {"en": "Overcast", "tr": "Kapalı"},
    45: {"en": "Fog", "tr": "Sis"},
    48: {"en": "Depositing rime fog", "tr": "Kırağılı sis"},
    51: {"en": "Light drizzle", "tr": "Hafif çisenti"},
    53: {"en": "Moderate drizzle", "tr": "Orta çisenti"},
    55: {"en": "Dense drizzle", "tr": "Yoğun çisenti"},
    56: {"en": "Light freezing drizzle", "tr": "Hafif donan çisenti"},
    57: {"en": "Dense freezing drizzle", "tr": "Yoğun donan çisenti"},
    61: {"en": "Slight rain", "tr": "Hafif yağmur"},
    63: {"en": "Moderate rain", "tr": "Orta yağmur"},
    65: {"en": "Heavy rain", "tr": "Şiddetli yağmur"},
    66: {"en": "Light freezing rain", "tr": "Hafif donan yağmur"},
    67: {"en": "Heavy freezing rain", "tr": "Şiddetli donan yağmur"},
    71: {"en": "Slight snow", "tr": "Hafif kar"},
    73: {"en": "Moderate snow", "tr": "Orta kar"},
    75: {"en": "Heavy snow", "tr": "Yoğun kar"},
    77: {"en": "Snow grains", "tr": "Kar taneleri"},
    80: {"en": "Slight rain showers", "tr": "Hafif yağmur sağanağı"},
    81: {"en": "Moderate rain showers", "tr": "Orta yağmur sağanağı"},
    82: {"en": "Violent rain showers", "tr": "Şiddetli yağmur sağanağı"},
    85: {"en": "Slight snow showers", "tr": "Hafif kar sağanağı"},
    86: {"en": "Heavy snow showers", "tr": "Şiddetli kar sağanağı"},
    95: {"en": "Thunderstorm", "tr": "Gök gürültülü fırtına"},
    96: {"en": "Thunderstorm with slight hail", "tr": "Hafif dolu ile fırtına"},
    99: {"en": "Thunderstorm with heavy hail", "tr": "Şiddetli dolu ile fırtına"},
}


def label(code: int | None, lang: str) -> str:
    if code is None:
        return ""
    entry = WMO_LABELS.get(int(code))
    if not entry:
        return f"WMO {code}"
    return entry.get(lang) or entry.get("en") or ""
