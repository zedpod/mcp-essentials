"""Entry point for `python -m paperforge`."""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
