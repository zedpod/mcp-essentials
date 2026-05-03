"""pagesignal MCP server (stdio). Run: python -m pagesignal"""

from mcp.server.fastmcp import FastMCP

from pagesignal.core import audit_page as core_audit_page

mcp = FastMCP("orzed-pagesignal")


@mcp.tool()
def audit_page(
    url: str,
    target_keywords: list[str] | None = None,
    language: str = "en",
    timeout_seconds: float = 10.0,
) -> dict:
    """Fetch a URL and audit its SEO + AI-answer-readiness signals.

    Args:
        url: Full http(s) URL to fetch.
        target_keywords: Optional list of keywords; counts hits in title+desc+body.
        language: Output language for messages and question-word lexicon. en/tr.
        timeout_seconds: Per-request timeout.

    Returns:
        Result envelope. `data` is a `PageAudit` with meta_tags, headings,
        readability, geo_signals, performance, and a list of issues.
    """
    result = core_audit_page(
        url,
        target_keywords=target_keywords,
        language=language,
        timeout_seconds=timeout_seconds,
    )
    return result.model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
