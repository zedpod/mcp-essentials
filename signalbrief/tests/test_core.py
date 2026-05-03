"""signalbrief unit tests."""

import respx
from httpx import Response

from signalbrief.core import collect, list_sources
from signalbrief.core.tokens import keyword_matches, tokenize
from signalbrief.tests.conftest import SAMPLE_RSS, SAMPLE_RSS_DUPE


class TestTokens:
    def test_basic_tokenize(self):
        assert tokenize("Hello, world! 123") == ["hello", "world", "123"]

    def test_no_substring_collision(self):
        # Canonical anti-bug: "ai" must not match "brain"/"train".
        haystack = tokenize("the brain trains itself")
        assert keyword_matches(haystack, "ai") == 0

    def test_whole_word_match(self):
        haystack = tokenize("an AI model")
        assert keyword_matches(haystack, "ai") == 1

    def test_multiword_phrase(self):
        haystack = tokenize("we used a large language model")
        assert keyword_matches(haystack, "large language model") == 1


class TestList:
    def test_default_catalog(self):
        r = list_sources()
        assert r.ok
        names = {s.name for s in r.data.sources}
        assert "TechCrunch" in names
        # Catalog must be deduped (no Webrazzi/ShiftDelete x2 — legacy bug).
        urls = [s.url for s in r.data.sources]
        assert len(urls) == len(set(urls))


class TestCollect:
    def test_invalid_hours(self):
        r = collect(hours=0)
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_empty_keywords_after_filter(self):
        # All-whitespace items filter down to an empty list; that's the failure mode.
        r = collect(topics=["", "   "], hours=24)
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    @respx.mock
    def test_aggregates_and_scores(self):
        respx.get("https://example.com/feed").mock(
            return_value=Response(200, content=SAMPLE_RSS.encode("utf-8"))
        )
        sources = [{"name": "Sample Feed", "url": "https://example.com/feed", "language": "en"}]
        # min_score=5 filters out items that only earned recency points (bakery has no
        # keyword hits → 0 + recency 3 = 3 < 5).
        r = collect(topics=["openai", "anthropic"], sources=sources, hours=24, min_score=5)
        assert r.ok
        titles = [i.title for i in r.data.items]
        assert any("OpenAI" in t for t in titles)
        assert any("Anthropic" in t for t in titles)
        assert not any("bakery" in t.lower() for t in titles)

    @respx.mock
    def test_dedupes_across_feeds(self):
        respx.get("https://a.example/feed").mock(
            return_value=Response(200, content=SAMPLE_RSS.encode("utf-8"))
        )
        respx.get("https://b.example/feed").mock(
            return_value=Response(200, content=SAMPLE_RSS_DUPE.encode("utf-8"))
        )
        sources = [
            {"name": "A", "url": "https://a.example/feed"},
            {"name": "B", "url": "https://b.example/feed"},
        ]
        r = collect(topics=["openai"], sources=sources, hours=24, min_score=1)
        assert r.ok
        # OpenAI article appears in both feeds with the same link → dedup keeps one.
        seen = [i for i in r.data.items if "openai" in i.title.lower()]
        assert len(seen) == 1

    @respx.mock
    def test_failed_source_recorded(self):
        respx.get("https://broken.example/feed").mock(
            return_value=Response(503, text="busy"),
        )
        sources = [{"name": "Broken", "url": "https://broken.example/feed"}]
        r = collect(topics=["x"], sources=sources, hours=24)
        assert r.ok
        assert r.data.failed_sources
        assert r.data.failed_sources[0].name == "Broken"
