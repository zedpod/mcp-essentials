"""Entry point for `python -m tripweather`."""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
