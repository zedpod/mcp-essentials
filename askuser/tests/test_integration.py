"""askuser live tests — RUN_LIVE=1.

Skipped by default because they actually open a browser window. Manual smoke
test: run `python -m askuser` from a desktop terminal and connect from an MCP
client.
"""

import pytest

pytestmark = pytest.mark.live


def test_live_placeholder():
    pytest.skip("askuser live tests must be driven manually with a real MCP client")
