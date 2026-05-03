"""flighthunter Pydantic models."""

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
    "MISSING_API_KEY",
]

TripType = Literal["round_trip", "one_way", "multi_city"]
CabinClass = Literal["economy", "premium_economy", "business", "first"]


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


class FlightLeg(BaseModel):
    airline: str | None = None
    flight_number: str | None = None
    departure_airport: str | None = None
    arrival_airport: str | None = None
    departure_time: str | None = None
    arrival_time: str | None = None
    duration_minutes: int | None = None
    travel_class: str | None = None
    aircraft: str | None = None


class FlightOption(BaseModel):
    price: float | None = None
    currency: str | None = None
    total_duration_minutes: int | None = None
    stops: int = 0
    layover_airports: list[str] = Field(default_factory=list)
    legs: list[FlightLeg] = Field(default_factory=list)
    booking_token: str | None = None
    type: str | None = None


class PriceInsight(BaseModel):
    lowest: float | None = None
    typical_low: float | None = None
    typical_high: float | None = None
    price_level: str | None = None  # "low" | "typical" | "high"


class FlightSearch(BaseModel):
    origin: str
    destination: str
    departure_date: Date
    return_date: Date | None = None
    trip_type: TripType
    cabin_class: CabinClass
    adults: int
    children: int = 0
    infants: int = 0
    currency: str
    options: list[FlightOption] = Field(default_factory=list)
    price_insight: PriceInsight | None = None
    search_url: str | None = None
