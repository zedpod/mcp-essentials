"""Pydantic models shared across currencypulse.core."""

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


class Rate(BaseModel):
    base: str
    quote: str
    value: float = Field(description="Decimal rate, base→quote.")
    on_date: Date
    source: str = Field(description="Provider name: frankfurter|exchangerate_host|oxr|tcmb.")


class Conversion(BaseModel):
    base: str
    quote: str
    amount: float
    rate: float
    converted: float
    on_date: Date
    source: str


class SnapshotEntry(BaseModel):
    quote: str
    rate: float
    name: str | None = None


class Snapshot(BaseModel):
    base: str
    on_date: Date
    rates: list[SnapshotEntry]
    source: str


class TimeSeriesPoint(BaseModel):
    on_date: Date
    rate: float


class TimeSeries(BaseModel):
    base: str
    quote: str
    start: Date
    end: Date
    points: list[TimeSeriesPoint]
    source: str
