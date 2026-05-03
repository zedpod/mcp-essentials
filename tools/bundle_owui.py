"""
Bundle a tool's core/ + OWUI wrapper into a single paste-portable file.

OWUI Admin → Tools accepts one Python file. This script concatenates `core/*.py`
plus an OWUI Tools class shell into `<tool>/owui/main.py`.

Usage:
    python tools/bundle_owui.py qrforge          # regenerate qrforge/owui/main.py
    python tools/bundle_owui.py qrforge --check  # exit 1 if regen would change the file

Per-tool inputs (under <tool>/owui/):
    _meta.py        Module attributes:
                        TITLE, DESCRIPTION, AUTHOR, VERSION, REQUIRED_OPEN_WEBUI_VERSION
    _wrapper.py     The OWUI Tools class. Imports from core/ are stripped at bundle time;
                    the names land in scope after the inlined core code.

Per-tool inputs (under <tool>/core/):
    __init__.py     Must define `__bundle_order__: list[str]` — module names (without .py)
                    in inclusion order. e.g. ["types", "i18n", "http", "qr", "render"].
"""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Imports we strip because they resolve to names already in the bundled scope.
# Anything else gets hoisted to the top of the bundle.
INTRA_IMPORT_RE = re.compile(
    r"""^\s*from\s+
        (?:
            \.\w*           # relative: from . / from .types / from .core.types
            |
            [\w_]+\.core(?:\.\w+)?   # absolute: from <tool>.core / from <tool>.core.types
        )
        \s+import\s+.*$
    """,
    re.VERBOSE,
)

EXTERNAL_IMPORT_RE = re.compile(
    r"""^\s*(?:
        import\s+\S.*
        |
        from\s+(?!\.|\w+\.core)[^\s]+\s+import\s+.*
    )$
    """,
    re.VERBOSE,
)


def load_meta(meta_path: Path) -> dict:
    """Load TITLE/DESCRIPTION/etc. attributes from a tool's owui/_meta.py."""
    spec = spec_from_file_location(f"_meta_{meta_path.parent.parent.name}", meta_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {meta_path}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    required = ("TITLE", "DESCRIPTION", "AUTHOR", "VERSION", "REQUIRED_OPEN_WEBUI_VERSION")
    out = {}
    for key in required:
        if not hasattr(module, key):
            raise RuntimeError(f"{meta_path} missing attribute {key}")
        out[key] = getattr(module, key)
    return out


def load_bundle_order(core_init: Path) -> list[str]:
    """Read __bundle_order__ from <tool>/core/__init__.py."""
    text = core_init.read_text(encoding="utf-8")
    match = re.search(r"__bundle_order__\s*=\s*\[([^\]]*)\]", text, re.DOTALL)
    if not match:
        raise RuntimeError(f"{core_init} missing __bundle_order__ list")
    raw = match.group(1)
    items = re.findall(r"['\"]([^'\"]+)['\"]", raw)
    if not items:
        raise RuntimeError(f"{core_init} __bundle_order__ is empty")
    return items


def _is_top_level(line: str) -> bool:
    """True iff the line starts at column 0 (not indented inside a function/class)."""
    return bool(line) and not line.startswith((" ", "\t"))


def split_module(text: str) -> tuple[list[str], str]:
    """Return (external_imports, body_without_top_level_imports).

    - Only top-level imports are hoisted. Imports inside function/class bodies
      (indented) are preserved verbatim — they often guard optional dependencies.
    - Intra-package imports (`from .` or `from <tool>.core...`) are dropped at the
      top level because the names are already inlined elsewhere in the bundle.
      Multi-line parenthesized forms are skipped as a unit.
    - The leading module docstring is consumed (we synthesize our own header).
    """
    lines = text.splitlines()
    external: list[str] = []
    body_lines: list[str] = []

    skip_paren_until_close = False
    in_module_docstring = False
    docstring_quote: str | None = None
    consumed_leading_docstring = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip the leading module docstring entirely — the bundler writes the OWUI header.
        if not consumed_leading_docstring and not external and not body_lines:
            if not in_module_docstring:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    docstring_quote = stripped[:3]
                    if (
                        stripped.endswith(docstring_quote)
                        and len(stripped) >= 6
                        and stripped.count(docstring_quote) >= 2
                    ):
                        consumed_leading_docstring = True
                        i += 1
                        continue
                    in_module_docstring = True
                    i += 1
                    continue
                if stripped == "" or stripped.startswith("#"):
                    i += 1
                    continue
                consumed_leading_docstring = True
            else:
                if docstring_quote and docstring_quote in line:
                    in_module_docstring = False
                    consumed_leading_docstring = True
                i += 1
                continue

        # We're in the middle of a multi-line top-level intra-import; keep eating lines
        # until the closing paren.
        if skip_paren_until_close:
            if ")" in line:
                skip_paren_until_close = False
            i += 1
            continue

        # Only inspect *top-level* lines (column 0) for hoisting/stripping.
        if _is_top_level(line):
            if INTRA_IMPORT_RE.match(line):
                if "(" in line and ")" not in line:
                    skip_paren_until_close = True
                i += 1
                continue
            if EXTERNAL_IMPORT_RE.match(line):
                collected = [line]
                if "(" in line and ")" not in line:
                    while i + 1 < len(lines) and ")" not in lines[i + 1]:
                        i += 1
                        collected.append(lines[i])
                    if i + 1 < len(lines):
                        i += 1
                        collected.append(lines[i])
                external.append("\n".join(collected))
                i += 1
                continue

        body_lines.append(line)
        i += 1

    body = "\n".join(body_lines).strip("\n")
    return external, body


def dedupe_imports(import_blocks: list[str]) -> list[str]:
    """Deduplicate exact-match import statements and order them sensibly.

    Order: `from __future__` first (Python requires it before other code), then
    plain `import X` lines, then `from X import Y` lines. Within each bucket we
    sort alphabetically to keep output diffs minimal across regenerations.
    """
    seen: set[str] = set()
    futures: list[str] = []
    plain: list[str] = []
    froms: list[str] = []
    for block in import_blocks:
        normalized = " ".join(block.split())
        if normalized in seen:
            continue
        seen.add(normalized)
        first = block.lstrip().split("\n", 1)[0]
        if first.startswith("from __future__"):
            futures.append(block)
        elif first.startswith("import "):
            plain.append(block)
        else:
            froms.append(block)
    futures.sort(key=str.lower)
    plain.sort(key=str.lower)
    froms.sort(key=str.lower)
    return futures + plain + froms


def build_owui_bundle(tool_dir: Path) -> str:
    core_dir = tool_dir / "core"
    meta_path = tool_dir / "_owui_meta.py"
    wrapper_path = tool_dir / "_owui_wrapper.py"
    core_init = core_dir / "__init__.py"

    if not core_dir.is_dir():
        raise RuntimeError(f"{core_dir} missing")
    if not meta_path.is_file():
        raise RuntimeError(f"{meta_path} missing")
    if not wrapper_path.is_file():
        raise RuntimeError(f"{wrapper_path} missing")

    meta = load_meta(meta_path)
    order = load_bundle_order(core_init)

    all_imports: list[str] = []
    inlined_bodies: list[str] = []

    for module_name in order:
        module_file = core_dir / f"{module_name}.py"
        if not module_file.is_file():
            raise RuntimeError(f"{module_file} listed in __bundle_order__ but does not exist")
        text = module_file.read_text(encoding="utf-8")
        imports, body = split_module(text)
        all_imports.extend(imports)
        inlined_bodies.append(f"# === core/{module_name}.py ===\n{body}".rstrip())

    wrapper_imports, wrapper_body = split_module(wrapper_path.read_text(encoding="utf-8"))
    all_imports.extend(wrapper_imports)

    deduped = dedupe_imports(all_imports)

    header = textwrap.dedent(
        f'''\
        """
        title: {meta["TITLE"]}
        description: {meta["DESCRIPTION"]}
        author: {meta["AUTHOR"]}
        version: {meta["VERSION"]}
        required_open_webui_version: {meta["REQUIRED_OPEN_WEBUI_VERSION"]}
        """
        '''
    )

    autogen_notice = textwrap.dedent(
        """\
        # ────────────────────────────────────────────────────────────────────────────
        # AUTO-GENERATED BY tools/bundle_owui.py — DO NOT EDIT BY HAND.
        # Source of truth: this tool's core/ and owui/_wrapper.py.
        # Run `make bundle` (or `python tools/bundle_owui.py <tool>`) to regenerate.
        # CI runs `make check-bundle` and fails on drift.
        # ────────────────────────────────────────────────────────────────────────────
        """
    )

    parts = [
        header.rstrip() + "\n",
        autogen_notice,
        "\n".join(deduped),
        "",
        "\n\n".join(inlined_bodies),
        "",
        "# === owui/_wrapper.py ===",
        wrapper_body,
        "",
    ]
    return "\n".join(p for p in parts if p is not None) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("tool", help="tool directory name, e.g. qrforge")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if regenerating would change the file. Used in CI.",
    )
    args = parser.parse_args()

    tool_dir = REPO_ROOT / args.tool
    if not tool_dir.is_dir():
        print(f"error: {tool_dir} is not a directory", file=sys.stderr)
        return 2

    try:
        new_content = build_owui_bundle(tool_dir)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    out_path = tool_dir / "owui.py"

    if args.check:
        existing = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
        if existing != new_content:
            print(
                f"error: {out_path} is out of date. Run `python tools/bundle_owui.py {args.tool}`.",
                file=sys.stderr,
            )
            return 1
        print(f"{out_path.relative_to(REPO_ROOT)}: up to date.")
        return 0

    out_path.write_text(new_content, encoding="utf-8")
    print(f"wrote {out_path} ({len(new_content)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
