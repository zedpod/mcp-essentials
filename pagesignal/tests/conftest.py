"""Pagesignal pytest fixtures."""

import os

import pytest


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_LIVE") == "1":
        return
    skip = pytest.mark.skip(reason="set RUN_LIVE=1 to run live-API tests")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)


SAMPLE_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Best Hosting Providers 2025: A Practical Guide</title>
<meta name="description" content="Compare major hosting providers based on speed, support, and uptime. Updated 2025.">
<meta name="robots" content="index,follow">
<meta property="og:title" content="Best Hosting Providers 2025">
<meta property="og:description" content="Compare hosting providers.">
<link rel="canonical" href="https://example.com/hosting">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question"}]}
</script>
</head>
<body>
<h1>Best Hosting Providers 2025</h1>
<h2>What is shared hosting?</h2>
<p>Shared hosting puts many websites on a single physical server. It is the cheapest option.</p>
<h2>Why choose managed WordPress hosting?</h2>
<p>Managed WordPress hosting handles updates, backups, and caching for you.</p>
<h3>How fast is each provider?</h3>
<p>We measured TTFB across nine regions over thirty days.</p>
</body></html>
"""

SHORT_HTML_NO_TITLE = """<!doctype html><html><body><p>Hi</p></body></html>"""

JS_HEAVY_PLACEHOLDER = (
    """<!doctype html><html><head><title>App</title>"""
    + ("<script>" + ("x=1;" * 1000) + "</script>") * 5
    + """</head><body><div id="root"></div></body></html>"""
)
