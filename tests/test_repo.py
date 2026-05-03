"""
Repo-level invariants. These run on every PR to catch structural drift.

For each refactored tool, assert:
- Required files exist (core/, mcp/, owui/, tests/, requirements.txt, README.md, AGENTS.md).
- core/i18n.py STRINGS["en"] and STRINGS["tr"] cover identical key sets.
- mcp/server.py exposes a FastMCP `mcp` instance.

Tools that haven't been migrated yet are listed in LEGACY_TOOLS and skipped.
Move them to REFACTORED_TOOLS as each migration lands.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

REFACTORED_TOOLS: list[str] = [
    "askuser",
    "currencypulse",
    "flighthunter",
    "pagesignal",
    "paperforge",
    "qrforge",
    "signalbrief",
    "sitepulse",
    "tripweather",
    "tubescript",
]

LEGACY_TOOLS: list[str] = []


def _required_paths(tool: str) -> list[Path]:
    base = REPO_ROOT / tool
    return [
        base / "__init__.py",
        base / "__main__.py",
        base / "server.py",
        base / "owui.py",
        base / "_owui_meta.py",
        base / "_owui_wrapper.py",
        base / "core" / "__init__.py",
        base / "core" / "types.py",
        base / "core" / "i18n.py",
        base / "tests" / "__init__.py",
        base / "requirements.txt",
        base / "README.md",
        base / "AGENTS.md",
    ]


@pytest.mark.parametrize("tool", REFACTORED_TOOLS)
def test_required_files_present(tool: str) -> None:
    missing = [str(p.relative_to(REPO_ROOT)) for p in _required_paths(tool) if not p.exists()]
    assert not missing, f"{tool}: missing files: {missing}"


@pytest.mark.parametrize("tool", REFACTORED_TOOLS)
def test_i18n_key_parity(tool: str) -> None:
    module = importlib.import_module(f"{tool}.core.i18n")
    strings = getattr(module, "STRINGS", None)
    assert isinstance(strings, dict), f"{tool}.core.i18n.STRINGS not a dict"
    assert "en" in strings and "tr" in strings, f"{tool}: STRINGS must contain 'en' and 'tr'"
    en_keys = set(strings["en"].keys())
    tr_keys = set(strings["tr"].keys())
    diff_only_en = en_keys - tr_keys
    diff_only_tr = tr_keys - en_keys
    assert not diff_only_en, f"{tool}: keys missing from tr: {sorted(diff_only_en)}"
    assert not diff_only_tr, f"{tool}: keys missing from en: {sorted(diff_only_tr)}"


@pytest.mark.parametrize("tool", REFACTORED_TOOLS)
def test_mcp_server_exports_fastmcp(tool: str) -> None:
    from mcp.server.fastmcp import FastMCP

    module = importlib.import_module(f"{tool}.server")
    instance = getattr(module, "mcp", None)
    assert isinstance(instance, FastMCP), f"{tool}.server must export `mcp: FastMCP`"


@pytest.mark.parametrize("tool", LEGACY_TOOLS)
def test_legacy_tool_present(tool: str) -> None:
    """Sanity: legacy tools still ship a main.py until their wave lands."""
    legacy_main = REPO_ROOT / tool / "main.py"
    refactored_core = REPO_ROOT / tool / "core"
    assert legacy_main.exists() or refactored_core.is_dir(), (
        f"{tool}: neither legacy main.py nor refactored core/ found. "
        "Did you start a refactor? Move the tool to REFACTORED_TOOLS."
    )
