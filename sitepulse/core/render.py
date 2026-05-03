"""Markdown rendering for sitepulse DomainHealth."""

from .i18n import t
from .types import DomainHealth, Result


def to_markdown(result: Result[DomainHealth], lang: str = "en") -> str:
    if not result.ok or result.data is None:
        if result.error is None:
            return f"**Error**: unknown failure (lang={lang})"
        msg = result.error.message_tr if lang == "tr" else result.error.message_en
        return f"**Error** ({result.error.code}): {msg}"

    h = result.data
    parts: list[str] = [
        f"# {t('title', lang)}",
        "",
        f"**{t('label.host', lang)}**: `{h.host}`  •  "
        f"**{t('label.registered_domain', lang)}**: `{h.registered_domain}`",
    ]

    if h.dns:
        parts += [
            "",
            f"## {t('section.dns', lang)}",
            f"- A: {', '.join(f'`{x}`' for x in h.dns.a) or t('label.no_records', lang)}",
            f"- AAAA: {', '.join(f'`{x}`' for x in h.dns.aaaa) or t('label.no_records', lang)}",
            f"- MX: {', '.join(f'`{x}`' for x in h.dns.mx) or t('label.no_records', lang)}",
            f"- NS: {', '.join(f'`{x}`' for x in h.dns.ns) or t('label.no_records', lang)}",
            f"- SPF: `{h.dns.spf_record or '-'}`",
            f"- DMARC: `{h.dns.dmarc_record or '-'}`",
        ]

    if h.rdap and h.rdap.ok:
        parts += [
            "",
            f"## {t('section.rdap', lang)}",
            f"- **{t('label.registrar', lang)}**: {h.rdap.registrar or '-'}",
            f"- **{t('label.registered_on', lang)}**: "
            f"`{h.rdap.registered_on.isoformat() if h.rdap.registered_on else '-'}`",
            f"- **{t('label.expires_on', lang)}**: "
            f"`{h.rdap.expires_on.isoformat() if h.rdap.expires_on else '-'}`",
            f"- **{t('label.name_servers', lang)}**: "
            f"{', '.join(f'`{n}`' for n in h.rdap.name_servers) or '-'}",
        ]

    if h.ssl:
        if h.ssl.ok:
            expiry_line = (
                f"`{h.ssl.not_after.isoformat()}`"
                if h.ssl.not_after else "-"
            )
            parts += [
                "",
                f"## {t('section.ssl', lang)}",
                f"- Issuer: `{h.ssl.issuer or '-'}`",
                f"- Subject: `{h.ssl.subject or '-'}`",
                f"- {t('label.expires_on', lang)}: {expiry_line}  "
                f"({t('label.expires_in', lang)} `{h.ssl.days_until_expiry}` "
                f"{t('label.days', lang)})",
            ]
        else:
            parts += [
                "",
                f"## {t('section.ssl', lang)}",
                f"- ❌ {h.ssl.error}",
            ]

    if h.https:
        parts += [
            "",
            f"## {t('section.https', lang)}",
            f"- {h.https.url} → "
            f"`{h.https.status_code or '?'}` "
            + (f"({h.https.response_time_ms} ms)" if h.https.response_time_ms else "")
            + (f" via `{h.https.server}`" if h.https.server else ""),
        ]
        if h.https.error:
            parts.append(f"- ❌ {h.https.error}")
        elif h.https.hsts:
            parts.append(f"- HSTS: `{h.https.hsts}`")
    if h.http:
        parts += [
            "",
            f"## {t('section.http', lang)}",
            f"- {h.http.url} → `{h.http.status_code or '?'}`",
        ]

    parts += ["", f"## {t('section.issues', lang)}"]
    if h.issues:
        parts.extend(f"- ⚠︎ {i}" for i in h.issues)
    else:
        parts.append("_no issues_")

    parts += ["", f"_{t('note.audit', lang)}_"]
    return "\n".join(parts)
