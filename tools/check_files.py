#!/usr/bin/env python3
"""Check tracked repository text with deterministic positive and negative fixtures."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".mjs", ".toml", ".txt",
                 ".bas", ".cls", ".frm"}
TEXT_NAMES = {".editorconfig", ".gitattributes", ".gitignore"}
EXCLUDED = {"LICENSE"}
# Byte-for-byte copies of regulatory sources (.gitattributes); only the README
# beside them is ordinary documentation.
SOURCE_COPIES = "docs/methodology/sources/"
SOURCE_README = SOURCE_COPIES + "README.md"


def validate(path: str, content: bytes) -> list[str]:
    """Return violations without depending on the checkout's line-ending conversion."""
    if path in EXCLUDED or (Path(path).suffix.lower() not in TEXT_SUFFIXES
                            and Path(path).name not in TEXT_NAMES):
        return []
    if path.startswith(SOURCE_COPIES) and path != SOURCE_README:
        return []
    errors: list[str] = []
    if not content:
        return [f"{path}: empty text file"]
    if b"\x00" in content:
        return [f"{path}: NUL byte"]
    try:
        content.decode("utf-8")
    except UnicodeDecodeError:
        return [f"{path}: invalid UTF-8"]
    if b"\r" in content:
        errors.append(f"{path}: CR byte in committed text")
    if not content.endswith(b"\n"):
        errors.append(f"{path}: missing final newline")
    for number, line in enumerate(content.split(b"\n"), 1):
        if line.endswith((b" ", b"\t")):
            errors.append(f"{path}:{number}: trailing whitespace")
    return errors


def tracked(root: Path) -> list[str]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=root, check=True,
                            capture_output=True)
    return [p.decode("utf-8") for p in result.stdout.split(b"\x00") if p]


def self_test() -> list[str]:
    cases = [
        ("README.md", b"# OK\n", False),
        ("tools/example.py", b"print(1)\n", False),
        (".github/workflows/ci.yml", b"name: CI\n", False),
        ("pyproject.toml", b"[tool.ruff]\n", False),
        ("pyproject.toml", b"[tool.ruff] \n", True),
        ("README.md", b"# Bad  \n", True),
        ("tools/example.py", b"print(1)", True),
        (".github/workflows/ci.yml", b"name: CI\r\n", True),
        ("tools/example.py", b"\xff\n", True),
        ("docs/methodology/sources/EBA_QA.md", b"Copy \r\nno final newline", False),
        ("docs/methodology/sources/README.md", b"# Sources \n", True),
    ]
    return [f"fixture {index}: unexpected outcome" for index, (path, data, bad)
            in enumerate(cases, 1) if bool(validate(path, data)) != bad]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    errors = self_test() if args.self_test else [
        message for path in tracked(root) for message in
        validate(path, subprocess.run(["git", "show", f":{path}"], cwd=root,
                                      check=True, capture_output=True).stdout)
    ]
    for error in errors:
        print(error, file=sys.stderr)
    if not errors:
        print("format fixtures passed" if args.self_test else "tracked text passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
