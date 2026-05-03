"""qrforge MCP server (stdio).

Run with:
    python -m qrforge

Each tool returns the structured Result as JSON; the calling LLM gets typed
fields (`ok`, `data`, `error`, `meta`) plus the auto-generated JSON Schema.
"""


from mcp.server.fastmcp import FastMCP

from qrforge.core import qr_text as core_qr_text
from qrforge.core import qr_url as core_qr_url
from qrforge.core import qr_vcard as core_qr_vcard
from qrforge.core import qr_wifi as core_qr_wifi

mcp = FastMCP("orzed-qrforge")


@mcp.tool()
def qr_text(
    text: str,
    size: int = 512,
    border: int = 4,
    ec_level: str = "M",
    use_remote_fallback: bool = False,
    language: str = "en",
) -> dict:
    """Encode arbitrary text or any payload as a PNG QR code.

    Args:
        text: Payload to encode (any string).
        size: Image edge length in pixels, 64-4096. Default 512.
        border: Quiet-zone width in modules, 0-16. Default 4.
        ec_level: Error correction level, one of L/M/Q/H. Default M.
        use_remote_fallback: If the local `qrcode` library is missing,
            optionally generate a URL pointing to api.qrserver.com.
            Disabled by default — payloads can leak.
        language: Output language for messages, "en" or "tr". Default "en".

    Returns:
        Result envelope with QrImage in `data` on success. The PNG arrives as
        base64 in `data.data_b64` for local rendering, or as `data.remote_url`
        when remote fallback is used.
    """
    result = core_qr_text(
        text,
        size=size,
        border=border,
        ec_level=ec_level,  # type: ignore[arg-type]
        use_remote_fallback=use_remote_fallback,
        language=language,
    )
    return result.model_dump(mode="json")


@mcp.tool()
def qr_url(
    url: str,
    size: int = 512,
    border: int = 4,
    ec_level: str = "M",
    use_remote_fallback: bool = False,
    language: str = "en",
) -> dict:
    """Encode an HTTP(S) URL as a PNG QR code. Rejects schemeless inputs.

    Args:
        url: Full URL including http:// or https://.
        size: Image edge length in pixels, 64-4096. Default 512.
        border: Quiet-zone width in modules, 0-16. Default 4.
        ec_level: Error correction level, one of L/M/Q/H. Default M.
        use_remote_fallback: Optional fallback to api.qrserver.com if local
            generation is unavailable. Default False.
        language: Output language for messages. Default "en".
    """
    result = core_qr_url(
        url,
        size=size,
        border=border,
        ec_level=ec_level,  # type: ignore[arg-type]
        use_remote_fallback=use_remote_fallback,
        language=language,
    )
    return result.model_dump(mode="json")


@mcp.tool()
def qr_wifi(
    ssid: str,
    password: str = "",
    encryption: str = "WPA",
    hidden: bool = False,
    size: int = 512,
    border: int = 4,
    ec_level: str = "M",
    language: str = "en",
) -> dict:
    """Encode Wi-Fi credentials as a QR code (WIFI: payload format).

    Remote fallback is intentionally disabled — sending Wi-Fi credentials to
    a third-party rendering service is a leak. If the local `qrcode` library
    is missing, the call returns UNSUPPORTED with an install hint.

    Args:
        ssid: Network name. Required.
        password: Network password (omit for NOPASS).
        encryption: One of WPA / WEP / NOPASS. Default WPA.
        hidden: Whether the network is hidden. Default False.
        size, border, ec_level, language: See qr_text.
    """
    result = core_qr_wifi(
        ssid,
        password=password,
        encryption=encryption,  # type: ignore[arg-type]
        hidden=hidden,
        size=size,
        border=border,
        ec_level=ec_level,  # type: ignore[arg-type]
        language=language,
    )
    return result.model_dump(mode="json")


@mcp.tool()
def qr_vcard(
    full_name: str,
    phone: str = "",
    email: str = "",
    org: str = "",
    title: str = "",
    url: str = "",
    size: int = 512,
    border: int = 4,
    ec_level: str = "M",
    language: str = "en",
) -> dict:
    """Encode contact details as a QR code (vCard 3.0).

    Remote fallback is disabled — contact data should not leave the host.

    Args:
        full_name: Full name. Required.
        phone, email, org, title, url: Optional fields. Validated when present.
        size, border, ec_level, language: See qr_text.
    """
    result = core_qr_vcard(
        full_name,
        phone=phone,
        email=email,
        org=org,
        title=title,
        url=url,
        size=size,
        border=border,
        ec_level=ec_level,  # type: ignore[arg-type]
        language=language,
    )
    return result.model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
