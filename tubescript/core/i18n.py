"""tubescript i18n strings."""

from typing import Final

STRINGS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "title.list": "Transcript Tracks",
        "title.transcript": "Transcript",
        "label.video_id": "Video ID",
        "label.language": "Language",
        "label.is_generated": "Auto-generated",
        "label.translated_to": "Translated to",
        "label.format": "Format",
        "label.chars": "Characters",
        "label.entries": "Entries",
        "label.tracks": "Available tracks",
        "error.empty_input": "URL or video ID is required.",
        "error.invalid_id": "Could not extract a YouTube video ID from the input.",
        "error.no_transcripts": "No transcripts are available for this video.",
        "error.transcripts_disabled": "Transcripts are disabled for this video.",
        "error.video_unavailable": (
            "Video is unavailable (private, deleted, region-blocked, or age-restricted)."
        ),
        "error.translation_unavailable": "Requested translation language is not available.",
        "error.preferred_unavailable": "None of the preferred languages are available.",
        "error.invalid_format": "Format must be one of: text, srt, vtt, json.",
        "error.upstream": "YouTube returned an unexpected error.",
        "hint.try_translate_to": "Try setting translate_to to en/tr if a language pair is supported.",
        "hint.list_first": "Call list_transcripts first to see which languages are available.",
        "note.truncated": "Output truncated at the word boundary nearest max_chars.",
    },
    "tr": {
        "title.list": "Transkript Kanalları",
        "title.transcript": "Transkript",
        "label.video_id": "Video ID",
        "label.language": "Dil",
        "label.is_generated": "Otomatik üretilmiş",
        "label.translated_to": "Çevrildiği dil",
        "label.format": "Biçim",
        "label.chars": "Karakter",
        "label.entries": "Giriş",
        "label.tracks": "Mevcut kanallar",
        "error.empty_input": "URL veya video ID zorunlu.",
        "error.invalid_id": "Girdiden YouTube video ID çıkarılamadı.",
        "error.no_transcripts": "Bu video için transkript yok.",
        "error.transcripts_disabled": "Bu videoda transkript devre dışı.",
        "error.video_unavailable": (
            "Video mevcut değil (özel, silinmiş, bölge kısıtlı veya yaş kısıtlı)."
        ),
        "error.translation_unavailable": "İstenen çeviri dili mevcut değil.",
        "error.preferred_unavailable": "Tercih edilen dillerin hiçbiri yok.",
        "error.invalid_format": "Biçim şunlardan biri olmalı: text, srt, vtt, json.",
        "error.upstream": "YouTube beklenmeyen bir hata döndürdü.",
        "hint.try_translate_to": "Desteklenen dil çiftleri için translate_to=en/tr deneyin.",
        "hint.list_first": "Hangi dillerin mevcut olduğunu görmek için list_transcripts'i çağırın.",
        "note.truncated": "Çıktı, max_chars'a en yakın kelime sınırında kesildi.",
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
