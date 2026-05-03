"""tubescript.core.transcript tests using a fake youtube_transcript_api surface."""

from tubescript.core import get_transcript, list_transcripts

from .conftest import FakeListing, FakeSnippet, FakeTranscript


def _two_line_snippets():
    return [
        FakeSnippet(text="hello world", start=0.0, duration=1.5),
        FakeSnippet(text="second line", start=1.5, duration=1.0),
    ]


def test_list_transcripts_happy(make_api):
    listing = FakeListing(
        manual={"en": FakeTranscript("en", "English", _two_line_snippets())},
        generated={"tr": FakeTranscript("tr", "Turkish (auto)", _two_line_snippets(), is_generated=True)},
    )
    api = make_api(VID00000001=listing)
    r = list_transcripts("VID00000001", api=api)
    assert r.ok
    codes = {t.language_code for t in r.data.tracks}
    assert codes == {"en", "tr"}


def test_list_transcripts_empty_input():
    r = list_transcripts("")
    assert not r.ok
    assert r.error and r.error.code == "INVALID_INPUT"


def test_list_transcripts_invalid_id():
    r = list_transcripts("not-an-id-or-url")
    assert not r.ok
    assert r.error and r.error.code == "INVALID_INPUT"


def test_get_transcript_text(make_api):
    listing = FakeListing(
        manual={"en": FakeTranscript("en", "English", _two_line_snippets())}
    )
    api = make_api(VID00000001=listing)
    r = get_transcript("VID00000001", api=api)
    assert r.ok
    assert r.data.format == "text"
    assert r.data.text == "hello world\nsecond line"
    assert r.data.entries and r.data.entries[0].text == "hello world"


def test_get_transcript_srt(make_api):
    listing = FakeListing(manual={"en": FakeTranscript("en", "English", _two_line_snippets())})
    api = make_api(VID00000001=listing)
    r = get_transcript("VID00000001", format="srt", api=api)
    assert r.ok
    assert "00:00:00,000 --> 00:00:01,500" in r.data.text


def test_get_transcript_invalid_format(make_api):
    listing = FakeListing(manual={"en": FakeTranscript("en", "English", _two_line_snippets())})
    api = make_api(VID00000001=listing)
    r = get_transcript("VID00000001", format="docx", api=api)
    assert not r.ok
    assert r.error and r.error.code == "INVALID_INPUT"


def test_get_transcript_translation(make_api):
    listing = FakeListing(manual={"en": FakeTranscript("en", "English", _two_line_snippets())})
    api = make_api(VID00000001=listing)
    r = get_transcript("VID00000001", translate_to="tr", api=api)
    assert r.ok
    assert r.data.translated_to == "tr"
    assert "[tr] hello world" in r.data.text


def test_get_transcript_falls_back_to_generated(make_api):
    listing = FakeListing(
        manual={},
        generated={"en": FakeTranscript("en", "English (auto)", _two_line_snippets(), is_generated=True)},
    )
    api = make_api(VID00000001=listing)
    r = get_transcript("VID00000001", api=api)
    assert r.ok
    assert r.data.is_generated is True


def test_get_transcript_no_languages_match(make_api):
    listing = FakeListing(manual={"de": FakeTranscript("de", "German", _two_line_snippets())})
    api = make_api(VID00000001=listing)
    r = get_transcript("VID00000001", prefer_lang=["en"], api=api)
    assert not r.ok
    assert r.error and r.error.code == "NOT_FOUND"


def test_get_transcript_max_chars_truncates(make_api):
    long_snip = [FakeSnippet(text="word " * 100, start=0.0, duration=1.0)]
    listing = FakeListing(manual={"en": FakeTranscript("en", "English", long_snip)})
    api = make_api(VID00000001=listing)
    r = get_transcript("VID00000001", max_chars=40, api=api)
    assert r.ok
    assert r.data.truncated
    assert "(truncated)" in r.data.text


def test_video_unavailable(make_api):
    api = make_api(VID00000001=RuntimeError("VideoUnavailable"))
    r = get_transcript("VID00000001", api=api)
    assert not r.ok
    assert r.error and r.error.code == "UNSUPPORTED"


def test_language_tr_returns_turkish_message():
    r = list_transcripts("", language="tr")
    assert r.error and "URL" in r.error.message_tr or "ID" in r.error.message_tr
