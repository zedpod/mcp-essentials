"""DNS-over-HTTPS lookups via Cloudflare's resolver."""

from .http import UpstreamError, get_with_retry
from .types import DnsResults

DOH_ENDPOINT = "https://cloudflare-dns.com/dns-query"


def _fetch(client, host: str, record_type: str) -> list[str]:
    try:
        r = get_with_retry(
            client,
            DOH_ENDPOINT,
            params={"name": host, "type": record_type},
            headers={"Accept": "application/dns-json"},
        )
    except UpstreamError:
        return []
    except Exception:
        return []
    if r.status_code != 200:
        return []
    try:
        data = r.json()
    except ValueError:
        return []
    out = []
    for ans in data.get("Answer") or []:
        d = ans.get("data")
        if d:
            out.append(str(d).strip().rstrip("."))
    return out


def fetch_all(client, host: str) -> DnsResults:
    a = _fetch(client, host, "A")
    aaaa = _fetch(client, host, "AAAA")
    cname = _fetch(client, host, "CNAME")
    mx_raw = _fetch(client, host, "MX")
    txt_raw = _fetch(client, host, "TXT")
    ns = _fetch(client, host, "NS")

    mx = [m for m in mx_raw if m]
    txt = [t.strip('"') for t in txt_raw if t]

    spf = next((t for t in txt if t.lower().startswith("v=spf1")), None)

    dmarc_records = _fetch(client, f"_dmarc.{host}", "TXT")
    dmarc = next(
        (t.strip('"') for t in dmarc_records if t.strip('"').lower().startswith("v=dmarc1")),
        None,
    )

    return DnsResults(
        a=a, aaaa=aaaa, cname=cname, mx=mx, txt=txt, ns=ns,
        spf_record=spf, dmarc_record=dmarc,
    )
