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
        Generate a QR code for arbitrary text or any payload.

        :param text: Payload to encode.
        :param size: Image edge length in pixels (64-4096).
        :param border: Quiet-zone width in modules (0-16).
        :param ec_level: Error correction level: L, M, Q, or H.
        :param language: Output language ('en' or 'tr').
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
        Generate a QR code for an HTTP(S) URL. Rejects schemeless inputs.

        :param url: Full URL including http:// or https://.
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
        Remote fallback is forbidden for Wi-Fi credentials.

        :param ssid: Wi-Fi network name.
        :param password: Wi-Fi password (empty for NOPASS).
        :param encryption: One of WPA, WEP, NOPASS.
        :param hidden: True if the network is hidden.
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
        Remote fallback is forbidden — contact data should not leave the host.

        :param full_name: Full name.
        :param phone: Phone number.
        :param email: Email address.
        :param org: Organization / company.
        :param title: Job title.
        :param url: Website URL.
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
