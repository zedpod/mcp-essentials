"""sitepulse.core — pure logic."""

from .checks import inspect
from .domain import normalize_host, registered_domain
from .i18n import DEFAULT, SUPPORTED, normalize_lang, t
from .render import to_markdown
from .types import (
    DnsResults,
    DomainHealth,
    ErrorInfo,
    HttpProbe,
    RdapInfo,
    Result,
    SslCert,
)

__bundle_order__ = ["types", "i18n", "domain", "http", "dns", "ssl_check", "rdap", "checks", "render"]

__all__ = [
    "inspect",
    "to_markdown",
    "normalize_host",
    "registered_domain",
    "Result",
    "DomainHealth",
    "DnsResults",
    "SslCert",
    "RdapInfo",
    "HttpProbe",
    "ErrorInfo",
    "t",
    "normalize_lang",
    "SUPPORTED",
    "DEFAULT",
]
