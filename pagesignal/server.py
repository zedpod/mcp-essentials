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

    When to use:
      - "audit this page: https://..."   / "şu sayfayı analiz et"
      - "is this page SEO-friendly"      / "SEO açısından nasıl"
      - "check structured data on X"     / "X sayfasının schema'sını kontrol et"
      - "is my page AI-ready / GEO"      / "AI cevap motorlarına hazır mı"

    When NOT to use:
      - User just wants the page summary - read the page yourself, don't tool-call
      - DNS / SSL / domain registration - use `sitepulse` instead
      - General "how to do SEO" advice - answer from your training, no tool

    Args:
        url: Full http(s) URL to fetch.
        target_keywords: Optional list; counts hits across title + description + body.
        language: en/tr for messages and question-word lexicon.
        timeout_seconds: Per-request timeout.
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
