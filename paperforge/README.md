# paperforge

> Synthesize a conversation's decisions, abandoned ideas, and current state into a flowing, downloadable document.

Part of [mcp-essentials](../README.md). Designed for the moment when a long AI conversation produces something worth keeping - a wave of decisions, a project state, a set of trade-offs you'd hate to lose. The LLM does the synthesis; paperforge formats it.

## What it does

One MCP tool - `create_document(title, summary, sections, format, decisions?, open_questions?, next_steps?, tags?, project?, language)` → `Result[DocumentArtifact]`.

The output is a flowing document with a clear hierarchy:

1. **Title** + YAML frontmatter (Obsidian-friendly tags, project, language, source).
2. **Summary** - the 3-5 sentence TL;DR a cold reader uses to orient.
3. **Body sections** - H2 → H3 → H4, progressively deeper. `content` is markdown prose, not bullet dumps. The reader scans the H2s, drills in where they care.
4. **Key decisions** - for each: what was chosen, why, what was rejected. The thing that's hardest to reconstruct from a transcript later.
5. **Open questions** - what's still unsettled.
6. **Next steps** - concrete action items.
7. **Footer** - short generated note.

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

> "This document has to make sense to someone - a human or another AI - who has not read the conversation. Lead with where things stand. Then explain how we got here. Then capture the decisions: what was chosen, what was rejected, why. Finally, list what's still open."

Good `summary` text answers: what is this about, what's the current state, what should the reader do next?

Good `Section.content` is *prose*. If the LLM is just copy-pasting bullets from the transcript, ask it to paraphrase into paragraphs.

Good `decisions` capture choices that wouldn't be obvious from reading the final code/state - paths not taken, trade-offs evaluated.

## Install - Open WebUI

### 1. Paste the tool code

Open Admin → Tools → "+ New tool". Copy the entire contents of [`./owui.py`](./owui.py) into the editor.

### 2. Description (paste-ready)

OWUI shows a description field above the editor. The metadata block at the top of `owui.py` usually populates it automatically; override it with the block below if you want a tighter user-facing summary. Tool-call triggers (the text the LLM uses to decide whether to fire) live in the function docstrings inside `owui.py` - bilingual triggers are already baked in there, so natural-language calls in either English or Turkish work without touching this field.

```text
Save the conversation as a flowing document file - Markdown (Obsidian-friendly), HTML, DOCX, or PDF.

Use when the user asks to:
- save this as a doc
- export this thread to PDF
- wrap up our decisions in a Word doc
- draft a meeting note from this thread

Do NOT use when:
- The user just wants an inline summary in chat (no file requested)
- For QR codes, news briefs, flight searches, weather - those tools save their own output
- The user asks to summarize a single article URL - read the page, do not produce a file
```

Click **Save**. Toggle the tool ON for your model in chat → Controls → Tools.

### 3. Configure Valves

In the tool list, click the cog icon next to PaperForge:

| Valve | Recommended | Notes |
|---|---|---|
| `DEFAULT_LANGUAGE` | `tr` or `en` | Section labels and YAML frontmatter language |
| `DEFAULT_FORMAT` | `md` | Most portable, opens in Obsidian/VS Code/any editor |
| `DEFAULT_PROJECT` | empty | Or set a fixed tag applied to every doc |
| `OUTPUT_DIR` | see below | Override the save directory |

### 4. ⚠ Where do the files actually go? (Docker users read this)

By default paperforge writes to `~/Documents/orzed-mcp/paperforge/`. **If OWUI runs in Docker, that path is inside the container**, not on your host - you won't see the files in your Documents folder.

Two ways to fix it:

**A. Volume mount (recommended)** - lets the container write directly to a host folder:

```bash
# Stop and recreate the OWUI container with an extra -v flag.
docker stop open-webui && docker rm open-webui
docker run -d \
  -v ~/Documents/orzed-mcp:/data/orzed-mcp \
  -v open-webui:/app/backend/data \
  -p 3000:8080 \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

Then in the PaperForge Valves, set `OUTPUT_DIR=/data/orzed-mcp/paperforge`. Every doc the tool writes shows up under `~/Documents/orzed-mcp/paperforge/` on your host.

**B. Copy out manually** - leave defaults alone, then pull files when you want them:

```bash
docker cp open-webui:/root/Documents/orzed-mcp/paperforge ~/Desktop/
```

If you run OWUI natively (not in Docker), the default path writes directly to your host home - no action needed.

### 5. DOCX / PDF support (optional)

Markdown and HTML work out of the box. For DOCX and PDF, install the optional engines inside the OWUI container:

```bash
docker exec -it open-webui pip install "python-docx" "weasyprint"
docker restart open-webui
```

`weasyprint` also needs Cairo/Pango - on most OWUI base images these are already present, but if PDF generation fails with a library error try:

```bash
docker exec -it open-webui apt-get update
docker exec -it open-webui apt-get install -y libpango-1.0-0 libpangoft2-1.0-0
```

If your container is Alpine-based, swap `apt-get` for `apk add cairo pango`.

When the engines are missing, paperforge returns `UNSUPPORTED` with the install hint inline - it won't crash silently.

### 6. Test prompts

End a real conversation with one of these and watch the tool fire:

✓ Should trigger:
- "Şu konuşmadan bir md dosyası çıkar."
- "Bunu PDF olarak kaydet."
- "Aldığımız kararları docx'e dök, Obsidian vault'uma atayım."

✗ Should NOT trigger (model should answer in chat instead):
- "Bunu özetle." (no file requested)
- "Ne karar verdik?" (information request, not a save request)
- "Şu makaleyi özetle https://..." (page-content task, no file)

If the tool fires when it shouldn't (or vice versa), it's an instruction-following limit on your current model. Smaller models benefit from the bilingual trigger phrases in the description; switching to Claude / GPT-4 / Llama 3.1 70B+ usually fixes it.

## Install - Claude Desktop / Cursor / Cline

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
