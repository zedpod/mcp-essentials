"""pagesignal.core — page-audit logic."""

from .audit import audit_page
from .i18n import DEFAULT, SUPPORTED, normalize_lang, t
from .render import to_markdown
from .types import (
    ErrorInfo,
    GeoSignals,
    HeadingsInfo,
    Issue,
    MetaTags,
    PageAudit,
    Performance,
    Readability,
    Result,
)

__bundle_order__ = ["types", "i18n", "lexicons", "http", "parse", "audit", "render"]

__all__ = [
    "audit_page",
    "to_markdown",
    "Result",
    "PageAudit",
    "MetaTags",
    "HeadingsInfo",
    "Readability",
    "GeoSignals",
    "Performance",
    "Issue",
    "ErrorInfo",
    "t",
    "normalize_lang",
    "SUPPORTED",
    "DEFAULT",
]
