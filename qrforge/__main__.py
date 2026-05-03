"""Entry point for `python -m qrforge` - runs the FastMCP server over stdio."""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
