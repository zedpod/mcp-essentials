"""paperforge unit tests."""

from pathlib import Path

from paperforge.core import create_document
from paperforge.core.md_writer import render_markdown
from paperforge.core.types import Section


class TestValidation:
    def test_empty_title_rejected(self, tmp_output, sample_payload):
        sample_payload["title"] = ""
        r = create_document(**sample_payload)
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_empty_summary_rejected(self, tmp_output, sample_payload):
        sample_payload["summary"] = "  "
        r = create_document(**sample_payload)
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_no_sections_rejected(self, tmp_output, sample_payload):
        sample_payload["sections"] = []
        r = create_document(**sample_payload)
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"

    def test_invalid_format_rejected(self, tmp_output, sample_payload):
        r = create_document(**sample_payload, format="rtf")  # type: ignore[arg-type]
        assert not r.ok
        assert r.error and r.error.code == "INVALID_INPUT"


class TestMarkdownOutput:
    def test_md_file_saved(self, tmp_output, sample_payload):
        r = create_document(**sample_payload, format="md")
        assert r.ok
        assert r.data
        path = Path(r.data.file_path)
        assert path.exists() and path.suffix == ".md"
        content = path.read_text(encoding="utf-8")
        # YAML frontmatter for Obsidian.
        assert content.startswith("---\n")
        assert "title:" in content
        assert "tags:" in content
        # Title and summary land in the body.
        assert "# mcp-essentials refactor" in content
        assert "Nine MCP tools" in content
        # Decisions render with chose/why/rejected.
        assert "Chose" in content
        assert "Why" in content
        assert "Rejected" in content

    def test_open_questions_block(self, tmp_output, sample_payload):
        r = create_document(**sample_payload)
        assert r.ok
        content = Path(r.data.file_path).read_text(encoding="utf-8")
        assert "Open questions" in content
        assert "community theme" in content

    def test_next_steps_block(self, tmp_output, sample_payload):
        r = create_document(**sample_payload)
        assert r.ok
        content = Path(r.data.file_path).read_text(encoding="utf-8")
        assert "Next steps" in content
        assert "PyPI" in content

    def test_progressive_depth(self, tmp_output, sample_payload):
        # Top-level Section becomes H2; child Section becomes H3.
        r = create_document(**sample_payload)
        content = Path(r.data.file_path).read_text(encoding="utf-8")
        assert "## Outcome" in content
        assert "### What changed structurally" in content

    def test_tr_labels(self, tmp_output, sample_payload):
        r = create_document(**sample_payload, language="tr")
        content = Path(r.data.file_path).read_text(encoding="utf-8")
        # Decision sub-labels in Turkish.
        assert "Seçilen" in content
        assert "Vazgeçilen" in content


class TestHtmlOutput:
    def test_html_file_saved(self, tmp_output, sample_payload):
        r = create_document(**sample_payload, format="html")
        assert r.ok
        path = Path(r.data.file_path)
        assert path.exists() and path.suffix == ".html"
        content = path.read_text(encoding="utf-8")
        assert "<!doctype html>" in content
        assert "<h1>mcp-essentials" in content
        assert "<h2>" in content
        assert "<h3>" in content


class TestDocxOutput:
    def test_docx_writes_when_lib_present(self, tmp_output, sample_payload):
        # python-docx is in requirements.txt; if it's installed, we should produce a .docx.
        try:
            import docx  # noqa: F401
        except ImportError:
            return  # skip silently if optional dep missing
        r = create_document(**sample_payload, format="docx")
        assert r.ok, r.error
        path = Path(r.data.file_path)
        assert path.exists() and path.suffix == ".docx"
        # python-docx files are ZIP containers, so they start with PK.
        with path.open("rb") as f:
            assert f.read(2) == b"PK"


class TestPdfOutput:
    def test_pdf_returns_unsupported_or_writes(self, tmp_output, sample_payload):
        r = create_document(**sample_payload, format="pdf")
        # Either weasyprint is set up and we got a PDF, or it isn't and we got
        # the structured UNSUPPORTED fallback. Both paths must surface a hint.
        if r.ok:
            assert r.data
            path = Path(r.data.file_path)
            assert path.exists() and path.suffix == ".pdf"
            with path.open("rb") as f:
                assert f.read(4) == b"%PDF"
        else:
            assert r.error and r.error.code == "UNSUPPORTED"
            assert r.error.hint  # caller must know how to recover


class TestRenderMarkdownDirect:
    def test_render_markdown_pure(self):
        md = render_markdown(
            title="Test",
            summary="A short test.",
            sections=[Section(heading="One", content="hi")],
            project="orzed",
            decisions=[],
            open_questions=[],
            next_steps=[],
            tags=["x", "y"],
            source=None,
            language="en",
        )
        assert md.startswith("---\n")
        assert "# Test" in md
        assert "## One" in md


class TestArtifactCounts:
    def test_counts_match_inputs(self, tmp_output, sample_payload):
        r = create_document(**sample_payload)
        assert r.ok
        d = r.data
        assert d.sections_count == 2
        assert d.decisions_count == 1
        assert d.open_questions_count == 1
        assert d.next_steps_count == 2
