"""Entry point for `python -m currencypulse` — runs the FastMCP server over stdio."""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
