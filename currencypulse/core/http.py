"""HTTP helpers: small httpx wrapper with retry, timeout, Retry-After honoring."""

import random
import time

import httpx


class RateLimited(Exception):
    def __init__(self, retry_after: float | None = None) -> None:
        self.retry_after = retry_after


class NetworkTimeout(Exception):
    pass


class UpstreamError(Exception):
    def __init__(self, status: int, body: str) -> None:
        self.status = status
        self.body = body


def build_client(
    timeout: float = 10.0, user_agent: str = "orzed-mcp-essentials/1.0"
) -> httpx.Client:
    return httpx.Client(
        timeout=timeout,
        headers={"User-Agent": user_agent, "Accept": "application/json"},
        follow_redirects=True,
    )


def get_json_with_retry(
    client: httpx.Client,
    url: str,
    *,
    params: dict | None = None,
    max_attempts: int = 3,
    base_delay: float = 0.5,
) -> dict:
    """GET ``url`` with retries on transient failures. Raises typed exceptions."""
    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        try:
            r = client.get(url, params=params)
        except httpx.TimeoutException:
            last_exc = NetworkTimeout()
        except httpx.RequestError as e:
            last_exc = e
        else:
            if r.status_code == 429:
                ra = r.headers.get("Retry-After")
                last_exc = RateLimited(retry_after=float(ra) if ra else None)
            elif r.status_code in (408, 500, 502, 503, 504):
                last_exc = UpstreamError(r.status_code, r.text[:500])
            elif r.is_success:
                return r.json()
            else:
                raise UpstreamError(r.status_code, r.text[:500])

        if attempt < max_attempts - 1:
            sleep_s = base_delay * (2**attempt) + random.uniform(0, base_delay)
            if isinstance(last_exc, RateLimited) and last_exc.retry_after:
                sleep_s = max(sleep_s, last_exc.retry_after)
            time.sleep(sleep_s)

    if last_exc is not None:
        raise last_exc
    raise UpstreamError(0, "no attempts succeeded")


def get_text_with_retry(
    client: httpx.Client,
    url: str,
    *,
    params: dict | None = None,
    max_attempts: int = 3,
    base_delay: float = 0.5,
) -> str:
    """Same as get_json_with_retry but returns response text (for XML feeds)."""
    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        try:
            r = client.get(url, params=params)
        except httpx.TimeoutException:
            last_exc = NetworkTimeout()
        except httpx.RequestError as e:
            last_exc = e
        else:
            if r.status_code == 429:
                ra = r.headers.get("Retry-After")
                last_exc = RateLimited(retry_after=float(ra) if ra else None)
            elif r.status_code in (408, 500, 502, 503, 504):
                last_exc = UpstreamError(r.status_code, r.text[:500])
            elif r.is_success:
                return r.text
            else:
                raise UpstreamError(r.status_code, r.text[:500])

        if attempt < max_attempts - 1:
            sleep_s = base_delay * (2**attempt) + random.uniform(0, base_delay)
            if isinstance(last_exc, RateLimited) and last_exc.retry_after:
                sleep_s = max(sleep_s, last_exc.retry_after)
            time.sleep(sleep_s)

    if last_exc is not None:
        raise last_exc
    raise UpstreamError(0, "no attempts succeeded")
