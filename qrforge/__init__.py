"""qrforge — QR codes for text, URLs, Wi-Fi, and vCards.

Two delivery surfaces share a single core:
    qrforge.core   — pure logic, returns Result[QrImage] (use this in tests).
    qrforge.server — FastMCP/stdio server. Run with `python -m qrforge`.
    qrforge/owui.py — generated single-file OWUI Tools bundle (paste into OWUI).
"""

__version__ = "1.0.0"
