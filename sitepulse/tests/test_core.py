"""sitepulse unit tests for the pure helpers."""

import respx
from httpx import Response

from sitepulse.core import inspect
from sitepulse.core.dns import fetch_all
from sitepulse.core.domain import normalize_host, registered_domain
from sitepulse.core.http import build_client


class TestDomainParsing:
    def test_normalize_with_scheme(self):
        assert normalize_host("https://Foo.example.COM/about?x=1") == "foo.example.com"

    def test_normalize_bare(self):
        assert normalize_host("foo.example.com") == "foo.example.com"

    def test_normalize_with_port(self):
        assert normalize_host("foo.example.com:8443") == "foo.example.com"

    def test_normalize_empty(self):
        assert normalize_host("") is None
        assert normalize_host(None) is None  # type: ignore[arg-type]

    def test_registered_modern_gtld(self):
        assert registered_domain("api.dev.orzed.io") == "orzed.io"
        assert registered_domain("docs.example.dev") == "example.dev"

    def test_registered_compound(self):
        assert registered_domain("a.b.example.co.uk") == "example.co.uk"


class TestDns:
    @respx.mock
    def test_happy_path_minimal(self):
        respx.get("https://cloudflare-dns.com/dns-query", params={"name": "orzed.com", "type": "A"}).mock(
            return_value=Response(200, json={"Status": 0, "Answer": [{"data": "1.2.3.4"}]})
        )
        respx.get("https://cloudflare-dns.com/dns-query").mock(
            return_value=Response(200, json={"Status": 0})
        )
        client = build_client()
        try:
            res = fetch_all(client, "orzed.com")
            assert "1.2.3.4" in res.a
        finally:
            client.close()


class TestInspect:
    def test_invalid_domain(self):
        r = inspect("")
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_invalid_check_name(self):
        r = inspect("example.com", checks=["dns", "bogus"])
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_dns_only_runs_just_dns(self):
        # respx not mocked — DNS will fail to connect; we only assert that
        # the result envelope is shaped right and other checks were skipped.
        r = inspect("nope.invalid", checks=["dns"], timeout_seconds=0.5)
        assert r.ok
        assert r.data and r.data.dns is not None
        assert r.data.https is None  # http check wasn't requested
        assert r.data.ssl is None
        assert r.data.rdap is None

    def test_language_tr_renders_turkish_error(self):
        r = inspect("", language="tr")
        assert r.error and "URL" in r.error.message_tr
