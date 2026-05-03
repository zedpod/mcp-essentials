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
    """Aggregate, dedupe, and score recent news items from RSS/Atom feeds.

    Args:
        topics: Keyword list. None uses the built-in default set.
        sources: List of {"name", "url", "language?"} dicts. None uses the default catalog.
        hours: Recency window, 1..336.
        max_per_source: Cap items kept per source.
        min_score: Drop items below this combined score (keyword + recency + source boost).
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
    """List the built-in default RSS/Atom source catalog."""
    return core_list_sources(language=language).model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
