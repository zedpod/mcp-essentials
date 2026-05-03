# AGENTS.md - sitepulse

> Read with [`../AGENTS.md`](../AGENTS.md).

## Public surface
- `inspect(domain, checks=None, *, language="en", timeout_seconds=6.0)` → `Result[DomainHealth]`

## Architecture
- `core/domain.py` - host normalization + eTLD+1 via `tldextract` (Public Suffix List).
- `core/dns.py` - DNS-over-HTTPS via Cloudflare. Returns `DnsResults` (A, AAAA, CNAME, MX, TXT, NS, SPF, DMARC).
- `core/ssl_check.py` - raw socket + `cryptography` for cert parsing. Locale-independent.
- `core/rdap.py` - RDAP via rdap.org bootstrap.
- `core/checks.py` - orchestrator using `ThreadPoolExecutor` to run independent checks in parallel.

## Edge cases
- **IDN domains** - pass Punycode (`xn--…`) explicitly. `tldextract` doesn't IDN-encode for you.
- **Unreachable host** - DNS still tries; HTTP/HTTPS probes will surface `error`.
- **Old/unknown TLDs** - `tldextract` keeps PSL fresh; first run downloads it. To work offline, set `TLDEXTRACT_CACHE` or call `tldextract.extract(suffix_list_urls=())`.
- **No `from __future__ import annotations`** in core modules using Pydantic generics.

## Tests
- `tests/test_core.py` - unit tests with respx-mocked DOH; pure helpers exercised separately.
- `tests/test_owui.py` / `tests/test_server.py` - bundle/MCP smoke.
- `tests/test_integration.py` - `RUN_LIVE=1`.
