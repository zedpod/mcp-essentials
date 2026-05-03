"""Pure QR code generation logic.

No HTTP, no I/O at import time. Optional dependency on the `qrcode` package
plus Pillow; if missing, callers can opt into a remote-render URL fallback
(but only for non-sensitive payloads).
"""

import base64
import io
import re
import urllib.parse

from .i18n import t
from .types import (
    EcLevel,
    ErrorInfo,
    PayloadKind,
    QrImage,
    Result,
    WifiEncryption,
)

_DEFAULT_REMOTE_BASE = "https://api.qrserver.com/v1/create-qr-code/"
_VCARD_FIELD_PATTERN = re.compile(r"[\r\n]+")
_PHONE_PATTERN = re.compile(r"^[+]?[\d\-\s().]{4,}$")
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_URL_PATTERN = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)
_VALID_EC_LEVELS = ("L", "M", "Q", "H")
_VALID_ENCRYPTIONS = ("WPA", "WEP", "NOPASS")


def _err(
    code: str,
    lang: str,
    en_key: str,
    tr_key: str | None = None,
    *,
    hint_key: str | None = None,
    fmt: dict | None = None,
) -> ErrorInfo:
    fmt = fmt or {}
    return ErrorInfo(
        code=code,
        message_en=t(en_key, "en", **fmt),
        message_tr=t(tr_key or en_key, "tr", **fmt),
        hint=t(hint_key, lang, **fmt) if hint_key else None,
    )


def _wifi_payload(ssid: str, password: str, encryption: WifiEncryption, hidden: bool) -> str:
    def esc(value: str) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace(";", "\\;")
            .replace(",", "\\,")
            .replace(":", "\\:")
            .replace('"', '\\"')
        )

    hidden_token = "true" if hidden else "false"
    if encryption == "NOPASS":
        return f"WIFI:T:nopass;S:{esc(ssid)};H:{hidden_token};;"
    return f"WIFI:T:{encryption};S:{esc(ssid)};P:{esc(password)};H:{hidden_token};;"


def _vcard_payload(
    full_name: str,
    phone: str,
    email: str,
    org: str,
    title: str,
    url: str,
) -> str:
    def clean(value: str) -> str:
        return _VCARD_FIELD_PATTERN.sub(" ", value).replace(";", "\\;").replace(",", "\\,")

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{clean(full_name)}",
    ]
    if org:
        lines.append(f"ORG:{clean(org)}")
    if title:
        lines.append(f"TITLE:{clean(title)}")
    if phone:
        lines.append(f"TEL:{clean(phone)}")
    if email:
        lines.append(f"EMAIL:{clean(email)}")
    if url:
        lines.append(f"URL:{clean(url)}")
    lines.append("END:VCARD")
    return "\r\n".join(lines)


def _remote_qr_url(data: str, size: int, base_url: str) -> str:
    encoded = urllib.parse.urlencode({"size": f"{size}x{size}", "data": data})
    return f"{base_url}?{encoded}"


def _generate_local_png(data: str, size: int, border: int, ec_level: EcLevel) -> bytes | None:
    """Return PNG bytes via the `qrcode` library, or None if it's not installed.

    Raises on payload-too-large; the caller must classify that into a Result error.
    """
    try:
        import qrcode
        from qrcode.constants import (
            ERROR_CORRECT_H,
            ERROR_CORRECT_L,
            ERROR_CORRECT_M,
            ERROR_CORRECT_Q,
        )
    except ImportError:
        return None

    correction_map = {
        "L": ERROR_CORRECT_L,
        "M": ERROR_CORRECT_M,
        "Q": ERROR_CORRECT_Q,
        "H": ERROR_CORRECT_H,
    }
    qr = qrcode.QRCode(
        version=None,
        error_correction=correction_map[ec_level],
        box_size=10,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size, size))
    with io.BytesIO() as buffer:
        img.save(buffer, format="PNG")
        return buffer.getvalue()


def _build_image(
    payload: str,
    payload_kind: PayloadKind,
    size: int,
    border: int,
    ec_level: EcLevel,
    use_remote_fallback: bool,
    remote_base_url: str,
    language: str,
) -> Result[QrImage]:
    if not payload:
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.empty_payload"))
    if ec_level not in _VALID_EC_LEVELS:
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.invalid_ec_level"))
    if not (64 <= size <= 4096):
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.invalid_size"))
    if not (0 <= border <= 16):
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.invalid_border"))

    try:
        png_bytes = _generate_local_png(payload, size=size, border=border, ec_level=ec_level)
    except Exception as exc:  # qrcode raises on capacity overflow, etc.
        message = str(exc).lower()
        if "data" in message and ("too" in message or "long" in message or "exceed" in message):
            return Result(
                ok=False,
                error=_err(
                    "INVALID_INPUT",
                    language,
                    "error.payload_too_large",
                    hint_key="hint.try_lower_ec",
                ),
            )
        return Result(
            ok=False,
            error=_err(
                "INTERNAL",
                language,
                "error.internal",
                fmt={"detail": str(exc)[:120]},
            ),
        )

    if png_bytes is not None:
        b64 = base64.b64encode(png_bytes).decode("ascii")
        image = QrImage(
            source="local",
            data_b64=b64,
            byte_length=len(png_bytes),
            pixel_size=size,
            border=border,
            ec_level=ec_level,
            payload_kind=payload_kind,
            payload_preview=payload[:80],
        )
        return Result(ok=True, data=image, meta={"source": "local"})

    # Local generation unavailable. Decide whether to fall back to remote.
    sensitive = payload_kind in ("wifi", "vcard")
    if sensitive:
        return Result(
            ok=False,
            error=_err(
                "UNSUPPORTED",
                language,
                "error.remote_disabled_for_sensitive",
                hint_key="hint.use_local_for_secrets",
                fmt={"kind": payload_kind},
            ),
        )
    if not use_remote_fallback:
        return Result(
            ok=False,
            error=_err(
                "UNSUPPORTED",
                language,
                "error.qrcode_missing",
                hint_key="hint.install_qrcode",
            ),
        )

    remote_url = _remote_qr_url(payload, size=size, base_url=remote_base_url)
    image = QrImage(
        source="remote",
        remote_url=remote_url,
        byte_length=0,
        pixel_size=size,
        border=border,
        ec_level=ec_level,
        payload_kind=payload_kind,
        payload_preview=payload[:80],
    )
    return Result(
        ok=True,
        data=image,
        meta={
            "source": "remote",
            "warning": "remote_fallback_used",
            "warning_message": t("warning.remote_used", language),
        },
    )


def qr_text(
    text: str,
    *,
    size: int = 512,
    border: int = 4,
    ec_level: EcLevel = "M",
    use_remote_fallback: bool = False,
    remote_base_url: str = _DEFAULT_REMOTE_BASE,
    language: str = "en",
) -> Result[QrImage]:
    """Encode arbitrary text as a QR code."""
    return _build_image(
        payload=(text or "").strip(),
        payload_kind="text",
        size=size,
        border=border,
        ec_level=ec_level,
        use_remote_fallback=use_remote_fallback,
        remote_base_url=remote_base_url,
        language=language,
    )


def qr_url(
    url: str,
    *,
    size: int = 512,
    border: int = 4,
    ec_level: EcLevel = "M",
    use_remote_fallback: bool = False,
    remote_base_url: str = _DEFAULT_REMOTE_BASE,
    language: str = "en",
) -> Result[QrImage]:
    """Encode a URL as a QR code; rejects anything missing an http(s) scheme."""
    cleaned = (url or "").strip()
    if not cleaned:
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.empty_payload"))
    if not _URL_PATTERN.match(cleaned):
        return Result(
            ok=False,
            error=_err(
                "INVALID_INPUT",
                language,
                "error.invalid_url",
                hint_key="hint.url_scheme",
            ),
        )
    return _build_image(
        payload=cleaned,
        payload_kind="url",
        size=size,
        border=border,
        ec_level=ec_level,
        use_remote_fallback=use_remote_fallback,
        remote_base_url=remote_base_url,
        language=language,
    )


def qr_wifi(
    ssid: str,
    *,
    password: str = "",
    encryption: WifiEncryption = "WPA",
    hidden: bool = False,
    size: int = 512,
    border: int = 4,
    ec_level: EcLevel = "M",
    language: str = "en",
) -> Result[QrImage]:
    """Encode Wi-Fi credentials as a QR code. Remote fallback is forbidden."""
    cleaned_ssid = (ssid or "").strip()
    if not cleaned_ssid:
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.empty_payload"))
    enc = (encryption or "WPA").upper()
    if enc not in _VALID_ENCRYPTIONS:
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.invalid_encryption"))
    payload = _wifi_payload(
        ssid=cleaned_ssid,
        password=password or "",
        encryption=enc,  # type: ignore[arg-type]
        hidden=bool(hidden),
    )
    return _build_image(
        payload=payload,
        payload_kind="wifi",
        size=size,
        border=border,
        ec_level=ec_level,
        use_remote_fallback=False,  # explicit: never remote for wifi
        remote_base_url=_DEFAULT_REMOTE_BASE,
        language=language,
    )


def qr_vcard(
    full_name: str,
    *,
    phone: str = "",
    email: str = "",
    org: str = "",
    title: str = "",
    url: str = "",
    size: int = 512,
    border: int = 4,
    ec_level: EcLevel = "M",
    language: str = "en",
) -> Result[QrImage]:
    """Encode contact details as a QR code (vCard 3.0). Remote fallback is forbidden."""
    cleaned_name = (full_name or "").strip()
    if not cleaned_name:
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.empty_payload"))
    if phone and not _PHONE_PATTERN.match(phone.strip()):
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.invalid_phone"))
    if email and not _EMAIL_PATTERN.match(email.strip()):
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.invalid_email"))
    if url and not _URL_PATTERN.match(url.strip()):
        return Result(ok=False, error=_err("INVALID_INPUT", language, "error.invalid_url"))

    payload = _vcard_payload(
        full_name=cleaned_name,
        phone=phone or "",
        email=email or "",
        org=org or "",
        title=title or "",
        url=url or "",
    )
    return _build_image(
        payload=payload,
        payload_kind="vcard",
        size=size,
        border=border,
        ec_level=ec_level,
        use_remote_fallback=False,  # explicit: never remote for vcard
        remote_base_url=_DEFAULT_REMOTE_BASE,
        language=language,
    )
