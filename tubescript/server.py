"""tubescript MCP server. Run: python -m tubescript"""

from mcp.server.fastmcp import FastMCP

from tubescript.core import (
    get_transcript as core_get_transcript,
)
from tubescript.core import (
    list_transcripts as core_list_transcripts,
)

mcp = FastMCP("orzed-tubescript")


@mcp.tool()
def list_transcripts(url_or_id: str, language: str = "en") -> dict:
    """List available transcript tracks for a YouTube video.

    Args:
        url_or_id: Full YouTube URL (any variant) or 11-char video ID.
        language: en/tr for output messages.
    """
    return core_list_transcripts(url_or_id, language=language).model_dump(mode="json")


@mcp.tool()
def get_transcript(
    url_or_id: str,
    prefer_lang: list[str] | None = None,
    translate_to: str | None = None,
    format: str = "text",
    max_chars: int | None = None,
    language: str = "en",
) -> dict:
    """Fetch a transcript and return it in the requested format.

    Args:
        url_or_id: YouTube URL or 11-char video ID.
        prefer_lang: Ordered list of language codes; defaults to ["en"].
        translate_to: Optional target language code for YouTube translation.
        format: One of "text", "srt", "vtt", "json".
        max_chars: Optional cap; truncation falls on the nearest word boundary.
        language: en/tr for output messages.
    """
    return core_get_transcript(
        url_or_id,
        prefer_lang=prefer_lang,
        translate_to=translate_to,
        format=format,
        max_chars=max_chars,
        language=language,
    ).model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
