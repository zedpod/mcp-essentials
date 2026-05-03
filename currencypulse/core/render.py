"""Markdown rendering for currencypulse Result types — language-aware formatting."""

from .i18n import t
from .types import (
    Conversion,
    Rate,
    Result,
    Snapshot,
    TimeSeries,
)


def _fmt_number(value: float, lang: str, digits: int = 4) -> str:
    """Format with language-correct thousands/decimal separators."""
    if value is None:
        return "?"
    if abs(value) >= 100:
        digits = 2
    raw = f"{value:,.{digits}f}"  # default en-US: 1,234.5678
    if lang == "tr":
        # Swap separators: 1,234.56 -> 1.234,56
        return raw.replace(",", "X").replace(".", ",").replace("X", ".")
    return raw


def to_markdown(result: Result, lang: str = "en") -> str:
    if not result.ok or result.data is None:
        if result.error is None:
            return f"**Error**: unknown failure (lang={lang})"
        message = result.error.message_tr if lang == "tr" else result.error.message_en
        body = f"**Error** ({result.error.code}): {message}"
        if result.error.hint:
            body += f"\n\n_Hint: {result.error.hint}_"
        return body

    data = result.data
    if isinstance(data, Rate):
        return _render_rate(data, lang)
    if isinstance(data, Conversion):
        return _render_conversion(data, lang)
    if isinstance(data, Snapshot):
        return _render_snapshot(data, lang)
    if isinstance(data, TimeSeries):
        return _render_timeseries(data, lang)
    return f"**Result**: {data}"


def _render_rate(r: Rate, lang: str) -> str:
    return "\n".join(
        [
            f"# {t('title.rate', lang)}",
            "",
            f"- **{t('label.base', lang)}**: `{r.base}`",
            f"- **{t('label.quote', lang)}**: `{r.quote}`",
            f"- **{t('label.rate', lang)}**: `{_fmt_number(r.value, lang)}`",
            f"- **{t('label.on_date', lang)}**: `{r.on_date.isoformat()}`",
            f"- **{t('label.source', lang)}**: `{r.source}`",
            "",
            f"_{t('note.rate', lang)}_",
        ]
    )


def _render_conversion(c: Conversion, lang: str) -> str:
    return "\n".join(
        [
            f"# {t('title.convert', lang)}",
            "",
            f"- **{t('label.amount', lang)}**: `{_fmt_number(c.amount, lang, digits=2)} {c.base}`",
            f"- **{t('label.rate', lang)}**: `{_fmt_number(c.rate, lang)}`",
            f"- **{t('label.converted', lang)}**: "
            f"`{_fmt_number(c.converted, lang, digits=2)} {c.quote}`",
            f"- **{t('label.on_date', lang)}**: `{c.on_date.isoformat()}`",
            f"- **{t('label.source', lang)}**: `{c.source}`",
        ]
    )


def _render_snapshot(s: Snapshot, lang: str) -> str:
    header = "| Quote | Rate |\n|---|---:|"
    rows = [f"| `{e.quote}` | `{_fmt_number(e.rate, lang)}` |" for e in s.rates]
    return "\n".join(
        [
            f"# {t('title.snapshot', lang)}",
            "",
            f"- **{t('label.base', lang)}**: `{s.base}`",
            f"- **{t('label.on_date', lang)}**: `{s.on_date.isoformat()}`",
            f"- **{t('label.source', lang)}**: `{s.source}`",
            "",
            header,
            *rows,
        ]
    )


def _render_timeseries(ts: TimeSeries, lang: str) -> str:
    if not ts.points:
        return f"# {t('title.timeseries', lang)}\n\n_{t('label.no_data', lang)}_"
    header = "| Date | Rate |\n|---|---:|"
    rows = [f"| `{p.on_date.isoformat()}` | `{_fmt_number(p.rate, lang)}` |" for p in ts.points]
    return "\n".join(
        [
            f"# {t('title.timeseries', lang)}",
            "",
            f"- **{t('label.base', lang)}**: `{ts.base}` → `{ts.quote}`",
            f"- {ts.start.isoformat()} → {ts.end.isoformat()} ({len(ts.points)} pts)",
            f"- **{t('label.source', lang)}**: `{ts.source}`",
            "",
            header,
            *rows,
        ]
    )
