# sitepulse

> DNS, RDAP, TLS certificate, and HTTP/HTTPS health snapshot for a domain.

Part of [mcp-essentials](../README.md).

## What it does

One MCP tool: `inspect(domain, checks?, language)` returning `Result[DomainHealth]`.

- **DNS**: A, AAAA, CNAME, MX, TXT, NS, SPF, DMARC (DNS-over-HTTPS via Cloudflare).
- **RDAP**: registrar, registration date, expiry, name servers (via rdap.org bootstrap).
- **TLS**: issuer, subject, validity, SAN, days until expiry — parsed with `cryptography` so locale doesn't matter.
- **HTTP/HTTPS**: status, response time, server header, HSTS.

`checks` lets you opt out of slow checks (`["dns","ssl"]`).

The eTLD+1 (registered domain) is computed via `tldextract` so modern gTLDs (`.dev`, `.io`, `.ai`, `.xyz`, …) are handled correctly.

## Install — Open WebUI

Paste [`./owui.py`](./owui.py) into Admin → Tools.

## Install — Claude Desktop / Cursor / Cline

```json
{
  "mcpServers": {
    "sitepulse": {
      "command": "python",
      "args": ["-m", "sitepulse"],
      "cwd": "/absolute/path/to/mcp-essentials",
      "env": { "PYTHONPATH": "/absolute/path/to/mcp-essentials" }
    }
  }
}
```

## License

Apache 2.0 — see [../LICENSE](../LICENSE).

---

*Part of mcp-essentials by [Orzed](https://orzed.com).*
