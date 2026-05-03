"""sitepulse Pydantic models."""

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

CheckName = Literal["dns", "rdap", "ssl", "http", "headers"]


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


class DnsResults(BaseModel):
    a: list[str] = Field(default_factory=list)
    aaaa: list[str] = Field(default_factory=list)
    cname: list[str] = Field(default_factory=list)
    mx: list[str] = Field(default_factory=list)
    txt: list[str] = Field(default_factory=list)
    ns: list[str] = Field(default_factory=list)
    spf_record: str | None = None
    dmarc_record: str | None = None
    note: str | None = None


class SslCert(BaseModel):
    ok: bool
    issuer: str | None = None
    subject: str | None = None
    not_before: datetime | None = None
    not_after: datetime | None = None
    days_until_expiry: int | None = None
    san: list[str] = Field(default_factory=list)
    error: str | None = None


class RdapInfo(BaseModel):
    ok: bool
    registrar: str | None = None
    registered_on: datetime | None = None
    expires_on: datetime | None = None
    name_servers: list[str] = Field(default_factory=list)
    status: list[str] = Field(default_factory=list)
    error: str | None = None


class HttpProbe(BaseModel):
    url: str
    status_code: int | None = None
    final_url: str | None = None
    redirects: int = 0
    response_time_ms: int = 0
    server: str | None = None
    content_type: str | None = None
    hsts: str | None = None
    error: str | None = None


class DomainHealth(BaseModel):
    input: str
    host: str
    registered_domain: str
    dns: DnsResults | None = None
    rdap: RdapInfo | None = None
    ssl: SslCert | None = None
    http: HttpProbe | None = None
    https: HttpProbe | None = None
    issues: list[str] = Field(default_factory=list)
