"""paperforge MCP server. Run: python -m paperforge

The synthesis is the LLM caller's job — provide:
  - a one-line title that orients a cold reader,
  - a 3-5 sentence summary that captures the document's purpose and current state,
  - a sequence of body sections that progressively deepen,
  - explicit decisions (chose / why / rejected),
  - open questions and next steps (optional but useful for resumption).

The tool writes the assembled document in md / html / docx / pdf and returns the
file path. The markdown form ships YAML frontmatter so Obsidian indexes it.
"""

from mcp.server.fastmcp import FastMCP

from paperforge.core import create_document as core_create_document

mcp = FastMCP("orzed-paperforge")


@mcp.tool()
def create_document(
    title: str,
    summary: str,
    sections: list[dict],
    format: str = "md",
    project: str | None = None,
    decisions: list[dict] | None = None,
    open_questions: list[str] | None = None,
    next_steps: list[str] | None = None,
    tags: list[str] | None = None,
    source: str | None = None,
    output_dir: str | None = None,
    filename: str | None = None,
    language: str = "en",
) -> dict:
    """Synthesize the current conversation into a flowing, downloadable document.

    Use this when the user wants to capture decisions, abandoned ideas, and
    current project state in a portable file they can re-open in Obsidian, hand
    back to a future LLM, or share with a teammate.

    Args:
        title: Scannable, project-style title — e.g. "mcp-essentials refactor — wave 4 wrap-up".
        summary: 3-5 sentence TL;DR a cold reader uses to orient.
        sections: Ordered list of {heading, content, children?}. `content` is
            markdown prose — write flowing paragraphs, not bullet dumps. Use
            `children` for sub-sections that progressively deepen the topic.
        format: One of "md", "html", "docx", "pdf". Default "md" — most portable
            and Obsidian-friendly.
        project: Optional project tag (lands in YAML frontmatter and metadata line).
        decisions: List of {title, chose, why, rejected?, when?}. Capture the
            non-obvious calls the conversation made — what was rejected and why.
        open_questions: Things still unsettled, as one-liners.
        next_steps: Concrete action items.
        tags: Obsidian-style tags for indexing.
        source: Optional reference to the originating conversation (URL, ticket id, etc.).
        output_dir: Override the default save directory.
        filename: Filename without extension. Default: "<timestamp>-<slug>".
        language: en/tr — affects section labels and frontmatter.

    Returns:
        Result envelope. `data.file_path` is the absolute path to the saved file
        and `data.preview_md` is the rendered markdown for inspection.
    """
    result = core_create_document(
        title=title,
        summary=summary,
        sections=sections,
        format=format,  # type: ignore[arg-type]
        project=project,
        decisions=decisions,
        open_questions=open_questions,
        next_steps=next_steps,
        tags=tags,
        source=source,
        output_dir=output_dir,
        filename=filename,
        language=language,
    )
    return result.model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
