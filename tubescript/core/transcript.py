"""Public API: list_transcripts and get_transcript via youtube-transcript-api.

We isolate the third-party calls inside this module so tests can monkeypatch them.
"""

from .extract import extract_video_id
from .format import format_transcript, truncate_at_word_boundary
from .i18n import normalize_lang, t
from .types import (
    AvailableTrack,
    ErrorInfo,
    Result,
    Transcript,
    TranscriptEntry,
    TranscriptList,
)


def _err(code: str, lang: str, en_key: str, *, hint_key: str | None = None,
         fmt: dict | None = None) -> ErrorInfo:
    fmt = fmt or {}
    return ErrorInfo(
        code=code,
        message_en=t(en_key, "en", **fmt),
        message_tr=t(en_key, "tr", **fmt),
        hint=t(hint_key, lang, **fmt) if hint_key else None,
    )


def _make_api():
    """Lazy import so monkeypatching for tests is straightforward."""
    from youtube_transcript_api import YouTubeTranscriptApi

    return YouTubeTranscriptApi()


def _classify_exception(exc: Exception, lang: str) -> ErrorInfo:
    """Map a youtube-transcript-api exception to a typed Result error.

    Classifies on the class name *or* the exception message so we don't have to
    import every concrete exception type from the library (which churns) and so
    tests can simulate them with plain RuntimeErrors.
    """
    name = exc.__class__.__name__
    text = str(exc)
    fingerprint = f"{name} {text}"
    if "TranscriptsDisabled" in fingerprint:
        return _err("UNSUPPORTED", lang, "error.transcripts_disabled", hint_key="hint.list_first")
    if "NoTranscriptFound" in fingerprint or "NoTranscriptAvailable" in fingerprint:
        return _err("NOT_FOUND", lang, "error.preferred_unavailable", hint_key="hint.list_first")
    if (
        "VideoUnavailable" in fingerprint
        or "AgeRestricted" in fingerprint
        or "RegionBlocked" in fingerprint
    ):
        return _err("UNSUPPORTED", lang, "error.video_unavailable")
    if "TranslationLanguageNotAvailable" in fingerprint:
        return _err(
            "UNSUPPORTED", lang, "error.translation_unavailable", hint_key="hint.list_first"
        )
    return _err("UPSTREAM_ERROR", lang, "error.upstream", hint_key="hint.list_first")


def list_transcripts(input_str: str, *, language: str = "en", api=None) -> Result[TranscriptList]:
    lang = normalize_lang(language)
    if not input_str:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.empty_input"))
    vid = extract_video_id(input_str)
    if not vid:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_id"))

    if api is None:
        try:
            api = _make_api()
        except ImportError:
            return Result(
                ok=False,
                error=_err("UNSUPPORTED", lang, "error.upstream"),
            )
    try:
        listing = api.list(vid)
    except Exception as exc:
        return Result(ok=False, error=_classify_exception(exc, lang), meta={"video_id": vid})

    tracks: list[AvailableTrack] = []
    try:
        for tr in listing:
            tracks.append(
                AvailableTrack(
                    language=getattr(tr, "language", "") or "",
                    language_code=getattr(tr, "language_code", "") or "",
                    is_generated=bool(getattr(tr, "is_generated", False)),
                    is_translatable=bool(getattr(tr, "is_translatable", False)),
                )
            )
    except Exception as exc:
        return Result(ok=False, error=_classify_exception(exc, lang), meta={"video_id": vid})

    if not tracks:
        return Result(ok=False, error=_err("NOT_FOUND", lang, "error.no_transcripts"))
    return Result(
        ok=True,
        data=TranscriptList(video_id=vid, tracks=tracks),
        meta={"video_id": vid, "track_count": len(tracks)},
    )


def get_transcript(
    input_str: str,
    prefer_lang: list[str] | None = None,
    translate_to: str | None = None,
    format: str = "text",
    max_chars: int | None = None,
    *,
    language: str = "en",
    api=None,
) -> Result[Transcript]:
    lang = normalize_lang(language)
    if not input_str:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.empty_input"))
    vid = extract_video_id(input_str)
    if not vid:
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_id"))

    if format not in ("text", "srt", "vtt", "json"):
        return Result(ok=False, error=_err("INVALID_INPUT", lang, "error.invalid_format"))

    preferred = [str(p) for p in (prefer_lang or ["en"]) if p]

    if api is None:
        try:
            api = _make_api()
        except ImportError:
            return Result(ok=False, error=_err("UNSUPPORTED", lang, "error.upstream"))

    # Pick the best available track honoring prefer_lang order.
    try:
        listing = api.list(vid)
    except Exception as exc:
        return Result(ok=False, error=_classify_exception(exc, lang), meta={"video_id": vid})

    chosen = None
    chosen_lang = None
    is_generated = False
    try:
        # First try human-curated tracks in the preferred order.
        chosen = listing.find_manually_created_transcript(preferred)
    except Exception:
        chosen = None
    if chosen is None:
        try:
            chosen = listing.find_generated_transcript(preferred)
            is_generated = True
        except Exception:
            chosen = None
    if chosen is None:
        return Result(
            ok=False,
            error=_err(
                "NOT_FOUND",
                lang,
                "error.preferred_unavailable",
                hint_key="hint.list_first",
            ),
            meta={"video_id": vid},
        )

    chosen_lang = getattr(chosen, "language_code", "") or ""
    is_generated = bool(getattr(chosen, "is_generated", is_generated))

    if translate_to:
        try:
            chosen = chosen.translate(translate_to)
            chosen_lang = translate_to
        except Exception as exc:
            return Result(
                ok=False,
                error=_classify_exception(exc, lang),
                meta={"video_id": vid},
            )

    try:
        fetched = chosen.fetch()
    except Exception as exc:
        return Result(ok=False, error=_classify_exception(exc, lang), meta={"video_id": vid})

    raw_entries: list[dict] = []
    for snippet in fetched:
        # Library returns an iterable of FetchedTranscriptSnippet (or dict on older versions).
        text_val = getattr(snippet, "text", None)
        if text_val is None and isinstance(snippet, dict):
            text_val = snippet.get("text")
        start_val = getattr(snippet, "start", None)
        if start_val is None and isinstance(snippet, dict):
            start_val = snippet.get("start", 0.0)
        dur_val = getattr(snippet, "duration", None)
        if dur_val is None and isinstance(snippet, dict):
            dur_val = snippet.get("duration", 0.0)
        raw_entries.append(
            {
                "text": text_val or "",
                "start": float(start_val or 0.0),
                "duration": float(dur_val or 0.0),
            }
        )

    formatted = format_transcript(raw_entries, format)
    truncated = False
    if max_chars and max_chars > 0:
        formatted, truncated = truncate_at_word_boundary(formatted, max_chars)

    transcript = Transcript(
        video_id=vid,
        language_code=chosen_lang,
        is_generated=is_generated,
        translated_to=translate_to or None,
        format=format,  # type: ignore[arg-type]
        text=formatted,
        entries=[TranscriptEntry(**e) for e in raw_entries],
        truncated=truncated,
        char_count=len(formatted),
    )
    return Result(
        ok=True,
        data=transcript,
        meta={
            "video_id": vid,
            "language_code": chosen_lang,
            "is_generated": is_generated,
            "truncated": truncated,
        },
    )
