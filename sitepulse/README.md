# sitepulse

> DNS, RDAP, TLS certificate, and HTTP/HTTPS health snapshot for a domain.

Part of [mcp-essentials](../README.md).

## What it does

One MCP tool: `inspect(domain, checks?, language)` returning `Result[DomainHealth]`.

- **DNS**: A, AAAA, CNAME, MX, TXT, NS, SPF, DMARC (DNS-over-HTTPS via Cloudflare).
- **RDAP**: registrar, registration date, expiry, name servers (via rdap.org bootstrap).
- **TLS**: issuer, subject, validity, SAN, days until expiry - parsed with `cryptography` so locale doesn't matter.
- **HTTP/HTTPS**: status, response time, server header, HSTS.

`checks` lets you opt out of slow checks (`["dns","ssl"]`).

The eTLD+1 (registered domain) is computed via `tldextract` so modern gTLDs (`.dev`, `.io`, `.ai`, `.xyz`, …) are handled correctly.

## Install - Open WebUI

1. Paste [`./owui.py`](./owui.py) into Admin → Tools.
2. Description field (optional - docstrings already carry bilingual EN/TR triggers):
   ```text
   Snapshot a domain's health: DNS, RDAP, TLS certificate, HTTP/HTTPS reachability.

   Use when the user provides a domain or URL and asks about:
   - DNS records (A / AAAA / MX / TXT / NS / SPF / DMARC)
   - SSL/TLS certificate (issuer, expiry, SAN)
   - registrar / registration date / expiry (RDAP)
   - HTTP / HTTPS reachability and headers

   Do NOT use for: page-content / SEO audit (use pagesignal), WHOIS history older than now, port scans, or subdomain enumeration.
   ```
3. Configure Valves (`DEFAULT_LANGUAGE`, `TIMEOUT_SECONDS`).

## Install - Claude Desktop / Cursor / Cline

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

Apache 2.0 - see [../LICENSE](../LICENSE).

---

*Part of mcp-essentials by [Orzed](https://orzed.com).*
