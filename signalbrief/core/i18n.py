"""signalbrief i18n strings."""

from typing import Final

STRINGS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "title": "SignalBrief",
        "label.window": "Window",
        "label.hours_back": "hours back",
        "label.sources": "Sources",
        "label.keywords": "Keywords",
        "label.failed": "Failed sources",
        "label.no_items": "No matching items.",
        "error.empty_keywords": "No keywords resolved (after filtering).",
        "error.empty_sources": "No source feeds resolved (after filtering).",
        "error.invalid_hours": "hours_back must be 1-336.",
        "hint.lower_min_score": "Lower min_score, widen hours_back, or add more keywords.",
        "note.brief": "Items are scored by token-level matches and recency. Subtitle: source name.",
    },
    "tr": {
        "title": "SignalBrief",
        "label.window": "Pencere",
        "label.hours_back": "saat önce",
        "label.sources": "Kaynaklar",
        "label.keywords": "Anahtar kelimeler",
        "label.failed": "Başarısız kaynaklar",
        "label.no_items": "Eşleşen öğe yok.",
        "error.empty_keywords": "Süzme sonrası anahtar kelime kalmadı.",
        "error.empty_sources": "Süzme sonrası kaynak kalmadı.",
        "error.invalid_hours": "hours_back 1-336 aralığında olmalı.",
        "hint.lower_min_score": "min_score'u düşür, hours_back'i genişlet veya daha fazla kelime ekle.",
        "note.brief": "Öğeler token düzeyi eşleşmeler ve tazeliğe göre puanlanır.",
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
