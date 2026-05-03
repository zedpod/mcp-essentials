"""paperforge pytest fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def tmp_output(tmp_path, monkeypatch) -> Path:
    """Redirect default output to a tmp_path so tests never touch real Documents/."""
    monkeypatch.setenv("PAPERFORGE_OUTPUT_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def sample_payload():
    return {
        "title": "mcp-essentials refactor — wave 4 wrap-up",
        "summary": (
            "Nine MCP tools were rewritten to a flat dual-mode layout. "
            "Each tool now ships an OWUI bundle, a FastMCP server, shared core "
            "logic, and respx-mocked tests. The next conversation can pick up "
            "from this document."
        ),
        "sections": [
            {
                "heading": "Outcome",
                "content": (
                    "Each of the nine tools was refactored end-to-end. The repo now "
                    "ships consistent file layouts, shared error contracts, and a "
                    "drift-detecting OWUI bundler."
                ),
                "children": [
                    {
                        "heading": "What changed structurally",
                        "content": (
                            "The legacy `<tool>/main.py` was replaced by a flat layout "
                            "with `owui.py`, `server.py`, `__main__.py`, and `core/`."
                        ),
                    }
                ],
            },
            {
                "heading": "Risks worth tracking",
                "content": "Live tests still consume third-party API credits.",
            },
        ],
        "decisions": [
            {
                "title": "Flat tool layout instead of subdirectories",
                "chose": "Each tool is a flat package with `owui.py` at the top.",
                "why": "Naming `owui.py` `main.py` would be misleading in an MCP-centric repo.",
                "rejected": ["Keep `<tool>/owui/main.py` (extra path depth)"],
                "when": "After Wave 1",
            }
        ],
        "open_questions": ["Do we ship a community theme for askuser overlays?"],
        "next_steps": [
            "Publish per-tool packages on PyPI",
            "Add a release.yml GitHub Actions workflow",
        ],
        "tags": ["mcp-essentials", "refactor", "wrap-up"],
    }
