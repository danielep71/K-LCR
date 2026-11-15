#!/usr/bin/env python3
"""Check the evidence of an Excel run of the neutral harness against one commit.

The harness runs only in Excel, by hand (INSTALLATION.md, Recording host
evidence). This reads what that run left in an evidence folder and checks it
against the candidate commit, without Excel:

- candidate.txt, written when the workbook was built: the commit, a clean
  working tree and the fingerprint (Git blob id) of tools/vba-projects.json;
  each must match the commit checked here;
- exported/: the modules exported back from the workbook equal the
  development workbook's components at the commit, none missing or extra
  (the synchronization round trip);
- the four logs that tests/host/TEST_LCR_Excel_Evidence.bas saves: each holds,
  record for record, what the commit's example suite writes in its mode, with
  counts that agree with one another, finite numbers only and each failure
  with the detail the suite causes;
- verification.txt, the report of VerifyExampleModes: every mode ended as
  required, with the error code the commit's suite requires;
- environment.txt and host-state.txt: the supported host (Microsoft Excel,
  64-bit Office, VBA7) and the same host state after the runs as before;
- host.txt, written by hand: the Windows build, the references and the
  compile result.

Every file the run wrote must be newer than candidate.txt, and none may hold
a path. The verdict is PASS, FAIL or NOT_RUN: NOT_RUN when the folder holds
no output of a run at all. It proves only that the evidence is consistent
with the commit; it does not run Excel and validates no LCR calculation.

Exit status: 0 PASS, 1 FAIL, 2 NOT_RUN or the commit could not be read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "tools/vba-projects.json"
EXAMPLES = "tests/unit/TEST_LCR_Examples.bas"
HARNESS = "tests/unit/TEST_LCR_Harness.bas"
EXPORTED = "exported"
CANDIDATE = "candidate.txt"
VERIFICATION = "verification.txt"
ENVIRONMENT = "environment.txt"
HOST_STATE = "host-state.txt"
HOST = "host.txt"
LOGS = {"NORMAL": "normal.log", "INJECTED_FAILURE": "injected.log",
        "SKIPPED_CASE": "skipped.log", "CLEANUP_PROBLEM": "cleanup.log"}
RUN_OUTPUTS = (*LOGS.values(), VERIFICATION, ENVIRONMENT, HOST_STATE)
CANDIDATE_FIELDS = ("commit", "worktree", "manifest")
ENVIRONMENT_FIELDS = ("host", "version", "build", "os", "office", "runtime", "decimal", "country")
SUPPORTED = {"host": "Microsoft Excel", "office": "64-bit", "runtime": "VBA7"}
HOST_FIELDS = ("windows", "references", "compile")
REFERENCES = ("Visual Basic For Applications", "Microsoft Excel 16.0 Object Library",
              "OLE Automation", "Microsoft Office 16.0 Object Library")
SIMULATED_CLEANUP = "simulated: the host state changed during the run"
RECORD = re.compile(r"^([A-Z_]+)=(.*)$")
CONSTANT = re.compile(r"^\s*Private Const (\w+)\s+As Long = (\d+)\b", re.M)
PROCEDURE = re.compile(r"^(?:Public|Private) Sub (\w+)\(.*?^End Sub$", re.M | re.S)
BEGIN_CASE = re.compile(r'TEST_LCR_Harness\.BeginCase "([^"]+)"')
ASSERTION = re.compile(r'TEST_LCR_Harness\.Assert\w+ "([^"]+)"')
CALL = re.compile(r"^\s+(Case\w+)$", re.M)
SKIPPED = re.compile(r'If mMode <> "SKIPPED_CASE" Then\n((?:\s+Case\w+\n)+)\s+End If')
INJECTED = re.compile(r'If mMode = "INJECTED_FAILURE" Then\n((?:.*\n)*?)\s+End If')
ASSIGNED = re.compile(r"^\s+(\w+) = ", re.M)
NUMBER = re.compile(r"^-?\d+(?:\.\d+)?(?:E[+-]?\d+)?$", re.I)
PATH = re.compile(r"[A-Za-z]:[\\/]|\\\\|(?<![\w.])/(?:home|Users|root)/|\\Users\\", re.I)
FAILED_CONSTANT = re.compile(r"^\s*Public Const ERR_TEST_FAILED\s+As Long = &H([0-9A-F]+)\b", re.M | re.I)
EQUAL_DOUBLE = re.compile(r'TEST_LCR_Harness\.AssertEqualDouble "([^"]+)", ([-+0-9.E#]+),', re.I)
DOCUMENT_HEADER = re.compile(r"^(?:VERSION |BEGIN|\s+\w+ = |END$|Attribute VB_)")


@dataclass
class Record:
    """One log line: its key, its first value and its named fields."""

    key: str
    value: str
    fields: dict[str, str]
    line: int


@dataclass
class Suite:
    """What the commit's example suite runs: case and assertion identifiers in
    order, the cases that SKIPPED_CASE leaves out and the assertions whose value
    INJECTED_FAILURE changes."""

    cases: list[str]
    assertions: list[str]
    skipped: list[str]
    injected: list[str]
    expected_cases: int
    expected_assertions: int
    literals: dict[str, float] = field(default_factory=dict)


@dataclass
class Plan:
    """What one mode's run must log: its cases and assertions in order, the
    failures it must report, its cleanup outcome and its RESULT."""

    mode: str
    cases: list[str]
    assertions: list[str]
    failing: list[str]
    cleanup: str
    result: dict[str, str]


@dataclass
class Evidence:
    findings: list[str] = field(default_factory=list)
    hashes: dict[str, str] = field(default_factory=dict)
    candidate: dict[str, str] = field(default_factory=dict)
    environment: dict[str, str] = field(default_factory=dict)
    host: dict[str, str] = field(default_factory=dict)
    modes: dict[str, str] = field(default_factory=dict)
    ran: bool = False


def git(root: Path, *args: str) -> bytes:
    completed = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace").strip())
    return completed.stdout


def git_blob(data: bytes) -> str:
    """The Git blob id of ``data``, as ``git hash-object`` gives it."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def read_fields(path: Path) -> dict[str, str]:
    """The ``key=value`` lines of a small record file."""
    fields: dict[str, str] = {}
    for text in path.read_text(encoding="utf-8", errors="replace").splitlines():
        key, separator, value = text.partition("=")
        if separator:
            fields[key.strip()] = value.strip()
    return fields


def components(root: Path, commit: str) -> dict[str, tuple[bytes, bool]]:
    """The development workbook's components at the commit, by file name: the
    file (LF line ends) and whether it is a document module."""
    manifest = json.loads(git(root, "show", f"{commit}:{MANIFEST}"))
    listed = [(path, False) for path in manifest["configurations"]["development"]["modules"]]
    listed += [(path, True) for path in manifest["document_modules"]]
    return {Path(path).name: (git(root, "show", f"{commit}:{path}"), document)
            for path, document in listed}


def code_body(data: bytes) -> bytes:
    """A document module without its header and Attribute lines: the code that a
    synchronization replaces, whatever the sheet's own attributes are."""
    lines = data.replace(b"\r\n", b"\n").decode("ascii", errors="replace").split("\n")
    start = 0
    while start < len(lines) and DOCUMENT_HEADER.match(lines[start]):
        start += 1
    return "\n".join(lines[start:]).strip("\n").encode("ascii", errors="replace")


def first_difference(actual: bytes, expected: bytes) -> int:
    for number, (left, right) in enumerate(zip(actual.split(b"\n"), expected.split(b"\n"),
                                               strict=False), 1):
        if left != right:
            return number
    return min(actual.count(b"\n"), expected.count(b"\n")) + 1


def check_candidate(root: Path, commit: str, folder: Path, evidence: Evidence) -> None:
    path = folder / CANDIDATE
    if not path.is_file():
        evidence.findings.append(f"{CANDIDATE}: missing: the folder was not prepared by a workbook "
                                 "build, so the run cannot be tied to a commit")
        return
    evidence.candidate = read_fields(path)
    for key in CANDIDATE_FIELDS:
        if not evidence.candidate.get(key):
            evidence.findings.append(f"{CANDIDATE}: no {key}=")
    built = evidence.candidate.get("commit", "")
    if built and built != commit:
        evidence.findings.append(f"{CANDIDATE}: stale or mismatched evidence: the workbook was built "
                                 f"from {built}, not from {commit}")
    worktree = evidence.candidate.get("worktree", "")
    if worktree and worktree != "clean":
        evidence.findings.append(f"{CANDIDATE}: worktree={worktree}: the workbook was built from a "
                                 "working tree with local changes")
    manifest = git_blob(git(root, "show", f"{commit}:{MANIFEST}"))
    evidence.hashes[MANIFEST] = manifest
    recorded = evidence.candidate.get("manifest", "")
    if recorded and recorded != manifest:
        evidence.findings.append(f"{CANDIDATE}: manifest={recorded} is not {MANIFEST} at "
                                 f"{commit[:12]} ({manifest})")


def check_sources(root: Path, commit: str, folder: Path, evidence: Evidence) -> dict[str, bytes]:
    expected = components(root, commit)
    exported = folder / EXPORTED
    present = {path.name: path for path in exported.iterdir()} if exported.is_dir() else {}
    if not present:
        evidence.findings.append(f"{EXPORTED}/: no module exported from the workbook")
    for name, (data, document) in sorted(expected.items()):
        evidence.hashes[name] = git_blob(data)
        if name not in present:
            if present:
                evidence.findings.append(f"{EXPORTED}/{name}: not exported from the workbook")
            continue
        actual = present[name].read_bytes().replace(b"\r\n", b"\n")
        wanted = data
        if document:
            actual, wanted = code_body(actual), code_body(data)
        if actual != wanted:
            evidence.findings.append(f"{EXPORTED}/{name}: differs from {name} at {commit[:12]} "
                                     f"(first difference at line {first_difference(actual, wanted)})")
    for name in sorted(set(present) - set(expected)):
        evidence.findings.append(f"{EXPORTED}/{name}: not a component of the development workbook")
    return {name: data for name, (data, _) in expected.items()}


def read_suite(source: bytes) -> Suite:
    text = source.decode("ascii", errors="replace").replace("\r\n", "\n")
    bodies = {match.group(1): match.group(0) for match in PROCEDURE.finditer(text)}
    constants = {name: int(value) for name, value in CONSTANT.findall(text)}
    runner = bodies.get("RunSuite", "")
    skipped_calls = {name for block in SKIPPED.findall(runner) for name in block.split()}
    suite = Suite([], [], [], [], constants.get("EXPECTED_CASES", -1),
                  constants.get("EXPECTED_ASSERTIONS", -1))
    for name in CALL.findall(runner):
        body = bodies.get(name, "")
        case = BEGIN_CASE.findall(body)
        case_id = case[0] if case else name
        suite.cases += case
        changed = {variable for block in INJECTED.findall(body)
                   for variable in ASSIGNED.findall(block)}
        statements = re.sub(r" _\n\s*", " ", body).split("\n")
        for statement in statements:
            for item, literal in EQUAL_DOUBLE.findall(statement):
                suite.literals[f"{case_id}/{item}"] = float(literal.rstrip("#"))
            for item in ASSERTION.findall(statement):
                suite.assertions.append(f"{case_id}/{item}")
                if any(re.search(rf"\b{variable}\b", statement) for variable in changed):
                    suite.injected.append(f"{case_id}/{item}")
                if name in skipped_calls:
                    suite.skipped.append(f"{case_id}/{item}")
        if name in skipped_calls:
            suite.skipped += case
    return suite


def failed_error(root: Path, commit: str, evidence: Evidence) -> int:
    """TEST_LCR_Harness.ERR_TEST_FAILED at the commit, as the signed Long VBA reports."""
    try:
        source = git(root, "show", f"{commit}:{HARNESS}").decode("ascii", errors="replace")
    except RuntimeError:
        source = ""
    found = FAILED_CONSTANT.search(source)
    if found is None:
        evidence.findings.append(f"no ERR_TEST_FAILED in {HARNESS} at {commit[:12]}")
        return 0
    value = int(found.group(1), 16)
    return value - (1 << 32) if value >= 1 << 31 else value


def plans(suite: Suite) -> list[Plan]:
    skipped = set(suite.skipped)
    kept_cases = [case for case in suite.cases if case not in skipped]
    kept_assertions = [item for item in suite.assertions if item not in skipped]

    def result(verdict: str, operation: str, complete: bool, kept: tuple[list[str], list[str]],
               failures: int, cleanup: str = "PASS") -> dict[str, str]:
        return {"RESULT": verdict, "suite": "examples", "operation": operation,
                "completeness": "COMPLETE" if complete else "INCOMPLETE",
                "cases": str(len(kept[0])), "assertions": str(len(kept[1])),
                "failures": str(failures), "cleanup": cleanup,
                "recovery": "NONE" if cleanup == "PASS" else "REQUIRED"}

    every = (suite.cases, suite.assertions)
    kept = (kept_cases, kept_assertions)
    return [Plan("NORMAL", *every, [], "PASS", result("PASS", "PASS", True, every, 0)),
            Plan("INJECTED_FAILURE", *every, suite.injected, "PASS",
                 result("FAIL", "FAIL", True, every, len(suite.injected))),
            Plan("SKIPPED_CASE", *kept, ["harness.completeness"], "PASS",
                 result("FAIL", "PASS", False, kept, 1)),
            Plan("CLEANUP_PROBLEM", *every, [], "FAIL",
                 result("FAIL", "PASS", True, every, 0, "FAIL"))]


def sequence(plan: Plan) -> list[tuple[str, str]]:
    """Every record the run writes, as (key, first value), in order."""
    records = [("RUN", "examples")]
    for case in plan.cases:
        records.append(("CASE", case))
        for item in (name for name in plan.assertions if name.startswith(f"{case}/")):
            records.append(("ASSERT", item))
            if item in plan.failing:
                records.append(("FAILURE", item))
    records += [("FAILURE", item) for item in plan.failing if "/" not in item]
    records += [("CASES", str(len(plan.cases))), ("ASSERTIONS", str(len(plan.assertions))),
                ("FAILURES", str(len(plan.failing)))]
    records += [("PRIMARY_FAILURE", plan.failing[0])] if plan.failing else []
    recovery = "NONE" if plan.cleanup == "PASS" else "REQUIRED"
    return records + [("CLEANUP", plan.cleanup), ("RECOVERY", recovery),
                      ("RESULT", plan.result["RESULT"])]


def parse_record(text: str, line: int) -> Record | None:
    match = RECORD.match(text)
    if not match:
        return None
    first, *rest = match.group(2).split("; ")
    fields = {}
    for part in rest:
        name, _, value = part.partition("=")
        fields[name] = value
    if "=" in first:
        name, _, value = first.partition("=")
        fields[name] = value
        first = ""
    return Record(match.group(1), first, fields, line)


def read_log(path: Path, problems: list[str]) -> list[Record]:
    records = []
    for number, text in enumerate(path.read_text(encoding="utf-8", errors="replace")
                                  .splitlines(), 1):
        record = parse_record(text, number)
        if record is None:
            problems.append(f"{path.name}:{number}: not a KEY=value record")
        else:
            records.append(record)
    if not records:
        problems.append(f"{path.name}: incomplete log: no record")
    return records


def check_sequence(name: str, records: list[Record], expected: list[tuple[str, str]],
                   problems: list[str]) -> bool:
    """The log holds exactly the expected records, in order: none missing, extra,
    repeated or contradicting the run's outcome."""
    for record, (key, value) in zip(records, expected, strict=False):
        if (record.key, record.value) != (key, value):
            problems.append(f"{name}:{record.line}: {record.key}={record.value}, "
                            f"expected {key}={value}")
            return False
    if len(records) < len(expected):
        key, value = expected[len(records)]
        problems.append(f"{name}: incomplete log: it ends before {key}={value}")
        return False
    if len(records) > len(expected):
        extra = records[len(expected)]
        problems.append(f"{name}:{extra.line}: {extra.key}={extra.value} after RESULT "
                        "(more than one run?)")
        return False
    return True


def expect(name: str, record: Record, wanted: dict[str, str], problems: list[str]) -> None:
    for key, value in wanted.items():
        actual = record.value if key == record.key else record.fields.get(key)
        if actual != value:
            problems.append(f"{name}:{record.line}: {record.key}={record.value}: {key}={actual}, "
                            f"expected {value}")


def check_fields(name: str, records: list[Record], plan: Plan, suite: Suite,
                 problems: list[str]) -> None:
    expected = {"CASES": str(suite.expected_cases), "ASSERTIONS": str(suite.expected_assertions)}
    detail = "no change reported" if plan.cleanup == "PASS" else SIMULATED_CLEANUP
    for record in records:
        if record.key == "RUN":
            expect(name, record, {"mode": plan.mode, "expected_cases": expected["CASES"],
                                  "expected_assertions": expected["ASSERTIONS"]}, problems)
        elif record.key == "ASSERT":
            status = "FAIL" if record.value in plan.failing else "PASS"
            expect(name, record, {"status": status}, problems)
        elif record.key in expected:
            expect(name, record, {"expected": expected[record.key]}, problems)
        elif record.key == "FAILURES":
            expect(name, record, {"errors": "0"}, problems)
        elif record.key == "CLEANUP":
            expect(name, record, {"detail": detail}, problems)
        elif record.key == "RESULT" and {"RESULT": record.value, **record.fields} != plan.result:
            problems.append(f"{name}:{record.line}: RESULT={record.value} with "
                            f"{record.fields}, expected {plan.result}")
    check_details(name, records, plan, suite, problems)


def check_details(name: str, records: list[Record], plan: Plan, suite: Suite,
                  problems: list[str]) -> None:
    """Each failure carries the detail its kind requires, the same in its ASSERT,
    FAILURE and PRIMARY_FAILURE records: an exact comparison its expected value
    from the commit's source and an actual value that differs from it, and the
    completeness failure the counts of the plan."""
    completeness = {"expected cases": f"{suite.expected_cases}, assertions={suite.expected_assertions}",
                    "observed cases": f"{len(plan.cases)}, assertions={len(plan.assertions)}"}
    details: dict[str, dict[str, str]] = {}
    for record in records:
        if record.key == "ASSERT" and record.fields.get("status") == "FAIL":
            details[record.value] = {key: value for key, value in record.fields.items()
                                     if key != "status"}
    for record in records:
        if record.key not in ("FAILURE", "PRIMARY_FAILURE"):
            continue
        wanted = completeness if record.value == "harness.completeness" else details.get(record.value)
        if wanted is not None and record.fields != wanted:
            problems.append(f"{name}:{record.line}: {record.key}={record.value}: detail "
                            f"{record.fields}, expected {wanted}")
    for item, fields in details.items():
        if item not in suite.literals:
            continue
        expected, actual = fields.get("expected"), fields.get("actual")
        if expected is None or actual is None:
            problems.append(f"{name}: ASSERT={item}: no expected= and actual= values")
        elif NUMBER.match(expected) and NUMBER.match(actual):
            if float(expected) != suite.literals[item]:
                problems.append(f"{name}: ASSERT={item}: expected={expected}, but the commit's "
                                f"suite expects {suite.literals[item]:g}")
            if float(actual) == float(expected):
                problems.append(f"{name}: ASSERT={item}: failed with actual equal to expected")


def count(name: str, records: list[Record], key: str, field_name: str,
          problems: list[str]) -> int | None:
    """The value of a count field, or None after reporting one that is not a count."""
    found = [record for record in records if record.key == key]
    if not found:
        return None
    text = found[-1].value if field_name == key else found[-1].fields.get(field_name, "")
    if not text.isdigit():
        problems.append(f"{name}:{found[-1].line}: {key} {field_name}={text!r} is not a count")
        return None
    return int(text)


def check_counts(name: str, records: list[Record], problems: list[str]) -> None:
    """The counts agree with one another and with the records they count, and
    every number compared in the log is finite."""
    for key, recorded, summary in (("CASE", "CASES", "cases"), ("ASSERT", "ASSERTIONS", "assertions"),
                                   ("FAILURE", "FAILURES", "failures")):
        logged = sum(record.key == key for record in records)
        totals = {f"{recorded}": count(name, records, recorded, recorded, problems),
                  f"RESULT {summary}": count(name, records, "RESULT", summary, problems)}
        for label, total in totals.items():
            if total is not None and total != logged:
                problems.append(f"{name}: inconsistent counts: {label}={total}, "
                                f"but {logged} {key} record(s)")
    run = count(name, records, "RUN", "expected_cases", problems)
    cases = count(name, records, "CASES", "expected", problems)
    if run is not None and cases is not None and run != cases:
        problems.append(f"{name}: inconsistent counts: RUN expected_cases={run}, CASES expected={cases}")
    for record in records:
        if record.key not in ("ASSERT", "FAILURE", "PRIMARY_FAILURE"):
            continue
        for key in ("expected", "actual"):
            value = record.fields.get(key)
            if value is None or value.startswith("'"):
                continue
            if not NUMBER.match(value) or not math.isfinite(float(value)):
                problems.append(f"{name}:{record.line}: {key}={value} is not a finite number")


def check_logs(folder: Path, suite: Suite, evidence: Evidence) -> dict[str, str]:
    """Check the four logs; return the RESULT record each mode requires."""
    results: dict[str, str] = {}
    for plan in plans(suite):
        filename = LOGS[plan.mode]
        path = folder / filename
        if not path.is_file():
            evidence.findings.append(f"{filename}: missing")
            evidence.modes[plan.mode] = "NOT_RUN (no log)"
            continue
        problems: list[str] = []
        records = read_log(path, problems)
        if records and check_sequence(filename, records, sequence(plan), problems):
            check_fields(filename, records, plan, suite, problems)
        check_counts(filename, records, problems)
        last = records[-1] if records else None
        results[plan.mode] = "; ".join(f"{key}={value}" for key, value in plan.result.items())
        if last is not None and last.key == "RESULT" and last.fields.get("operation") == "NOT_RUN":
            evidence.modes[plan.mode] = "NOT_RUN (start refused)"
        elif problems:
            evidence.modes[plan.mode] = "FAIL (did not end as required)"
        else:
            evidence.modes[plan.mode] = f"PASS (RESULT={plan.result['RESULT']}, as required)"
        evidence.findings += problems
    return results


def check_verification(folder: Path, results: dict[str, str], failed: int,
                       evidence: Evidence) -> None:
    path = folder / VERIFICATION
    if not path.is_file():
        evidence.findings.append(f"{VERIFICATION}: missing")
        return
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    modes = [line for line in lines if line.startswith("MODE=")]
    if [line.split(";", 1)[0].removeprefix("MODE=") for line in modes] != list(LOGS):
        evidence.findings.append(f"{VERIFICATION}: the modes are not {', '.join(LOGS)}, in order")
    for line in modes:
        mode = line.split(";", 1)[0].removeprefix("MODE=")
        errors = re.search(r"; required_error=(-?\d+); error=(-?\d+); ", line)
        report = re.search(r"; required=(RESULT=.*); actual=(RESULT=.*)$", line)
        if errors is None or report is None:
            evidence.findings.append(f"{VERIFICATION}: MODE={mode}: not a MODE record")
            continue
        if errors.group(1) != errors.group(2) or report.group(1) != report.group(2):
            evidence.findings.append(f"{VERIFICATION}: MODE={mode} did not end as required")
        required = 0 if mode == "NORMAL" else failed
        if errors.group(1) != str(required):
            evidence.findings.append(f"{VERIFICATION}: MODE={mode}: required_error={errors.group(1)}, "
                                     f"but the commit's suite requires {required}")
        if mode in results and report.group(1) != results[mode]:
            evidence.findings.append(f"{VERIFICATION}: MODE={mode}: the suite requires "
                                     f"{report.group(1)}, but its source gives {results[mode]}")
    if not lines or lines[-1] != f"VERIFICATION=PASS; modes={len(LOGS)}; deviations=0":
        evidence.findings.append(f"{VERIFICATION}: does not end with VERIFICATION=PASS; "
                                 f"modes={len(LOGS)}; deviations=0")


def check_host(folder: Path, evidence: Evidence) -> None:
    path = folder / ENVIRONMENT
    if path.is_file():
        evidence.environment = read_fields(path)
        missing = [key for key in ENVIRONMENT_FIELDS if not evidence.environment.get(key)]
        if missing:
            evidence.findings.append(f"{ENVIRONMENT}: no {', '.join(missing)}")
        for key, value in SUPPORTED.items():
            if evidence.environment.get(key) and evidence.environment[key] != value:
                evidence.findings.append(f"{ENVIRONMENT}: not the supported target: {key}="
                                         f"{evidence.environment[key]}, expected {value}")
    else:
        evidence.findings.append(f"{ENVIRONMENT}: missing")
    path = folder / HOST_STATE
    if path.is_file():
        state = read_fields(path)
        if not state.get("before") or state.get("before") != state.get("after"):
            evidence.findings.append(f"{HOST_STATE}: the host state after the runs "
                                     f"({state.get('after')}) is not the state before "
                                     f"({state.get('before')})")
        if state.get("cleanup") != "PASS":
            evidence.findings.append(f"{HOST_STATE}: cleanup={state.get('cleanup')}, expected PASS")
    else:
        evidence.findings.append(f"{HOST_STATE}: missing")
    path = folder / HOST
    if not path.is_file():
        evidence.findings.append(f"{HOST}: missing: write the Windows build, the references and "
                                 "the compile result")
        return
    evidence.host = read_fields(path)
    for key in HOST_FIELDS:
        if not evidence.host.get(key):
            evidence.findings.append(f"{HOST}: no {key}=")
    references = tuple(item.strip() for item in evidence.host.get("references", "").split(";"))
    if evidence.host.get("references") and sorted(references) != sorted(REFERENCES):
        evidence.findings.append(f"{HOST}: references must be exactly {'; '.join(REFERENCES)}")
    if evidence.host.get("compile") and evidence.host["compile"] != "PASS":
        evidence.findings.append(f"{HOST}: compile={evidence.host['compile']}, expected PASS")


def check_files(folder: Path, evidence: Evidence) -> None:
    """Every file of the run is newer than the build, and none holds a path."""
    candidate = folder / CANDIDATE
    built = candidate.stat().st_mtime if candidate.is_file() else None
    for name in (*RUN_OUTPUTS, HOST, CANDIDATE):
        path = folder / name
        if not path.is_file():
            continue
        if built is not None and name != CANDIDATE and path.stat().st_mtime < built:
            evidence.findings.append(f"{name}: older than {CANDIDATE}: left from an earlier run "
                                     "(stale)")
        if PATH.search(path.read_text(encoding="utf-8", errors="replace")):
            evidence.findings.append(f"{name}: holds a file path; remove machine details")


def check(root: Path, commit: str, folder: Path) -> Evidence:
    evidence = Evidence()
    evidence.ran = folder.is_dir() and any((folder / name).is_file() for name in RUN_OUTPUTS)
    if not evidence.ran:
        evidence.modes = dict.fromkeys(LOGS, "NOT_RUN (no log)")
        return evidence
    check_candidate(root, commit, folder, evidence)
    sources = check_sources(root, commit, folder, evidence)
    suite = read_suite(sources.get(Path(EXAMPLES).name, b""))
    if not suite.cases:
        evidence.findings.append(f"no example suite in {EXAMPLES} at {commit[:12]}")
    if len(suite.injected) != 1:
        evidence.findings.append(f"{EXAMPLES} at {commit[:12]}: INJECTED_FAILURE must change "
                                 f"exactly one assertion, found {suite.injected}")
    results = check_logs(folder, suite, evidence)
    check_verification(folder, results, failed_error(root, commit, evidence), evidence)
    check_host(folder, evidence)
    check_files(folder, evidence)
    return evidence


def verdict(evidence: Evidence) -> str:
    if not evidence.ran:
        return "NOT_RUN"
    return "FAIL" if evidence.findings else "PASS"


def report(commit: str, evidence: Evidence) -> str:
    environment = "; ".join(f"{key}={evidence.environment.get(key, '')}"
                            for key in ENVIRONMENT_FIELDS)
    lines = [f"Candidate commit: {commit}",
             f"Built from: {evidence.candidate.get('commit', '')} "
             f"(worktree={evidence.candidate.get('worktree', '')})",
             f"Environment: {environment}",
             f"Windows: {evidence.host.get('windows', '')}",
             f"References: {evidence.host.get('references', '')}",
             f"Compile: {evidence.host.get('compile', '')}",
             "Modes:"]
    lines += [f"  {mode}: {status}" for mode, status in evidence.modes.items()]
    lines.append("Fingerprints (Git blob ids at the commit):")
    lines += [f"  {name} {blob}" for name, blob in sorted(evidence.hashes.items())]
    lines += [f"FAIL: {finding}" for finding in evidence.findings]
    status = verdict(evidence)
    if status == "NOT_RUN":
        lines.append("NOT_RUN: the folder holds no output of a run")
    lines.append(f"excel-run: {status} (evidence checked against the commit; Excel is not run "
                 "here and no LCR calculation is validated)")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("evidence", type=Path, help="folder holding the run's evidence")
    parser.add_argument("--commit", required=True, help="the commit the workbook was built from")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        commit = git(root, "rev-parse", "--verify", f"{args.commit}^{{commit}}").decode().strip()
    except RuntimeError as error:
        print(f"excel-run: NOT_RUN (commit {args.commit} not found: {error})")
        return 2
    evidence = check(root, commit, args.evidence)
    print(report(commit, evidence))
    return {"PASS": 0, "FAIL": 1}.get(verdict(evidence), 2)


if __name__ == "__main__":
    sys.exit(main())
