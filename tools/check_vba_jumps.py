#!/usr/bin/env python3
"""Check VBA jumps against docs/VBA_HOUSE_STYLE.md, Module rules.

``GoTo``, ``Resume <label>`` and ``On Error GoTo <label>`` must name a label
defined in the same procedure, labels must be unique within a procedure, and
every procedure must be closed. Jumps serve a single error/cleanup handler
only: no ``GoSub``, no computed ``On <expression> GoTo``, no
``On Error GoTo -1``, at most one ``On Error GoTo`` handler label and one other
(cleanup) label per procedure, and no backward ``GoTo``. Each compilation
environment of check_vba_conditionals.py is checked separately, so that
mutually exclusive ``#If`` branches are never combined.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from check_vba_conditionals import reachable_sources
from vba_lexer import (
    Finding,
    logical_units,
    read_component,
    report,
    split_statements,
    tracked_components,
)

ROOT = Path(__file__).resolve().parents[1]
PROC_OPEN = re.compile(
    r"^\s*(?:(?:Public|Private|Friend)\s+)?(?:Static\s+)?"
    r"(Sub|Function|Property\s+(?:Get|Let|Set))\s+([A-Za-z_]\w*)\b", re.IGNORECASE)
PROC_CLOSE = re.compile(r"^\s*End\s+(Sub|Function|Property)\b", re.IGNORECASE)
NAMED_LABEL = re.compile(r"^\s*([A-Za-z_]\w*|\d+):")
# A line number, followed by a statement or by nothing once a comment such
# as "100 Rem target" or "100 ' target" has been stripped.
NUMBERED_LABEL = re.compile(r"^\s*(\d+)(?=\s|$)")
# A keyword after a dot is a member call, such as Application.Goto or .Goto
# in a With block, not a jump.
JUMP = re.compile(r"(?<![\w.])(GoTo|GoSub|Resume)\b(?:\s+([A-Za-z_]\w*|\d+|-1))?", re.IGNORECASE)
ON_ERROR = re.compile(r"\bon\s+error\s*$", re.IGNORECASE)
# On <expression> GoTo|GoSub <label>, <label>, ...: every listed target.
LABEL = r"(?:[A-Za-z_]\w*|\d+)"
COMPUTED_JUMP = re.compile(rf"\bOn\b(?!\s+Error\b).*?(?<![\w.])(GoTo|GoSub)\s+"
                           rf"({LABEL}(?:\s*,\s*{LABEL})*)", re.IGNORECASE)
# Statements that can stand alone before a colon, as in "Else: x = 1"; a
# keyword is never a label.
KEYWORDS = frozenset({"beep", "do", "else", "end", "loop", "next", "resume", "return", "stop",
                      "wend"})


ON_ERROR_GOTO = "On Error GoTo"


@dataclass
class Procedure:
    name: str
    line: int
    labels: dict[str, int] = field(default_factory=dict)
    jumps: list[tuple[int, str, str]] = field(default_factory=list)
    forbidden: list[tuple[int, str]] = field(default_factory=list)


def is_procedure(code: str) -> re.Match[str] | None:
    """A procedure header; a Declare statement never matches, since its
    keyword stands where PROC_OPEN expects Sub, Function or Property."""
    return PROC_OPEN.match(code)


def label_at_start(code: str) -> str | None:
    match = NAMED_LABEL.match(code) or NUMBERED_LABEL.match(code)
    return match.group(1) if match and match.group(1).casefold() not in KEYWORDS else None


def statement_jumps(code: str) -> list[tuple[str, str]]:
    """``(operation, target)`` for each jump to a label in one statement.

    ``Resume``, ``Resume 0``, ``Resume Next`` and ``On Error GoTo 0`` or ``-1`` name no
    label; ``On Error GoTo <label>`` is reported as the operation ``On Error GoTo``;
    ``On <expression> GoTo`` and ``GoSub`` name every target of their list.
    """
    jumps: list[tuple[str, str]] = []
    computed = COMPUTED_JUMP.search(code)
    if computed:
        jumps.extend((computed.group(1), target.strip())
                     for target in computed.group(2).split(","))
        code = code[:computed.start()] + " " * (computed.end() - computed.start()) + \
            code[computed.end():]
    for match in JUMP.finditer(code):
        operation, target = match.group(1), match.group(2)
        if target is None or (operation.casefold() == "resume"
                              and target.casefold() in {"next", "0"}):
            continue
        on_error = operation.casefold() == "goto" and ON_ERROR.search(code[:match.start()])
        if on_error and target in {"0", "-1"}:
            continue
        jumps.append((ON_ERROR_GOTO if on_error else operation, target))
    return jumps


def statement_forbidden(code: str) -> list[str]:
    """The jumps the house style forbids in one statement, as messages."""
    messages: list[str] = []
    computed = COMPUTED_JUMP.search(code)
    if computed:
        messages.append(f"On <expression> {computed.group(1)} is a computed jump; jumps serve a "
                        "single error/cleanup handler only")
        code = code[:computed.start()] + " " * (computed.end() - computed.start()) + \
            code[computed.end():]
    for match in JUMP.finditer(code):
        operation, target = match.group(1).casefold(), match.group(2)
        if operation == "gosub":
            messages.append("GoSub is not allowed")
        elif operation == "goto" and target == "-1" and ON_ERROR.search(code[:match.start()]):
            messages.append("On Error GoTo -1 is not allowed")
    return messages


def scan(path: str, text: str) -> tuple[list[Procedure], list[Finding]]:
    """Collect each procedure's labels and jumps; report structural defects."""
    procedures: list[Procedure] = []
    findings: list[Finding] = []
    current: Procedure | None = None
    for line, _, _, code in logical_units(text.split("\n"), blank_strings=True):
        # A label starts the logical line; the statements after it, split at
        # ":" separators, may open or close a procedure and may jump.
        label = label_at_start(code) if current is not None else None
        if current is not None and label is not None:
            if label.casefold() in current.labels:
                findings.append(Finding(path, line, f"duplicate label {label!r} in procedure "
                                                    f"{current.name}; first defined at line "
                                                    f"{current.labels[label.casefold()]}"))
            else:
                current.labels[label.casefold()] = line
        for statement in split_statements(code):
            current = scan_statement(path, line, statement, current, procedures, findings)
    if current is not None:
        findings.append(Finding(path, current.line, f"procedure {current.name} is not closed"))
    return procedures, findings


def scan_statement(path: str, line: int, statement: str, current: Procedure | None,
                   procedures: list[Procedure], findings: list[Finding]) -> Procedure | None:
    """Apply one statement; return the procedure open after it."""
    opener = is_procedure(statement)
    if opener:
        if current is not None:
            findings.append(Finding(path, line, f"procedure {current.name} opened at line "
                                                f"{current.line} is not closed before "
                                                f"{opener.group(2)}"))
        current = Procedure(opener.group(2), line)
        procedures.append(current)
    elif PROC_CLOSE.match(statement):
        if current is None:
            findings.append(Finding(path, line, "End statement outside any procedure"))
        current = None
    elif current is not None:
        current.jumps.extend((line, operation, target)
                             for operation, target in statement_jumps(statement))
        current.forbidden.extend((line, message) for message in statement_forbidden(statement))
    elif statement_forbidden(statement) or statement_jumps(statement):
        findings.append(Finding(path, line, "jump statement outside any procedure"))
    return current


def handler_findings(path: str, procedure: Procedure) -> list[Finding]:
    """One handler label, one cleanup label and forward GoTo only."""
    findings: list[Finding] = []
    handlers: dict[str, int] = {}
    others: dict[str, int] = {}
    for line, operation, target in procedure.jumps:
        key = target.casefold()
        if operation == ON_ERROR_GOTO:
            handlers.setdefault(key, line)
        elif operation.casefold() in {"goto", "resume"}:
            others.setdefault(key, line)
        defined = procedure.labels.get(key)
        if operation.casefold() == "goto" and defined is not None and defined <= line:
            findings.append(Finding(path, line, f"GoTo {target} jumps backward in procedure "
                                                f"{procedure.name}; a backward jump is a loop"))
    if len(handlers) > 1:
        line = sorted(handlers.values())[1]
        findings.append(Finding(path, line, f"procedure {procedure.name} has more than one "
                                            "On Error GoTo handler label"))
    cleanup = {key: line for key, line in others.items() if key not in handlers}
    if len(cleanup) > 1:
        line = sorted(cleanup.values())[1]
        findings.append(Finding(path, line, f"procedure {procedure.name} jumps to more than one "
                                            "label besides its error handler"))
    return findings


def analyze_source(path: str, text: str) -> list[Finding]:
    procedures, findings = scan(path, text)
    for procedure in procedures:
        findings.extend(Finding(path, line, message) for line, message in procedure.forbidden)
        findings.extend(Finding(path, line, f"{operation} target {target!r} is not a label of "
                                            f"procedure {procedure.name}")
                        for line, operation, target in procedure.jumps
                        if target.casefold() not in procedure.labels)
        findings.extend(handler_findings(path, procedure))
    return findings


def analyze(path: str, text: str) -> list[Finding]:
    """Findings of every environment, each listed once with the environments it occurs in."""
    sources, findings = reachable_sources(path, text)
    environments: dict[Finding, list[str]] = {}
    for environment, source in sources.items():
        for finding in analyze_source(path, source):
            environments.setdefault(finding, []).append(environment)
    findings.extend(Finding(item.path, item.line, f"{item.message} [{', '.join(names)}]")
                    for item, names in environments.items())
    return findings


def check(root: Path) -> tuple[list[Finding], int, int]:
    components = tracked_components(root)
    findings: list[Finding] = []
    procedures = 0
    for path in components:
        text = read_component(root, path)
        findings.extend(analyze(path, text))
        procedures += sum(bool(is_procedure(statement)) for _, _, _, code
                          in logical_units(text.split("\n"), blank_strings=True)
                          for statement in split_statements(code))
    return findings, len(components), procedures


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    findings, components, procedures = check(args.root.resolve())
    return report("vba-jumps", findings,
                  f"{components} VBA component(s), {procedures} procedure(s)")


if __name__ == "__main__":
    sys.exit(main())
