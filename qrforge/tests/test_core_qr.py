"""Unit tests for qrforge.core.qr - pure functions, no network, no file I/O."""

from __future__ import annotations

from qrforge.core import qr_text, qr_url, qr_vcard, qr_wifi
from qrforge.core.qr import _vcard_payload, _wifi_payload


# ──────────────────────────────────────────────────────────────────────────────
# qr_text
# ──────────────────────────────────────────────────────────────────────────────
class TestQrText:
    def test_happy_path_local(self) -> None:
        result = qr_text("hello world", size=128)
        assert result.ok is True
        assert result.data is not None
        assert result.data.source == "local"
        assert result.data.byte_length > 0
        assert result.data.payload_kind == "text"
        assert result.data.pixel_size == 128
        assert result.data.payload_preview == "hello world"

    def test_empty_payload_returns_invalid_input(self) -> None:
        result = qr_text("")
        assert result.ok is False
        assert result.error is not None
        assert result.error.code == "INVALID_INPUT"
        assert result.error.message_en
        assert result.error.message_tr  # repo-level rule

    def test_whitespace_only_treated_as_empty(self) -> None:
        result = qr_text("   \t\n  ")
        assert result.ok is False
        assert result.error and result.error.code == "INVALID_INPUT"

    def test_invalid_ec_level(self) -> None:
        result = qr_text("hi", ec_level="X")  # type: ignore[arg-type]
        assert result.ok is False
        assert result.error and result.error.code == "INVALID_INPUT"

    def test_invalid_size_too_small(self) -> None:
        result = qr_text("hi", size=32)
        assert result.ok is False
        assert result.error and result.error.code == "INVALID_INPUT"

    def test_invalid_size_too_large(self) -> None:
        result = qr_text("hi", size=8000)
        assert result.ok is False
        assert result.error and result.error.code == "INVALID_INPUT"

    def test_invalid_border(self) -> None:
        result = qr_text("hi", border=20)
        assert result.ok is False
        assert result.error and result.error.code == "INVALID_INPUT"

    def test_unicode_payload(self) -> None:
        # Japanese + emoji should round-trip cleanly into the QR.
        result = qr_text("こんにちは 🌸 Merhaba", size=256)
        assert result.ok is True
        assert result.data and result.data.byte_length > 0

    def test_remote_disabled_when_qrcode_missing(self, monkeypatch) -> None:
        # Simulate qrcode-missing by patching the helper to return None.
        from qrforge.core import qr as qr_module

        monkeypatch.setattr(qr_module, "_generate_local_png", lambda *a, **kw: None)
        result = qr_text("hello", use_remote_fallback=False)
        assert result.ok is False
        assert result.error and result.error.code == "UNSUPPORTED"
        assert result.error.hint  # tells the LLM how to recover

    def test_remote_fallback_path_when_opted_in(self, monkeypatch) -> None:
        from qrforge.core import qr as qr_module

        monkeypatch.setattr(qr_module, "_generate_local_png", lambda *a, **kw: None)
        result = qr_text("hello", use_remote_fallback=True)
        assert result.ok is True
        assert result.data and result.data.source == "remote"
        assert result.data.remote_url and result.data.remote_url.startswith("https://")
        assert result.meta.get("warning") == "remote_fallback_used"


# ──────────────────────────────────────────────────────────────────────────────
# qr_url
# ──────────────────────────────────────────────────────────────────────────────
class TestQrUrl:
    def test_https_url_succeeds(self) -> None:
        result = qr_url("https://orzed.com", size=128)
        assert result.ok is True
        assert result.data and result.data.payload_kind == "url"

    def test_http_url_succeeds(self) -> None:
        result = qr_url("http://example.com", size=128)
        assert result.ok is True

    def test_schemeless_input_rejected(self) -> None:
        result = qr_url("orzed.com")
        assert result.ok is False
        assert result.error and result.error.code == "INVALID_INPUT"
        assert result.error.hint

    def test_ftp_rejected(self) -> None:
        result = qr_url("ftp://example.com/file")
        assert result.ok is False
        assert result.error and result.error.code == "INVALID_INPUT"

    def test_empty_rejected(self) -> None:
        result = qr_url("")
        assert result.ok is False
        assert result.error and result.error.code == "INVALID_INPUT"


# ──────────────────────────────────────────────────────────────────────────────
# qr_wifi
# ──────────────────────────────────────────────────────────────────────────────
class TestQrWifi:
    def test_wpa_credentials(self) -> None:
        result = qr_wifi("OrzedGuest", password="welcome2025", encryption="WPA")
        assert result.ok is True
        assert result.data
        assert "WIFI:T:WPA" in result.data.payload_preview
        assert "OrzedGuest" in result.data.payload_preview

    def test_nopass_omits_password_field(self) -> None:
        result = qr_wifi("OpenAP", encryption="NOPASS")
        assert result.ok is True
        assert result.data
        assert "T:nopass" in result.data.payload_preview
        assert "P:" not in result.data.payload_preview

    def test_invalid_encryption_rejected(self) -> None:
        result = qr_wifi("AnyAP", password="x", encryption="ROT13")  # type: ignore[arg-type]
        assert result.ok is False
        assert result.error and result.error.code == "INVALID_INPUT"

    def test_empty_ssid_rejected(self) -> None:
        result = qr_wifi("")
        assert result.ok is False
        assert result.error and result.error.code == "INVALID_INPUT"

    def test_special_chars_in_ssid_are_escaped(self) -> None:
        result = qr_wifi('Office;Guest', password='pa,ss;wd:"x"', encryption="WPA")
        assert result.ok is True
        # Escapes are visible in the WIFI string; raw `;` after the SSID name
        # should be backslash-escaped.
        assert result.data
        assert "Office\\;Guest" in result.data.payload_preview

    def test_remote_fallback_forbidden_for_wifi(self, monkeypatch) -> None:
        from qrforge.core import qr as qr_module

        monkeypatch.setattr(qr_module, "_generate_local_png", lambda *a, **kw: None)
        result = qr_wifi("AnyAP", password="x")
        assert result.ok is False
        assert result.error and result.error.code == "UNSUPPORTED"
        assert "wifi" in result.error.message_en.lower()


# ──────────────────────────────────────────────────────────────────────────────
# qr_vcard
# ──────────────────────────────────────────────────────────────────────────────
class TestQrVcard:
    def test_minimal_vcard(self) -> None:
        result = qr_vcard("Ada Lovelace")
        assert result.ok is True
        assert result.data
        assert "BEGIN:VCARD" in result.data.payload_preview

    def test_full_vcard(self) -> None:
        result = qr_vcard(
            "Ada Lovelace",
            phone="+44 20 7946 0958",
            email="ada@example.org",
            org="Analytical Engine Co.",
            title="Mathematician",
            url="https://example.org/ada",
        )
        assert result.ok is True

    def test_invalid_email_rejected(self) -> None:
        result = qr_vcard("Ada", email="not-an-email")
        assert result.ok is False
        assert result.error and result.error.code == "INVALID_INPUT"

    def test_invalid_phone_rejected(self) -> None:
        result = qr_vcard("Ada", phone="abc")
        assert result.ok is False
        assert result.error and result.error.code == "INVALID_INPUT"

    def test_invalid_url_rejected(self) -> None:
        result = qr_vcard("Ada", url="not-a-url")
        assert result.ok is False
        assert result.error and result.error.code == "INVALID_INPUT"

    def test_remote_fallback_forbidden_for_vcard(self, monkeypatch) -> None:
        from qrforge.core import qr as qr_module

        monkeypatch.setattr(qr_module, "_generate_local_png", lambda *a, **kw: None)
        result = qr_vcard("Ada")
        assert result.ok is False
        assert result.error and result.error.code == "UNSUPPORTED"


# ──────────────────────────────────────────────────────────────────────────────
# Payload formatting helpers
# ──────────────────────────────────────────────────────────────────────────────
class TestPayloadFormatters:
    def test_wifi_payload_basic(self) -> None:
        out = _wifi_payload("MyAP", "secret", "WPA", False)
        assert out == "WIFI:T:WPA;S:MyAP;P:secret;H:false;;"

    def test_wifi_payload_hidden_true(self) -> None:
        out = _wifi_payload("MyAP", "secret", "WPA", True)
        assert "H:true" in out

    def test_vcard_payload_includes_optional_fields(self) -> None:
        out = _vcard_payload("Ada", "+1 555 0100", "ada@x.org", "Org", "T", "https://x.org")
        assert "BEGIN:VCARD" in out
        assert "FN:Ada" in out
        assert "ORG:Org" in out
        assert "TEL:+1 555 0100" in out
        assert "EMAIL:ada@x.org" in out
        assert "END:VCARD" in out

    def test_vcard_payload_strips_newlines(self) -> None:
        out = _vcard_payload("Ada\nLovelace", "", "", "Some\r\nOrg", "", "", )
        assert "Ada Lovelace" in out
        assert "Some Org" in out


# ──────────────────────────────────────────────────────────────────────────────
# Language / i18n
# ──────────────────────────────────────────────────────────────────────────────
class TestI18n:
    def test_language_tr_returns_turkish_error(self) -> None:
        result = qr_text("", language="tr")
        assert result.error
        assert result.error.message_tr == "QR verisi boş."
        # message_en is always populated regardless of caller language
        assert result.error.message_en == "QR payload is empty."

    def test_unknown_language_falls_back_to_english(self) -> None:
        result = qr_text("", language="xx")
        assert result.error
        assert result.error.message_en == "QR payload is empty."

    def test_message_tr_always_populated(self) -> None:
        # Repo-wide rule: message_tr is required even when caller language is en.
        result = qr_text("")
        assert result.error and result.error.message_tr.strip() != ""
