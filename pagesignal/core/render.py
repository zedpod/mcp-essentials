"""Markdown rendering for PageAudit."""

from .i18n import t
from .types import PageAudit, Result


def to_markdown(result: Result[PageAudit], lang: str = "en") -> str:
    if not result.ok or result.data is None:
        if result.error is None:
            return f"**Error**: unknown failure (lang={lang})"
        msg = result.error.message_tr if lang == "tr" else result.error.message_en
        body = f"**Error** ({result.error.code}): {msg}"
        if result.error.hint:
            body += f"\n\n_Hint: {result.error.hint}_"
        return body

    a = result.data
    title = t("title", lang)
    parts: list[str] = [
        f"# {title}",
        "",
        f"**{t('label.url', lang)}**: `{a.url}`",
    ]
    if a.final_url and a.final_url != a.url:
        parts.append(f"**{t('label.final_url', lang)}**: `{a.final_url}`")

    parts += [
        "",
        f"## {t('section.meta', lang)}",
        f"- **{t('label.title', lang)}** ({a.meta_tags.title_length} chars): "
        f"{a.meta_tags.title or '_(missing)_'}",
        f"- **{t('label.description', lang)}** ({a.meta_tags.description_length} chars): "
        f"{a.meta_tags.description or '_(missing)_'}",
        f"- **{t('label.canonical', lang)}**: `{a.meta_tags.canonical or '—'}`",
        f"- **{t('label.robots', lang)}**: `{a.meta_tags.robots or '—'}`",
        f"- **{t('label.lang', lang)}**: `{a.meta_tags.lang or '—'}`",
    ]
    parts += [
        "",
        f"## {t('section.headings', lang)}",
        f"- **{t('label.h1_count', lang)}**: {a.headings.h1_count}"
        + (f" — _{', '.join(a.headings.h1_texts[:3])}_" if a.headings.h1_texts else ""),
        f"- **{t('label.h2_count', lang)}**: {a.headings.h2_count}",
    ]
    parts += [
        "",
        f"## {t('section.readability', lang)}",
        f"- **{t('label.word_count', lang)}**: {a.readability.word_count}",
        f"- **{t('label.sentence_count', lang)}**: {a.readability.sentence_count}",
        f"- **{t('label.avg_sentence_length', lang)}**: {a.readability.avg_sentence_length}",
        f"- **{t('label.detected_language', lang)}**: `{a.readability.detected_language or '—'}`",
    ]
    parts += [
        "",
        f"## {t('section.geo', lang)}",
        f"- FAQ: {'✓' if a.geo_signals.has_faq_schema else '—'}  "
        f"HowTo: {'✓' if a.geo_signals.has_howto_schema else '—'}  "
        f"Article: {'✓' if a.geo_signals.has_article_schema else '—'}  "
        f"Question: {'✓' if a.geo_signals.has_question_schema else '—'}",
        f"- **{t('label.schema_types', lang)}**: "
        f"{', '.join(f'`{s}`' for s in a.geo_signals.schema_types) or '—'}",
        f"- **{t('label.question_headings', lang)}** "
        f"({len(a.geo_signals.question_headings)}): "
        + (
            ", ".join(f"_{q}_" for q in a.geo_signals.question_headings[:5])
            or "—"
        ),
    ]
    if a.geo_signals.keywords_found:
        kw_lines = ", ".join(
            f"`{k}`: {v}" for k, v in a.geo_signals.keywords_found.items()
        )
        parts.append(f"- Keyword hits: {kw_lines}")

    parts += [
        "",
        f"## {t('section.performance', lang)}",
        f"- **{t('label.status', lang)}**: `{a.performance.status_code}`  "
        f"**{t('label.redirects', lang)}**: {a.performance.redirect_count}",
        f"- **{t('label.bytes', lang)}**: {a.performance.bytes_total}",
        f"- **{t('label.response_time', lang)}**: `{a.performance.response_time_ms} ms`",
    ]

    parts += ["", f"## {t('section.issues', lang)}"]
    if not a.issues:
        parts.append(f"_{t('label.no_issues', lang)}_")
    else:
        emoji = {"info": "ℹ︎", "warning": "⚠︎", "error": "✗"}
        for issue in a.issues:
            mark = emoji.get(issue.severity, "•")
            msg = issue.message_tr if lang == "tr" else issue.message_en
            parts.append(f"- {mark} **{issue.severity}** `{issue.code}` — {msg}")

    parts += ["", f"_{t('note.audit', lang)}_"]
    return "\n".join(parts)
