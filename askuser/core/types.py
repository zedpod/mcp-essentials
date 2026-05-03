"""askuser Pydantic models."""

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

AskMode = Literal["single", "multi", "free_text"]
AnswerType = Literal["select", "custom", "skip", "timeout", "cancelled"]


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


class Option(BaseModel):
    label: str
    description: str | None = None
    value: str | None = None  # defaults to label


class Question(BaseModel):
    """Type-checked container; `validate_question` enforces business rules.

    Pydantic stays type-only here so business errors flow through
    `Result(ok=False, error=...)` rather than raising ValidationError at
    construction time.
    """

    prompt: str
    options: list[Option] = Field(default_factory=list)
    mode: AskMode = "single"
    allow_custom: bool = True
    required: bool = False
    min_select: int | None = None
    max_select: int | None = None
    timeout_s: float = 300.0
    accent: str = "#E8713A"


class Answer(BaseModel):
    type: AnswerType
    indices: list[int] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)
    custom_text: str | None = None
    elapsed_ms: int = 0
