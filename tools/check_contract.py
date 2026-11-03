#!/usr/bin/env python3
"""Reference validator of the K-LCR input contract (docs/methodology/data-contract.json).

It reads the three CSV files of one run, reports every finding with its stable
code, file, physical line, record and column, and computes reconciliation
totals and a fingerprint of the run. It checks the form of the input only: it
calculates no LCR figure and says nothing about regulatory correctness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

CONTRACT = Path("docs/methodology/data-contract.json")
CATEGORIES = Path("docs/methodology/categories.json")
FIXTURES = Path("tests/contract")
EXPECTED = FIXTURES / "expected.json"
REPORT_SCHEMA = "klcr-validation-report"
REPORT_VERSION = 1
BOM = b"\xef\xbb\xbf"
DELIMITER = ";"
QUOTE = '"'
AMOUNT = re.compile(r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
INTEGER = re.compile(r"^(?:0|[1-9][0-9]*)$")
DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
NON_FINITE = re.compile(r"^[+-]?(?:nan|inf|infinity)$", re.IGNORECASE)
FORMULA_START = ("=", "+", "-", "@", "\t", "\r")
# Findings after which the file cannot be read as records.
STRUCTURAL = frozenset({"LCR-FILE-MISSING", "LCR-ENCODING", "LCR-SYNTAX", "LCR-EMPTY",
                        "LCR-DELIMITER", "LCR-HEADER-DUPLICATE", "LCR-HEADER-MISSING",
                        "LCR-HEADER-UNKNOWN", "LCR-FIELD-COUNT", "LCR-TOO-LARGE"})


@dataclass(frozen=True)
class Finding:
    """One contract violation; record 0 is the header, and column is "" when none applies."""
    code: str
    file: str
    line: int
    record: int
    column: str
    message: str

    def key(self) -> list[Any]:
        return [self.code, self.file, self.record, self.column]


@dataclass(frozen=True)
class Record:
    """One logical CSV record: its fields and the physical line it starts on."""
    fields: list[str]
    line: int


@dataclass
class Table:
    """A file read as records keyed by column name, with the findings found so far."""
    name: str
    rows: list[dict[str, str]] = field(default_factory=list)
    lines: list[int] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    sha256: str = ""
    readable: bool = False


def load_json(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


# --- CSV syntax -------------------------------------------------------------


def split_records(text: str) -> tuple[list[Record], str | None, int]:
    """Split CSV text into records; return an error message and its line on bad syntax."""
    records: list[Record] = []
    fields: list[str] = []
    value: list[str] = []
    line, start = 1, 1
    quoted = after_quote = False
    index = 0
    while index < len(text):
        char = text[index]
        if quoted:
            if char == QUOTE and text[index + 1:index + 2] == QUOTE:
                value.append(QUOTE)
                index += 1
            elif char == QUOTE:
                quoted, after_quote = False, True
            else:
                line += char == "\n"
                value.append(char)
        elif char == DELIMITER:
            fields.append("".join(value))
            value, after_quote = [], False
        elif char in "\r\n":
            if char == "\r" and text[index + 1:index + 2] != "\n":
                return records, "a carriage return outside a quoted field", line
            index += char == "\r"
            fields.append("".join(value))
            records.append(Record(fields, start))
            fields, value, after_quote = [], [], False
            line += 1
            start = line
        elif after_quote:
            return records, "text after a closing quote", line
        elif char == QUOTE:
            if value:
                return records, "a quote inside an unquoted field", line
            quoted = True
        else:
            value.append(char)
        index += 1
    if quoted:
        return records, "a quoted field is not closed", start
    if fields or value:
        fields.append("".join(value))
        records.append(Record(fields, start))
    return records, None, line


def decode(name: str, data: bytes) -> tuple[str | None, list[Finding]]:
    if data.startswith(BOM):
        data = data[len(BOM):]
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        return None, [Finding("LCR-ENCODING", name, 0, 0, "", f"not valid UTF-8 at byte {error.start}")]
    if "\x00" in text:
        return None, [Finding("LCR-ENCODING", name, 0, 0, "", "contains a NUL character")]
    return text, []


def read_table(name: str, spec: Mapping[str, Any], folder: Path,
               limits: Mapping[str, Any]) -> Table:
    """Read one file of the run into a Table, reporting structural findings."""
    table = Table(name)
    path = folder / spec["file"]
    if not path.is_file():
        table.findings.append(Finding("LCR-FILE-MISSING", name, 0, 0, "", f"{spec['file']} is missing"))
        return table
    data = path.read_bytes()
    table.sha256 = hashlib.sha256(data).hexdigest()
    if len(data) > limits["max_bytes"]:
        table.findings.append(Finding("LCR-TOO-LARGE", name, 0, 0, "", f"{len(data)} bytes"))
        return table
    text, problems = decode(name, data)
    if text is None:
        table.findings += problems
        return table
    records, error, line = split_records(text)
    if error:
        table.findings.append(Finding("LCR-SYNTAX", name, line, 0, "", error))
        return table
    table.findings += header_findings(name, spec, records)
    if table.findings:
        return table
    return fill_table(table, records, limits)


def header_findings(name: str, spec: Mapping[str, Any], records: Sequence[Record]) -> list[Finding]:
    if not records:
        return [Finding("LCR-EMPTY", name, 0, 0, "", "no header record")]
    header = records[0].fields
    if len(header) == 1 and ("," in header[0] or "\t" in header[0]):
        return [Finding("LCR-DELIMITER", name, 1, 0, "", "the header is not delimited by ';'")]
    expected = [column["name"] for column in spec["columns"]]
    findings = [Finding("LCR-HEADER-DUPLICATE", name, 1, 0, column, f"{column} appears twice")
                for index, column in enumerate(header) if column in header[:index]]
    findings += [Finding("LCR-HEADER-MISSING", name, 1, 0, column, f"{column} is missing")
                 for column in expected if column not in header]
    findings += [Finding("LCR-HEADER-UNKNOWN", name, 1, 0, column, f"{column} is not in the contract")
                 for column in dict.fromkeys(header) if column not in expected]
    return findings


def fill_table(table: Table, records: Sequence[Record], limits: Mapping[str, Any]) -> Table:
    header = records[0].fields
    body = records[1:]
    if len(body) > limits["max_records"]:
        table.findings.append(Finding("LCR-TOO-LARGE", table.name, 0, 0, "", f"{len(body)} records"))
        return table
    for number, record in enumerate(body, 1):
        if len(record.fields) != len(header):
            table.findings.append(Finding("LCR-FIELD-COUNT", table.name, record.line, number, "",
                                          f"{len(record.fields)} fields, the header has {len(header)}"))
    if table.findings:
        return table
    table.rows = [dict(zip(header, record.fields, strict=True)) for record in body]
    table.lines = [record.line for record in body]
    table.readable = True
    return table


# --- Field values -----------------------------------------------------------


def significant_digits(value: str) -> int:
    digits = value.lstrip("-").replace(".", "").lstrip("0")
    return len(digits)


def amount_finding(value: str, rules: Mapping[str, Any]) -> tuple[str, str] | None:
    if NON_FINITE.match(value):
        return "LCR-NON-FINITE", f"{value!r} is not a finite number"
    if not AMOUNT.match(value):
        return "LCR-TYPE", f"{value!r} is not a decimal number with '.' as separator"
    if significant_digits(value) > rules["max_significant_digits"]:
        return "LCR-PRECISION", f"{value!r} has more than {rules['max_significant_digits']} significant digits"
    if Decimal(value) < Decimal(rules["amount_min"]) or value.startswith("-"):
        return "LCR-RANGE", f"{value!r} is negative"
    return None


def date_finding(value: str, rules: Mapping[str, Any]) -> tuple[str, str] | None:
    if not DATE.match(value):
        return "LCR-TYPE", f"{value!r} is not a date YYYY-MM-DD"
    try:
        day = date.fromisoformat(value)
    except ValueError:
        return "LCR-TYPE", f"{value!r} is not a calendar date"
    if not rules["date_min"] <= day.isoformat() <= rules["date_max"]:
        return "LCR-RANGE", f"{value} is outside {rules['date_min']} to {rules['date_max']}"
    return None


def value_finding(value: str, column: Mapping[str, Any],
                  rules: Mapping[str, Any]) -> tuple[str, str] | None:
    """The first finding for a non-blank value, or None."""
    kind = column["type"]
    if kind in ("id", "code", "text") and value.startswith(FORMULA_START):
        return "LCR-FORMULA", "text may not start with =, +, -, @, a tab or a carriage return"
    if kind == "amount":
        return amount_finding(value, rules)
    if kind == "date":
        return date_finding(value, rules)
    if kind == "integer":
        if not INTEGER.match(value):
            return "LCR-TYPE", f"{value!r} is not an integer"
        if not rules["integer_min"] <= int(value) <= rules["integer_max"]:
            return "LCR-RANGE", f"{value} is outside {rules['integer_min']} to {rules['integer_max']}"
        return None
    pattern = rules["patterns"].get(kind)
    if pattern and not re.match(pattern, value):
        return "LCR-TYPE", f"{value!r} does not have the form of a {kind}"
    if kind == "text" and len(value) > rules["text_max"]:
        return "LCR-LENGTH", f"{len(value)} characters"
    allowed = column.get("allowed") or (rules["flag"] if kind == "flag" else None)
    if allowed and value not in allowed:
        return "LCR-ALLOWED", f"{value!r} is not one of {', '.join(allowed)}"
    return None


def type_rules(contract: Mapping[str, Any]) -> dict[str, Any]:
    types = contract["types"]
    return {
        "patterns": {name: spec["pattern"] for name, spec in types.items() if "pattern" in spec},
        "flag": types["flag"]["allowed"],
        "text_max": types["text"]["max_length"],
        "integer_min": types["integer"]["min"],
        "integer_max": types["integer"]["max"],
        "amount_min": types["amount"]["min"],
        "date_min": types["date"]["min"],
        "date_max": types["date"]["max"],
        "max_significant_digits": contract["format"]["max_significant_digits"],
    }


def field_findings(table: Table, spec: Mapping[str, Any], rules: Mapping[str, Any]) -> set[int]:
    """Append blank, type and key findings; return the numbers of records that have any."""
    bad: set[int] = set()
    seen: dict[str, int] = {}
    key = spec.get("key")
    for number, (row, line) in enumerate(zip(table.rows, table.lines, strict=True), 1):
        found = record_findings(table.name, row, line, number, spec, rules)
        if key and row.get(key) and not any(f.column == key for f in found):
            folded = row[key].casefold()
            if folded in seen:
                found.append(Finding("LCR-DUPLICATE-KEY", table.name, line, number, key,
                                     f"{row[key]} repeats record {seen[folded]}"))
            else:
                seen[folded] = number
        if found:
            bad.add(number)
            table.findings += found
    return bad


def record_findings(name: str, row: Mapping[str, str], line: int, number: int,
                    spec: Mapping[str, Any], rules: Mapping[str, Any]) -> list[Finding]:
    if not any(value.strip() for value in row.values()):
        return [Finding("LCR-BLANK-RECORD", name, line, number, "", "every field is blank")]
    found = []
    for column in spec["columns"]:
        value = row[column["name"]]
        if value == "":
            if column["required"]:
                found.append(Finding("LCR-REQUIRED", name, line, number, column["name"], "blank"))
            continue
        result = value_finding(value, column, rules)
        if result:
            found.append(Finding(result[0], name, line, number, column["name"], result[1]))
    return found


# --- Rules across fields and files ------------------------------------------


@dataclass(frozen=True)
class Profile:
    """The categories of one profile, by file or direction."""
    assets: frozenset[str]
    flows: Mapping[str, frozenset[str]]
    excluded: frozenset[str]
    secured: frozenset[str]
    derivative: frozenset[str]


def profile_from(categories: Mapping[str, Any], name: str) -> Profile:
    data = categories["profiles"][name]

    def codes(items: Iterable[Mapping[str, Any]], flag: str | None = None) -> frozenset[str]:
        return frozenset(item["code"] for item in items if flag is None or item.get(flag))

    flows = data["outflows"] + data["inflows"]
    return Profile(
        assets=codes(data["assets"]),
        flows={"OUTFLOW": codes(data["outflows"]), "INFLOW": codes(data["inflows"])},
        excluded=codes(data["excluded"]),
        secured=codes(flows, "secured"),
        derivative=codes(flows, "derivative"),
    )


def run_findings(run: Table, contract: Mapping[str, Any]) -> list[Finding]:
    if len(run.rows) != 1:
        return [Finding("LCR-RECORD-COUNT", "run", 0, 0, "", f"{len(run.rows)} records, expected one")]
    row, line = run.rows[0], run.lines[0]
    found = []
    expected = contract["profiles"].get(row["profile"], {}).get("parameter_set")
    if expected and row["parameter_set"] != expected:
        found.append(Finding("LCR-PARAMETER-SET", "run", line, 1, "parameter_set",
                             f"profile {row['profile']} uses {expected}"))
    if row["source_register_version"] != str(contract["source_register_version"]):
        found.append(Finding("LCR-REGISTER-VERSION", "run", line, 1, "source_register_version",
                             f"the contract cites version {contract['source_register_version']}"))
    return found


def category_finding(code: str, allowed: frozenset[str], profile: Profile,
                     what: str) -> tuple[str, str] | None:
    if code in allowed:
        return None
    if code in profile.excluded:
        return "LCR-OUT-OF-SCOPE", f"{code} is excluded from v0.1"
    return "LCR-CATEGORY-UNKNOWN", f"{code} is not {what} of the profile"


def asset_findings(assets: Table, bad: set[int], profile: Profile) -> list[Finding]:
    found = []
    for number, (row, line) in enumerate(zip(assets.rows, assets.lines, strict=True), 1):
        if number in bad:
            continue
        result = category_finding(row["category"], profile.assets, profile, "a liquid-asset category")
        if result:
            found.append(Finding(result[0], "assets", line, number, "category", result[1]))
    return found


def flow_findings(flows: Table, bad: set[int], profile: Profile, reporting: str) -> list[Finding]:
    found = []
    for number, (row, line) in enumerate(zip(flows.rows, flows.lines, strict=True), 1):
        if number in bad:
            continue

        def add(code: str, column: str, message: str, line: int = line, number: int = number) -> None:
            found.append(Finding(code, "flows", line, number, column, message))

        direction, code = row["direction"], row["category"]
        what = f"an {direction.lower()} category"
        result = category_finding(code, profile.flows[direction], profile, what)
        if result:
            add(result[0], "category", result[1])
            continue
        collateral = row["collateral_category"]
        if code in profile.secured and not collateral:
            add("LCR-COLLATERAL", "collateral_category", f"{code} is secured: give its collateral")
        elif code not in profile.secured and collateral:
            add("LCR-COLLATERAL", "collateral_category", f"{code} is not a secured category")
        elif collateral and collateral not in profile.assets:
            add("LCR-COLLATERAL", "collateral_category", f"{collateral} is not a liquid-asset category")
        if row["netting_set_id"] and code not in profile.derivative:
            add("LCR-NETTING-SET", "netting_set_id", f"{code} is not a derivative category")
        maturity = row["maturity_date"]
        if direction == "INFLOW" and not maturity:
            add("LCR-MATURITY", "maturity_date", "an inflow needs its maturity date")
        elif maturity and maturity < reporting:
            add("LCR-MATURITY", "maturity_date", f"{maturity} is before the reporting date {reporting}")
    return found


# --- Reconciliation, fingerprint and report -----------------------------------


def total(rows: Iterable[Mapping[str, str]], column: str, by: Sequence[str]) -> dict[str, str]:
    sums: dict[str, Decimal] = {}
    for row in rows:
        group = "/".join(row[name] for name in by)
        sums[group] = sums.get(group, Decimal(0)) + Decimal(row[column])
    return {group: format(value, "f") for group, value in sorted(sums.items())}


def reconciliation(tables: Mapping[str, Table], bad: Mapping[str, set[int]]) -> dict[str, Any]:
    """Counts of every readable file and exact totals over its records without field findings."""
    summary: dict[str, Any] = {}
    for name, table in sorted(tables.items()):
        if not table.readable:
            continue
        clean = [row for number, row in enumerate(table.rows, 1) if number not in bad.get(name, set())]
        entry: dict[str, Any] = {"records": len(table.rows), "records_with_findings": len(table.rows) - len(clean)}
        if name == "assets":
            entry["market_value_by_category"] = total(clean, "market_value", ["category"])
            entry["market_value_total"] = format(sum((Decimal(r["market_value"]) for r in clean), Decimal(0)), "f")
        if name == "flows":
            entry["amount_by_direction_and_category"] = total(clean, "amount", ["direction", "category"])
            entry["amount_by_direction"] = total(clean, "amount", ["direction"])
        summary[name] = entry
    return summary


def fingerprint(root: Path, tables: Mapping[str, Table]) -> str:
    """SHA-256 over the contract, the categories and every input file, in a fixed order."""
    parts = {
        "contract": hashlib.sha256((root / CONTRACT).read_bytes()).hexdigest(),
        "categories": hashlib.sha256((root / CATEGORIES).read_bytes()).hexdigest(),
        "files": {name: table.sha256 for name, table in sorted(tables.items())},
    }
    canonical = json.dumps(parts, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_run(root: Path, folder: Path) -> dict[str, Any]:
    """Validate the run in folder against the contract; return the report."""
    contract = load_json(root / CONTRACT)
    categories = load_json(root / CATEGORIES)
    limits = contract["format"]
    rules = type_rules(contract)
    tables = {name: read_table(name, spec, folder, limits) for name, spec in contract["files"].items()}
    bad = {name: field_findings(table, contract["files"][name], rules)
           for name, table in tables.items() if table.readable}
    run = tables["run"]
    findings = [finding for table in tables.values() for finding in table.findings]
    if run.readable and not bad["run"]:
        findings += run_findings(run, contract)
    run_ok = run.readable and not bad["run"] and len(run.rows) == 1
    if run_ok and run.rows[0]["profile"] in categories["profiles"]:
        profile = profile_from(categories, run.rows[0]["profile"])
        if tables["assets"].readable:
            findings += asset_findings(tables["assets"], bad["assets"], profile)
        if tables["flows"].readable:
            findings += flow_findings(tables["flows"], bad["flows"], profile, run.rows[0]["reporting_date"])
    findings.sort(key=lambda f: (list(contract["files"]).index(f.file), f.record, f.line, f.column, f.code))
    return {
        "schema": REPORT_SCHEMA,
        "report_version": REPORT_VERSION,
        "contract_version": contract["contract_version"],
        "categories_version": categories["categories_version"],
        "status": "fail" if findings else "pass",
        "fingerprint": fingerprint(root, tables),
        "files": {name: {"file": contract["files"][name]["file"], "sha256": table.sha256}
                  for name, table in tables.items()},
        "reconciliation": reconciliation(tables, bad),
        "findings": [asdict(f) for f in findings],
    }


# --- Fixtures and command line ------------------------------------------------


def check_fixtures(root: Path) -> list[str]:
    """Compare every fixture run with its expected findings and reconciliation."""
    expected = load_json(root / EXPECTED)
    problems = []
    folders = sorted(path.name for path in (root / FIXTURES).iterdir() if path.is_dir())
    if folders != sorted(expected["cases"]):
        problems.append(f"fixture folders {folders} do not match expected.json {sorted(expected['cases'])}")
    for name, case in sorted(expected["cases"].items()):
        report = validate_run(root, root / FIXTURES / name)
        got = [[f["code"], f["file"], f["record"], f["column"]] for f in report["findings"]]
        if got != case["findings"]:
            problems.append(f"{name}: findings {got}, expected {case['findings']}")
        if "reconciliation" in case and report["reconciliation"] != case["reconciliation"]:
            problems.append(f"{name}: reconciliation {report['reconciliation']}, expected {case['reconciliation']}")
        if report != validate_run(root, root / FIXTURES / name):
            problems.append(f"{name}: two validations of the same files gave different reports")
    return problems


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", type=Path, help="folder holding run.csv, assets.csv and flows.csv")
    mode.add_argument("--check-fixtures", action="store_true",
                      help="validate every fixture run in tests/contract against expected.json")
    parser.add_argument("--output", type=Path, help="write the report as JSON (with --run)")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    if args.check_fixtures:
        problems = check_fixtures(root)
        for problem in problems:
            print(f"FAIL: {problem}")
        print(f"data-contract: {'PASS' if not problems else 'FAIL'}")
        return 1 if problems else 0
    report = validate_run(root, args.run)
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
