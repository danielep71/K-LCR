"""Valid and invalid fixtures for check_vba_manifest.py.

Each fixture is a throw-away Git repository (test_check_vba.repository) with
synthetic components and a tools/vba-projects.json; no workbook is involved.
"""

from __future__ import annotations

import contextlib
import io
import json
import unittest
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import check_vba_manifest
from test_check_vba import repository

ROOT = Path(__file__).resolve().parents[1]


def module(name: str) -> str:
    return f'Attribute VB_Name = "{name}"\nOption Explicit\n'


def document(name: str) -> str:
    return (f'VERSION 1.0 CLASS\nBEGIN\n  MultiUse = -1  \'True\nEND\nAttribute VB_Name = "{name}"\n'
            'Attribute VB_Base = "0{00020819-0000-0000-C000-000000000046}"\nOption Explicit\n')


FILES: dict[str, str | bytes] = {
    "src/core/CORE_Engine.bas": module("CORE_Engine"),
    "src/modules/LCR_Formulas.bas": module("LCR_Formulas"),
    "src/workbook/ThisWorkbook.cls": document("ThisWorkbook"),
    "tests/modules/TEST_Engine.bas": module("TEST_Engine"),
    "tests/unit/TEST_LCR_Harness.bas": module("TEST_LCR_Harness"),
}
PRODUCTION = ["src/core/CORE_Engine.bas", "src/modules/LCR_Formulas.bas"]
TESTS = ["tests/modules/TEST_Engine.bas", "tests/unit/TEST_LCR_Harness.bas"]


def manifest(**changes: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "schema_version": 1,
        "document_modules": ["src/workbook/ThisWorkbook.cls"],
        "configurations": {
            "production": {"modules": list(PRODUCTION)},
            "development": {"modules": [*PRODUCTION, *TESTS]},
        },
    }
    data.update(changes)
    return data


def findings(data: Any, files: Mapping[str, str | bytes] = FILES) -> list[str]:
    text = data if isinstance(data, str) else json.dumps(data)
    with repository({**files, check_vba_manifest.MANIFEST: text}) as root:
        return [str(finding) for finding in check_vba_manifest.check(root)[0]]


class ManifestTest(unittest.TestCase):
    def assertFinding(self, data: Any, text: str) -> None:
        found = findings(data)
        self.assertTrue(any(text in item for item in found), found)

    def test_valid_manifest_passes(self) -> None:
        self.assertEqual(findings(manifest()), [])

    def test_repository_manifest_passes(self) -> None:
        self.assertEqual(check_vba_manifest.check(ROOT)[0], [])

    def test_unreadable_or_wrong_schema(self) -> None:
        self.assertFinding("{", "not valid UTF-8 JSON")
        self.assertFinding(manifest(schema_version=2), "schema_version 1")
        self.assertFinding(manifest(configurations={"production": []}),
                           "production: needs a list of paths")

    def test_a_component_left_out_or_misplaced(self) -> None:
        data = manifest()
        data["configurations"]["development"]["modules"].remove("tests/unit/TEST_LCR_Harness.bas")
        self.assertFinding(data, "development: tests/unit/TEST_LCR_Harness.bas is missing")
        self.assertFinding(manifest(document_modules=[]),
                           "document_modules: src/workbook/ThisWorkbook.cls is missing")
        data = manifest()
        data["configurations"]["production"]["modules"].append("tests/modules/TEST_Engine.bas")
        self.assertFinding(data, "production: tests/modules/TEST_Engine.bas does not belong")

    def test_a_document_module_is_not_a_production_module(self) -> None:
        data = manifest()
        data["configurations"]["production"]["modules"] = sorted(
            [*PRODUCTION, "src/workbook/ThisWorkbook.cls"])
        self.assertFinding(data, "production: src/workbook/ThisWorkbook.cls does not belong")

    def test_untracked_paths_are_refused(self) -> None:
        data = manifest()
        data["configurations"]["production"]["modules"].append("src/core/CORE_Gone.bas")
        self.assertFinding(data, "production: src/core/CORE_Gone.bas does not belong")

    def test_order_and_duplicates(self) -> None:
        data = manifest()
        data["configurations"]["production"]["modules"].reverse()
        self.assertFinding(data, "production: paths must be in sorted order")
        data = manifest()
        data["configurations"]["production"]["modules"].insert(0, PRODUCTION[0])
        self.assertFinding(data, "production: a path is listed twice")

    def test_missing_manifest(self) -> None:
        with repository(FILES) as root:
            self.assertEqual([str(item) for item in check_vba_manifest.check(root)[0]],
                             ["tools/vba-projects.json: missing"])

    def test_main_reports_the_verdict(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(check_vba_manifest.main(["--root", str(ROOT)]), 0)
        self.assertIn("vba-manifest: PASS", output.getvalue())


if __name__ == "__main__":
    unittest.main()
