"""Markdown rendering for flighthunter."""

from .i18n import t
from .types import FlightSearch, Result


def _fmt_duration(minutes: int | None) -> str:
    if not minutes:
        return "?"
    h, m = divmod(int(minutes), 60)
    return f"{h}h{m:02d}m" if h else f"{m}m"


def _fmt_price(value: float | None, currency: str | None) -> str:
    if value is None:
        return "-"
    return f"{value:.0f} {currency or ''}".strip()


def to_markdown(result: Result[FlightSearch], lang: str = "en") -> str:
    if not result.ok or result.data is None:
        if result.error is None:
            return f"**Error**: unknown failure (lang={lang})"
        msg = result.error.message_tr if lang == "tr" else result.error.message_en
        body = f"**Error** ({result.error.code}): {msg}"
        if result.error.hint:
            body += f"\n\n_Hint: {result.error.hint}_"
        return body

    s = result.data
    parts: list[str] = [
        f"# {t('title', lang)}",
        "",
        f"**{t('label.route', lang)}**: `{s.origin}` → `{s.destination}`",
        f"**{t('label.dates', lang)}**: `{s.departure_date.isoformat()}`"
        + (f" ↺ `{s.return_date.isoformat()}`" if s.return_date else ""),
        f"**{t('label.trip_type', lang)}**: {t(f'trip.{s.trip_type}', lang)}  •  "
        f"**{t('label.cabin', lang)}**: {t(f'cabin.{s.cabin_class}', lang)}",
        f"**{t('label.passengers', lang)}**: {s.adults} {t('label.adults', lang)}"
        + (f", {s.children} {t('label.children', lang)}" if s.children else "")
        + (f", {s.infants} {t('label.infants', lang)}" if s.infants else ""),
    ]

    if s.price_insight and s.price_insight.lowest is not None:
        level = s.price_insight.price_level
        parts.append(
            f"**{t('label.price_insight', lang)}**: "
            f"`{_fmt_price(s.price_insight.lowest, s.currency)}`"
            + (f"  ({t(f'level.{level}', lang)})" if level else "")
        )

    parts += ["", f"## {t('label.cheapest', lang)}"]
    if not s.options:
        parts.append(f"_{t('label.no_results', lang)}_")
    else:
        for i, opt in enumerate(s.options[:8], start=1):
            stops_str = (
                t("label.nonstop", lang) if opt.stops == 0 else f"{opt.stops} {t('label.stops', lang)}"
            )
            via = (
                f" ({t('label.via', lang)} {', '.join(opt.layover_airports)})"
                if opt.layover_airports
                else ""
            )
            airlines = ", ".join({leg.airline or "?" for leg in opt.legs})
            parts.append(
                f"{i}. **{_fmt_price(opt.price, opt.currency or s.currency)}** · "
                f"{_fmt_duration(opt.total_duration_minutes)} · {stops_str}{via} · {airlines}"
            )

    if s.search_url:
        parts += ["", f"[{t('label.book', lang)}]({s.search_url})"]

    parts += ["", f"_{t('note.search', lang)}_"]
    return "\n".join(parts)
