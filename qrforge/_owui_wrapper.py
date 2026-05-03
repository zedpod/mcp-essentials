"""OWUI Tools wrapper for qrforge.

This file is concatenated with core/ modules by tools/bundle_owui.py to
produce owui/main.py — the single paste-portable file users drop into the
Open WebUI Admin → Tools panel. Imports below resolve to symbols inlined
from core/ in the bundled output.
"""


from pydantic import BaseModel, Field

from qrforge.core import qr_text, qr_url, qr_vcard, qr_wifi, to_markdown


class Tools:
    class Valves(BaseModel):
        DEFAULT_LANGUAGE: str = Field(
            default="en",
            description="Output language for messages. 'en' or 'tr'. Unknown codes fall back to 'en'.",
        )
        DEFAULT_SIZE: int = Field(
            default=512,
            description="Default QR image edge length in pixels. Range 64-4096.",
        )
        DEFAULT_BORDER: int = Field(
            default=4,
            description="Default QR quiet-zone border (modules). Range 0-16.",
        )
        DEFAULT_EC_LEVEL: str = Field(
            default="M",
            description="Default error correction level. One of L, M, Q, H. Higher is more robust but denser.",
        )
        USE_REMOTE_FALLBACK: bool = Field(
            default=False,
            description=(
                "If the local 'qrcode' library is missing, fall back to api.qrserver.com "
                "for text/URL payloads only. Wi-Fi and vCard always require local rendering."
            ),
        )

    def __init__(self):
        self.valves = self.Valves()
        self.citation = False

    def _lang(self, language: str | None) -> str:
        return (language or self.valves.DEFAULT_LANGUAGE or "en").strip()

    def qr_text(
        self,
        text: str,
        size: int | None = None,
        border: int | None = None,
        ec_level: str | None = None,
        language: str | None = None,
    ) -> str:
        """
        Generate a QR code for arbitrary text.

        Use when: "QR for this text" / "şu metin için QR". Skip if the input is
        a URL (use qr_url), Wi-Fi (qr_wifi), or contact info (qr_vcard).
        """
        lang = self._lang(language)
        result = qr_text(
            text,
            size=size or self.valves.DEFAULT_SIZE,
            border=border if border is not None else self.valves.DEFAULT_BORDER,
            ec_level=(ec_level or self.valves.DEFAULT_EC_LEVEL).upper(),
            use_remote_fallback=self.valves.USE_REMOTE_FALLBACK,
            language=lang,
        )
        return to_markdown(result, lang=lang)

    def qr_url(
        self,
        url: str,
        size: int | None = None,
        border: int | None = None,
        ec_level: str | None = None,
        language: str | None = None,
    ) -> str:
        """
        Generate a QR code for an HTTP(S) URL.

        Use when: "QR for https://..." / "şu link için QR". Schemeless inputs
        are rejected - use qr_text for those.
        """
        lang = self._lang(language)
        result = qr_url(
            url,
            size=size or self.valves.DEFAULT_SIZE,
            border=border if border is not None else self.valves.DEFAULT_BORDER,
            ec_level=(ec_level or self.valves.DEFAULT_EC_LEVEL).upper(),
            use_remote_fallback=self.valves.USE_REMOTE_FALLBACK,
            language=lang,
        )
        return to_markdown(result, lang=lang)

    def qr_wifi(
        self,
        ssid: str,
        password: str = "",
        encryption: str = "WPA",
        hidden: bool = False,
        size: int | None = None,
        border: int | None = None,
        ec_level: str | None = None,
        language: str | None = None,
    ) -> str:
        """
        Generate a Wi-Fi connection QR code (WIFI:... payload).

        Use when: "Wi-Fi QR for guests" / "misafir Wi-Fi QR'ı". User provides
        SSID and usually a password. Encryption: WPA / WEP / NOPASS.
        Remote fallback is forbidden - credentials never leave the host.
        """
        lang = self._lang(language)
        result = qr_wifi(
            ssid,
            password=password,
            encryption=encryption.upper(),
            hidden=hidden,
            size=size or self.valves.DEFAULT_SIZE,
            border=border if border is not None else self.valves.DEFAULT_BORDER,
            ec_level=(ec_level or self.valves.DEFAULT_EC_LEVEL).upper(),
            language=lang,
        )
        return to_markdown(result, lang=lang)

    def qr_vcard(
        self,
        full_name: str,
        phone: str = "",
        email: str = "",
        org: str = "",
        title: str = "",
        url: str = "",
        size: int | None = None,
        border: int | None = None,
        ec_level: str | None = None,
        language: str | None = None,
    ) -> str:
        """
        Generate a vCard 3.0 contact QR code.

        Use when: "kartvizit QR" / "QR with my phone and email". User provides
        a name plus at least one of phone/email/url. Remote fallback is
        forbidden - contact data never leaves the host.
        """
        lang = self._lang(language)
        result = qr_vcard(
            full_name,
            phone=phone,
            email=email,
            org=org,
            title=title,
            url=url,
            size=size or self.valves.DEFAULT_SIZE,
            border=border if border is not None else self.valves.DEFAULT_BORDER,
            ec_level=(ec_level or self.valves.DEFAULT_EC_LEVEL).upper(),
            language=lang,
        )
        return to_markdown(result, lang=lang)
