"""Pydantic models for pagesignal."""

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

IssueSeverity = Literal["info", "warning", "error"]


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


class MetaTags(BaseModel):
    title: str | None = None
    title_length: int = 0
    description: str | None = None
    description_length: int = 0
    canonical: str | None = None
    robots: str | None = None
    og_title: str | None = None
    og_description: str | None = None
    og_image: str | None = None
    twitter_card: str | None = None
    lang: str | None = None
    charset: str | None = None


class HeadingsInfo(BaseModel):
    h1_count: int = 0
    h1_texts: list[str] = Field(default_factory=list)
    h2_count: int = 0
    h2_texts: list[str] = Field(default_factory=list)
    h3_count: int = 0
    skipped_levels: list[str] = Field(default_factory=list)


class Readability(BaseModel):
    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    detected_language: str | None = None


class GeoSignals(BaseModel):
    """Signals that indicate AI-answer readiness (GEO = generative engine optimization)."""

    has_faq_schema: bool = False
    has_question_schema: bool = False
    has_howto_schema: bool = False
    has_article_schema: bool = False
    schema_types: list[str] = Field(default_factory=list)
    question_headings: list[str] = Field(default_factory=list)
    answers_first_mode: bool = False  # Heading immediately followed by direct answer text
    keywords_found: dict[str, int] = Field(default_factory=dict)


class Performance(BaseModel):
    bytes_total: int = 0
    bytes_html: int = 0
    response_time_ms: int = 0
    redirect_count: int = 0
    final_url: str | None = None
    status_code: int = 0


class Issue(BaseModel):
    severity: IssueSeverity
    code: str
    message_en: str
    message_tr: str


class PageAudit(BaseModel):
    url: str
    final_url: str
    meta_tags: MetaTags
    headings: HeadingsInfo
    readability: Readability
    geo_signals: GeoSignals
    performance: Performance
    issues: list[Issue]
