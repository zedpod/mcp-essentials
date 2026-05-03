"""Unit tests for pagesignal.core.audit with respx-mocked HTTP."""

import respx
from httpx import Response

from pagesignal.core import audit_page
from pagesignal.tests.conftest import JS_HEAVY_PLACEHOLDER, SAMPLE_HTML, SHORT_HTML_NO_TITLE


@respx.mock
def test_happy_path_extracts_meta_and_geo():
    respx.get("https://example.com/hosting").mock(
        return_value=Response(200, text=SAMPLE_HTML, headers={"content-type": "text/html"})
    )
    r = audit_page("https://example.com/hosting", target_keywords=["hosting", "wordpress"])
    assert r.ok, r.error
    a = r.data
    assert a is not None
    assert a.meta_tags.title and "Hosting" in a.meta_tags.title
    assert a.headings.h1_count == 1
    assert a.headings.h2_count == 2
    assert a.geo_signals.has_faq_schema
    assert "FAQPage" in a.geo_signals.schema_types
    # Question-style headings detected via the en lexicon.
    assert any("What is" in q or "Why choose" in q for q in a.geo_signals.question_headings)
    assert a.geo_signals.keywords_found.get("hosting", 0) >= 1


@respx.mock
def test_invalid_url_rejected():
    r = audit_page("not-a-url")
    assert not r.ok
    assert r.error and r.error.code == "INVALID_INPUT"
    # Repo invariant: both languages populated.
    assert r.error.message_en and r.error.message_tr


@respx.mock
def test_empty_url_rejected():
    r = audit_page("")
    assert not r.ok
    assert r.error and r.error.code == "INVALID_INPUT"


@respx.mock
def test_unsupported_content_type():
    respx.get("https://example.com/file.pdf").mock(
        return_value=Response(200, content=b"%PDF...", headers={"content-type": "application/pdf"})
    )
    r = audit_page("https://example.com/file.pdf")
    assert not r.ok
    assert r.error and r.error.code == "UNSUPPORTED"


@respx.mock
def test_network_failure_returns_upstream_error():
    respx.get("https://broken.example/page").mock(
        return_value=Response(503, text="busy"),
    )
    r = audit_page("https://broken.example/page")
    assert not r.ok
    assert r.error and r.error.code in ("UPSTREAM_ERROR", "NETWORK_TIMEOUT")


@respx.mock
def test_short_html_flags_missing_title_issue():
    respx.get("https://example.com/empty").mock(
        return_value=Response(200, text=SHORT_HTML_NO_TITLE, headers={"content-type": "text/html"})
    )
    r = audit_page("https://example.com/empty")
    assert r.ok
    codes = {i.code for i in r.data.issues}
    assert "empty_title" in codes
    assert "no_h1" in codes


@respx.mock
def test_js_heavy_page_flags_warning():
    respx.get("https://app.example/").mock(
        return_value=Response(200, text=JS_HEAVY_PLACEHOLDER, headers={"content-type": "text/html"})
    )
    r = audit_page("https://app.example/")
    assert r.ok
    codes = {i.code for i in r.data.issues}
    assert "javascript_heavy" in codes


@respx.mock
def test_noindex_flagged_as_error():
    html = '<!doctype html><html lang="en"><head><title>X' + "x"*40 + '</title>'
    html += '<meta name="description" content="' + "y"*80 + '">'
    html += '<meta name="robots" content="noindex,follow"></head><body><h1>Hi</h1></body></html>'
    respx.get("https://noidx.example/").mock(
        return_value=Response(200, text=html, headers={"content-type": "text/html"})
    )
    r = audit_page("https://noidx.example/")
    assert r.ok
    issues = {i.code: i for i in r.data.issues}
    assert "noindex" in issues
    assert issues["noindex"].severity == "error"


@respx.mock
def test_language_tr_returns_turkish_messages():
    r = audit_page("not-a-url", language="tr")
    assert r.error and "http" in r.error.message_tr.lower()


@respx.mock
def test_unknown_language_falls_back_to_en():
    r = audit_page("not-a-url", language="xx")
    assert r.error and "http" in r.error.message_en.lower()
