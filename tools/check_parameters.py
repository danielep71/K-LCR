#!/usr/bin/env python3
"""Reference validator of K-LCR parameter sets and results
(docs/methodology/parameter-result-contract.json).

It checks the form and completeness of a parameter set or a result file and
reports findings with stable codes. It does not check that a value is the
right regulatory value, and it calculates nothing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import check_contract

CONTRACT = Path("docs/methodology/parameter-result-contract.json")
FIXTURES = Path("tests/parameters")
EXPECTED = FIXTURES / "expected.json"
FACTOR_KEYS = {"category", "kind", "value", "source", "locator"}
LIMIT_KEYS = {"id", "value", "source", "locator"}
COMPONENT_KEYS = {"category", "amount", "factor", "weighted"}


@dataclass(frozen=True)
class Finding:
    code: str
    path: str
    message: str


def load(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (check_contract.load_json(root / CONTRACT),
            check_contract.load_json(root / check_contract.CONTRACT),
            check_contract.load_json(root / check_contract.CATEGORIES))


def text(value: Any) -> str | None:
    """value when it is a string; None for anything else, so that a lookup never fails on it."""
    return value if isinstance(value, str) else None


def decimal_problem(value: Any, rules: Mapping[str, Any], maximum: Decimal | None) -> str | None:
    """Why value is not an admissible decimal string, or None."""
    if not isinstance(value, str) or not re.match(rules["pattern"], value):
        return f"{value!r} is not a decimal string such as \"0.25\""
    if check_contract.significant_digits(value) > rules["max_significant_digits"]:
        return f"{value} has more than {rules['max_significant_digits']} significant digits"
    if maximum is not None and Decimal(value) > maximum:
        return f"{value} is above {maximum}"
    return None


# --- Parameter sets -----------------------------------------------------------


def header_findings(data: Mapping[str, Any], contract: Mapping[str, Any], inputs: Mapping[str, Any],
                    categories: Mapping[str, Any]) -> list[Finding]:
    spec = contract["parameter_set"]
    found = []
    expected = {"schema": spec["schema"], "parameter_set_version": 1,
                "source_register_version": inputs["source_register_version"],
                "categories_version": categories["categories_version"]}
    for key, value in expected.items():
        if data.get(key) != value:
            found.append(Finding("PAR-HEADER", key, f"expected {value!r}, found {data.get(key)!r}"))
    profile = text(data.get("profile"))
    if profile not in inputs["profiles"]:
        found.append(Finding("PAR-HEADER", "profile", f"{profile!r} is not EU or BASEL"))
    elif data.get("parameter_set") != inputs["profiles"][profile]["parameter_set"]:
        found.append(Finding("PAR-HEADER", "parameter_set",
                             f"profile {profile} uses {inputs['profiles'][profile]['parameter_set']}"))
    status = text(data.get("status"))
    if status not in spec["statuses"]:
        found.append(Finding("PAR-HEADER", "status", f"{status!r} is not one of {', '.join(spec['statuses'])}"))
    found += verified_findings(data, status)
    return found


def verified_findings(data: Mapping[str, Any], status: Any) -> list[Finding]:
    verified = data.get("verified_on")
    if status == "sourced":
        try:
            date.fromisoformat(str(verified))
        except ValueError:
            return [Finding("PAR-HEADER", "verified_on", "a sourced set needs its verification date")]
    elif verified is not None:
        return [Finding("PAR-HEADER", "verified_on", "only a sourced set has a verification date")]
    return []


def category_kinds(profile: Mapping[str, Any]) -> dict[str, tuple[str, bool]]:
    """Each in-scope category that takes a factor, with its kind and whether it is a national discretion."""
    kinds = {}
    for group, kind in (("assets", "asset"), ("outflows", "outflow"), ("inflows", "inflow")):
        for item in profile[group]:
            # An exclusion category keeps its items out of the calculation: it has no factor.
            if item.get("treatment") != "exclusion":
                kinds[item["code"]] = (kind, bool(item.get("national_discretion")))
    return kinds


def factor_findings(data: Mapping[str, Any], contract: Mapping[str, Any],
                    categories: Mapping[str, Any]) -> list[Finding]:
    profile = str(data.get("profile"))
    if profile not in categories["profiles"]:
        return []
    spec = contract["parameter_set"]
    kinds = category_kinds(categories["profiles"][profile])
    factors = data.get("factors")
    if not isinstance(factors, list):
        return [Finding("PAR-FACTOR", "factors", "factors must be a list")]
    found: list[Finding] = []
    seen: set[str] = set()
    for index, factor in enumerate(factors):
        found += one_factor(factor, f"factors[{index}]", kinds, seen, spec, profile, contract["decimal"])
    found += [Finding("PAR-FACTOR-MISSING", "factors", f"no factor for {code}")
              for code in sorted(set(kinds) - seen)]
    return found


def one_factor(factor: Any, path: str, kinds: Mapping[str, tuple[str, bool]], seen: set[str],
               spec: Mapping[str, Any], profile: str, rules: Mapping[str, Any]) -> list[Finding]:
    if not isinstance(factor, dict):
        return [Finding("PAR-FACTOR", path, "a factor must be an object")]
    code = str(factor.get("category"))
    if code not in kinds:
        return [Finding("PAR-FACTOR-CATEGORY", path, f"{code!r} is not a category of {profile} that takes a factor")]
    if code in seen:
        return [Finding("PAR-FACTOR-DUPLICATE", path, f"{code} has more than one factor")]
    seen.add(code)
    kind, discretion = kinds[code]
    found = []
    keys = FACTOR_KEYS | ({"discretion_choice"} if discretion else set())
    if set(factor) != keys:
        found.append(Finding("PAR-FACTOR", path, f"keys must be exactly {', '.join(sorted(keys))}"))
    if factor.get("kind") != spec["factor_kinds"][kind]:
        found.append(Finding("PAR-FACTOR", path, f"{code} needs kind {spec['factor_kinds'][kind]}"))
    problem = decimal_problem(factor.get("value"), rules, Decimal(1))
    if problem:
        found.append(Finding("PAR-VALUE", path, problem))
    found += source_findings(factor, path, spec["sources"][profile])
    if discretion and not str(factor.get("discretion_choice") or "").strip():
        found.append(Finding("PAR-DISCRETION", path, f"{code} is a national discretion: record the choice (A07)"))
    return found


def source_findings(entry: Mapping[str, Any], path: str, sources: Sequence[str]) -> list[Finding]:
    found = []
    if entry.get("source") not in sources:
        found.append(Finding("PAR-SOURCE", path, f"source must be one of {', '.join(sources)}"))
    if not str(entry.get("locator") or "").strip():
        found.append(Finding("PAR-SOURCE", path, "a locator is required"))
    return found


def limit_findings(data: Mapping[str, Any], contract: Mapping[str, Any]) -> list[Finding]:
    profile = text(data.get("profile"))
    spec = contract["parameter_set"]
    if profile not in spec["limits"]:
        return []
    limits = data.get("limits")
    if not isinstance(limits, list):
        return [Finding("PAR-LIMIT", "limits", "limits must be a list")]
    expected = {item["id"]: item for item in spec["limits"][profile]}
    found = []
    seen: set[str] = set()
    for index, limit in enumerate(limits):
        path = f"limits[{index}]"
        if not isinstance(limit, dict) or text(limit.get("id")) not in expected or limit["id"] in seen:
            found.append(Finding("PAR-LIMIT", path, "unknown, malformed or repeated limit"))
            continue
        seen.add(limit["id"])
        reference = expected[limit["id"]]
        if set(limit) != LIMIT_KEYS or (limit["source"], limit["locator"]) != (reference["source"], reference["locator"]):
            found.append(Finding("PAR-LIMIT", path, f"{limit['id']} must cite {reference['source']} "
                                                    f"{reference['locator']}"))
        problem = decimal_problem(limit.get("value"), contract["decimal"], None)
        if problem:
            found.append(Finding("PAR-VALUE", path, problem))
    found += [Finding("PAR-LIMIT", "limits", f"no value for {name}") for name in sorted(set(expected) - seen)]
    return found


def check_parameter_set(data: Any, root: Path) -> list[Finding]:
    contract, inputs, categories = load(root)
    if not isinstance(data, dict):
        return [Finding("PAR-HEADER", "", "a parameter set must be a JSON object")]
    return (header_findings(data, contract, inputs, categories)
            + factor_findings(data, contract, categories) + limit_findings(data, contract))


# --- Results ------------------------------------------------------------------


def lineage_findings(data: Mapping[str, Any], spec: Mapping[str, Any]) -> list[Finding]:
    lineage = data.get("lineage")
    if not isinstance(lineage, dict):
        return [Finding("RES-LINEAGE", "lineage", "lineage must be an object")]
    return [Finding("RES-LINEAGE", f"lineage.{name}", "required")
            for name in spec["lineage_fields"] if lineage.get(name) in (None, "")]


def figure_findings(data: Mapping[str, Any], spec: Mapping[str, Any], rules: Mapping[str, Any]) -> list[Finding]:
    calculated = data.get("status") == "calculated"
    figures, components = data.get("figures"), data.get("components")
    if not calculated:
        if figures is not None or components is not None:
            return [Finding("RES-FIGURES", "figures", "only a calculated result has figures and components")]
        return []
    if not isinstance(figures, dict) or set(figures) != set(spec["figures"]):
        return [Finding("RES-FIGURES", "figures", f"figures must be exactly {', '.join(spec['figures'])}")]
    found = [Finding("RES-FIGURES", f"figures.{name}", problem) for name in spec["figures"]
             if (problem := decimal_problem(figures[name], rules, None))]
    if not isinstance(components, list) or not components:
        found.append(Finding("RES-FIGURES", "components", "a calculated result lists its components"))
        return found
    for index, component in enumerate(components):
        found += component_findings(component, f"components[{index}]", rules)
    return found


def component_findings(component: Any, path: str, rules: Mapping[str, Any]) -> list[Finding]:
    """A component names its category and gives its amount, factor and weighted amount."""
    if not isinstance(component, dict) or set(component) != COMPONENT_KEYS:
        return [Finding("RES-FIGURES", path, f"a component has exactly {', '.join(sorted(COMPONENT_KEYS))}")]
    found = []
    if not text(component["category"]):
        found.append(Finding("RES-FIGURES", f"{path}.category", "a component names its category"))
    for name, maximum in (("amount", None), ("factor", Decimal(1)), ("weighted", None)):
        problem = decimal_problem(component[name], rules, maximum)
        if problem:
            found.append(Finding("RES-FIGURES", f"{path}.{name}", problem))
    return found


def diagnostic_findings(data: Mapping[str, Any], spec: Mapping[str, Any]) -> list[Finding]:
    diagnostics = data.get("diagnostics")
    if not isinstance(diagnostics, list):
        return [Finding("RES-DIAGNOSTIC", "diagnostics", "diagnostics must be a list")]
    found, codes = [], set()
    for index, item in enumerate(diagnostics):
        path = f"diagnostics[{index}]"
        known = spec["diagnostics"].get(text(item.get("code"))) if isinstance(item, dict) else None
        if known is None or set(item) != {"code", "severity", "message", "refs"}:
            found.append(Finding("RES-DIAGNOSTIC", path, "unknown code or keys other than code, severity, message, refs"))
            continue
        codes.add(item["code"])
        if item["severity"] != known["severity"]:
            found.append(Finding("RES-DIAGNOSTIC", path, f"{item['code']} has severity {known['severity']}"))
    return found + consistency_findings(data, spec, codes, diagnostics)


def consistency_findings(data: Mapping[str, Any], spec: Mapping[str, Any], codes: set[str],
                         diagnostics: Iterable[Any]) -> list[Finding]:
    found = []
    status = text(data.get("status"))
    errors = {str(item.get("code")) for item in diagnostics if isinstance(item, dict)
              and spec["diagnostics"].get(text(item.get("code")), {}).get("severity") == "error"}
    if status == "calculated" and errors:
        found.append(Finding("RES-STATUS", "status", f"a calculated result has error diagnostics {sorted(errors)}"))
    if status in ("rejected", "failed") and not errors:
        found.append(Finding("RES-STATUS", "status", f"a {status} result names its error diagnostic"))
    if status == "rejected" and "CALC-INPUT-REJECTED" not in codes:
        found.append(Finding("RES-STATUS", "status", "a rejected result has CALC-INPUT-REJECTED"))
    if data.get("illustrative") is True and "CALC-ILLUSTRATIVE" not in codes:
        found.append(Finding("RES-ILLUSTRATIVE", "illustrative", "an illustrative result has CALC-ILLUSTRATIVE"))
    return found


def check_result(data: Any, root: Path) -> list[Finding]:
    contract = load(root)[0]
    spec = contract["result"]
    if not isinstance(data, dict):
        return [Finding("RES-HEADER", "", "a result must be a JSON object")]
    found = []
    if data.get("schema") != spec["schema"] or data.get("result_version") != 1:
        found.append(Finding("RES-HEADER", "schema", "expected klcr-result, version 1"))
    if text(data.get("status")) not in spec["statuses"]:
        found.append(Finding("RES-HEADER", "status", f"{data.get('status')!r} is not a result status"))
    if not isinstance(data.get("illustrative"), bool):
        found.append(Finding("RES-HEADER", "illustrative", "must be true or false"))
    return (found + lineage_findings(data, spec) + figure_findings(data, spec, contract["decimal"])
            + diagnostic_findings(data, spec))


# --- Fixtures and command line --------------------------------------------------


def check_file(path: Path, root: Path) -> list[Finding]:
    data = json.loads(path.read_text(encoding="utf-8"))
    schema = data.get("schema") if isinstance(data, dict) else None
    return check_result(data, root) if schema == "klcr-result" else check_parameter_set(data, root)


def check_fixtures(root: Path) -> list[str]:
    expected = check_contract.load_json(root / EXPECTED)["cases"]
    files = sorted(path.name for path in (root / FIXTURES).glob("*.json") if path.name != EXPECTED.name)
    problems = []
    if files != sorted(expected):
        problems.append(f"fixture files {files} do not match expected.json {sorted(expected)}")
    for name, codes in sorted(expected.items()):
        got = [[f.code, f.path] for f in check_file(root / FIXTURES / name, root)]
        if got != codes:
            problems.append(f"{name}: findings {got}, expected {codes}")
    return problems


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--file", type=Path, help="a parameter set or result JSON file")
    mode.add_argument("--check-fixtures", action="store_true", help="check tests/parameters against expected.json")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.check_fixtures:
        problems = check_fixtures(root)
        for problem in problems:
            print(f"FAIL: {problem}")
        print(f"parameter-result-contract: {'PASS' if not problems else 'FAIL'}")
        return 1 if problems else 0
    findings = check_file(args.file, root)
    print(json.dumps([asdict(f) for f in findings], indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
