"""askuser i18n strings."""

from typing import Final

STRINGS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "title": "AskUser",
        "label.skip": "Skip",
        "label.cancel": "Cancel",
        "label.confirm": "Confirm",
        "label.search": "Search options…",
        "label.custom_input": "Or type a custom answer…",
        "label.no_answer": "User did not provide an answer.",
        "label.user_selected": "User selected",
        "label.user_typed": "User typed",
        "label.cancelled": "User cancelled.",
        "label.timeout": "Question timed out.",
        "label.no_display": "Cannot open a browser in this environment (no display).",
        "error.empty_prompt": "prompt is required.",
        "error.invalid_mode": "mode must be 'single', 'multi', or 'free_text'.",
        "error.options_required": "At least one option is required for select/multi modes.",
        "error.too_many_options": "options exceeds the 200-item limit.",
        "error.min_max": "min_select must be ≤ max_select and ≤ option count.",
        "error.invalid_timeout": "timeout_s must be in (0, 1800].",
        "error.no_display": (
            "No display detected; the askuser tool cannot open a browser. "
            "Run from a desktop session, or use askuser inside Open WebUI."
        ),
        "error.csrf": "CSRF token mismatch.",
        "hint.set_display": "Run from a session with $DISPLAY (Linux) or a normal desktop user.",
    },
    "tr": {
        "title": "AskUser",
        "label.skip": "Atla",
        "label.cancel": "İptal",
        "label.confirm": "Onayla",
        "label.search": "Seçenekleri ara…",
        "label.custom_input": "Veya kendi yanıtınızı yazın…",
        "label.no_answer": "Kullanıcı bir yanıt vermedi.",
        "label.user_selected": "Kullanıcı seçti",
        "label.user_typed": "Kullanıcı yazdı",
        "label.cancelled": "Kullanıcı iptal etti.",
        "label.timeout": "Soru zaman aşımına uğradı.",
        "label.no_display": "Bu ortamda tarayıcı açılamadı (ekran yok).",
        "error.empty_prompt": "prompt zorunlu.",
        "error.invalid_mode": "mode 'single', 'multi' veya 'free_text' olmalı.",
        "error.options_required": "select/multi modları için en az bir seçenek gerekli.",
        "error.too_many_options": "options 200 öğe sınırını aşıyor.",
        "error.min_max": "min_select ≤ max_select ve ≤ seçenek sayısı olmalı.",
        "error.invalid_timeout": "timeout_s (0, 1800] aralığında olmalı.",
        "error.no_display": (
            "Ekran bulunamadı; askuser tarayıcı açamaz. Masaüstü oturumundan "
            "çalıştırın veya Open WebUI içinde kullanın."
        ),
        "error.csrf": "CSRF token eşleşmiyor.",
        "hint.set_display": "Linux'ta $DISPLAY tanımlı bir oturum veya normal masaüstü kullanıcısı kullanın.",
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
