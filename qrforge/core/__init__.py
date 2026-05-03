"""qrforge.core - pure logic for QR code generation."""

from .i18n import DEFAULT, SUPPORTED, normalize_lang, t
from .qr import qr_text, qr_url, qr_vcard, qr_wifi
from .render import to_markdown
from .types import ErrorInfo, QrImage, Result

# Order in which core modules are inlined into owui/main.py by tools/bundle_owui.py.
# Dependencies must come before the modules that use them.
__bundle_order__ = ["types", "i18n", "qr", "render"]

__all__ = [
    "qr_text",
    "qr_url",
    "qr_wifi",
    "qr_vcard",
    "to_markdown",
    "Result",
    "QrImage",
    "ErrorInfo",
    "t",
    "normalize_lang",
    "SUPPORTED",
    "DEFAULT",
]
