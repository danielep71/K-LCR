"""Tests of the workbook builder and the LibreOffice smoke test that need no LibreOffice.

They cover reading the exported VBA, the change to a macro-enabled package and
the comparison helpers. Building the workbook and running its VBA need
LibreOffice and are not part of the repository checks.
"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

import build_xlsm
import run_lo_test

ROOT = Path(__file__).resolve().parents[1]
CONTENT_TYPES = ('<Types><Default Extension="xml" ContentType="application/xml"/>'
                 f'<Override PartName="/xl/workbook.xml" ContentType="{build_xlsm.MAIN_TYPE}"/></Types>')
RELS = '<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>'


class SourceTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.scratch = Path(directory.name)

    def write(self, name: str, text: str) -> Path:
        path = self.scratch / name
        path.write_bytes(text.encode("cp1252"))
        return path

    def test_a_standard_module_loses_only_its_attribute_lines(self) -> None:
        path = self.write("M_A.bas", 'Attribute VB_Name = "M_A"\r\nOption Explicit\r\n\r\nSub X()\r\nEnd Sub\r\n')
        self.assertEqual(build_xlsm.source_body(path), ("M_A", "Option Explicit\n\nSub X()\nEnd Sub\n"))

    def test_a_document_module_loses_its_class_header(self) -> None:
        text = ('VERSION 1.0 CLASS\r\nBEGIN\r\n  MultiUse = -1  \'True\r\nEND\r\n'
                'Attribute VB_Name = "shHome"\r\nAttribute VB_Base = "0{00020820-0000-0000-C000-000000000046}"\r\n'
                'Option Explicit\r\n')
        self.assertEqual(build_xlsm.source_body(self.write("shHome.cls", text)), ("shHome", "Option Explicit\n"))

    def test_a_module_without_a_name_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            build_xlsm.source_body(self.write("M_B.bas", "Option Explicit\r\n"))

    def test_every_tracked_component_has_a_name_and_option_explicit(self) -> None:
        components = build_xlsm.modules(mode="development") + build_xlsm.documents()
        self.assertTrue(components)
        for path in components:
            with self.subTest(path=path.name):
                name, body = build_xlsm.source_body(path)
                self.assertEqual(name, path.stem)
                self.assertIn("Option Explicit", body)

    def test_the_components_are_those_of_the_manifest(self) -> None:
        data = build_xlsm.manifest()
        for mode in build_xlsm.MODES:
            with self.subTest(mode=mode):
                listed = [path.relative_to(ROOT).as_posix() for path in build_xlsm.modules(mode=mode)]
                self.assertEqual(listed, data["configurations"][mode]["modules"])
        self.assertEqual([path.relative_to(ROOT).as_posix() for path in build_xlsm.documents()],
                         data["document_modules"])

    def test_the_development_workbook_holds_every_test_and_production_none(self) -> None:
        folders = {mode: {path.parent.relative_to(ROOT).parts[0] for path in build_xlsm.modules(mode=mode)}
                   for mode in build_xlsm.MODES}
        self.assertEqual(folders, {"development": {"src", "tests"}, "production": {"src"}})

    def test_an_unknown_workbook_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            build_xlsm.modules(mode="staging")


class PackageTests(unittest.TestCase):
    def test_the_content_types_become_macro_enabled(self) -> None:
        text = build_xlsm.macro_enabled("[Content_Types].xml", CONTENT_TYPES.encode()).decode()
        self.assertIn(build_xlsm.MACRO_TYPE, text)
        self.assertNotIn(build_xlsm.MAIN_TYPE, text)
        self.assertEqual(text.count('Extension="bin"'), 1)

    def test_the_workbook_relationships_gain_the_vba_project(self) -> None:
        text = build_xlsm.macro_enabled("xl/_rels/workbook.xml.rels", RELS.encode()).decode()
        self.assertIn('Target="vbaProject.bin"', text)
        self.assertTrue(text.endswith("</Relationships>"))

    def test_other_parts_are_copied_unchanged(self) -> None:
        self.assertEqual(build_xlsm.macro_enabled("xl/styles.xml", b"<styleSheet/>"), b"<styleSheet/>")

    def test_inject_copies_the_template_and_adds_the_project(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            template, output = Path(scratch) / "t.xlsx", Path(scratch) / "out" / "w.xlsm"
            with zipfile.ZipFile(template, "w") as z:
                z.writestr("[Content_Types].xml", CONTENT_TYPES)
                z.writestr("xl/_rels/workbook.xml.rels", RELS)
                z.writestr("xl/styles.xml", "<styleSheet/>")
            build_xlsm.inject(template, b"VBA", output)
            with zipfile.ZipFile(output) as z:
                self.assertEqual(z.namelist(), ["[Content_Types].xml", "xl/_rels/workbook.xml.rels",
                                                "xl/styles.xml", "xl/vbaProject.bin"])
                self.assertEqual(z.read("xl/vbaProject.bin"), b"VBA")

    def test_the_workbook_is_written_under_test_results(self) -> None:
        self.assertEqual(build_xlsm.OUTPUT.parent, ROOT / "test-results")
        self.assertEqual(run_lo_test.SNAPSHOT.parent, ROOT / "test-results")


class ComparisonTests(unittest.TestCase):
    def test_close_allows_a_relative_difference_of_one_millionth(self) -> None:
        self.assertTrue(run_lo_test.close(1_000_000.5, 1_000_000.0))
        self.assertFalse(run_lo_test.close(1_000_002.0, 1_000_000.0))

    def test_close_refuses_a_blank_cell(self) -> None:
        self.assertFalse(run_lo_test.close(None, 0.0))

    def test_the_outcome_counts_failures(self) -> None:
        outcome = run_lo_test.Outcome()
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            outcome.expect("passes", True)
            outcome.expect("fails", False, "detail")
        self.assertEqual(outcome.failures, ["fails"])
        self.assertEqual(printed.getvalue(), "PASS passes\nFAIL fails  detail\n")
        self.assertEqual(outcome.summary(), "FAIL: 2 expectation(s), 1 failure(s)")


if __name__ == "__main__":
    unittest.main()
