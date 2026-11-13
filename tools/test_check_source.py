"""Tests of the prototype's source check (tools/check_source.py)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import check_source

GOOD = ('Attribute VB_Name = "CORE_Good"\r\n'
        "    Option Explicit\r\n"
        "    Option Private Module\r\n")


class Tree:
    """A temporary root with the folders the check reads."""

    def __init__(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)

    def write(self, relative: str, text: str, encoding: str = "cp1252") -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode(encoding))

    def close(self) -> None:
        self.directory.cleanup()


class CheckSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = Tree()
        self.addCleanup(self.tree.close)

    def findings(self, relative: str, text: str) -> list[str]:
        self.tree.write(relative, text)
        return check_source.check(self.tree.root)

    def test_a_clean_component_has_no_finding(self) -> None:
        self.assertEqual(self.findings("src/core/CORE_Good.bas", GOOD), [])

    def test_the_repository_source_passes(self) -> None:
        self.assertEqual(check_source.check(), [])

    def test_a_name_that_differs_from_the_file_is_found(self) -> None:
        self.assertEqual(self.findings("src/core/CORE_Other.bas", GOOD),
                         ["src/core/CORE_Other.bas: VB_Name does not match the file name"])

    def test_a_missing_option_explicit_is_found(self) -> None:
        text = GOOD.replace("    Option Explicit\r\n", "")
        self.assertEqual(self.findings("src/core/CORE_Good.bas", text),
                         ["src/core/CORE_Good.bas: no Option Explicit"])

    def test_the_core_and_the_tests_need_option_private_module(self) -> None:
        text = GOOD.replace("    Option Private Module\r\n", "").replace("CORE_Good", "TEST_Good")
        self.assertEqual(self.findings("tests/modules/TEST_Good.bas", text),
                         ["tests/modules/TEST_Good.bas: no Option Private Module"])

    def test_a_workbook_module_needs_no_option_private_module(self) -> None:
        text = GOOD.replace("    Option Private Module\r\n", "").replace("CORE_Good", "M_Main")
        self.assertEqual(self.findings("src/workbook/M_Main.bas", text), [])

    def test_a_tab_trailing_space_and_a_long_line_are_found(self) -> None:
        text = GOOD + "\tTabbed\r\n" + "Trailing \r\n" + "x" * 121 + "\r\n"
        self.assertEqual(self.findings("src/core/CORE_Good.bas", text), [
            "src/core/CORE_Good.bas:4: tab",
            "src/core/CORE_Good.bas:5: trailing whitespace",
            "src/core/CORE_Good.bas:6: 121 columns",
        ])

    def test_a_non_ascii_byte_is_found(self) -> None:
        text = GOOD + "'café\r\n"
        findings = self.findings("src/core/CORE_Good.bas", text)
        self.assertEqual(len(findings), 1)
        self.assertIn("non-ASCII byte", findings[0])

    def test_main_exits_with_one_when_a_finding_exists(self) -> None:
        self.tree.write("src/core/CORE_Other.bas", GOOD)
        findings = check_source.check(self.tree.root)
        self.assertEqual(len(findings), 1)


if __name__ == "__main__":
    unittest.main()
