#!/usr/bin/env python3
"""Check native declarations, dynamic calls and COM object construction in VBA.

docs/VBA_HOUSE_STYLE.md, Module rules: calculation code makes no native,
dynamic or late-bound call. These constructs are reported:

- ``Declare``: a native library declaration;
- ``CreateObject`` and ``GetObject``, with or without parentheses;
- ``New`` of a type that is neither a component of this project nor
  ``Collection``: an automation (COM) object, as in ``New Scripting.Dictionary``;
- ``CallByName``, ``AddressOf``, ``Run``, ``Evaluate``, ``ExecuteExcel4Macro``,
  ``OnTime``, ``OnKey`` and ``MacroOptions``, unqualified or as a member
  (``Application.Run``, ``.Run`` in a ``With`` block), and a ``[...]``
  expression, which Excel evaluates.

In src/core/, src/api/, tests/unit/ and any other home they are never
allowed. In the host homes, src/host/excel/ and tests/host/, each needs a
reviewed exception in tools/vba-exceptions.json; a ``Declare`` is allowed in
src/host/excel/ only. An exception that matches nothing is stale and is
reported too. Every ``#If`` branch is read at once. This is a name-based
static rule, not a resolution of calls; the *Static checks* section of
docs/VBA_HOUSE_STYLE.md lists its limits.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from check_vba_jumps import PROC_CLOSE, is_procedure
from vba_lexer import (
    Finding,
    logical_units,
    read_component,
    report,
    split_statements,
    strip_code,
    tracked_components,
)

ROOT = Path(__file__).resolve().parents[1]
EXCEPTIONS = "tools/vba-exceptions.json"
SCHEMA = "klcr-vba-exceptions"
ADAPTER = "src/host/excel/"
HOST_HOMES = (ADAPTER, "tests/host/")
FIELDS = ("path", "procedure", "construct", "target", "issue", "reason", "reviewed_by", "date")
# Constructs whose exception names a target: the declared procedure, the
# literal ProgID or the type created.
TARGETED = ("Declare", "CreateObject", "New")
DYNAMIC_NAMES = ("CallByName", "AddressOf", "Run", "Evaluate", "ExecuteExcel4Macro", "OnTime",
                 "OnKey", "MacroOptions")
CONSTRUCTS = (*TARGETED, "GetObject", *DYNAMIC_NAMES, "[...]")
CANONICAL = {name.casefold(): name for name in CONSTRUCTS}

DECLARE = re.compile(r"^(?:(?:Public|Private|Global)\s+)?Declare\s+(?:PtrSafe\s+)?"
                     r"(?:Function|Sub)\s+([A-Za-z_]\w*)", re.I)
# CreateObject and GetObject in any call form: with or without parentheses,
# as VBA allows for a call whose result is not used, with the literal argument
# only when it is the whole argument list: a concatenated ProgID or a server
# name leaves the object type to run time.
OBJECT = re.compile(r'(?<![\w.])(CreateObject|GetObject)\b\s*\(?\s*(?:"([^"]*)"\s*(?:\)|$))?',
                    re.I)
STRING = re.compile(r'"(?:[^"]|"")*"?')
# A dynamic call, unqualified or as a member of any object: only a preceding
# letter, digit or underscore makes it part of another name.
DYNAMIC = re.compile(rf"(?<!\w)({'|'.join(DYNAMIC_NAMES)})\b", re.I)
# A standalone New or As New, with the type optionally library-qualified.
NEW = re.compile(r"(?<![\w.])New\s+((?:[A-Za-z_]\w*\.)?[A-Za-z_]\w*)", re.I)
BUILTIN_TYPES = frozenset({"collection", "vba.collection"})
# Bracketed expressions such as [A1] are evaluated by Excel; an Enum's hidden
# member such as [_First] is not.
BRACKET = re.compile(r"\[(?!_\w*\])")
# A numeric line label, an explicit Call, and the VBA library qualifiers that
# reach a built-in under another name, as in VBA.Interaction.CreateObject.
LINE_LABEL = re.compile(r"^\s*\d+(?=\s|$)\s*")
CALL = re.compile(r"^Call\s+", re.I)
VBA_QUALIFIER = re.compile(r"(?<![\w.])(?:VBA\.)?(?:Interaction|Information|Strings|Conversion)\.|"
                           r"(?<![\w.])VBA\.(?!Collection\b)", re.I)
# The members of a Type or Enum block are names, not statements: Run As
# Double is a field and Evaluate = 1 a member, also in brackets as [Run].
BLOCK_OPEN = re.compile(r"^(?:(?:Public|Private)\s+)?(?:Type|Enum)\s+[A-Za-z_]", re.I)
BLOCK_CLOSE = re.compile(r"^End\s+(?:Type|Enum)\b", re.I)
MEMBER_NAME = re.compile(r"^(?:[A-Za-z_]\w*|\[[^\]]*\])")


@dataclass(frozen=True)
class Use:
    """One construct in one component: where, in which procedure, on what."""

    path: str
    line: int
    procedure: str | None
    construct: str
    target: str | None

    def key(self) -> tuple[str, str | None, str, str | None]:
        return (self.path, self.procedure and self.procedure.casefold(), self.construct,
                self.target and self.target.casefold())


def normalize(statement: str) -> str:
    """The statement without a numeric line label, an explicit Call or VBA
    library qualifiers, so that Call VBA.Interaction.CreateObject("X") reads
    as CreateObject("X")."""
    return VBA_QUALIFIER.sub("", CALL.sub("", LINE_LABEL.sub("", statement).strip()))


def statements(text: str) -> list[tuple[int, str, str]]:
    """``(line, code, raw)`` per statement, code with strings blanked; directives
    are skipped, so every #If branch is read. Each statement is split once,
    with its strings, and then blanked, so code and raw always pair up."""
    result: list[tuple[int, str, str]] = []
    for line, _, kind, raw in logical_units(text.split("\n")):
        if kind == "directive" or raw.lstrip().startswith(("Attribute ", "Option ")):
            continue
        result.extend((line, normalize(strip_code(part, blank_strings=True)), normalize(part))
                      for part in split_statements(raw))
    return result


def constructs(code: str, raw: str, classes: frozenset[str]) -> list[tuple[str, str | None]]:
    """``(construct, target)`` for each construct in one statement."""
    found: list[tuple[str, str | None]] = []
    declaration = DECLARE.match(code)
    if declaration:
        found.append(("Declare", declaration.group(1)))
    literals = [match.span() for match in STRING.finditer(raw)]
    for match in OBJECT.finditer(raw):
        if not any(start <= match.start() < end for start, end in literals):
            name = CANONICAL[match.group(1).casefold()]
            found.append((name, match.group(2) if name == "CreateObject" else None))
    for match in NEW.finditer(code):
        if match.group(1).casefold() not in BUILTIN_TYPES | classes:
            found.append(("New", match.group(1)))
    found.extend((CANONICAL[match.group(1).casefold()], None) for match in DYNAMIC.finditer(code))
    if BRACKET.search(STRING.sub('""', raw)):
        found.append(("[...]", None))
    return found


def uses(path: str, text: str, classes: frozenset[str]) -> list[Use]:
    """Every construct of one component, with the procedure it is in."""
    result: list[Use] = []
    procedure: str | None = None
    member = False
    for line, statement, raw_statement in statements(text):
        code, raw = statement, raw_statement
        header = is_procedure(code)
        # A procedure header also ends a block, so that a missing End Type
        # cannot hide the statements after it.
        if BLOCK_CLOSE.match(code) or header:
            member = False
        elif member:
            code, raw = MEMBER_NAME.sub("", code), MEMBER_NAME.sub("", raw)
        elif BLOCK_OPEN.match(code):
            member = True
        if header:
            procedure = header.group(2)
        result.extend(Use(path, line, procedure, construct, target)
                      for construct, target in constructs(code, raw, classes))
        if PROC_CLOSE.match(statement):
            procedure = None
    return list(dict.fromkeys(result))


def text_field(entry: dict[str, Any], name: str) -> bool:
    value = entry.get(name)
    return isinstance(value, str) and value.strip() == value and bool(value)


def real_date(value: Any) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def entry_problems(entry: Any) -> list[str]:
    """What is wrong with one exception entry, as messages."""
    if not isinstance(entry, dict):
        return ["an exception must be an object"]
    problems = [f"unknown field {name!r}" for name in entry if name not in FIELDS]
    problems += [f"missing field {name!r}" for name in FIELDS if name not in entry]
    if problems:
        return problems
    construct, path = entry["construct"], entry["path"]
    if construct not in CONSTRUCTS:
        problems.append(f"construct must be one of {', '.join(CONSTRUCTS)}")
    if not text_field(entry, "path") or not str(path).startswith(HOST_HOMES):
        problems.append(f"path must be a component in {' or '.join(HOST_HOMES)}")
    elif construct == "Declare" and not str(path).startswith(ADAPTER):
        problems.append(f"a Declare is allowed in {ADAPTER} only")
    if entry["procedure"] is not None and not text_field(entry, "procedure"):
        problems.append("procedure must be a name, or null at module level")
    if construct in TARGETED and not text_field(entry, "target"):
        problems.append(f"a {construct} exception names its target")
    elif construct not in TARGETED and entry["target"] is not None:
        problems.append(f"a {construct} exception has a null target")
    issue = entry["issue"]
    if not isinstance(issue, int) or isinstance(issue, bool) or issue < 1:
        problems.append("issue must be a positive issue number")
    for name in ("reason", "reviewed_by"):
        if not text_field(entry, name):
            problems.append(f"{name} must be a non-empty text")
    if not real_date(entry["date"]):
        problems.append("date must be a real date written YYYY-MM-DD")
    return problems


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    keys = [key for key, _ in pairs]
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        raise ValueError(f"duplicate key(s) {', '.join(duplicates)}")
    return dict(pairs)


def reject_constant(name: str) -> None:
    raise ValueError(f"non-finite number {name}")


def load_exceptions(root: Path) -> tuple[list[dict[str, Any]], list[Finding]]:
    """The valid exception entries and the findings about the file."""
    path = root / EXCEPTIONS
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object,
                          parse_constant=reject_constant)
    except (OSError, ValueError) as error:
        return [], [Finding(EXCEPTIONS, None, f"cannot be read: {error}")]
    if not isinstance(data, dict) or set(data) != {"schema", "version", "exceptions"} or \
            data["schema"] != SCHEMA or data["version"] != 1 or \
            not isinstance(data["exceptions"], list):
        return [], [Finding(EXCEPTIONS, None, f'must be {{"schema": "{SCHEMA}", "version": 1, '
                                              '"exceptions": [...]}')]
    entries: list[dict[str, Any]] = []
    findings: list[Finding] = []
    seen: set[tuple[Any, ...]] = set()
    for index, entry in enumerate(data["exceptions"]):
        problems = entry_problems(entry)
        if not problems:
            key = Use(entry["path"], 0, entry["procedure"], entry["construct"],
                      entry["target"]).key()
            if key in seen:
                problems = ["duplicates an earlier exception"]
            seen.add(key)
        findings.extend(Finding(EXCEPTIONS, None, f"exceptions[{index}]: {problem}")
                        for problem in problems)
        if not problems:
            entries.append(entry)
    return entries, findings


def describe(use: Use) -> str:
    target = f" {use.target}" if use.target else ""
    where = f"procedure {use.procedure}" if use.procedure else "module level"
    return f"{use.construct}{target} ({where})"


def verdict(use: Use, covered: bool) -> str | None:
    """The finding message for one use, or None when an exception covers it."""
    if not use.path.startswith(HOST_HOMES):
        return f"{describe(use)}: not allowed outside {' and '.join(HOST_HOMES)}"
    if use.construct == "Declare" and not use.path.startswith(ADAPTER):
        return f"{describe(use)}: a Declare is allowed in {ADAPTER} only"
    if use.construct == "CreateObject" and use.target is None:
        return (f"{describe(use)}: the ProgID is not a literal, so no exception can cover it")
    if covered:
        return None
    return f"{describe(use)}: needs a reviewed exception in {EXCEPTIONS}"


def analyze(root: Path, components: Sequence[str]) -> tuple[list[Finding], int]:
    """Findings for these components and the exceptions file; the number of uses."""
    entries, findings = load_exceptions(root)
    classes = frozenset(Path(path).stem.casefold() for path in components
                        if Path(path).suffix.lower() in {".cls", ".frm"})
    allowed = {Use(entry["path"], 0, entry["procedure"], entry["construct"],
                   entry["target"]).key(): index for index, entry in enumerate(entries)}
    used: set[int] = set()
    count = 0
    for path in components:
        for use in uses(path, read_component(root, path), classes):
            count += 1
            index = allowed.get(use.key())
            message = verdict(use, index is not None)
            if message is None and index is not None:
                used.add(index)
            elif message:
                findings.append(Finding(path, use.line, message))
    findings.extend(Finding(EXCEPTIONS, None, f"stale exception for {entry['construct']} in "
                                              f"{entry['path']}: it matches no use")
                    for index, entry in enumerate(entries) if index not in used)
    return findings, count


def check(root: Path) -> tuple[list[Finding], int, int]:
    components = tracked_components(root)
    findings, count = analyze(root, components)
    return findings, len(components), count


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    findings, components, count = check(args.root.resolve())
    return report("vba-dynamic", findings,
                  f"{components} VBA component(s), {count} native, dynamic or COM use(s)")


if __name__ == "__main__":
    sys.exit(main())
