"""Pure tests for video-id extraction and format helpers."""

from tubescript.core.extract import extract_video_id
from tubescript.core.format import format_transcript, truncate_at_word_boundary


class TestExtract:
    def test_raw_id(self):
        assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_watch_url(self):
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_youtu_be_short(self):
        assert extract_video_id("https://youtu.be/dQw4w9WgXcQ?t=3") == "dQw4w9WgXcQ"

    def test_shorts_url(self):
        assert extract_video_id("https://youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_embed_url(self):
        assert extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_live_url(self):
        assert extract_video_id("https://www.youtube.com/live/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_nocookie(self):
        assert extract_video_id("https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_garbage(self):
        assert extract_video_id("not-a-url-or-id") is None

    def test_empty(self):
        assert extract_video_id("") is None
        assert extract_video_id(None) is None  # type: ignore[arg-type]


class TestFormat:
    ENTRIES = [
        {"text": "Hello world", "start": 0.0, "duration": 1.5},
        {"text": "Second line", "start": 1.5, "duration": 1.0},
    ]

    def test_text(self):
        out = format_transcript(self.ENTRIES, "text")
        assert out == "Hello world\nSecond line"

    def test_srt(self):
        out = format_transcript(self.ENTRIES, "srt")
        assert out.startswith("1\n00:00:00,000 --> 00:00:01,500\nHello world")
        assert "2\n00:00:01,500 --> 00:00:02,500\nSecond line" in out

    def test_vtt(self):
        out = format_transcript(self.ENTRIES, "vtt")
        assert out.startswith("WEBVTT")
        assert "00:00:00.000 --> 00:00:01.500" in out

    def test_json(self):
        out = format_transcript(self.ENTRIES, "json")
        assert '"text": "Hello world"' in out

    def test_truncate_word_boundary(self):
        text = "the quick brown fox jumps over the lazy dog"
        cut, was = truncate_at_word_boundary(text, max_chars=20)
        assert was
        assert cut.endswith("(truncated)")
        # Cut should land at a whitespace boundary, not mid-word.
        body = cut.split("…")[0].rstrip()
        assert not body.endswith("ck")
        assert " " in body

    def test_truncate_below_threshold_noop(self):
        text = "short"
        cut, was = truncate_at_word_boundary(text, max_chars=100)
        assert not was
        assert cut == text
