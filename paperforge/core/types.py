"""paperforge Pydantic models."""

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

DocumentFormat = Literal["md", "html", "docx", "pdf"]


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


class Section(BaseModel):
    """One section of the document body. Supports nesting for progressive depth."""

    heading: str
    content: str = Field(
        default="",
        description="Markdown-formatted prose. Aim for flowing paragraphs, not bullet dumps.",
    )
    children: list["Section"] = Field(default_factory=list)


class Decision(BaseModel):
    """An explicit decision worth preserving — what was chosen, why, what was rejected."""

    title: str
    chose: str = Field(description="The choice that was made.")
    why: str = Field(description="The rationale, in one or two sentences.")
    rejected: list[str] = Field(
        default_factory=list,
        description="Alternatives considered and the reason they were rejected.",
    )
    when: str | None = Field(
        default=None,
        description="Optional ISO date or human-readable phase marker (e.g. 'Wave 2').",
    )


class DocumentArtifact(BaseModel):
    """The output of a successful create_document call."""

    title: str
    format: DocumentFormat
    file_path: str
    byte_length: int
    sections_count: int
    decisions_count: int
    open_questions_count: int
    next_steps_count: int
    preview_md: str = Field(
        description="Always the markdown rendition, regardless of file format — for inspection."
    )
