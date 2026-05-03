"""tubescript pytest fixtures."""

import os
from dataclasses import dataclass

import pytest


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_LIVE") == "1":
        return
    skip = pytest.mark.skip(reason="set RUN_LIVE=1 to run live-API tests")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)


# ─────────────────────────────────────────────────────────────────────────────
# Fakes for the youtube_transcript_api surface we use.
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class FakeSnippet:
    text: str
    start: float
    duration: float


class FakeTranscript:
    def __init__(self, language_code, language, snippets, *, is_generated=False, translatable=True):
        self.language_code = language_code
        self.language = language
        self.is_generated = is_generated
        self.is_translatable = translatable
        self._snippets = snippets

    def fetch(self):
        return list(self._snippets)

    def translate(self, target_lang):
        # Fake translation: clone with the target language and a marker prefix.
        return FakeTranscript(
            language_code=target_lang,
            language=f"{self.language} (translated→{target_lang})",
            snippets=[
                FakeSnippet(text=f"[{target_lang}] {s.text}", start=s.start, duration=s.duration)
                for s in self._snippets
            ],
            is_generated=self.is_generated,
            translatable=False,
        )


class FakeListing:
    def __init__(self, manual: dict[str, FakeTranscript] | None = None,
                 generated: dict[str, FakeTranscript] | None = None):
        self.manual = manual or {}
        self.generated = generated or {}

    def __iter__(self):
        yield from self.manual.values()
        yield from self.generated.values()

    def find_manually_created_transcript(self, langs):
        for lang in langs:
            if lang in self.manual:
                return self.manual[lang]
        raise RuntimeError("NoTranscriptFound")  # name pattern matched by classifier

    def find_generated_transcript(self, langs):
        for lang in langs:
            if lang in self.generated:
                return self.generated[lang]
        raise RuntimeError("NoTranscriptFound")


class FakeApi:
    def __init__(self, listings: dict[str, FakeListing | Exception]):
        self._listings = listings

    def list(self, video_id):
        result = self._listings.get(video_id)
        if isinstance(result, Exception):
            raise result
        if result is None:
            raise RuntimeError("VideoUnavailable")
        return result


@pytest.fixture
def make_api():
    """Helper for building a FakeApi with one or more video listings."""
    def _build(**listings):
        return FakeApi(listings)
    return _build
