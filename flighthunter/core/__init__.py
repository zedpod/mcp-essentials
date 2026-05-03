"""flighthunter.core — pure logic."""

from .i18n import DEFAULT, SUPPORTED, normalize_lang, t
from .render import to_markdown
from .search import search_flights
from .types import (
    ErrorInfo,
    FlightLeg,
    FlightOption,
    FlightSearch,
    PriceInsight,
    Result,
)

__bundle_order__ = ["types", "i18n", "http", "search", "render"]

__all__ = [
    "search_flights",
    "to_markdown",
    "Result",
    "FlightSearch",
    "FlightOption",
    "FlightLeg",
    "PriceInsight",
    "ErrorInfo",
    "t",
    "normalize_lang",
    "SUPPORTED",
    "DEFAULT",
]
