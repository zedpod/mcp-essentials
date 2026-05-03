"""Pydantic models for tubescript."""

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

TranscriptFormat = Literal["text", "srt", "vtt", "json"]


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


class AvailableTrack(BaseModel):
    language: str
    language_code: str
    is_generated: bool = False
    is_translatable: bool = False


class TranscriptList(BaseModel):
    video_id: str
    tracks: list[AvailableTrack]


class TranscriptEntry(BaseModel):
    start: float
    duration: float
    text: str


class Transcript(BaseModel):
    video_id: str
    language_code: str
    is_generated: bool
    translated_to: str | None = None
    format: TranscriptFormat
    text: str = Field(description="The formatted transcript content (text/srt/vtt or JSON string).")
    entries: list[TranscriptEntry] = Field(default_factory=list)
    truncated: bool = False
    char_count: int = 0
