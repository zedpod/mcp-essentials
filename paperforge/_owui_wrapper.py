"""OWUI Tools wrapper for paperforge."""

from pydantic import BaseModel, Field

from paperforge.core import create_document, default_output_dir, to_markdown  # noqa: F401


class Tools:
    class Valves(BaseModel):
        DEFAULT_LANGUAGE: str = Field(
            default="en",
            description="Output language. 'en' or 'tr'.",
        )
        DEFAULT_FORMAT: str = Field(
            default="md",
            description="Default output format if the LLM doesn't specify (md/html/docx/pdf).",
        )
        DEFAULT_PROJECT: str = Field(
            default="",
            description="Optional project tag used when the caller doesn't pass `project`.",
        )
        OUTPUT_DIR: str = Field(
            default="",
            description=(
                "Override the save directory. Empty falls back to "
                "PAPERFORGE_OUTPUT_DIR env, then ~/Documents/orzed-mcp/paperforge."
            ),
        )

    def __init__(self):
        self.valves = self.Valves()
        self.citation = False

    def _lang(self, language):
        return (language or self.valves.DEFAULT_LANGUAGE or "en").strip()

    def create_document(
        self,
        title: str,
        body: str | None = None,
        summary: str | None = None,
        sections: list[dict] | None = None,
        format: str | None = None,
        project: str | None = None,
        decisions: list[dict] | None = None,
        open_questions: list[str] | None = None,
        next_steps: list[str] | None = None,
        tags: list[str] | None = None,
        source: str | None = None,
        filename: str | None = None,
        language: str | None = None,
    ) -> str:
        """
        Create and save a document file - markdown, HTML, DOCX, or PDF.

        Simplest call: `title` plus `body` (one markdown chunk). For richer docs
        pass structured `sections`, `decisions`, `open_questions`, `next_steps`.
        Synthesize a real title from the user's request; "Untitled" stubs are refused.

        When to use:
        - "save this as a doc"     / "bunu doküman yap"
        - "create a markdown file" / "md dosyası oluştur"
        - "export to PDF / docx"   / "PDF / docx olarak kaydet"
        - User wants a downloadable, shareable, or Obsidian-importable file.

        When NOT to use:
        - User just wants an inline summary in chat
        - User asks for a QR code, flight search, news brief - those tools save themselves

        :param title: REQUIRED. Synthesize from the request - no "Untitled" stubs.
        :param body: OPTIONAL. The whole doc body as one markdown string (simplest).
        :param summary: OPTIONAL. Derived from first section's content if omitted.
        :param sections: OPTIONAL list of {heading, content, children?} for structured docs.
        :param format: 'md' (default), 'html', 'docx', or 'pdf'.
        :param decisions: OPTIONAL list of {title, chose, why, rejected?, when?}.
        """
        lang = self._lang(language)
        fmt = format or self.valves.DEFAULT_FORMAT or "md"
        result = create_document(
            title=title,
            body=body,
            summary=summary,
            sections=sections,
            format=fmt,
            project=project or (self.valves.DEFAULT_PROJECT or None),
            decisions=decisions,
            open_questions=open_questions,
            next_steps=next_steps,
            tags=tags,
            source=source,
            output_dir=(self.valves.OUTPUT_DIR or None),
            filename=filename,
            language=lang,
        )
        return to_markdown(result, lang=lang)
