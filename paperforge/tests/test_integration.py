"""paperforge live tests - none required.

paperforge has no external network dependencies; the file-system writes are
covered by the unit tests. This file exists for the repo invariant only.
"""

import pytest

pytestmark = pytest.mark.live


def test_live_placeholder():
    pytest.skip("paperforge has no live network surface")
