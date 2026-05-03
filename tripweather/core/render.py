"""Markdown rendering for tripweather Result types."""

from .i18n import t
from .types import ForecastResult, GeocodeResult, Result


def to_markdown(result: Result, lang: str = "en") -> str:
    if not result.ok or result.data is None:
        if result.error is None:
            return f"**Error**: unknown failure (lang={lang})"
        msg = result.error.message_tr if lang == "tr" else result.error.message_en
        body = f"**Error** ({result.error.code}): {msg}"
        if result.error.hint:
            body += f"\n\n_Hint: {result.error.hint}_"
        return body

    data = result.data
    if isinstance(data, GeocodeResult):
        return _render_geocode(data, lang)
    if isinstance(data, ForecastResult):
        return _render_forecast(data, lang)
    return f"**Result**: {data}"


def _render_geocode(g: GeocodeResult, lang: str) -> str:
    parts: list[str] = [f"# {t('title.geocode', lang, query=g.query)}", ""]
    if not g.candidates:
        parts.append(f"_{t('label.no_candidates', lang)}_")
        return "\n".join(parts)
    for i, c in enumerate(g.candidates, start=1):
        admin = ", ".join(x for x in (c.admin1, c.country) if x)
        parts.append(
            f"{i}. **{c.name}** - {admin or c.country_code or ''}  "
            f"`({c.latitude:.4f}, {c.longitude:.4f})`"
            + (f" · {t('label.population', lang)}: {c.population:,}" if c.population else "")
            + (f" · {t('label.timezone', lang)}: `{c.timezone}`" if c.timezone else "")
        )
    return "\n".join(parts)


def _render_forecast(f: ForecastResult, lang: str) -> str:
    unit = "F" if f.units == "imperial" else "C"
    parts: list[str] = [
        f"# {t('title.forecast', lang)}",
        "",
    ]
    header = f"**{t('label.coords', lang)}**: `({f.latitude:.4f}, {f.longitude:.4f})`"
    if f.place_name:
        header = f"**{f.place_name}**" + (f" ({f.country_code})" if f.country_code else "") + " · " + header
    parts.append(header)
    parts.append(
        f"**{t('label.timezone', lang)}**: `{f.timezone or '?'}`  •  "
        f"**{t('label.units', lang)}**: `{f.units}`"
    )
    parts.append("")
    if not f.days:
        parts.append(f"_{t('label.no_days', lang)}_")
        return "\n".join(parts)

    parts.append(
        f"| {t('header.day', lang)} | {t('header.weather', lang)} | "
        f"{t('header.temp', lang, unit=unit)} | "
        f"{t('header.precip', lang)} | {t('header.wind', lang)} |"
    )
    parts.append("|---|---|---|---|---|")
    for d in f.days:
        temp = (
            f"{d.min_temp:.0f}/{d.max_temp:.0f}"
            if d.max_temp is not None and d.min_temp is not None
            else "?"
        )
        precip = (
            f"{d.precipitation:.1f}"
            + (f" ({d.precipitation_probability}%)" if d.precipitation_probability is not None else "")
            if d.precipitation is not None
            else "-"
        )
        wind = f"{d.wind_speed:.0f}" if d.wind_speed is not None else "-"
        parts.append(
            f"| `{d.date.isoformat()}` | {d.weather_label or '-'} | {temp} | {precip} | {wind} |"
        )

    parts += ["", f"_{t('note.forecast', lang)}_"]
    return "\n".join(parts)
