"""Live integration tests for qrforge.

qrforge has very little to integrate with - local QR generation is offline by
design. The single live path is the optional remote fallback to
api.qrserver.com when the `qrcode` library is missing. We don't actually want
to depend on that service in CI, so this file is mostly a placeholder showing
the @pytest.mark.live convention for sibling tools to copy.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.live


def test_remote_fallback_url_shape() -> None:
    """Without monkeypatching, force the remote-fallback path and verify the URL shape."""
    from qrforge.core.qr import _remote_qr_url

    url = _remote_qr_url("hello", size=256, base_url="https://api.qrserver.com/v1/create-qr-code/")
    assert url.startswith("https://api.qrserver.com/v1/create-qr-code/")
    assert "size=256x256" in url
    assert "data=hello" in url
