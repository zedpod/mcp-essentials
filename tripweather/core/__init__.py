"""tripweather.core — pure logic."""

from .forecast import forecast, forecast_by_query
from .geocode import geocode
from .i18n import DEFAULT, SUPPORTED, normalize_lang, t
from .render import to_markdown
from .types import (
    ErrorInfo,
    ForecastDay,
    ForecastResult,
    GeocodeCandidate,
    GeocodeResult,
    Result,
)

__bundle_order__ = ["types", "i18n", "wmo", "http", "geocode", "forecast", "render"]

__all__ = [
    "geocode",
    "forecast",
    "forecast_by_query",
    "to_markdown",
    "Result",
    "GeocodeCandidate",
    "GeocodeResult",
    "ForecastDay",
    "ForecastResult",
    "ErrorInfo",
    "t",
    "normalize_lang",
    "SUPPORTED",
    "DEFAULT",
]
