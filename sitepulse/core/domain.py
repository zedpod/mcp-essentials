"""Domain parsing - uses tldextract (which keeps the Public Suffix List fresh)."""

import urllib.parse


def normalize_host(input_str: str) -> str | None:
    """Strip schemes, ports, paths, and lowercase. Returns None if nothing usable."""
    if not input_str:
        return None
    raw = input_str.strip().rstrip("/")
    if "://" in raw:
        try:
            parsed = urllib.parse.urlparse(raw)
            host = parsed.hostname or ""
        except ValueError:
            return None
    else:
        host = raw
    host = host.split("/")[0].split("@")[-1].split(":")[0].strip(".")
    if not host or " " in host:
        return None
    return host.lower()


def registered_domain(host: str) -> str:
    """Return the registered domain (eTLD+1) for a host using tldextract.

    Falls back to the dotted-pair if tldextract is unavailable or the host
    looks like an IP/raw token.
    """
    if not host:
        return host
    try:
        import tldextract

        ext = tldextract.extract(host)
        if ext.domain and ext.suffix:
            return f"{ext.domain}.{ext.suffix}"
        return ext.domain or host
    except Exception:
        parts = host.split(".")
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return host
