"""Smoke tests for the OWUI bundle.

These exercise the generated qrforge/owui/main.py as if a user pasted it into
Open WebUI Admin. We import it from disk under a synthetic module name to
mimic OWUI's evaluation strategy.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

OWUI_BUNDLE = Path(__file__).resolve().parent.parent / "owui.py"


@pytest.fixture(scope="module")
def bundled_module():
    import sys

    spec = importlib.util.spec_from_file_location("qrforge_owui_bundle", OWUI_BUNDLE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Pydantic generic-model registry uses sys.modules[__module__] during creation;
    # register before exec_module to avoid KeyError.
    sys.modules["qrforge_owui_bundle"] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop("qrforge_owui_bundle", None)
        raise
    yield module
    sys.modules.pop("qrforge_owui_bundle", None)


def test_tools_class_exposes_expected_methods(bundled_module) -> None:
    tools = bundled_module.Tools()
    for name in ("qr_text", "qr_url", "qr_wifi", "qr_vcard"):
        assert callable(getattr(tools, name)), f"OWUI bundle missing method {name}"


def test_qr_text_returns_markdown(bundled_module) -> None:
    tools = bundled_module.Tools()
    out = tools.qr_text("hello bundle", size=128)
    assert isinstance(out, str)
    assert "QRForge" in out
    assert "data:image/png;base64," in out


def test_qr_text_honors_default_language_valve(bundled_module) -> None:
    tools = bundled_module.Tools()
    tools.valves.DEFAULT_LANGUAGE = "tr"
    out = tools.qr_text("")  # invalid → renders error in Turkish
    assert "QR verisi boş" in out


def test_qr_text_call_arg_overrides_valve_language(bundled_module) -> None:
    tools = bundled_module.Tools()
    tools.valves.DEFAULT_LANGUAGE = "tr"
    out = tools.qr_text("", language="en")
    assert "QR payload is empty" in out


def test_qr_wifi_renders_warning_about_local_only(bundled_module) -> None:
    tools = bundled_module.Tools()
    out = tools.qr_wifi("OrzedGuest", password="welcome2025")
    assert isinstance(out, str)
    assert "Wi-Fi" in out
    assert "local" in out.lower() or "yerel" in out.lower()


def test_qr_url_rejects_schemeless(bundled_module) -> None:
    tools = bundled_module.Tools()
    out = tools.qr_url("orzed.com")
    assert "Error" in out
    assert "INVALID_INPUT" in out


def test_default_use_remote_fallback_is_false(bundled_module) -> None:
    tools = bundled_module.Tools()
    assert tools.valves.USE_REMOTE_FALLBACK is False


def test_owui_and_core_outputs_agree(bundled_module) -> None:
    """Parity check: the OWUI wrapper renders the same markdown as core+render
    when fed the same inputs. Catches drift between hand-tuned wrapper behavior
    and the bundled inlined code."""
    from qrforge.core import qr_text as core_qr_text
    from qrforge.core import to_markdown

    tools = bundled_module.Tools()
    owui_out = tools.qr_text("parity check", size=128, language="en")
    core_result = core_qr_text(
        "parity check",
        size=128,
        border=4,
        ec_level="M",
        use_remote_fallback=False,
        language="en",
    )
    core_out = to_markdown(core_result, lang="en")
    # Strip the base64 blob, which is deterministic per payload but huge - compare structure.
    def strip_b64(s: str) -> str:
        import re

        return re.sub(r"base64,[A-Za-z0-9+/=]+", "base64,...", s)

    assert strip_b64(owui_out) == strip_b64(core_out)
