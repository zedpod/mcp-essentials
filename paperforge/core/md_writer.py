"""Render the document to Markdown — the source format every other writer also uses.

The output includes YAML frontmatter so Obsidian (and other markdown editors)
can index title, project, tags, date, and source.
"""

from datetime import datetime, timezone

from .i18n import t
from .types import Decision, Section


def _yaml_frontmatter(
    title: str,
    project: str | None,
    tags: list[str],
    created: datetime,
    source: str | None,
    language: str,
) -> str:
    lines = ["---"]
    # YAML strings are conservative — quote anything containing special chars.
    def yq(s: str) -> str:
        if not s:
            return '""'
        if any(c in s for c in [':', '#', '"', "'", '[', ']', '{', '}', ',', '&', '*', '!', '|', '>', '%', '@', '`']):
            escaped = s.replace('"', '\\"')
            return f'"{escaped}"'
        return s

    lines.append(f"title: {yq(title)}")
    if project:
        lines.append(f"project: {yq(project)}")
    lines.append(f"created: {created.isoformat()}")
    lines.append(f"language: {language}")
    if source:
        lines.append(f"source: {yq(source)}")
    if tags:
        lines.append("tags:")
        for tag in tags:
            lines.append(f"  - {yq(tag)}")
    lines.append("---")
    return "\n".join(lines)


def _render_section(section: Section, depth: int) -> str:
    """Render a section header at depth+2 (so top-level body sections are H2)."""
    level = min(6, depth + 2)
    parts = [f"{'#' * level} {section.heading}"]
    if section.content.strip():
        parts.append("")
        parts.append(section.content.strip())
    for child in section.children:
        parts.append("")
        parts.append(_render_section(child, depth + 1))
    return "\n".join(parts)


def _render_decisions(decisions: list[Decision], lang: str) -> str:
    if not decisions:
        return ""
    parts = [f"## {t('section.decisions', lang)}", ""]
    for d in decisions:
        parts.append(f"### {d.title}" + (f" — _{d.when}_" if d.when else ""))
        parts.append("")
        parts.append(f"**{t('decision.chose', lang)}**: {d.chose}")
        parts.append("")
        parts.append(f"**{t('decision.why', lang)}**: {d.why}")
        if d.rejected:
            parts.append("")
            parts.append(f"**{t('decision.rejected', lang)}**:")
            for r in d.rejected:
                parts.append(f"- {r}")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def _render_bullets(heading: str, items: list[str]) -> str:
    if not items:
        return ""
    parts = [f"## {heading}", ""]
    for item in items:
        parts.append(f"- {item}")
    return "\n".join(parts) + "\n"


def render_markdown(
    *,
    title: str,
    summary: str,
    sections: list[Section],
    project: str | None,
    decisions: list[Decision],
    open_questions: list[str],
    next_steps: list[str],
    tags: list[str],
    source: str | None,
    language: str,
    created: datetime | None = None,
) -> str:
    """Assemble a flowing markdown document with progressive depth.

    Layout:
        YAML frontmatter
        # Title
        TL;DR (summary, plain prose)
        ## Summary section heading is implicit — the summary sits right under the title
        Body sections (each `Section` becomes ## with optional ###/#### children)
        ## Key decisions   (only if any)
        ## Open questions  (only if any)
        ## Next steps      (only if any)
        Footer note
    """
    created = created or datetime.now(timezone.utc).replace(microsecond=0)
    parts: list[str] = [
        _yaml_frontmatter(title, project, tags, created, source, language),
        "",
        f"# {title}",
        "",
        f"> {summary.strip()}",
        "",
    ]

    # Body sections — flowing prose by design. Reader scans the H2s, drills into
    # H3/H4 if interested. Top-level Section -> H2.
    for section in sections:
        parts.append(_render_section(section, depth=0))
        parts.append("")

    decision_block = _render_decisions(decisions, language)
    if decision_block:
        parts.append(decision_block)

    open_q_block = _render_bullets(t("section.open_questions", language), open_questions)
    if open_q_block:
        parts.append(open_q_block)

    steps_block = _render_bullets(t("section.next_steps", language), next_steps)
    if steps_block:
        parts.append(steps_block)

    parts.append("---")
    parts.append("")
    parts.append(f"_{t('footer.note', language)}_")
    parts.append("")
    return "\n".join(parts)
