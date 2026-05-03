"""Per-tool string table for qrforge. en / tr; fallback to en."""

from typing import Final

STRINGS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "title": "QRForge",
        "label.size": "Size",
        "label.payload_chars": "Payload length",
        "label.ec_level": "Error correction",
        "label.kind": "Kind",
        "label.source": "Source",
        "kind.text": "Text",
        "kind.url": "URL",
        "kind.wifi": "Wi-Fi",
        "kind.vcard": "vCard",
        "source.local": "local (in-process)",
        "source.remote": "remote (api.qrserver.com)",
        "note.local": "Generated locally. Payload was not sent to any third party.",
        "note.remote": (
            "Generated via remote service. The payload was sent to api.qrserver.com — "
            "do not use remote rendering for sensitive data."
        ),
        "warning.remote_used": "Remote rendering was used.",
        "error.empty_payload": "QR payload is empty.",
        "error.invalid_url": "Input does not look like a valid URL (expected http(s)://...).",
        "error.invalid_email": "Email address looks invalid.",
        "error.invalid_phone": "Phone number looks invalid.",
        "error.invalid_ec_level": "Error-correction level must be one of L, M, Q, H.",
        "error.invalid_encryption": "Wi-Fi encryption must be one of WPA, WEP, NOPASS.",
        "error.invalid_size": "Image size must be between 64 and 4096 pixels.",
        "error.invalid_border": "Border must be between 0 and 16 modules.",
        "error.qrcode_missing": "Local 'qrcode' library is not installed.",
        "error.remote_disabled_for_sensitive": (
            "Remote fallback is not allowed for {kind} payloads (security)."
        ),
        "error.remote_disabled": "Remote fallback is disabled (USE_REMOTE_FALLBACK=False).",
        "error.payload_too_large": (
            "Payload exceeds the QR capacity at the requested error-correction level."
        ),
        "error.internal": "Unexpected error: {detail}",
        "hint.install_qrcode": (
            "Install with `pip install qrcode[pil]`. Inside an OWUI container: "
            "`docker exec -it open-webui pip install qrcode[pil]` then restart the container."
        ),
        "hint.try_lower_ec": "Try a lower error-correction level (L) or shorten the payload.",
        "hint.use_local_for_secrets": (
            "Generate Wi-Fi/vCard QR codes locally only — install `qrcode[pil]`."
        ),
        "hint.url_scheme": "Add an explicit scheme such as https:// to the URL.",
    },
    "tr": {
        "title": "QRForge",
        "label.size": "Boyut",
        "label.payload_chars": "Veri uzunluğu",
        "label.ec_level": "Hata düzeltme",
        "label.kind": "Tür",
        "label.source": "Kaynak",
        "kind.text": "Metin",
        "kind.url": "URL",
        "kind.wifi": "Wi-Fi",
        "kind.vcard": "vCard",
        "source.local": "yerel (süreç içi)",
        "source.remote": "uzak (api.qrserver.com)",
        "note.local": "Yerelde üretildi. Veri üçüncü tarafa gönderilmedi.",
        "note.remote": (
            "Uzak servis ile üretildi. Veri api.qrserver.com'a gönderildi — "
            "hassas verilerde uzak üretim kullanmayın."
        ),
        "warning.remote_used": "Uzak üretim kullanıldı.",
        "error.empty_payload": "QR verisi boş.",
        "error.invalid_url": "URL geçerli görünmüyor (http(s)://... bekleniyor).",
        "error.invalid_email": "E-posta adresi geçerli görünmüyor.",
        "error.invalid_phone": "Telefon numarası geçerli görünmüyor.",
        "error.invalid_ec_level": "Hata düzeltme seviyesi L, M, Q veya H olmalı.",
        "error.invalid_encryption": "Wi-Fi şifreleme WPA, WEP veya NOPASS olmalı.",
        "error.invalid_size": "Görsel boyutu 64 ile 4096 piksel arasında olmalı.",
        "error.invalid_border": "Kenar (border) 0 ile 16 modül arasında olmalı.",
        "error.qrcode_missing": "'qrcode' kütüphanesi yüklü değil.",
        "error.remote_disabled_for_sensitive": (
            "{kind} verileri için uzak üretim güvenlik nedeniyle kapalı."
        ),
        "error.remote_disabled": "Uzak fallback kapalı (USE_REMOTE_FALLBACK=False).",
        "error.payload_too_large": (
            "Veri, seçilen hata düzeltme seviyesinde QR kapasitesini aşıyor."
        ),
        "error.internal": "Beklenmeyen hata: {detail}",
        "hint.install_qrcode": (
            "Kurulum: `pip install qrcode[pil]`. OWUI container içinde: "
            "`docker exec -it open-webui pip install qrcode[pil]`, sonra container'ı yeniden başlatın."
        ),
        "hint.try_lower_ec": "Daha düşük hata düzeltme (L) deneyin veya veriyi kısaltın.",
        "hint.use_local_for_secrets": (
            "Wi-Fi/vCard QR kodlarını yalnızca yerel üretim ile alın — `qrcode[pil]` kurun."
        ),
        "hint.url_scheme": "URL'e açık bir şema ekleyin (örneğin https://).",
    },
}

SUPPORTED: Final[tuple[str, ...]] = ("en", "tr")
DEFAULT: Final[str] = "en"


def normalize_lang(lang: str | None) -> str:
    """Map any language tag to a supported code; unknown -> DEFAULT ('en')."""
    if not lang:
        return DEFAULT
    base = lang.lower().split("-")[0]
    return base if base in SUPPORTED else DEFAULT


def t(key: str, lang: str = DEFAULT, **kwargs: object) -> str:
    """Look up a string for `lang`; fall back to en, then to the key itself.

    Missing format placeholders are tolerated (returns the unformatted template),
    so a typo in a kwarg shows up as visible debug text instead of an exception.
    """
    lang = normalize_lang(lang)
    table = STRINGS.get(lang) or STRINGS[DEFAULT]
    template = table.get(key) or STRINGS[DEFAULT].get(key) or key
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template
