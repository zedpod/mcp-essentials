"""paperforge — synthesize an AI conversation into a flowing, downloadable document.

The LLM caller does the synthesis (decisions, summary, sections, open questions);
this tool assembles those parts into a polished file in the requested format
(md / html / docx / pdf).

    paperforge.core   — pure builders + format writers.
    paperforge.server — FastMCP/stdio server. Run `python -m paperforge`.
    paperforge/owui.py — generated single-file OWUI bundle.
"""

__version__ = "1.0.0"
