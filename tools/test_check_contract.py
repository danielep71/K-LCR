"""Tests for the reference validator of the input contract (tools/check_contract.py)."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any

import check_contract

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES: dict[str, Any] = {
    "schema": "klcr-categories",
    "categories_version": 1,
    "profiles": {
        "EU": {
            "assets": [{"code": "EU-A-L1-CASH"}, {"code": "EU-A-L2A-BOND"}],
            "outflows": [{"code": "EU-O-RETAIL"},
                         {"code": "EU-O-SECURED", "collateral": {"rule": "required", "allowed": ["EU-A-L2A-BOND"]}},
                         {"code": "EU-O-SWAP", "collateral": {"rule": "optional"}},
                         {"code": "EU-O-DERIVATIVES", "derivative": True}],
            "inflows": [{"code": "EU-I-LOANS"}],
            "excluded": [{"code": "EU-A-CIU"}, {"code": "EU-O-INTRAGROUP"}],
        },
        "BASEL": {"assets": [{"code": "BASEL-A-L1-CASH"}], "outflows": [{"code": "BASEL-O-RETAIL"}],
                  "inflows": [], "excluded": []},
    },
}
RUN = ("run_id;profile;parameter_set;source_register_version;reporting_date;reporting_currency;"
       "perimeter_type;perimeter_id;synthetic\n"
       "R1;EU;EU-LCR-DA-2022-07-08;1;2026-06-30;EUR;INDIVIDUAL;BANK-A;Y\n")
ASSETS = ("asset_id;category;market_value;original_currency;requirements_met\n"
          "A1;EU-A-L1-CASH;100.50;EUR;Y\nA2;EU-A-L2A-BOND;20;USD;N\nA3;EU-A-L1-CASH;0.25;EUR;Y\n")
FLOWS = ("flow_id;direction;category;amount;original_currency;maturity_date;collateral_category;"
         "netting_set_id\n"
         "F1;OUTFLOW;EU-O-RETAIL;1000;EUR;;;\n"
         "F2;OUTFLOW;EU-O-SECURED;50;EUR;2026-07-10;EU-A-L2A-BOND;\n"
         "F3;INFLOW;EU-I-LOANS;30;EUR;2026-07-15;;\n"
         "F4;OUTFLOW;EU-O-DERIVATIVES;5;EUR;2026-07-01;;NS-1\n")


class Workspace:
    """A temporary root with the real contract, test categories and one run folder."""

    def __init__(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        contract = self.root / check_contract.CONTRACT
        contract.parent.mkdir(parents=True)
        shutil.copy(ROOT / check_contract.CONTRACT, contract)
        (self.root / check_contract.CATEGORIES).write_text(json.dumps(CATEGORIES), encoding="utf-8")
        self.run = self.root / "run"
        self.run.mkdir()
        self.write(RUN, ASSETS, FLOWS)

    def write(self, run: str | None = None, assets: str | None = None, flows: str | None = None) -> None:
        for name, text in (("run.csv", run), ("assets.csv", assets), ("flows.csv", flows)):
            if text is not None:
                (self.run / name).write_text(text, encoding="utf-8", newline="")

    def findings(self) -> list[list[Any]]:
        report = check_contract.validate_run(self.root, self.run)
        return [[f["code"], f["file"], f["record"], f["column"]] for f in report["findings"]]

    def close(self) -> None:
        self.directory.cleanup()


class ContractTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.space = Workspace()
        self.addCleanup(self.space.close)


class SyntaxTests(unittest.TestCase):
    def test_quoted_fields_with_delimiters_quotes_and_newlines(self) -> None:
        records, error, _ = check_contract.split_records('a;"b;c";"say ""hi"""\n"x\ny";z;\n')
        self.assertIsNone(error)
        self.assertEqual([r.fields for r in records], [["a", "b;c", 'say "hi"'], ["x\ny", "z", ""]])
        self.assertEqual([r.line for r in records], [1, 2])

    def test_crlf_and_missing_final_newline(self) -> None:
        records, error, _ = check_contract.split_records("a;b\r\n1;2")
        self.assertIsNone(error)
        self.assertEqual([r.fields for r in records], [["a", "b"], ["1", "2"]])

    def test_syntax_errors(self) -> None:
        for text, message in (('a;b"c\n', "a quote inside an unquoted field"),
                              ('"a"b\n', "text after a closing quote"),
                              ('a;"b\n', "a quoted field is not closed"),
                              ("a\rb\n", "a carriage return outside a quoted field")):
            with self.subTest(text=text):
                self.assertEqual(check_contract.split_records(text)[1], message)


class ValidRunTests(ContractTestCase):
    def test_valid_run_passes_with_exact_reconciliation(self) -> None:
        report = check_contract.validate_run(self.space.root, self.space.run)
        self.assertEqual(report["status"], "pass", report["findings"])
        assets = report["reconciliation"]["assets"]
        self.assertEqual(assets["market_value_by_category"], {"EU-A-L1-CASH": "100.75", "EU-A-L2A-BOND": "20"})
        self.assertEqual(assets["market_value_total"], "120.75")
        self.assertEqual(report["reconciliation"]["flows"]["amount_by_direction"],
                         {"INFLOW": "30", "OUTFLOW": "1055"})

    def test_bom_and_crlf_input_is_read_like_lf_input(self) -> None:
        before = check_contract.validate_run(self.space.root, self.space.run)
        self.space.write(run="﻿" + RUN.replace("\n", "\r\n"))
        after = check_contract.validate_run(self.space.root, self.space.run)
        self.assertEqual(after["status"], "pass", after["findings"])
        self.assertEqual(after["reconciliation"], before["reconciliation"])
        self.assertNotEqual(after["fingerprint"], before["fingerprint"])

    def test_report_is_repeatable_and_inputs_unchanged(self) -> None:
        data = {path.name: path.read_bytes() for path in self.space.run.iterdir()}
        first = check_contract.validate_run(self.space.root, self.space.run)
        second = check_contract.validate_run(self.space.root, self.space.run)
        self.assertEqual(first, second)
        self.assertEqual(data, {path.name: path.read_bytes() for path in self.space.run.iterdir()})

    def test_fingerprint_covers_contract_categories_and_inputs(self) -> None:
        base = check_contract.validate_run(self.space.root, self.space.run)["fingerprint"]
        self.space.write(assets=ASSETS + "A4;EU-A-L1-CASH;1;EUR;Y\n")
        self.assertNotEqual(check_contract.validate_run(self.space.root, self.space.run)["fingerprint"], base)
        self.space.write(assets=ASSETS)
        categories = self.space.root / check_contract.CATEGORIES
        categories.write_text(categories.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        self.assertNotEqual(check_contract.validate_run(self.space.root, self.space.run)["fingerprint"], base)


class ReconciliationTests(ContractTestCase):
    def test_records_with_cross_record_findings_are_left_out(self) -> None:
        self.space.write(assets=ASSETS + "A4;EU-A-CIU;1000;EUR;Y\n",
                         flows=FLOWS + "F5;OUTFLOW;EU-O-RETAIL;7;EUR;;EU-A-L1-CASH;\n")
        report = check_contract.validate_run(self.space.root, self.space.run)
        assets, flows = report["reconciliation"]["assets"], report["reconciliation"]["flows"]
        self.assertEqual((assets["records"], assets["records_with_findings"]), (4, 1))
        self.assertEqual(assets["market_value_total"], "120.75")
        self.assertEqual((flows["records"], flows["records_with_findings"]), (5, 1))
        self.assertEqual(flows["amount_by_direction"]["OUTFLOW"], "1055")

    def test_totals_are_exact_whatever_the_scales(self) -> None:
        self.assertEqual(check_contract.exact_sum(["999999999999999", "0.00000000000001"]),
                         "999999999999999.00000000000001")
        self.assertEqual(check_contract.exact_sum(["0.1"] * 3), "0.3")
        self.assertEqual(check_contract.exact_sum([]), "0")
        self.space.write(assets=ASSETS.splitlines()[0] + "\nA1;EU-A-L1-CASH;999999999999999;EUR;Y\n"
                                                         "A2;EU-A-L1-CASH;0.00000000000001;EUR;Y\n")
        report = check_contract.validate_run(self.space.root, self.space.run)
        self.assertEqual(report["reconciliation"]["assets"]["market_value_total"], "999999999999999.00000000000001")


class FileTests(ContractTestCase):
    def test_missing_file_and_empty_file(self) -> None:
        (self.space.run / "flows.csv").unlink()
        self.space.write(assets="")
        self.assertEqual(self.space.findings(), [["LCR-EMPTY", "assets", 0, ""],
                                                 ["LCR-FILE-MISSING", "flows", 0, ""]])

    def test_encoding_and_nul(self) -> None:
        (self.space.run / "assets.csv").write_bytes(b"asset_id\n\xff\n")
        self.space.write(flows="flow_id\x00\n")
        self.assertEqual(self.space.findings(), [["LCR-ENCODING", "assets", 0, ""],
                                                 ["LCR-ENCODING", "flows", 0, ""]])

    def test_header_findings(self) -> None:
        header = "asset_id;category;market_value;original_currency;requirements_met;extra;asset_id\n"
        self.space.write(assets=header.replace("market_value;", ""))
        # Findings are sorted by file, record, line and column.
        self.assertEqual(self.space.findings(), [["LCR-HEADER-DUPLICATE", "assets", 0, "asset_id"],
                                                 ["LCR-HEADER-UNKNOWN", "assets", 0, "extra"],
                                                 ["LCR-HEADER-MISSING", "assets", 0, "market_value"]])

    def test_comma_delimited_file(self) -> None:
        self.space.write(assets=ASSETS.replace(";", ","))
        self.assertEqual(self.space.findings(), [["LCR-DELIMITER", "assets", 0, ""]])

    def test_field_count_and_syntax(self) -> None:
        self.space.write(assets=ASSETS + "A9;EU-A-L1-CASH\n", flows=FLOWS + 'F9;"OUT\n')
        self.assertEqual(self.space.findings(), [["LCR-FIELD-COUNT", "assets", 4, ""],
                                                 ["LCR-SYNTAX", "flows", 0, ""]])

    def test_size_limits(self) -> None:
        contract = self.space.root / check_contract.CONTRACT
        data = json.loads(contract.read_text(encoding="utf-8"))
        data["format"]["max_records"] = 2
        contract.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(self.space.findings(), [["LCR-TOO-LARGE", "assets", 0, ""],
                                                 ["LCR-TOO-LARGE", "flows", 0, ""]])


class FieldTests(ContractTestCase):
    def assets_with(self, *rows: str) -> list[list[Any]]:
        header = ASSETS.splitlines()[0]
        self.space.write(assets="\n".join([header, *rows]) + "\n")
        return self.space.findings()

    def test_required_blank_record_and_formula(self) -> None:
        self.assertEqual(self.assets_with(";;;;", "A1;;5;EUR;Y", "=1+1;EU-A-L1-CASH;5;EUR;Y"),
                         [["LCR-BLANK-RECORD", "assets", 1, ""], ["LCR-REQUIRED", "assets", 2, "category"],
                          ["LCR-FORMULA", "assets", 3, "asset_id"]])

    def test_numbers(self) -> None:
        rows = ["A1;EU-A-L1-CASH;NaN;EUR;Y", "A2;EU-A-L1-CASH;-inf;EUR;Y", "A3;EU-A-L1-CASH;1,5;EUR;Y",
                "A4;EU-A-L1-CASH;1e3;EUR;Y", "A5;EU-A-L1-CASH;1234567890123456;EUR;Y",
                "A6;EU-A-L1-CASH;-1;EUR;Y", "A7;EU-A-L1-CASH;0.000000000000001;EUR;Y"]
        self.assertEqual(self.assets_with(*rows),
                         [["LCR-NON-FINITE", "assets", 1, "market_value"],
                          ["LCR-NON-FINITE", "assets", 2, "market_value"],
                          ["LCR-TYPE", "assets", 3, "market_value"], ["LCR-TYPE", "assets", 4, "market_value"],
                          ["LCR-PRECISION", "assets", 5, "market_value"],
                          ["LCR-RANGE", "assets", 6, "market_value"]])

    def test_allowed_values_currency_and_duplicate_key(self) -> None:
        self.assertEqual(self.assets_with("A1;EU-A-L1-CASH;1;eur;Y", "A2;EU-A-L1-CASH;1;EUR;yes",
                                          "a2;EU-A-L1-CASH;1;EUR;Y"),
                         [["LCR-TYPE", "assets", 1, "original_currency"],
                          ["LCR-ALLOWED", "assets", 2, "requirements_met"],
                          ["LCR-DUPLICATE-KEY", "assets", 3, "asset_id"]])

    def test_a_trailing_newline_never_passes_a_pattern(self) -> None:
        # Python's $ also matches before a final newline; a quoted field may hold one.
        rows = ['"A1\n";EU-A-L1-CASH;5;EUR;Y', "A1;EU-A-L1-CASH;5;EUR;Y",
                'A2;EU-A-L1-CASH;"5\n";EUR;Y', 'A3;EU-A-L1-CASH;5;"EUR\n";Y']
        self.assertEqual(self.assets_with(*rows),
                         [["LCR-TYPE", "assets", 1, "asset_id"], ["LCR-TYPE", "assets", 3, "market_value"],
                          ["LCR-TYPE", "assets", 4, "original_currency"]])
        header = FLOWS.splitlines()[0]
        self.space.write(assets=ASSETS, flows=header + '\nF1;INFLOW;EU-I-LOANS;1;EUR;"2026-07-10\n";;\n')
        self.assertEqual(self.space.findings(), [["LCR-TYPE", "flows", 1, "maturity_date"]])

    def test_dates(self) -> None:
        header = FLOWS.splitlines()[0]
        rows = ["F1;INFLOW;EU-I-LOANS;1;EUR;2026-02-30;;", "F2;INFLOW;EU-I-LOANS;1;EUR;30/06/2026;;",
                "F3;INFLOW;EU-I-LOANS;1;EUR;2300-01-01;;"]
        self.space.write(flows="\n".join([header, *rows]) + "\n")
        self.assertEqual(self.space.findings(), [["LCR-TYPE", "flows", 1, "maturity_date"],
                                                 ["LCR-TYPE", "flows", 2, "maturity_date"],
                                                 ["LCR-RANGE", "flows", 3, "maturity_date"]])


class RunTests(ContractTestCase):
    def test_run_record_count(self) -> None:
        self.space.write(run=RUN + RUN.splitlines()[1].replace("R1", "R2") + "\n")
        self.assertEqual(self.space.findings(), [["LCR-RECORD-COUNT", "run", 0, ""]])

    def test_parameter_set_register_version_and_synthetic_flag(self) -> None:
        self.space.write(run=RUN.replace("EU-LCR-DA-2022-07-08;1", "BASEL-LCR-2019-12-15;2").replace(";Y\n", ";N\n"))
        self.assertEqual(self.space.findings(), [["LCR-ALLOWED", "run", 1, "synthetic"]])
        self.space.write(run=RUN.replace("EU-LCR-DA-2022-07-08;1", "BASEL-LCR-2019-12-15;2"))
        self.assertEqual(self.space.findings(), [["LCR-PARAMETER-SET", "run", 1, "parameter_set"],
                                                 ["LCR-REGISTER-VERSION", "run", 1, "source_register_version"]])

    def test_an_overlong_integer_is_out_of_range_without_conversion(self) -> None:
        # Python refuses to convert a decimal string of more than 4,300 digits to int.
        self.space.write(run=RUN.replace("EU-LCR-DA-2022-07-08;1", "EU-LCR-DA-2022-07-08;" + "9" * 4301))
        self.assertEqual(self.space.findings(), [["LCR-RANGE", "run", 1, "source_register_version"]])

    def test_invalid_run_skips_rules_against_the_run(self) -> None:
        self.space.write(run=RUN.replace(";EU;", ";XX;"),
                         assets=ASSETS + "A9;NO-SUCH-CATEGORY;1;EUR;Y\n")
        self.assertEqual(self.space.findings(), [["LCR-ALLOWED", "run", 1, "profile"]])


class CategoryTests(ContractTestCase):
    def test_unknown_excluded_and_other_profile_categories(self) -> None:
        self.space.write(assets=ASSETS + "A4;EU-A-CIU;1;EUR;Y\nA5;BASEL-A-L1-CASH;1;EUR;Y\n",
                         flows=FLOWS + "F5;OUTFLOW;EU-O-INTRAGROUP;1;EUR;;;\nF6;INFLOW;EU-O-RETAIL;1;EUR;2026-07-01;;\n")
        self.assertEqual(self.space.findings(), [["LCR-OUT-OF-SCOPE", "assets", 4, "category"],
                                                 ["LCR-CATEGORY-UNKNOWN", "assets", 5, "category"],
                                                 ["LCR-OUT-OF-SCOPE", "flows", 5, "category"],
                                                 ["LCR-CATEGORY-UNKNOWN", "flows", 6, "category"]])

    def test_collateral_netting_set_and_maturity(self) -> None:
        rows = ["G1;OUTFLOW;EU-O-SECURED;1;EUR;2026-07-01;;", "G2;OUTFLOW;EU-O-RETAIL;1;EUR;;EU-A-L1-CASH;",
                "G3;OUTFLOW;EU-O-SECURED;1;EUR;2026-07-01;EU-A-CIU;", "G4;OUTFLOW;EU-O-RETAIL;1;EUR;;;NS-1",
                "G5;INFLOW;EU-I-LOANS;1;EUR;;;", "G6;OUTFLOW;EU-O-RETAIL;1;EUR;2026-06-29;;",
                "G7;OUTFLOW;EU-O-SECURED;1;EUR;2026-07-01;EU-A-L1-CASH;", "G8;OUTFLOW;EU-O-SWAP;1;EUR;2026-07-01;;",
                "G9;OUTFLOW;EU-O-SWAP;1;EUR;2026-07-01;EU-A-L1-CASH;", "G10;OUTFLOW;EU-O-SWAP;1;EUR;2026-07-01;EU-A-CIU;"]
        header = FLOWS.splitlines()[0]
        self.space.write(flows="\n".join([header, *rows]) + "\n")
        self.assertEqual(self.space.findings(), [["LCR-COLLATERAL", "flows", 1, "collateral_category"],
                                                 ["LCR-COLLATERAL", "flows", 2, "collateral_category"],
                                                 ["LCR-COLLATERAL", "flows", 3, "collateral_category"],
                                                 ["LCR-NETTING-SET", "flows", 4, "netting_set_id"],
                                                 ["LCR-MATURITY", "flows", 5, "maturity_date"],
                                                 ["LCR-MATURITY", "flows", 6, "maturity_date"],
                                                 ["LCR-COLLATERAL", "flows", 7, "collateral_category"],
                                                 ["LCR-COLLATERAL", "flows", 10, "collateral_category"]])


class MainTests(unittest.TestCase):
    def test_repository_fixtures_match_expected(self) -> None:
        self.assertEqual(check_contract.check_fixtures(ROOT), [])


class CategoryFileTests(unittest.TestCase):
    def test_level_2b_secured_flows_allow_every_asset_their_point_names(self) -> None:
        # Art. 28(3)(g) and Art. 32(3)(b)(vii) cover the Level 2B assets of Art. 12(1)(b), (c) and (f).
        categories = check_contract.load_json(ROOT / check_contract.CATEGORIES)
        eu = categories["profiles"]["EU"]
        assets = sorted(a["code"] for a in eu["assets"]
                        if a["locator"] in ("Art. 12(1)(b)", "Art. 12(1)(c)", "Art. 12(1)(f)"))
        self.assertEqual(len(assets), 3)
        flows = [f for f in eu["outflows"] + eu["inflows"]
                 if f["locator"] in ("Art. 28(3)(g)", "Art. 32(3)(b)(vii)")]
        self.assertEqual(len(flows), 2)
        for flow in flows:
            self.assertEqual(sorted(flow["collateral"]["allowed"]), assets, flow["code"])


if __name__ == "__main__":
    unittest.main()
