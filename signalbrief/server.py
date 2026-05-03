"""signalbrief MCP server. Run: python -m signalbrief"""

from mcp.server.fastmcp import FastMCP

from signalbrief.core import collect as core_collect
from signalbrief.core import list_sources as core_list_sources

mcp = FastMCP("orzed-signalbrief")


@mcp.tool()
def collect(
    topics: list[str] | None = None,
    sources: list[dict] | None = None,
    hours: int = 24,
    max_per_source: int = 10,
    min_score: int = 2,
    language: str = "en",
) -> dict:
    """Aggregate, dedupe, and score recent news items from curated RSS / Atom feeds.

    When to use:
      - "AI haberleri özetle"             / "AI news brief"
      - "what happened in tech today"     / "bugün teknolojide neler oldu"
      - "scan startup funding headlines"  / "girişim yatırım haberleri"
      - User wants a multi-source briefing on a topic

    When NOT to use:
      - User has a specific article URL - use `pagesignal` or just read it
      - General Web search ("what is X") - news-feed only, not a search engine
      - Real-time breaking news in seconds (this is feed-refresh latency)
      - Stock prices / sports scores / weather - out of scope

    Args:
        topics: Keyword list. None uses a built-in AI / tech / business set.
        sources: List of {"name", "url", "language?"}. None uses the default catalog.
        hours: Recency window 1-336 (max 14 days).
        max_per_source: Cap items kept per source.
        min_score: Drop items below this score (keyword + recency + source boost).
        language: en/tr.
    """
    return core_collect(
        topics=topics,
        sources=sources,
        hours=hours,
        max_per_source=max_per_source,
        min_score=min_score,
        language=language,
    ).model_dump(mode="json")


@mcp.tool()
def list_sources(language: str = "en") -> dict:
    """List the built-in RSS / Atom source catalog (no fetching).

    When to use:
      - "what news sources do you cover" / "hangi kaynakları tarıyorsun"
      - User wants to see the catalog before customizing `sources` in `collect`

    When NOT to use:
      - User wants actual news - call `collect` instead
    """
    return core_list_sources(language=language).model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
