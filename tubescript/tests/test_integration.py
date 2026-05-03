"""Live tests - RUN_LIVE=1."""

import pytest

from tubescript.core import list_transcripts

pytestmark = pytest.mark.live

# A long-lived YouTube tech-talk video; if it disappears, swap the ID.
LIVE_VIDEO_ID = "9bZkp7q19f0"


def test_live_list_transcripts():
    r = list_transcripts(LIVE_VIDEO_ID)
    # Either we got tracks or YouTube blocked the request - both are acceptable
    # in a real-network test. The contract is that we never raise.
    if not r.ok:
        assert r.error and r.error.code in ("NOT_FOUND", "UNSUPPORTED", "UPSTREAM_ERROR")
