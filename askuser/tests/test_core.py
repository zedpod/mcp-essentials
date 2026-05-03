"""askuser unit tests — validation + overlay JS shape."""

import json

from askuser.core import (
    Answer,
    Option,
    Question,
    Result,
    build_localhost_html,
    build_overlay_js,
    to_markdown,
    validate_question,
)


def _q(**overrides) -> Question:
    base = {
        "prompt": "Pick one",
        "options": [Option(label="Alpha"), Option(label="Beta"), Option(label="Gamma")],
        "mode": "single",
    }
    base.update(overrides)
    return Question(**base)


class TestValidate:
    def test_happy_path(self):
        assert validate_question(_q()) is None

    def test_empty_prompt_rejected(self):
        err = validate_question(_q(prompt="   "))
        assert err and err.code == "INVALID_INPUT"

    def test_select_without_options_rejected(self):
        err = validate_question(_q(options=[]))
        assert err and err.code == "INVALID_INPUT"

    def test_free_text_without_options_ok(self):
        err = validate_question(_q(options=[], mode="free_text"))
        assert err is None

    def test_min_max_inversion_rejected(self):
        err = validate_question(_q(mode="multi", min_select=3, max_select=1))
        assert err and err.code == "INVALID_INPUT"

    def test_max_more_than_options_rejected(self):
        err = validate_question(_q(mode="multi", max_select=99))
        assert err and err.code == "INVALID_INPUT"

    def test_invalid_timeout_rejected(self):
        err = validate_question(_q(timeout_s=0))
        assert err and err.code == "INVALID_INPUT"
        err2 = validate_question(_q(timeout_s=99999))
        assert err2 and err2.code == "INVALID_INPUT"

    def test_tr_language_returns_turkish_error(self):
        err = validate_question(_q(prompt=""), language="tr")
        assert err and "prompt" in err.message_tr.lower()


class TestOverlayJS:
    def test_overlay_owui_includes_prompt(self):
        js = build_overlay_js(_q(), mode="owui")
        assert "Pick one" in js
        assert "Alpha" in js
        # OWUI mode does NOT need a CSRF token in the payload.
        assert "csrf_token" in js

    def test_overlay_localhost_embeds_csrf_token(self):
        js = build_overlay_js(_q(), mode="localhost", csrf_token="abc123")
        assert "abc123" in js

    def test_overlay_payload_round_trips(self):
        # Extract the embedded JSON and ensure it parses cleanly.
        js = build_overlay_js(_q(timeout_s=60.0))
        # Pull the config object — first JSON-looking blob after `var CFG =`.
        marker = "var CFG = "
        start = js.index(marker) + len(marker)
        end = js.index(";", start)
        cfg = json.loads(js[start:end])
        assert cfg["prompt"] == "Pick one"
        assert cfg["timeout_s"] == 60.0
        assert len(cfg["options"]) == 3


class TestLocalhostHTML:
    def test_html_contains_overlay_and_csrf(self):
        html = build_localhost_html(_q(), language="en", csrf_token="zzz")
        assert "<!doctype html>" in html
        assert "Pick one" in html
        assert "zzz" in html
        # The page injects its CSS inline so it survives a same-origin sandbox.
        assert ".au-card" in html


class TestRender:
    def test_render_select_answer(self):
        ans = Answer(type="select", indices=[0, 2], values=["Alpha", "Gamma"])
        out = to_markdown(Result(ok=True, data=ans), lang="en")
        assert "selected" in out.lower()
        assert "`Alpha`" in out and "`Gamma`" in out

    def test_render_skip(self):
        out = to_markdown(Result(ok=True, data=Answer(type="skip")), lang="en")
        assert "did not provide" in out.lower()

    def test_render_custom(self):
        out = to_markdown(
            Result(ok=True, data=Answer(type="custom", custom_text="hello world")),
            lang="en",
        )
        assert "hello world" in out

    def test_render_error(self):
        from askuser.core.types import ErrorInfo

        out = to_markdown(
            Result(ok=False, error=ErrorInfo(code="INVALID_INPUT", message_en="bad", message_tr="kötü")),
            lang="tr",
        )
        assert "kötü" in out
