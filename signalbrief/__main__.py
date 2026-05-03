"""Entry point for `python -m signalbrief`."""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
