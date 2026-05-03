"""Top-level orchestrator: inspect(domain, checks)."""

import time
from concurrent.futures import ThreadPoolExecutor

from . import dns as dns_mod
from . import rdap as rdap_mod
from . import ssl_check
from .domain import normalize_host, registered_domain
from .http import build_client, get_with_retry
from .i18n import normalize_lang, t
from .types import (
    DomainHealth,
    ErrorInfo,
    HttpProbe,
    Result,
)

ALL_CHECKS = ("dns", "rdap", "ssl", "http")


def _err(code: str, lang: str, en_key: str) -> ErrorInfo:
    return ErrorInfo(
        code=code,
        message_en=t(en_key, "en"),
        message_tr=t(en_key, "tr"),
    )


def _http_probe(client, scheme: str, host: str) -> HttpProbe:
    url = f"{scheme}://{host}/"
    started = time.monotonic()
    try:
        r = get_with_retry(client, url)
    except Exception as exc:
        return HttpProbe(url=url, error=f"{type(exc).__name__}: {exc}")
    elapsed_ms = int((time.monotonic() - started) * 1000)
    return HttpProbe(
        url=url,
        status_code=r.status_code,
        final_url=str(r.url),
        redirects=len(r.history),
        response_time_ms=elapsed_ms,
        server=r.headers.get("server"),
        content_type=r.headers.get("content-type"),
        hsts=r.headers.get("strict-transport-security"),
    )


def inspect(
    domain: str,
    checks: list[str] | None = None,
    *,
    language: str = "en",
    timeout_seconds: float = 6.0,
) -> Result[DomainHealth]:
    lang = normalize_lang(language)

    if not domain:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.empty_input"))
    host = normalize_host(domain)
    if not host:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_input"))
    reg = registered_domain(host)

    requested = list(dict.fromkeys(checks or list(ALL_CHECKS)))
    invalid = [c for c in requested if c not in ALL_CHECKS]
    if invalid:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_input"))

    client = build_client(timeout=timeout_seconds)
    try:
        results: dict[str, object] = {}

        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = {}
            if "dns" in requested:
                futures["dns"] = pool.submit(dns_mod.fetch_all, client, host)
            if "rdap" in requested:
                futures["rdap"] = pool.submit(rdap_mod.fetch, client, reg)
            if "ssl" in requested:
                futures["ssl"] = pool.submit(ssl_check.fetch_cert, host)
            if "http" in requested:
                futures["http"] = pool.submit(_http_probe, client, "http", host)
                futures["https"] = pool.submit(_http_probe, client, "https", host)

            for key, fut in futures.items():
                try:
                    results[key] = fut.result(timeout=timeout_seconds + 5)
                except Exception as exc:
                    results[key] = exc

        issues: list[str] = []
        dns_obj = results.get("dns")
        if dns_obj is not None and not isinstance(dns_obj, Exception):
            if not dns_obj.a and not dns_obj.aaaa:
                issues.append(t("issue.no_a_records", lang))
            if not dns_obj.spf_record:
                issues.append(t("issue.no_spf", lang))
            if not dns_obj.dmarc_record:
                issues.append(t("issue.no_dmarc", lang))

        ssl_obj = results.get("ssl")
        if ssl_obj is not None and not isinstance(ssl_obj, Exception) and ssl_obj.ok:
            if ssl_obj.days_until_expiry is not None:
                if ssl_obj.days_until_expiry < 0:
                    issues.append(t("issue.cert_expired", lang))
                elif ssl_obj.days_until_expiry < 14:
                    issues.append(t("issue.cert_expiring_soon", lang, days=ssl_obj.days_until_expiry))

        https_obj = results.get("https")
        if https_obj is not None and not isinstance(https_obj, Exception):
            if https_obj.error or (https_obj.status_code and https_obj.status_code >= 500):
                issues.append(t("issue.https_unreachable", lang))
            elif not https_obj.hsts:
                issues.append(t("issue.no_hsts", lang))

        health = DomainHealth(
            input=domain,
            host=host,
            registered_domain=reg,
            dns=dns_obj if not isinstance(dns_obj, Exception) else None,
            rdap=results.get("rdap") if not isinstance(results.get("rdap"), Exception) else None,
            ssl=ssl_obj if not isinstance(ssl_obj, Exception) else None,
            http=results.get("http") if not isinstance(results.get("http"), Exception) else None,
            https=https_obj if not isinstance(https_obj, Exception) else None,
            issues=issues,
        )
        return Result(ok=True, data=health, meta={"host": host, "registered_domain": reg})
    finally:
        client.close()
