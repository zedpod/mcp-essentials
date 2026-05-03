"""tubescript.core - pure logic."""

from .extract import extract_video_id
from .format import format_transcript
from .i18n import DEFAULT, SUPPORTED, normalize_lang, t
from .render import to_markdown
from .transcript import get_transcript, list_transcripts
from .types import (
    AvailableTrack,
    ErrorInfo,
    Result,
    Transcript,
    TranscriptEntry,
    TranscriptList,
)

__bundle_order__ = ["types", "i18n", "extract", "format", "transcript", "render"]

__all__ = [
    "list_transcripts",
    "get_transcript",
    "format_transcript",
    "extract_video_id",
    "to_markdown",
    "Result",
    "Transcript",
    "TranscriptList",
    "TranscriptEntry",
    "AvailableTrack",
    "ErrorInfo",
    "t",
    "normalize_lang",
    "SUPPORTED",
    "DEFAULT",
]
