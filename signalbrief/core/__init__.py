"""signalbrief.core - pure logic."""

from .brief import collect, list_sources
from .i18n import DEFAULT, SUPPORTED, normalize_lang, t
from .render import to_markdown
from .types import (
    ErrorInfo,
    NewsBrief,
    NewsItem,
    Result,
    SourceCatalog,
    SourceFailure,
    SourceInfo,
)

__bundle_order__ = ["types", "i18n", "sources", "tokens", "feed", "brief", "render"]

__all__ = [
    "collect",
    "list_sources",
    "to_markdown",
    "Result",
    "NewsBrief",
    "NewsItem",
    "SourceCatalog",
    "SourceInfo",
    "SourceFailure",
    "ErrorInfo",
    "t",
    "normalize_lang",
    "SUPPORTED",
    "DEFAULT",
]
