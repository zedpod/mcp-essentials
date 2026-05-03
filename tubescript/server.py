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

    When to use:
      - "what languages are this video subtitled in"
      - "şu videoda hangi dil altyazıları var"
      - User wants to pick a track before fetching the transcript

    When NOT to use:
      - User just wants the transcript itself - jump to `get_transcript`
      - Non-YouTube videos (Vimeo, TikTok, etc.) - not supported
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
    """Fetch a YouTube transcript in text / SRT / VTT / JSON.

    When to use:
      - "transcript of this YouTube link"   / "şu YouTube videosunun transkripti"
      - "subtitle this video in TR"         / "şu videoyu Türkçe'ye çevir altyazı"
      - "give me the captions of X"
      - "export YouTube subtitles as SRT"

    When NOT to use:
      - User wants a video summary without the raw transcript - answer from
        page metadata or other sources, not this tool
      - Non-YouTube videos (Vimeo, TikTok, etc.) - not supported
      - Live streams without captions yet - returns UNSUPPORTED
      - Audio-only podcasts without YouTube uploads

    Args:
        url_or_id: YouTube URL or 11-char video ID.
        prefer_lang: Ordered list of language codes (default ["en"]).
        translate_to: Optional target language code (uses YouTube's translator).
        format: "text", "srt", "vtt", or "json".
        max_chars: Optional cap; truncates at the nearest word boundary.
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
