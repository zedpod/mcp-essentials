"""RDAP lookup via the bootstrap registry."""

from datetime import datetime

from .http import UpstreamError, get_with_retry
from .types import RdapInfo

RDAP_BOOTSTRAP = "https://rdap.org/domain"


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        # rdap.org returns ISO-8601 with Z; fromisoformat in 3.11+ accepts that.
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def fetch(client, registered: str) -> RdapInfo:
    if not registered:
        return RdapInfo(ok=False, error="no domain")
    try:
        r = get_with_retry(
            client,
            f"{RDAP_BOOTSTRAP}/{registered}",
            headers={"Accept": "application/rdap+json, application/json"},
        )
    except UpstreamError as exc:
        return RdapInfo(ok=False, error=f"upstream {exc.status}")
    except Exception as exc:
        return RdapInfo(ok=False, error=f"{type(exc).__name__}: {exc}")
    if r.status_code != 200:
        return RdapInfo(ok=False, error=f"http {r.status_code}")
    try:
        data = r.json()
    except ValueError:
        return RdapInfo(ok=False, error="parse")

    registrar = None
    for entity in data.get("entities") or []:
        roles = [r.lower() for r in (entity.get("roles") or [])]
        if "registrar" not in roles:
            continue
        vcard = entity.get("vcardArray")
        if isinstance(vcard, list) and len(vcard) > 1:
            for tag in vcard[1]:
                if isinstance(tag, list) and tag and tag[0] == "fn" and len(tag) >= 4:
                    registrar = tag[3]
                    break

    registered_on = None
    expires_on = None
    for ev in data.get("events") or []:
        action = (ev.get("eventAction") or "").lower()
        date = _parse_iso(ev.get("eventDate"))
        if action == "registration":
            registered_on = date
        elif action in ("expiration", "expires"):
            expires_on = date

    name_servers: list[str] = []
    for ns in data.get("nameservers") or []:
        if isinstance(ns, dict):
            name = ns.get("ldhName") or ns.get("unicodeName")
            if name:
                name_servers.append(name)

    return RdapInfo(
        ok=True,
        registrar=registrar,
        registered_on=registered_on,
        expires_on=expires_on,
        name_servers=name_servers,
        status=list(data.get("status") or []),
    )
