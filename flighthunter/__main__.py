"""Entry point for `python -m flighthunter`."""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
