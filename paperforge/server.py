"""paperforge MCP server. Run: python -m paperforge"""

from mcp.server.fastmcp import FastMCP

from paperforge.core import create_document as core_create_document

mcp = FastMCP("orzed-paperforge")


@mcp.tool()
def create_document(
    title: str,
    body: str | None = None,
    summary: str | None = None,
    sections: list[dict] | None = None,
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
    """Create and save a document file - markdown, HTML, DOCX, or PDF.

    The simplest call is `title` plus `body` (one markdown chunk); for richer
    output pass structured `sections`, `decisions`, `open_questions`, and
    `next_steps` instead. Synthesize a real `title` from the user's request -
    the tool will reject "Untitled" stubs.

    When to use:
      - "save this conversation as a doc"          / "bunu doküman yap"
      - "create a markdown file about X"           / "X hakkında md dosyası oluştur"
      - "export our discussion to PDF"             / "konuşmayı PDF'e aktar"
      - "wrap up our decisions in a Word doc"      / "kararları docx olarak kaydet"
      - "draft a meeting note from this thread"    / "şu konuşmadan toplantı notu çıkar"
      - User asks for a downloadable / shareable / Obsidian-importable file

    When NOT to use:
      - User just wants an inline summary in chat (answer with text, no file)
      - User asks "what did we decide" - answer directly unless they want a file
      - For QR codes, news briefs, flight searches, etc. - those tools save their own output

    Args:
        title: REQUIRED. Short scannable title - synthesize one from the user's
            request. Stub text like "Untitled Document" is refused.
        body: OPTIONAL, the simplest path - the whole document in one markdown
            string. Wrapped as a single section under `title`. Use this for
            short docs.
        summary: OPTIONAL. 2-4 sentence TL;DR. When omitted, derived from the
            first section with content.
        sections: OPTIONAL ordered list of {heading, content, children?}. Use
            this for richly structured docs; otherwise pass `body`. If both are
            given, `sections` wins.
        format: "md" (default, Obsidian-friendly), "html", "docx", or "pdf".
        decisions: OPTIONAL list of {title, chose, why, rejected?, when?} - the
            non-obvious calls worth preserving.
        open_questions, next_steps: OPTIONAL lists for resumability.
        tags: OPTIONAL Obsidian-style tags.
        project, source, output_dir, filename, language: see README.

    Returns:
        Result envelope. `data.file_path` is the absolute path to the saved file.
    """
    result = core_create_document(
        title=title,
        body=body,
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
