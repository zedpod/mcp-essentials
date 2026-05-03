# AGENTS.md - paperforge

> Read with [`../AGENTS.md`](../AGENTS.md). The "synthesize and write" tool.

## Tool identity
Captures decisions, abandoned ideas, and current state from an AI conversation into a flowing document (md / html / docx / pdf). Stable. Owned by Orzed, LLC.

## Public surface
- `create_document(*, title, summary, sections, format='md', project=None, decisions=None, open_questions=None, next_steps=None, tags=None, source=None, output_dir=None, filename=None, language='en')` → `Result[DocumentArtifact]`

## Architecture
- `core/types.py` - Pydantic models for Section / Decision / DocumentArtifact.
- `core/md_writer.py` - markdown is the canonical render. Includes YAML frontmatter for Obsidian.
- `core/html_writer.py` - minimal markdown→HTML (no external lib needed).
- `core/docx_writer.py` - uses `python-docx` (optional dep). Headings + bullet lists; inline formatting is stripped.
- `core/pdf_writer.py` - `weasyprint` HTML→PDF (optional dep). Returns False if not available.
- `core/build.py` - orchestrator. Writes the chosen format. Default output dir: `PAPERFORGE_OUTPUT_DIR` env → `~/Documents/orzed-mcp/paperforge` → `./paperforge-out`.
- `core/render.py` - OWUI-side markdown renderer (the file-saved confirmation message).

## How the LLM should populate the input
This is the LLM's responsibility, but worth memorializing here:
- **`title`** - scannable. Project + phase + outcome. "mcp-essentials refactor - wave 4 wrap-up", not "summary of our chat".
- **`summary`** - 3-5 sentences. Lead with current state. Answers "what is this and where do things stand?"
- **`sections`** - ordered, progressively deeper. Top-level sections are H2; children become H3/H4. **Content is prose**, not bullet dumps. If the LLM only has bullets, it should turn them into paragraphs.
- **`decisions`** - capture the choices that aren't obvious from the final state. What was rejected and why is the load-bearing field.
- **`open_questions`**, **`next_steps`** - short one-liners.
- **`tags`** - Obsidian-style; appear in YAML frontmatter.

## Edge cases
- **Empty title / summary / sections** → `INVALID_INPUT` with a clear message.
- **`docx` requested without python-docx** → `UNSUPPORTED` with `hint.install_docx`.
- **`pdf` requested without weasyprint or with weasyprint failing** → `UNSUPPORTED` with `hint.install_pdf` (Cairo/Pango install instructions).
- **Filename collision** - none expected because filenames default to `<timestamp>-<slug>`. If the caller supplies a fixed `filename`, we overwrite without warning.
- **Tags with YAML special chars** - quoted automatically by the YAML emitter.
- **No external network** - paperforge is offline-first.

## i18n
Section labels (`Summary`, `Key decisions`, `Open questions`, `Next steps`, `Chose`, `Why`, `Rejected`) honor the `language` parameter. Adding a new language requires updating both `en` and `tr` keys in `core/i18n.py`; the repo-level test enforces parity.

## Tests
- `tests/test_core.py` - validation, all four format outputs, progressive depth, frontmatter, i18n labels, artifact counts. Uses a `tmp_output` fixture that redirects writes to `tmp_path`.
- `tests/test_owui.py`, `tests/test_server.py` - bundle / MCP smoke.
- `tests/test_integration.py` - placeholder; no live network surface to test.

## How to add a new format
1. Add a writer module under `core/<fmt>_writer.py` returning `bool` (False if optional dep missing).
2. Wire it in `core/build.py` alongside the existing format dispatch.
3. Add the format literal to `DocumentFormat` in `core/types.py` and the validation list in `build.py`.
4. Add the corresponding `error.<fmt>_missing` and `hint.install_<fmt>` keys to `core/i18n.py` (en + tr).
5. Add a test in `tests/test_core.py` mirroring `TestPdfOutput`.
6. `python tools/bundle_owui.py paperforge && pytest paperforge/tests`.
