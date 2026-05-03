"""signalbrief Pydantic models."""

from datetime import datetime
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


class NewsItem(BaseModel):
    title: str
    link: str | None = None
    summary: str | None = None
    source: str
    published: datetime | None = None
    score: int = 0
    matched_keywords: list[str] = Field(default_factory=list)


class SourceFailure(BaseModel):
    name: str
    url: str
    error: str


class NewsBrief(BaseModel):
    items: list[NewsItem]
    sources_used: list[str]
    failed_sources: list[SourceFailure] = Field(default_factory=list)
    keywords: list[str]
    hours_back: int


class SourceInfo(BaseModel):
    name: str
    url: str
    language: str | None = None


class SourceCatalog(BaseModel):
    sources: list[SourceInfo]
