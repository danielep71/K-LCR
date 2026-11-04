"""Tests for the validator of parameter sets and results (tools/check_parameters.py)."""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any

import check_contract
import check_parameters

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES: dict[str, Any] = {
    "schema": "klcr-categories",
    "categories_version": 3,
    "profiles": {
        "EU": {"assets": [{"code": "EU-A-L1"}],
               "outflows": [{"code": "EU-O-1"}, {"code": "EU-O-EXCL", "treatment": "exclusion"}],
               "inflows": [{"code": "EU-I-1"}], "excluded": [{"code": "EU-A-CIU"}]},
        "BASEL": {"assets": [{"code": "BASEL-A-L1"}],
                  "outflows": [{"code": "BASEL-O-1", "national_discretion": True}],
                  "inflows": [], "excluded": []},
    },
}
EU_LIMITS = [["LCR-MINIMUM", "Art. 4(2)"], ["LEVEL1-MINIMUM-SHARE", "Art. 17(1)(a)"],
             ["LEVEL1-EXCL-EHQCB-MINIMUM-SHARE", "Art. 17(1)(b)"], ["LEVEL2B-MAXIMUM-SHARE", "Art. 17(1)(c)"],
             ["INFLOW-CAP", "Art. 33(1)"]]
EU_SET: dict[str, Any] = {
    "schema": "klcr-parameter-set", "parameter_set_version": 1, "parameter_set": "EU-LCR-DA-2022-07-08",
    "profile": "EU", "status": "illustrative", "source_register_version": 1, "categories_version": 3,
    "factors": [
        {"category": "EU-A-L1", "kind": "haircut", "value": "0", "source": "SRC-02", "locator": "Art. 10(2)"},
        {"category": "EU-O-1", "kind": "outflow_rate", "value": "0.1", "source": "SRC-02", "locator": "Art. 25(1)"},
        {"category": "EU-I-1", "kind": "inflow_rate", "value": "0.5", "source": "SRC-02", "locator": "Art. 32(3)"},
    ],
    "limits": [{"id": name, "value": "0.5", "source": "SRC-02", "locator": locator} for name, locator in EU_LIMITS],
}
RESULT: dict[str, Any] = {
    "schema": "klcr-result", "result_version": 1, "status": "calculated", "illustrative": True,
    "lineage": {"run_fingerprint": "a" * 64, "input_contract_version": 1, "parameter_set": "EU-LCR-DA-2022-07-08",
                "parameter_set_sha256": "b" * 64, "categories_version": 3, "source_register_version": 1,
                "code_commit": "c" * 40},
    "figures": {"liquidity_buffer": "100", "outflows": "80", "inflows": "20", "inflows_after_cap": "20",
                "net_outflows": "60", "lcr": "1.66666666666667"},
    "components": [{"category": "EU-A-L1", "amount": "100", "factor": "0", "weighted": "100"}],
    "diagnostics": [{"code": "CALC-ILLUSTRATIVE", "severity": "warning", "message": "illustrative", "refs": []}],
}


class ParameterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for path in (check_contract.CONTRACT, check_parameters.CONTRACT):
            (self.root / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / path, self.root / path)
        (self.root / check_contract.CATEGORIES).write_text(json.dumps(CATEGORIES), encoding="utf-8")

    def codes(self, data: Any) -> list[list[str]]:
        check = check_parameters.check_result if isinstance(data, dict) and data.get("schema") == "klcr-result" \
            else check_parameters.check_parameter_set
        return [[f.code, f.path] for f in check(data, self.root)]


class ParameterSetTests(ParameterTestCase):
    def test_valid_illustrative_set(self) -> None:
        # EU-O-EXCL is an exclusion category: it takes no factor.
        self.assertEqual(self.codes(EU_SET), [])
        data = copy.deepcopy(EU_SET)
        data["factors"].append({"category": "EU-O-EXCL", "kind": "outflow_rate", "value": "0", "source": "SRC-02",
                                "locator": "Art. 25(4)"})
        self.assertEqual(self.codes(data), [["PAR-FACTOR-CATEGORY", "factors[3]"]])

    def test_header_profile_and_verification_date(self) -> None:
        data = copy.deepcopy(EU_SET)
        data.update(parameter_set="BASEL-LCR-2019-12-15", categories_version=2, status="sourced")
        self.assertEqual(self.codes(data), [["PAR-HEADER", "categories_version"], ["PAR-HEADER", "parameter_set"],
                                            ["PAR-HEADER", "verified_on"]])
        data = copy.deepcopy(EU_SET)
        data["verified_on"] = "2026-11-03"
        self.assertEqual(self.codes(data), [["PAR-HEADER", "verified_on"]])
        data["status"] = "sourced"
        self.assertEqual(self.codes(data), [])

    def test_factor_coverage_duplicates_and_categories(self) -> None:
        data = copy.deepcopy(EU_SET)
        data["factors"] = [data["factors"][0], data["factors"][0],
                           {**data["factors"][1], "category": "EU-A-CIU"}]
        self.assertEqual(self.codes(data), [["PAR-FACTOR-DUPLICATE", "factors[1]"],
                                            ["PAR-FACTOR-CATEGORY", "factors[2]"],
                                            ["PAR-FACTOR-MISSING", "factors"], ["PAR-FACTOR-MISSING", "factors"]])

    def test_factor_kind_value_and_source(self) -> None:
        data = copy.deepcopy(EU_SET)
        data["factors"][0].update(kind="outflow_rate", value="15%")
        data["factors"][1].update(value=0.1, source="SRC-06", locator="")
        data["factors"][2].update(value="1.5")
        self.assertEqual(self.codes(data), [["PAR-FACTOR", "factors[0]"], ["PAR-VALUE", "factors[0]"],
                                            ["PAR-VALUE", "factors[1]"], ["PAR-SOURCE", "factors[1]"],
                                            ["PAR-SOURCE", "factors[1]"], ["PAR-VALUE", "factors[2]"]])

    def test_limits_are_complete_and_cite_their_locator(self) -> None:
        data = copy.deepcopy(EU_SET)
        data["limits"] = data["limits"][1:] + [data["limits"][1]]
        data["limits"][0]["locator"] = "Art. 17(1)"
        self.assertEqual(self.codes(data), [["PAR-LIMIT", "limits[0]"], ["PAR-LIMIT", "limits[4]"],
                                            ["PAR-LIMIT", "limits"]])

    def test_basel_discretion_needs_a_recorded_choice(self) -> None:
        data = {**copy.deepcopy(EU_SET), "profile": "BASEL", "parameter_set": "BASEL-LCR-2019-12-15",
                "factors": [{"category": "BASEL-A-L1", "kind": "haircut", "value": "0", "source": "SRC-06",
                             "locator": "LCR30.40"},
                            {"category": "BASEL-O-1", "kind": "outflow_rate", "value": "0.05", "source": "SRC-06",
                             "locator": "LCR40.7", "discretion_choice": " "}],
                "limits": [{"id": name, "value": "1", "source": "SRC-06", "locator": locator}
                           for name, locator in (("LCR-MINIMUM", "LCR20.5"), ("LEVEL2-MAXIMUM-SHARE", "LCR30.34"),
                                                 ("LEVEL2B-MAXIMUM-SHARE", "LCR30.33"),
                                                 ("INFLOW-CAP", "LCR40.77"))]}
        self.assertEqual(self.codes(data), [["PAR-DISCRETION", "factors[1]"]])
        del data["factors"][1]["discretion_choice"]
        self.assertEqual(self.codes(data), [["PAR-FACTOR", "factors[1]"], ["PAR-DISCRETION", "factors[1]"]])


class ResultTests(ParameterTestCase):
    def test_valid_calculated_result(self) -> None:
        self.assertEqual(self.codes(RESULT), [])

    def test_rejected_result_has_no_figures_and_names_its_error(self) -> None:
        data = copy.deepcopy(RESULT)
        data["status"] = "rejected"
        self.assertEqual(self.codes(data), [["RES-FIGURES", "figures"], ["RES-STATUS", "status"],
                                            ["RES-STATUS", "status"]])
        del data["figures"], data["components"]
        data["diagnostics"].append({"code": "CALC-INPUT-REJECTED", "severity": "error", "message": "x",
                                    "refs": ["LCR-TYPE"]})
        self.assertEqual(self.codes(data), [])

    def test_calculated_result_with_an_error_or_missing_lineage(self) -> None:
        data = copy.deepcopy(RESULT)
        data["lineage"]["code_commit"] = ""
        data["figures"]["lcr"] = "NaN"
        data["diagnostics"].append({"code": "CALC-ZERO-NET-OUTFLOWS", "severity": "error", "message": "x",
                                    "refs": []})
        self.assertEqual(self.codes(data), [["RES-LINEAGE", "lineage.code_commit"], ["RES-FIGURES", "figures.lcr"],
                                            ["RES-STATUS", "status"]])

    def test_diagnostics_and_illustrative_flag(self) -> None:
        data = copy.deepcopy(RESULT)
        data["diagnostics"] = [{"code": "CALC-INFLOW-CAP", "severity": "error", "message": "x", "refs": []},
                               {"code": "NO-SUCH", "severity": "info", "message": "x", "refs": []}]
        self.assertEqual(self.codes(data), [["RES-DIAGNOSTIC", "diagnostics[0]"],
                                            ["RES-DIAGNOSTIC", "diagnostics[1]"],
                                            ["RES-ILLUSTRATIVE", "illustrative"]])


class MalformedInputTests(ParameterTestCase):
    def test_non_scalar_values_give_findings_not_errors(self) -> None:
        values: list[Any] = [[], {}, 1.5, None]
        for bad in values:
            for key in ("profile", "status", "parameter_set", "factors", "limits"):
                with self.subTest(key=key, bad=bad):
                    self.assertTrue(self.codes({**copy.deepcopy(EU_SET), key: bad}))
            for key in ("status", "lineage", "figures", "components", "diagnostics", "illustrative"):
                with self.subTest(key=key, bad=bad):
                    self.assertTrue(self.codes({**copy.deepcopy(RESULT), key: bad}))
        data = copy.deepcopy(EU_SET)
        data["limits"][0]["id"] = ["LCR-MINIMUM"]
        self.assertIn(["PAR-LIMIT", "limits[0]"], self.codes(data))
        result = copy.deepcopy(RESULT)
        result["diagnostics"][0]["code"] = {"x": 1}
        self.assertIn(["RES-DIAGNOSTIC", "diagnostics[0]"], self.codes(result))

    def test_every_component_is_checked(self) -> None:
        data = copy.deepcopy(RESULT)
        data["components"] = [None, {"category": "EU-A-L1", "amount": "1", "factor": "1.5", "weighted": "x"},
                              {"category": "", "amount": "1", "factor": "0", "weighted": "1"}]
        self.assertEqual(self.codes(data), [["RES-FIGURES", "components[0]"], ["RES-FIGURES", "components[1].factor"],
                                            ["RES-FIGURES", "components[1].weighted"],
                                            ["RES-FIGURES", "components[2].category"]])


class FixtureTests(unittest.TestCase):
    def test_repository_fixtures_match_expected(self) -> None:
        self.assertEqual(check_parameters.check_fixtures(ROOT), [])


if __name__ == "__main__":
    unittest.main()
