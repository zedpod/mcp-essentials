"""tripweather Pydantic models."""

from datetime import date as Date
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)

ErrorCode = Literal[
    "INVALID_INPUT",
    "NOT_FOUND",
    "RATE_LIMITED",
    "NETWORK_TIMEOUT",
    "UPSTREAM_ERROR",
    "UNSUPPORTED",
    "PARSE_ERROR",
    "TIMEOUT",
    "CANCELLED",
    "INTERNAL",
]

Units = Literal["metric", "imperial"]


class ErrorInfo(BaseModel):
    code: ErrorCode
    message_en: str
    message_tr: str
    hint: str | None = None
    upstream: str | None = None
    retry_after_s: float | None = None


class Result(BaseModel, Generic[T]):
    ok: bool
    data: T | None = None
    error: ErrorInfo | None = None
    meta: dict = Field(default_factory=dict)


class GeocodeCandidate(BaseModel):
    name: str
    country_code: str | None = None
    country: str | None = None
    admin1: str | None = None
    admin2: str | None = None
    latitude: float
    longitude: float
    timezone: str | None = None
    population: int | None = None
    elevation: float | None = None
    score: float = 0.0


class GeocodeResult(BaseModel):
    query: str
    candidates: list[GeocodeCandidate]


class ForecastDay(BaseModel):
    date: Date
    weather_code: int | None = None
    weather_label: str | None = None
    max_temp: float | None = None
    min_temp: float | None = None
    precipitation: float | None = None
    precipitation_probability: int | None = None
    wind_speed: float | None = None
    humidity: int | None = None
    sunrise: str | None = None
    sunset: str | None = None
    uv_index: float | None = None


class ForecastResult(BaseModel):
    latitude: float
    longitude: float
    timezone: str | None = None
    units: Units
    days: list[ForecastDay]
    place_name: str | None = None
    country_code: str | None = None
