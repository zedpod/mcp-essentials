"""Entry point for `python -m sitepulse`."""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
