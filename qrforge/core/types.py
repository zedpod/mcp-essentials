"""Pydantic models shared across qrforge.core."""

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

PayloadKind = Literal["text", "url", "wifi", "vcard"]
EcLevel = Literal["L", "M", "Q", "H"]
WifiEncryption = Literal["WPA", "WEP", "NOPASS"]
ImageSource = Literal["local", "remote"]


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


class QrImage(BaseModel):
    """Represents a generated QR code image plus its metadata."""

    format: Literal["png"] = "png"
    source: ImageSource
    data_b64: str | None = Field(
        default=None,
        description="Base64-encoded PNG bytes when source=='local'.",
    )
    remote_url: str | None = Field(
        default=None,
        description="Full URL pointing to a remote QR rendering service when source=='remote'.",
    )
    byte_length: int = Field(
        default=0,
        description="Decoded PNG byte length (0 for remote-only images).",
    )
    pixel_size: int
    border: int
    ec_level: EcLevel
    payload_kind: PayloadKind
    payload_preview: str = Field(
        description="First 80 characters of the encoded payload, for inspection.",
    )
