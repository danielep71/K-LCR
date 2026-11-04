"""Tests for the test-case checker (tools/check_test_cases.py)."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from typing import Any

import check_test_cases as ctc

ROOT = Path(__file__).resolve().parents[1]
CASE = "illustrative-eu-input-totals"
INVALID = "illustrative-eu-rejected-input"


class Workspace(unittest.TestCase):
    """A temporary copy of the files the checker reads."""

    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for folder in ("docs/methodology", "tests/parameters", "tests/cases", "tests/derivations"):
            shutil.copytree(ROOT / folder, self.root / folder,
                            ignore=shutil.ignore_patterns("sources", "__pycache__"))

    def load(self, case: str, name: str) -> Any:
        return json.loads((self.root / ctc.CASES / case / name).read_text(encoding="utf-8"))

    def save(self, case: str, name: str, data: Any) -> None:
        (self.root / ctc.CASES / case / name).write_text(json.dumps(data), encoding="utf-8")

    def codes(self) -> list[list[str]]:
        return [[f.code, f.case, f.path] for f in ctc.check_all(self.root).findings]


class RepositoryTests(unittest.TestCase):
    def test_registered_cases_pass_and_counts_are_reported(self) -> None:
        summary = ctc.check_all(ROOT)
        self.assertEqual(summary.findings, [])
        self.assertEqual((summary.cases, summary.executed, summary.registered_only), (2, 6, 2))


class ComparisonTests(unittest.TestCase):
    def test_tolerance_rule(self) -> None:
        exact = {"absolute": "0", "relative": "0"}
        self.assertTrue(ctc.matches("1.50", "1.5", exact))
        self.assertFalse(ctc.matches("1.5000001", "1.5", exact))
        loose = {"absolute": "0.001", "relative": "0.01"}
        self.assertTrue(ctc.matches("101", "100", loose))
        self.assertFalse(ctc.matches("101.1", "100", loose))
        # Near zero the absolute bound governs.
        self.assertTrue(ctc.matches("0.0009", "0", loose))
        self.assertFalse(ctc.matches("0.002", "0", loose))

    def test_comparison_never_rounds(self) -> None:
        self.assertFalse(ctc.matches("1.0000000000000000000000000001", "0", {"absolute": "1", "relative": "0"}))
        self.assertTrue(ctc.matches("1.0000000000000000000000000000", "0", {"absolute": "1", "relative": "0"}))
        self.assertFalse(ctc.matches("100.0000000000000000000000000001", "100",
                                     {"absolute": "0", "relative": "0"}))

    def test_non_finite_and_non_decimal_values_never_match(self) -> None:
        loose = {"absolute": "1000", "relative": "1"}
        for actual in ("NaN", "inf", "-Infinity", "1e3", "", "None"):
            with self.subTest(actual=actual):
                self.assertFalse(ctc.matches(actual, "1", loose))
        self.assertEqual(ctc.decimal_value("0.25"), Decimal("0.25"))
        self.assertIsNone(ctc.decimal_value(0.25))


class MetadataTests(Workspace):
    def test_metadata_rules(self) -> None:
        data = self.load(CASE, "case.json")
        data.update(id="other", synthetic=False, requirements=["REQ-99"], profile="BASEL")
        data["review"]["status"] = "reviewed"
        self.save(CASE, "case.json", data)
        self.assertEqual(self.codes(), [
            ["CASE-METADATA", CASE, "case.json:id"], ["CASE-METADATA", CASE, "case.json:synthetic"],
            ["CASE-METADATA", CASE, "case.json:requirements"], ["CASE-METADATA", CASE, "case.json:parameter_set"],
            ["CASE-METADATA", CASE, "case.json:review"], ["CASE-METADATA", CASE, "case.json:profile"]])

    def test_strict_json(self) -> None:
        (self.root / ctc.CASES / CASE / "case.json").write_text('{"id": 1, "id": 2}', encoding="utf-8")
        (self.root / ctc.CASES / INVALID / "expected.json").write_text('{"value": NaN}', encoding="utf-8")
        self.assertEqual(self.codes(), [["CASE-JSON", CASE, ""], ["CASE-JSON", INVALID, ""]])

    def test_valid_case_must_pass_the_input_contract(self) -> None:
        shutil.copy(self.root / ctc.CASES / INVALID / "assets.csv", self.root / ctc.CASES / CASE / "assets.csv")
        self.assertIn(["CASE-INPUT", CASE, ""], self.codes())


class OutputTests(Workspace):
    def test_output_form_unit_and_tolerance(self) -> None:
        data = self.load(CASE, "expected.json")
        outputs = data["outputs"]
        outputs[2].update(unit="USD", value=56750.5)
        outputs[3]["tolerance"] = {"absolute": "-1", "relative": "0"}
        outputs.append({"quantity": "lcr_total", "value": "1", "unit": "1",
                        "tolerance": {"absolute": "0", "relative": "0"}, "reference": outputs[2]["reference"]})
        self.save(CASE, "expected.json", data)
        self.assertEqual(self.codes(), [["CASE-OUTPUT", CASE, "expected.json:outputs[2]"],
                                        ["CASE-OUTPUT", CASE, "expected.json:outputs[2]"],
                                        ["CASE-OUTPUT", CASE, "expected.json:outputs[3]"],
                                        ["CASE-OUTPUT", CASE, "expected.json:outputs[5]"]])

    def test_illustrative_quantities_only_in_illustrative_cases(self) -> None:
        folder = self.root / ctc.CASES
        shutil.copytree(folder / CASE, folder / "eu-input-totals")
        data = self.load("eu-input-totals", "case.json")
        data["id"] = "eu-input-totals"
        self.save("eu-input-totals", "case.json", data)
        expected = self.load("eu-input-totals", "expected.json")
        expected["case"] = "eu-input-totals"
        self.save("eu-input-totals", "expected.json", expected)
        self.assertEqual([c[0] for c in self.codes()], ["CASE-OUTPUT", "CASE-OUTPUT"])

    def test_invalid_parameters_case(self) -> None:
        folder = self.root / ctc.CASES
        shutil.copytree(folder / CASE, folder / "illustrative-eu-basel-parameters")
        data = self.load("illustrative-eu-basel-parameters", "case.json")
        data.update(id="illustrative-eu-basel-parameters", category="invalid-parameters",
                    parameter_set="tests/parameters/parameter-set-basel-illustrative.json")
        self.save("illustrative-eu-basel-parameters", "case.json", data)
        expected = self.load("illustrative-eu-basel-parameters", "expected.json")
        expected["case"] = "illustrative-eu-basel-parameters"
        expected["outputs"] = [expected["outputs"][0], expected["outputs"][1],
                               {**expected["outputs"][4], "text": "failed"}]
        self.save("illustrative-eu-basel-parameters", "expected.json", expected)
        self.assertEqual(self.codes(), [])
        expected["outputs"][2]["text"] = "rejected"
        self.save("illustrative-eu-basel-parameters", "expected.json", expected)
        self.assertEqual(self.codes(), [["CASE-EXPECTED", "illustrative-eu-basel-parameters", "expected.json"]])

    def test_invalid_case_shape(self) -> None:
        data = self.load(INVALID, "expected.json")
        data["outputs"] = data["outputs"][:2]
        self.save(INVALID, "expected.json", data)
        self.assertEqual(self.codes(), [["CASE-EXPECTED", INVALID, "expected.json"]])


class ReferenceTests(Workspace):
    def test_reference_classes(self) -> None:
        data = self.load(CASE, "expected.json")
        outputs = data["outputs"]
        outputs[0]["reference"].update({"class": "published", "source": "SRC-99", "locator": "Art. 1"})
        outputs[1]["reference"]["class"] = "independent"
        outputs[2]["reference"].update({"class": "contract", "source": "docs/methodology/data-contract.json"})
        outputs[4]["reference"]["date"] = "yesterday"
        self.save(CASE, "expected.json", data)
        self.assertEqual(self.codes(), [
            ["CASE-REFERENCE", CASE, "expected.json:outputs[0].reference"],
            ["CASE-REFERENCE", CASE, "expected.json:outputs[1].reference"],
            ["CASE-REFERENCE", CASE, "expected.json:outputs[2].reference"],
            ["CASE-REFERENCE", CASE, "expected.json:outputs[2].reference"],
            ["CASE-REFERENCE", CASE, "expected.json:outputs[4].reference"]])

    def test_derivation_may_not_import_the_code_under_test(self) -> None:
        script = self.root / "tests/derivations/illustrative_input_totals.py"
        for line in ("import check_contract\n", "from tools import check_contract\n", "from . import x\n"):
            with self.subTest(line=line):
                script.write_text(line + (ROOT / "tests/derivations/illustrative_input_totals.py").read_text(),
                                  encoding="utf-8")
                self.assertEqual({c[0] for c in self.codes()}, {"CASE-ORACLE"})
        data = self.load(CASE, "expected.json")
        data["outputs"][2]["reference"]["script"] = "tests/derivations/missing.py"
        self.save(CASE, "expected.json", data)
        self.assertIn(["CASE-SCRIPT", CASE, "expected.json:outputs[2].reference"], self.codes())


class ExecutionTests(Workspace):
    def test_mismatches_are_reported(self) -> None:
        data = self.load(CASE, "expected.json")
        data["outputs"][2]["value"] = "56750.51"
        data["outputs"][1]["text"] = "LCR-RANGE"
        self.save(CASE, "expected.json", data)
        invalid = self.load(INVALID, "expected.json")
        invalid["outputs"][1]["text"] = "LCR-TYPE"
        self.save(INVALID, "expected.json", invalid)
        self.assertEqual(self.codes(), [["CASE-MISMATCH", CASE, "expected.json:outputs[1]"],
                                        ["CASE-MISMATCH", CASE, "expected.json:outputs[2]"],
                                        ["CASE-MISMATCH", INVALID, "expected.json:outputs[1]"]])

    def test_failing_script_is_reported(self) -> None:
        (self.root / "tests/derivations/illustrative_input_totals.py").write_text("raise SystemExit(3)\n",
                                                                                  encoding="utf-8")
        self.assertEqual([c[0] for c in self.codes()], ["CASE-MISMATCH", "CASE-MISMATCH"])


if __name__ == "__main__":
    unittest.main()
