#!/usr/bin/env python3
"""Check the registered LCR test cases (docs/methodology/TEST_CASES.md) and run what can run.

It checks every case folder under tests/cases: metadata, expected outputs,
references, tolerances and derivation scripts. It executes the input-contract
assertions with tools/check_contract.py and the outputs of each derivation
script, and reports the result figures as registered but not executed: no LCR
calculation reads the input contract yet (the prototype reads worksheet inputs,
docs/PROTOTYPE.md).
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Context, Decimal, Inexact, InvalidOperation, localcontext
from pathlib import Path
from typing import Any

import check_contract
import check_parameters

CASES = Path("tests/cases")
DERIVATIONS = Path("tests/derivations")
PARAMETERS = Path("tests/parameters")
APPLICABILITY = Path("docs/methodology/APPLICABILITY.md")
SOURCES = Path("docs/methodology/SOURCES.md")
CASE_KEYS = {"schema", "case_version", "id", "synthetic", "description", "profile", "category",
             "requirements", "parameter_set", "review"}
REVIEW_KEYS = {"derived_by", "reviewed_by", "date", "status"}
REFERENCE_KEYS = {"class", "source", "locator", "derivation", "script", "derived_by", "reviewed_by", "date"}
CATEGORIES = ("nominal", "boundary", "invalid-input", "invalid-parameters")
CASE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
DECIMAL = re.compile(r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
CONTRACT_TEXTS = ("input_status", "input_findings", "result_status")
RESULT_STATUSES = ("calculated", "rejected", "failed")
AMOUNTS = ("liquidity_buffer", "outflows", "inflows", "inflows_after_cap", "net_outflows")
CONTRACT_FILES = ("docs/methodology/data-contract.json", "docs/methodology/parameter-result-contract.json")


@dataclass(frozen=True)
class Finding:
    code: str
    case: str
    path: str
    message: str


@dataclass
class Summary:
    cases: int = 0
    executed: int = 0
    registered_only: int = 0
    findings: list[Finding] = field(default_factory=list)


# --- Strict JSON ----------------------------------------------------------------


def strict_json(path: Path) -> Any:
    """Parse JSON refusing duplicate keys and non-finite numbers."""

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        keys = [key for key, _ in items]
        duplicates = sorted({key for key in keys if keys.count(key) > 1})
        if duplicates:
            raise ValueError(f"duplicate keys {duplicates}")
        return dict(items)

    def constant(name: str) -> Any:
        raise ValueError(f"non-finite number {name}")

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=constant)


def known_ids(root: Path) -> tuple[set[str], set[str]]:
    """The REQ- IDs of the applicability map and the SRC-/IMPL- IDs of the source register."""
    requirements = set(re.findall(r"`(REQ-\d{2})`", (root / APPLICABILITY).read_text(encoding="utf-8")))
    sources = set(re.findall(r"^\| `((?:SRC|IMPL)-\d{2})` \|", (root / SOURCES).read_text(encoding="utf-8"),
                             re.M))
    return requirements, sources


# --- Metadata -------------------------------------------------------------------


def metadata_findings(case: str, data: Any, root: Path, requirements: set[str]) -> list[Finding]:
    if not isinstance(data, dict) or set(data) != CASE_KEYS:
        return [Finding("CASE-METADATA", case, "case.json", f"keys must be exactly {', '.join(sorted(CASE_KEYS))}")]
    found = []

    def bad(key: str, message: str) -> None:
        found.append(Finding("CASE-METADATA", case, f"case.json:{key}", message))

    if data["schema"] != "klcr-test-case" or not check_contract.same_value(data["case_version"], 1):
        bad("schema", "expected klcr-test-case, version 1")
    if data["id"] != case or not CASE_ID.fullmatch(case):
        bad("id", "must equal the folder name: lower case, digits and hyphens")
    if data["synthetic"] is not True:
        bad("synthetic", "every case is synthetic")
    if not isinstance(data["description"], str) or not data["description"].strip():
        bad("description", "required")
    if data["profile"] not in ("EU", "BASEL"):
        bad("profile", "EU or BASEL")
    if data["category"] not in CATEGORIES:
        bad("category", f"one of {', '.join(CATEGORIES)}")
    reqs = data["requirements"]
    if not isinstance(reqs, list) or any(not isinstance(r, str) or r not in requirements for r in reqs):
        bad("requirements", "a list of REQ- IDs of APPLICABILITY.md")
    found += parameter_set_findings(case, data, root)
    found += review_findings(case, data["review"], "case.json:review")
    return found


def parameter_set_findings(case: str, data: Mapping[str, Any], root: Path) -> list[Finding]:
    path = data["parameter_set"]
    if not isinstance(path, str) or not path.startswith(f"{PARAMETERS.as_posix()}/") or not (root / path).is_file():
        return [Finding("CASE-METADATA", case, "case.json:parameter_set", "an existing file under tests/parameters")]
    if data["category"] == "invalid-parameters":
        return []  # The case deliberately names a set of another profile or an invalid one.
    try:
        parameters = strict_json(root / path)
    except ValueError:
        parameters = None
    if not isinstance(parameters, dict) or parameters.get("profile") != data["profile"]:
        return [Finding("CASE-METADATA", case, "case.json:parameter_set", "the parameter set is of another profile")]
    if check_parameters.check_parameter_set(parameters, root):
        return [Finding("CASE-METADATA", case, "case.json:parameter_set",
                        "the parameter set has findings of tools/check_parameters.py")]
    return []


def review_findings(case: str, review: Any, path: str) -> list[Finding]:
    if not isinstance(review, dict) or set(review) != REVIEW_KEYS:
        return [Finding("CASE-METADATA", case, path, f"keys must be exactly {', '.join(sorted(REVIEW_KEYS))}")]
    found = []
    if not isinstance(review["derived_by"], str) or not review["derived_by"].strip():
        found.append(Finding("CASE-METADATA", case, path, "derived_by is required"))
    if not valid_date(review["date"]):
        found.append(Finding("CASE-METADATA", case, path, "date must be YYYY-MM-DD"))
    if review["status"] not in ("unreviewed", "reviewed"):
        found.append(Finding("CASE-METADATA", case, path, "status is unreviewed or reviewed"))
    elif review["status"] == "reviewed" and review["reviewed_by"] in (None, "", review["derived_by"]):
        found.append(Finding("CASE-METADATA", case, path, "a reviewed case names a reviewer other than its author"))
    return found


def valid_date(value: Any) -> bool:
    return check_contract.iso_date(value) is not None


# --- Expected outputs ---------------------------------------------------------


def decimal_value(value: Any) -> Decimal | None:
    if not isinstance(value, str) or not DECIMAL.fullmatch(value):
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def output_findings(case: str, index: int, output: Any, currency: str | None) -> list[Finding]:
    """Form, unit and tolerance of one expected output."""
    path = f"expected.json:outputs[{index}]"
    if not isinstance(output, dict) or not isinstance(output.get("quantity"), str):
        return [Finding("CASE-OUTPUT", case, path, "an output is an object with a quantity")]
    quantity = output["quantity"]
    illustrative = quantity.startswith("illustrative_")
    if illustrative and not case.startswith("illustrative-"):
        return [Finding("CASE-OUTPUT", case, path, "illustrative_ quantities belong to illustrative- cases only")]
    if "text" in output:
        return text_output_findings(case, path, output, illustrative)
    if quantity not in (*AMOUNTS, "lcr") and not illustrative:
        return [Finding("CASE-OUTPUT", case, path, f"unknown quantity {quantity!r}")]
    if set(output) != {"quantity", "value", "unit", "tolerance", "reference"}:
        return [Finding("CASE-OUTPUT", case, path, "a number has quantity, value, unit, tolerance and reference")]
    found = []
    if decimal_value(output["value"]) is None:
        found.append(Finding("CASE-OUTPUT", case, path, "value must be a finite decimal string"))
    expected_unit = "1" if quantity == "lcr" else currency
    if output["unit"] != expected_unit and not (illustrative and output["unit"] in ("1", currency)):
        found.append(Finding("CASE-OUTPUT", case, path, f"unit must be {expected_unit}"))
    tolerance = output["tolerance"]
    if not isinstance(tolerance, dict) or set(tolerance) != {"absolute", "relative"} or any(
            (bound := decimal_value(tolerance[key])) is None or bound < 0 for key in tolerance):
        found.append(Finding("CASE-OUTPUT", case, path, "tolerance has absolute and relative decimals of at least 0"))
    return found


def text_output_findings(case: str, path: str, output: Mapping[str, Any], illustrative: bool) -> list[Finding]:
    quantity, text = output["quantity"], output["text"]
    if set(output) != {"quantity", "text", "reference"} or not isinstance(text, str):
        return [Finding("CASE-OUTPUT", case, path, "a text output has quantity, text and reference")]
    allowed = {"input_status": ("pass", "fail"), "result_status": RESULT_STATUSES}
    if quantity in allowed and text not in allowed[quantity]:
        return [Finding("CASE-OUTPUT", case, path, f"{quantity} is one of {', '.join(allowed[quantity])}")]
    if quantity == "input_findings" and not re.fullmatch(r"^(?:LCR-[A-Z-]+(?:,LCR-[A-Z-]+)*)?$", text):
        return [Finding("CASE-OUTPUT", case, path, "input_findings lists finding codes joined by ',', or is empty")]
    if quantity not in CONTRACT_TEXTS and not illustrative:
        return [Finding("CASE-OUTPUT", case, path, f"unknown text quantity {quantity!r}")]
    return []


def reference_findings(case: str, index: int, output: Mapping[str, Any], sources: set[str],
                       root: Path) -> list[Finding]:
    path = f"expected.json:outputs[{index}].reference"
    reference = output.get("reference")
    if not isinstance(reference, dict) or set(reference) != REFERENCE_KEYS:
        return [Finding("CASE-REFERENCE", case, path, f"keys must be exactly {', '.join(sorted(REFERENCE_KEYS))}")]
    kind, source = reference["class"], reference["source"]
    quantity = str(output.get("quantity"))
    found = []

    def bad(message: str) -> None:
        found.append(Finding("CASE-REFERENCE", case, path, message))

    if kind == "published" and not (isinstance(source, str) and source.startswith("SRC-") and source in sources):
        bad("a published value cites a SRC- entry of the source register")
    elif kind == "independent" and not (isinstance(source, str) and source.startswith("IMPL-") and source in sources):
        bad("an independent value cites an IMPL- entry of the source register")
    elif kind == "contract" and (quantity not in CONTRACT_TEXTS or source not in CONTRACT_FILES):
        bad("a contract value is a status or finding text citing a contract file")
    elif kind == "illustrative" and not str(reference["derivation"] or "").strip():
        bad("an illustrative value explains its derivation")
    elif kind not in ("published", "independent", "contract", "illustrative"):
        bad("class is published, independent, contract or illustrative")
    if kind in ("published", "independent") and not str(reference["locator"] or "").strip():
        bad("a locator is required")
    if quantity.startswith("illustrative_") and kind != "illustrative":
        bad("an illustrative_ quantity has an illustrative reference")
    if not str(reference["derived_by"] or "").strip() or not valid_date(reference["date"]):
        bad("derived_by and a YYYY-MM-DD date are required")
    found += script_findings(case, path, reference["script"], root)
    return found


def script_findings(case: str, path: str, script: Any, root: Path) -> list[Finding]:
    if script is None:
        return []
    if not isinstance(script, str) or not re.fullmatch(rf"^{DERIVATIONS.as_posix()}/[a-z0-9_]+\.py$", script) \
            or not (root / script).is_file():
        return [Finding("CASE-SCRIPT", case, path, "script names an existing file in tests/derivations")]
    problem = oracle_problem(root / script)
    return [Finding("CASE-ORACLE", case, path, problem)] if problem else []


def oracle_problem(script: Path) -> str | None:
    """Why a derivation script could use the code under test, or None: it may import the standard library only."""
    try:
        tree = ast.parse(script.read_text(encoding="utf-8"))
    except SyntaxError as error:
        return f"{script.name} does not parse: {error.msg}"
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level:
            return f"{script.name} uses a relative import"
        names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else \
            [node.module or ""] if isinstance(node, ast.ImportFrom) else []
        for name in names:
            if name.split(".")[0] not in sys.stdlib_module_names:
                return f"{script.name} imports {name}: a derivation may use the standard library only"
    return None


def expected_findings(case: str, data: Any, metadata: Mapping[str, Any], currency: str | None,
                      sources: set[str], root: Path) -> list[Finding]:
    if not isinstance(data, dict) or set(data) != {"schema", "expected_version", "case", "outputs"}:
        return [Finding("CASE-EXPECTED", case, "expected.json", "keys must be schema, expected_version, case, outputs")]
    if data["schema"] != "klcr-test-expected" or data["case"] != case \
            or not check_contract.same_value(data["expected_version"], 1):
        return [Finding("CASE-EXPECTED", case, "expected.json", "expected klcr-test-expected, version 1, for this case")]
    outputs = data["outputs"]
    if not isinstance(outputs, list) or not outputs:
        return [Finding("CASE-EXPECTED", case, "expected.json", "outputs is a non-empty list")]
    found = []
    for index, output in enumerate(outputs):
        found += output_findings(case, index, output, currency)
        if isinstance(output, dict):
            found += reference_findings(case, index, output, sources, root)
    quantities = [o.get("quantity") for o in outputs if isinstance(o, dict)]
    if len(quantities) != len(set(quantities)):
        found.append(Finding("CASE-EXPECTED", case, "expected.json", "each quantity appears once"))
    if metadata.get("category") in ("invalid-input", "invalid-parameters"):
        found += invalid_case_findings(case, outputs, str(metadata["category"]))
    return found


def invalid_case_findings(case: str, outputs: Sequence[Any], category: str) -> list[Finding]:
    """An invalid-input case is rejected by the input contract; an invalid-parameters case
    passes it and fails on its parameter set."""
    texts = {o["quantity"]: o.get("text") for o in outputs if isinstance(o, dict) and "quantity" in o}
    expected = (("fail", "rejected") if category == "invalid-input" else ("pass", "failed"))
    if (texts.get("input_status"), texts.get("result_status")) != expected or "input_findings" not in texts:
        return [Finding("CASE-EXPECTED", case, "expected.json",
                        f"an {category} case expects input_status {expected[0]}, its input_findings and "
                        f"result_status {expected[1]}")]
    if any(isinstance(o, dict) and "value" in o for o in outputs):
        return [Finding("CASE-EXPECTED", case, "expected.json", "an invalid case has no numeric output")]
    return []


# --- Execution ------------------------------------------------------------------


def matches(actual: Any, expected: str, tolerance: Mapping[str, str]) -> bool:
    """|a - e| <= max(absolute, relative * |e|), with finite decimals only."""
    a, e = decimal_value(str(actual)), Decimal(expected)
    absolute, relative = Decimal(tolerance["absolute"]), Decimal(tolerance["relative"])
    if a is None:
        return False
    # A precision wide enough for every operand and product, trapping any rounding.
    digits = sum(len(n.as_tuple().digits) + abs(int(n.as_tuple().exponent)) for n in (a, e, absolute, relative))
    with localcontext(Context(prec=digits + 2, traps=[Inexact])):
        bound = max(absolute, relative * abs(e))
        return abs(a - e) <= bound


def run_script(root: Path, script: str, folder: Path) -> tuple[dict[str, Any] | None, str]:
    result = subprocess.run([sys.executable, "-I", str(root / script), str(folder)],
                            capture_output=True, text=True, check=False, timeout=60)
    if result.returncode:
        return None, f"{script} exited {result.returncode}: {result.stderr.strip()[:200]}"
    try:
        data = json.loads(result.stdout)
        values = {str(o["quantity"]): o for o in data["outputs"]}
    except (ValueError, KeyError, TypeError):
        return None, f"{script} did not print {{\"outputs\": [...]}}"
    return values, ""


def execute(case: str, outputs: Sequence[Any], report: Mapping[str, Any], root: Path,
            summary: Summary) -> None:
    """Run every executable assertion of a case and count the rest as registered only."""
    folder = root / CASES / case
    actual_inputs = {"input_status": report["status"],
                     "input_findings": ",".join(sorted({f["code"] for f in report["findings"]}))}
    scripts: dict[str, tuple[dict[str, Any] | None, str]] = {}
    for index, output in enumerate(o for o in outputs if isinstance(o, dict)):
        quantity, script = output["quantity"], output.get("reference", {}).get("script")
        path = f"expected.json:outputs[{index}]"
        if quantity in actual_inputs:
            summary.executed += 1
            if output.get("text") != actual_inputs[quantity]:
                summary.findings.append(Finding("CASE-MISMATCH", case, path,
                                                f"{quantity} is {actual_inputs[quantity]!r}, expected {output.get('text')!r}"))
        elif script:
            if script not in scripts:
                scripts[script] = run_script(root, script, folder)
            values, error = scripts[script]
            summary.executed += 1
            got = values.get(quantity) if values else None
            if got is None:
                summary.findings.append(Finding("CASE-MISMATCH", case, path, error or f"{script} gives no {quantity}"))
            elif not output_matches(output, got):
                summary.findings.append(Finding("CASE-MISMATCH", case, path, f"{quantity}: script gives {got}"))
        else:
            summary.registered_only += 1


def output_matches(output: Mapping[str, Any], got: Mapping[str, Any]) -> bool:
    if "text" in output:
        return bool(got.get("text") == output["text"])
    return matches(got.get("value"), output["value"], output["tolerance"])


def check_case(root: Path, case: str, requirements: set[str], sources: set[str], summary: Summary) -> None:
    folder = root / CASES / case
    try:
        metadata = strict_json(folder / "case.json")
        expected = strict_json(folder / "expected.json")
    except (OSError, ValueError) as error:
        summary.findings.append(Finding("CASE-JSON", case, "", str(error)))
        return
    found = metadata_findings(case, metadata, root, requirements)
    report = check_contract.validate_run(root, folder)
    run = read_run(root, folder)
    currency = run.get("reporting_currency")
    if isinstance(metadata, dict) and run.get("profile") not in (None, metadata.get("profile")):
        found.append(Finding("CASE-METADATA", case, "case.json:profile", "run.csv names another profile"))
    if isinstance(metadata, dict) and metadata.get("category") != "invalid-input" and report["status"] != "pass":
        found.append(Finding("CASE-INPUT", case, "", "only an invalid-input case may break the input contract"))
    found += expected_findings(case, expected, metadata if isinstance(metadata, dict) else {}, currency,
                               sources, root)
    summary.findings += found
    if not found:
        execute(case, expected["outputs"], report, root, summary)


def read_run(root: Path, folder: Path) -> dict[str, str]:
    """The single record of run.csv, read as the input contract reads it, or {} when unreadable."""
    contract = check_contract.load_json(root / check_contract.CONTRACT)
    table = check_contract.read_table("run", contract["files"]["run"], folder, contract["format"])
    return dict(table.rows[0]) if table.readable and len(table.rows) == 1 else {}


def check_all(root: Path) -> Summary:
    summary = Summary()
    requirements, sources = known_ids(root)
    base = root / CASES
    cases = sorted(path.name for path in base.iterdir() if path.is_dir()) if base.is_dir() else []
    for case in cases:
        summary.cases += 1
        check_case(root, case, requirements, sources, summary)
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        summary = check_all(args.root.resolve())
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"test-cases: ERROR: {error}", file=sys.stderr)
        return 2
    for finding in summary.findings:
        print(f"FAIL: {finding.case} {finding.path} {finding.code}: {finding.message}")
    print(f"cases: {summary.cases}; executed assertions: {summary.executed}; "
          f"registered, not executed: {summary.registered_only}")
    print(f"test-cases: {'PASS' if not summary.findings else 'FAIL'}")
    return 1 if summary.findings else 0


if __name__ == "__main__":
    sys.exit(main())
