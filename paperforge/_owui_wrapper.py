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
        summary: str,
        sections: list[dict],
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
        Synthesize the conversation into a flowing document and save it.
        Provide title + 3-5 sentence summary + ordered sections with prose content.
        Decisions, open_questions, and next_steps make the doc resumable later.

        :param title: Scannable, project-style title.
        :param summary: 3-5 sentence orientation text.
        :param sections: Ordered list of {heading, content, children?}.
        :param format: 'md' (default), 'html', 'docx', or 'pdf'.
        :param decisions: List of {title, chose, why, rejected?, when?}.
        """
        lang = self._lang(language)
        fmt = format or self.valves.DEFAULT_FORMAT or "md"
        result = create_document(
            title=title,
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
