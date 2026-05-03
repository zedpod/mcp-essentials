"""Markdown rendering for QrImage results - used by the OWUI wrapper."""

from .i18n import t
from .types import QrImage, Result


def to_markdown(result: Result[QrImage], lang: str = "en") -> str:
    """Render a Result[QrImage] as a markdown block suitable for chat display."""
    if not result.ok or result.data is None:
        if result.error is None:
            return f"**Error**: unknown failure (lang={lang})"
        message = result.error.message_tr if lang == "tr" else result.error.message_en
        body = f"**Error** ({result.error.code}): {message}"
        if result.error.hint:
            body += f"\n\n_Hint: {result.error.hint}_"
        return body

    img = result.data
    title = t("title", lang)
    kind_label = t(f"kind.{img.payload_kind}", lang)
    source_label = t(f"source.{img.source}", lang)
    note_key = "note.local" if img.source == "local" else "note.remote"

    if img.source == "local" and img.data_b64:
        embed = f"data:image/png;base64,{img.data_b64}"
    elif img.remote_url:
        embed = img.remote_url
    else:
        embed = ""

    lines = [
        f"# {title}",
        "",
        f"- **{t('label.kind', lang)}**: {kind_label}",
        f"- **{t('label.size', lang)}**: `{img.pixel_size}x{img.pixel_size}`",
        f"- **{t('label.ec_level', lang)}**: `{img.ec_level}`",
        f"- **{t('label.payload_chars', lang)}**: `{len(img.payload_preview)}"
        + ("+` (truncated)" if len(img.payload_preview) >= 80 else "`"),
        f"- **{t('label.source', lang)}**: {source_label}",
        "",
        f"![QR Code]({embed})" if embed else "_(no image)_",
        "",
        f"_{t(note_key, lang)}_",
    ]
    return "\n".join(lines)
