# paperforge

> Synthesize a conversation's decisions, abandoned ideas, and current state into a flowing, downloadable document.

Part of [mcp-essentials](../README.md). Designed for the moment when a long AI conversation produces something worth keeping — a wave of decisions, a project state, a set of trade-offs you'd hate to lose. The LLM does the synthesis; paperforge formats it.

## What it does

One MCP tool — `create_document(title, summary, sections, format, decisions?, open_questions?, next_steps?, tags?, project?, language)` → `Result[DocumentArtifact]`.

The output is a flowing document with a clear hierarchy:

1. **Title** + YAML frontmatter (Obsidian-friendly tags, project, language, source).
2. **Summary** — the 3-5 sentence TL;DR a cold reader uses to orient.
3. **Body sections** — H2 → H3 → H4, progressively deeper. `content` is markdown prose, not bullet dumps. The reader scans the H2s, drills in where they care.
4. **Key decisions** — for each: what was chosen, why, what was rejected. The thing that's hardest to reconstruct from a transcript later.
5. **Open questions** — what's still unsettled.
6. **Next steps** — concrete action items.
7. **Footer** — short generated note.

Output formats:

| Format | Library | Notes |
|---|---|---|
| `md` | built-in | Obsidian-ready (YAML frontmatter, fenced sections). The default. |
| `html` | built-in | Self-contained HTML, no external CSS, prints decently. |
| `docx` | `python-docx` | Word/Pages-friendly. Headings + bullet lists. |
| `pdf` | `weasyprint` | Renders the HTML to PDF. Falls back to UNSUPPORTED with install hint if weasyprint isn't available. |

Files land in `~/Documents/orzed-mcp/paperforge/` by default. Override with `PAPERFORGE_OUTPUT_DIR` env or the `OUTPUT_DIR` Valve.

## How to think about the synthesis prompt

The LLM caller's job is to read the conversation and produce a structured synthesis. A solid mental model:

> "This document has to make sense to someone — a human or another AI — who has not read the conversation. Lead with where things stand. Then explain how we got here. Then capture the decisions: what was chosen, what was rejected, why. Finally, list what's still open."

Good `summary` text answers: what is this about, what's the current state, what should the reader do next?

Good `Section.content` is *prose*. If the LLM is just copy-pasting bullets from the transcript, ask it to paraphrase into paragraphs.

Good `decisions` capture choices that wouldn't be obvious from reading the final code/state — paths not taken, trade-offs evaluated.

## Install — Open WebUI

Paste [`./owui.py`](./owui.py) into Admin → Tools. Configure Valves:
- `DEFAULT_FORMAT` — md / html / docx / pdf
- `OUTPUT_DIR` — override save directory
- `DEFAULT_PROJECT` — project tag applied to every doc

For docx and pdf, install the optional libraries inside the OWUI runtime:
```bash
docker exec -it open-webui pip install "python-docx" "weasyprint"
docker restart open-webui
```

## Install — Claude Desktop / Cursor / Cline

```json
{
  "mcpServers": {
    "paperforge": {
      "command": "python",
      "args": ["-m", "paperforge"],
      "cwd": "/absolute/path/to/mcp-essentials",
      "env": {
        "PYTHONPATH": "/absolute/path/to/mcp-essentials",
        "PAPERFORGE_OUTPUT_DIR": "/path/to/your/notes/orzed-mcp"
      }
    }
  }
}
```

## Errors

| Code | When |
|---|---|
| `INVALID_INPUT` | Missing title/summary/sections, unknown format |
| `UNSUPPORTED` | Requested docx/pdf without the underlying library available |
| `INTERNAL` | File-system write failed (permissions, disk full) |

`UNSUPPORTED` always carries a `hint` describing how to install the missing dependency.

## Resuming a conversation

Re-open the markdown file, point a future LLM at it, and ask "continue from here." YAML frontmatter gives the model the project context, the `decisions` block prevents re-litigating settled calls, and `open_questions` becomes the natural next-turn agenda.

For Obsidian users: the document drops into your vault as-is. Tags become Obsidian tags. Internal `[[wikilinks]]` work if you reference them in `Section.content`.

## License

Apache 2.0.

---

*Part of mcp-essentials by [Orzed](https://orzed.com).*
