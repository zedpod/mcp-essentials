"""Default RSS/Atom source catalog and editable source-boost map."""

DEFAULT_SOURCES: list[dict[str, str | None]] = [
    {"name": "Hacker News (top)", "url": "https://news.ycombinator.com/rss", "language": "en"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "language": "en"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "language": "en"},
    {"name": "arXiv cs.AI", "url": "https://export.arxiv.org/rss/cs.AI", "language": "en"},
    {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "language": "en"},
    {"name": "NPR Tech", "url": "https://feeds.npr.org/1019/rss.xml", "language": "en"},
    {"name": "The Guardian Tech", "url": "https://www.theguardian.com/uk/technology/rss", "language": "en"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "language": "en"},
    {"name": "Euronews", "url": "https://www.euronews.com/rss?level=theme&name=news", "language": "en"},
    {"name": "ShiftDelete", "url": "https://shiftdelete.net/feed", "language": "tr"},
    {"name": "DonanımHaber", "url": "https://www.donanimhaber.com/rss/tum/", "language": "tr"},
    {"name": "Webrazzi", "url": "https://webrazzi.com/feed/", "language": "tr"},
]

DEFAULT_KEYWORDS: list[str] = [
    "ai", "llm", "machine learning", "deep learning", "neural network",
    "openai", "anthropic", "google", "deepmind", "mistral", "huggingface",
    "model", "agent", "robotics",
    "saas", "startup", "venture", "ipo", "acquisition", "funding",
]

# Editable source-boost map. Match is case-insensitive substring on the source name.
SOURCE_BOOSTS: dict[str, int] = {
    "openai": 1,
    "anthropic": 1,
    "deepmind": 1,
    "mit tech review": 1,
    "arxiv": 1,
    "hacker news": 1,
    "techcrunch": 1,
}


def boost_for(source_name: str) -> int:
    lower = (source_name or "").lower()
    for key, val in SOURCE_BOOSTS.items():
        if key in lower:
            return val
    return 0


def dedupe_sources(sources: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for src in sources:
        url = (src.get("url") or "").strip().lower()
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(src)
    return out
