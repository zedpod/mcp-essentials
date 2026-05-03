"""askuser MCP server. Run: python -m askuser.

When called, it opens an ephemeral localhost page in the user's default browser.
The page renders the same overlay used by the OWUI bundle. The user picks an
answer; the page POSTs back to the server; the server returns Result[Answer]
and shuts itself down.
"""

import asyncio
import os
import secrets
import socket
import time
import webbrowser
from typing import Any

from aiohttp import web
from mcp.server.fastmcp import FastMCP

from askuser.core import (
    Answer,
    Option,
    Question,
    Result,
    build_localhost_html,
    normalize_lang,
    t,
    validate_question,
)
from askuser.core.types import ErrorInfo

mcp = FastMCP("orzed-askuser")


def _err(code: str, en_key: str, lang: str, *, hint_key: str | None = None) -> ErrorInfo:
    return ErrorInfo(
        code=code,
        message_en=t(en_key, "en"),
        message_tr=t(en_key, "tr"),
        hint=t(hint_key, lang) if hint_key else None,
    )


def _no_display() -> bool:
    if os.name != "posix":
        return False
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        return False
    return True


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def _serve_question(question: Question, language: str) -> Result[Answer]:
    started = time.monotonic()
    token = secrets.token_urlsafe(32)
    port = _free_port()
    future: asyncio.Future = asyncio.get_event_loop().create_future()

    html = build_localhost_html(question, language=language, csrf_token=token)

    async def index_handler(_req):
        return web.Response(text=html, content_type="text/html", charset="utf-8")

    async def answer_handler(req):
        if req.headers.get("X-Token") != token:
            return web.Response(status=403, text="csrf mismatch")
        try:
            payload = await req.json()
        except Exception:
            return web.Response(status=400, text="bad json")
        if not future.done():
            future.set_result(payload)
        return web.Response(status=204)

    app = web.Application()
    app.router.add_get("/", index_handler)
    app.router.add_post("/answer", answer_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", port)
    await site.start()

    try:
        url = f"http://127.0.0.1:{port}/?t={token}"
        webbrowser.open(url, new=2, autoraise=True)
        try:
            payload = await asyncio.wait_for(future, timeout=question.timeout_s)
        except asyncio.TimeoutError:
            elapsed = int((time.monotonic() - started) * 1000)
            return Result(
                ok=True,
                data=Answer(type="timeout", elapsed_ms=elapsed),
                meta={"timed_out": True},
            )
        # Give the browser a beat to receive the 204.
        await asyncio.sleep(0.2)
        elapsed = int((time.monotonic() - started) * 1000)
        return Result(
            ok=True,
            data=Answer(
                type=payload.get("type", "skip"),
                indices=payload.get("indices") or [],
                values=payload.get("values") or [],
                custom_text=payload.get("custom_text"),
                elapsed_ms=elapsed,
            ),
        )
    finally:
        await runner.cleanup()


@mcp.tool()
async def ask_user_question(
    prompt: str,
    options: list[dict[str, Any]] | None = None,
    mode: str = "single",
    allow_custom: bool = True,
    required: bool = False,
    min_select: int | None = None,
    max_select: int | None = None,
    timeout_s: float = 300.0,
    language: str = "en",
) -> dict:
    """Ask the user an interactive question. YOU decide when to call this, not the user.

    When to use:
      - About to do something with multiple valid approaches and you want the
        user to pick (e.g. "Which DB? Postgres / MySQL / SQLite")
      - User's request is ambiguous and the right choice is non-obvious
      - You need a specific factual input (location, format, key) to proceed

    When NOT to use:
      - Trivial yes/no confirmations - just proceed unless action is risky
      - The right answer is obvious from context - don't waste the user's time
      - To display information - this asks, it doesn't show
      - When the user already provided the answer in their last message

    Renders an overlay (OWUI) or opens a localhost browser page (MCP). The user
    clicks, types, or skips. Headless servers (no display) return UNSUPPORTED.

    Args:
        prompt: The question text shown to the user.
        options: List of {label, description?, value?} dicts.
        mode: 'single' / 'multi' / 'free_text'.
        allow_custom: Show a free-text input below options.
        required: Hide the Skip button.
        min_select / max_select: Constraints for `multi` mode.
        timeout_s: Auto-resolves as `timeout` after this many seconds (≤ 1800).
        language: en/tr.
    """
    lang = normalize_lang(language)
    opt_models = [Option(**o) for o in (options or [])]
    question = Question(
        prompt=prompt,
        options=opt_models,
        mode=mode,  # type: ignore[arg-type]
        allow_custom=allow_custom,
        required=required,
        min_select=min_select,
        max_select=max_select,
        timeout_s=timeout_s,
    )
    err = validate_question(question, language=lang)
    if err is not None:
        return Result(ok=False, error=err).model_dump(mode="json")

    if _no_display():
        return Result(
            ok=False,
            error=_err(
                "UNSUPPORTED",
                "error.no_display",
                lang,
                hint_key="hint.set_display",
            ),
        ).model_dump(mode="json")

    result = await _serve_question(question, lang)
    return result.model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
