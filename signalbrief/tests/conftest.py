"""signalbrief pytest fixtures."""

import os
from datetime import datetime, timezone
from email.utils import format_datetime

import pytest


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_LIVE") == "1":
        return
    skip = pytest.mark.skip(reason="set RUN_LIVE=1 to run live-API tests")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)


# Generate fresh pubDates each test session so the recency cutoff doesn't drop them.
_PUB_NOW = format_datetime(datetime.now(timezone.utc).replace(microsecond=0))


SAMPLE_RSS = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>Sample Feed</title>
<item>
  <title>OpenAI announces a new model</title>
  <link>https://example.com/openai-new-model</link>
  <description>OpenAI today announced a new LLM with improved reasoning.</description>
  <pubDate>{_PUB_NOW}</pubDate>
  <guid>g1</guid>
</item>
<item>
  <title>Local bakery wins award</title>
  <link>https://example.com/bakery</link>
  <description>An unrelated story about croissants.</description>
  <pubDate>{_PUB_NOW}</pubDate>
  <guid>g2</guid>
</item>
<item>
  <title>Anthropic launches new agent toolkit</title>
  <link>https://example.com/anthropic-agents</link>
  <description>Anthropic announces an agent toolkit with model context protocol support.</description>
  <pubDate>{_PUB_NOW}</pubDate>
  <guid>g3</guid>
</item>
</channel></rss>
"""

SAMPLE_RSS_DUPE = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<item>
  <title>OpenAI announces a new model</title>
  <link>https://example.com/openai-new-model</link>
  <description>Same article copied to a second feed.</description>
  <pubDate>{_PUB_NOW}</pubDate>
  <guid>g1</guid>
</item>
</channel></rss>
"""
