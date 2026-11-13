#!/usr/bin/env python3
"""Static checks of the prototype's VBA source, beyond the Repository integrity gates.

Per component of src/ and tests/: ASCII only, `Attribute VB_Name` equal to the
file name, `Option Explicit`, `Option Private Module` in the core and in the
tests, no tab, no trailing whitespace and no line over 120 columns. It runs on
its own (`python tools/check_source.py`); it is not a gate of tools/check.py.
Exit code 0 means no finding and 1 means at least one.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_COLUMNS = 120


def components(root: Path) -> list[Path]:
    """The VBA components of src/ and tests/, in a fixed order."""
    return (sorted(root.glob("src/**/*.bas")) + sorted(root.glob("src/**/*.cls"))
            + sorted(root.glob("tests/**/*.bas")))


def problems_in(path: Path, root: Path) -> list[str]:
    """What is wrong with one component, one finding per line."""
    raw = path.read_bytes()
    rel = path.relative_to(root)
    found: list[str] = []
    try:
        raw.decode("ascii")
    except UnicodeDecodeError as error:
        found.append(f"{rel}: non-ASCII byte at {error.start}")
    text = raw.decode("cp1252")
    name = re.search(r'Attribute VB_Name = "([^"]+)"', text)
    if not name or name.group(1) != path.stem:
        found.append(f"{rel}: VB_Name does not match the file name")
    if not re.search(r"^\s*Option Explicit\s*$", text, re.M):
        found.append(f"{rel}: no Option Explicit")
    if ("core" in path.parts or "tests" in path.parts) and "Option Private Module" not in text:
        found.append(f"{rel}: no Option Private Module")
    for number, line in enumerate(text.splitlines(), 1):
        if "\t" in line:
            found.append(f"{rel}:{number}: tab")
        if line != line.rstrip():
            found.append(f"{rel}:{number}: trailing whitespace")
        if len(line) > MAX_COLUMNS:
            found.append(f"{rel}:{number}: {len(line)} columns")
    return found


def check(root: Path = ROOT) -> list[str]:
    """Every finding of every component under root."""
    return [finding for path in components(root) for finding in problems_in(path, root)]


def main() -> int:
    findings = check()
    print("\n".join(findings) if findings else "check_source: OK")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
