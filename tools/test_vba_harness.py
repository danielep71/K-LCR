"""Static consistency of the neutral VBA test harness and its example suite (tests/unit/).

The harness runs only in Excel, and nothing here compiles or runs VBA. These
tests check what the source text can show without a host: that the example
suite's expected counts equal the cases and assertions it contains, that every
case runs once with a well-formed unique identifier, that the RESULT records
documented for each mode follow from those counts, that the harness touches no
host object, clock or file, and that every record it writes is documented.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import ClassVar

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tests/unit/TEST_LCR_Harness.bas"
EXAMPLES = ROOT / "tests/unit/TEST_LCR_Examples.bas"
GUIDE = ROOT / "docs/methodology/TEST_HARNESS.md"
CASE_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
# Names that would tie the neutral harness to a host, a file, the clock or chance.
HOST_NAMES = (
    "Application", "ThisWorkbook", "ActiveWorkbook", "Workbooks", "Worksheets", "Sheets",
    "Range", "Cells", "Environ", "Shell", "Kill", "Open", "FileSystemObject", "Timer",
    "Now", "Date", "Time", "Rnd", "Randomize", "DoEvents", "SendKeys",
)


def source(path: Path) -> str:
    """The text of a file: ASCII for VBA source, UTF-8 for the guide."""
    encoding = "ascii" if path.suffix == ".bas" else "utf-8"
    return path.read_text(encoding=encoding).replace("\r\n", "\n")


def strip_comment(line: str) -> str:
    """A line of VBA without its comment: an apostrophe outside a string starts one."""
    in_text = False
    for position, character in enumerate(line):
        if character == '"':
            in_text = not in_text
        elif character == "'" and not in_text:
            return line[:position].rstrip()
    return line.rstrip()


def code_lines(text: str) -> list[str]:
    """The lines of a module that are code: no blank line, no comment, no trailing comment."""
    return [code for code in (strip_comment(line) for line in text.split("\n")) if code.strip()]


def constant(text: str, name: str) -> int:
    match = re.search(rf"^\s*Private Const {name}\s+As Long = (\d+)\b", text, re.M)
    assert match, name
    return int(match.group(1))


def procedures(text: str) -> dict[str, str]:
    """Body of every Sub and Function, by name."""
    pattern = re.compile(r"^(?:Public|Private) (?:Sub|Function) (\w+)\(.*?^End (?:Sub|Function)$",
                         re.M | re.S)
    return {match.group(1): match.group(0) for match in pattern.finditer(text)}


class ModuleTests(unittest.TestCase):
    def test_each_module_is_explicit_private_and_named_after_its_file(self) -> None:
        for path in (HARNESS, EXAMPLES):
            with self.subTest(module=path.name):
                text = source(path)
                self.assertTrue(text.startswith(f'Attribute VB_Name = "{path.stem}"\n'))
                self.assertRegex(text, r"(?m)^    Option Explicit$")
                self.assertRegex(text, r"(?m)^    Option Private Module$")

    def test_modules_follow_the_naming_rule_of_the_house_style(self) -> None:
        for path in (HARNESS, EXAMPLES):
            self.assertRegex(path.stem, r"^TEST_LCR_[A-Za-z]+$")
            self.assertEqual(path.parent, ROOT / "tests/unit")

    def test_modules_are_ascii_with_four_space_indentation_and_no_trailing_space(self) -> None:
        for path in (HARNESS, EXAMPLES):
            for number, line in enumerate(source(path).split("\n"), 1):
                with self.subTest(module=path.name, line=number):
                    self.assertEqual(line, line.rstrip(), "trailing whitespace")
                    self.assertNotIn("\t", line)

    def test_the_harness_touches_no_host_object_file_clock_or_generator(self) -> None:
        for path in (HARNESS, EXAMPLES):
            code = "\n".join(code_lines(source(path)))
            for name in HOST_NAMES:
                with self.subTest(module=path.name, name=name):
                    self.assertIsNone(re.search(rf"\b{name}\b", code), name)

    def test_the_test_error_numbers_are_distinct(self) -> None:
        numbers = re.findall(r"Const (ERR_\w+)\s+As Long = (&H[0-9A-F]+)", source(HARNESS) + source(EXAMPLES))
        self.assertEqual(len(numbers), len({value for _, value in numbers}))
        self.assertEqual(len(numbers), len({name for name, _ in numbers}))


class ExampleSuiteTests(unittest.TestCase):
    text = source(EXAMPLES)
    bodies = procedures(text)
    cases: ClassVar[dict[str, str]] = {name: body for name, body in bodies.items() if name.startswith("Case")}

    def assertions(self, body: str) -> int:
        return len(re.findall(r"TEST_LCR_Harness\.Assert\w+", "\n".join(code_lines(body))))

    def test_expected_counts_equal_the_cases_and_assertions_of_the_source(self) -> None:
        self.assertEqual(constant(self.text, "EXPECTED_CASES"), len(self.cases))
        self.assertEqual(constant(self.text, "EXPECTED_ASSERTIONS"),
                         sum(self.assertions(body) for body in self.cases.values()))

    def test_each_case_states_its_assertions_and_the_count_is_right(self) -> None:
        for name, body in self.cases.items():
            with self.subTest(case=name):
                stated = re.search(r"(\d+) assertions?\.", body.split("End Sub")[0])
                self.assertIsNotNone(stated, "the contract states the count")
                assert stated is not None
                self.assertEqual(int(stated.group(1)), self.assertions(body))

    def test_the_runner_calls_every_case_once_in_order(self) -> None:
        runner = "\n".join(code_lines(self.bodies["RunSuite"]))
        called = re.findall(r"^\s+(Case\w+)$", runner, re.M)
        self.assertEqual(called, list(self.cases))

    def test_only_the_last_case_is_skipped_in_the_skipped_mode(self) -> None:
        runner = self.bodies["RunSuite"]
        guarded = re.search(r'If mMode <> "SKIPPED_CASE" Then\n\s+(Case\w+)\n\s+End If', runner)
        self.assertIsNotNone(guarded)
        assert guarded is not None
        self.assertEqual(guarded.group(1), list(self.cases)[-1])

    def test_each_case_begins_once_with_a_unique_identifier_and_records_its_error(self) -> None:
        identifiers = []
        for name, body in self.cases.items():
            begun = re.findall(r'TEST_LCR_Harness\.BeginCase "([^"]+)"', body)
            with self.subTest(case=name):
                self.assertEqual(len(begun), 1)
                self.assertRegex(begun[0], CASE_ID)
                self.assertIn("TEST_LCR_Harness.RecordCaseError", body)
            identifiers += begun
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_the_documented_result_of_each_mode_follows_from_the_counts(self) -> None:
        total = constant(self.text, "EXPECTED_ASSERTIONS")
        last = list(self.cases.values())[-1]
        skipped_assertions = total - self.assertions(last)
        cases = len(self.cases)
        head = "RESULT=%s; suite=examples; operation=%s; completeness=%s"
        expected = [
            (head % ("PASS", "PASS", "COMPLETE"), f"cases={cases}; assertions={total}; failures=0; cleanup=PASS; recovery=NONE"),
            (head % ("FAIL", "FAIL", "COMPLETE"), f"cases={cases}; assertions={total}; failures=1; cleanup=PASS; recovery=NONE"),
            (head % ("FAIL", "PASS", "INCOMPLETE"),
             f"cases={cases - 1}; assertions={skipped_assertions}; failures=1; cleanup=PASS; recovery=NONE"),
            (head % ("FAIL", "PASS", "COMPLETE"), f"cases={cases}; assertions={total}; failures=0; cleanup=FAIL; recovery=REQUIRED"),
        ]
        # Join the string literals that the source continues over several lines.
        joined = re.sub(r'"\s*&\s*_\n\s*"', "", self.bodies["VerifyExampleModes"])
        for first, rest in expected:
            with self.subTest(result=first):
                self.assertIn(f'"{first}; {rest}"', joined)

    def test_the_verification_acknowledges_recovery_only_after_its_own_simulated_run(self) -> None:
        body = "\n".join(code_lines(self.bodies["VerifyExampleModes"]))
        resets = [m.start() for m in re.finditer(r"TEST_LCR_Harness\.ResetTests", body)]
        self.assertEqual(len(resets), 1)
        guard = body.rfind("If Simulated Then", 0, resets[0])
        self.assertGreater(guard, 0, "the reset is guarded")
        self.assertNotIn("End If", body[guard:resets[0]])
        # The flag is set only for the simulated mode, and only when it ended as required.
        self.assertRegex(body, r'ElseIf CStr\(Modes\(i\)\) = "CLEANUP_PROBLEM" Then\n\s+Simulated = True')

    def test_the_documented_modes_are_the_modes_the_runner_knows(self) -> None:
        modes = re.search(r"Modes = Array\(([^)]*)\)", self.bodies["VerifyExampleModes"])
        assert modes is not None
        listed = re.findall(r'"([A-Z_]+)"', modes.group(1))
        self.assertEqual(listed, ["NORMAL", "INJECTED_FAILURE", "SKIPPED_CASE", "CLEANUP_PROBLEM"])
        guide = source(GUIDE)
        for mode in listed:
            self.assertIn(f"`{mode}`", guide, mode)


class HarnessLogTests(unittest.TestCase):
    text = source(HARNESS)
    guide = source(GUIDE)

    def test_every_record_the_harness_writes_is_documented(self) -> None:
        written = set(re.findall(r'Say "([A-Z_]+)=', self.text))
        written |= set(re.findall(r'"(RESULT)=', self.text))
        self.assertTrue(written, "the harness writes records")
        for key in sorted(written):
            with self.subTest(key=key):
                self.assertIn(f"`{key}=", self.guide)

    def test_result_is_the_last_record_the_harness_writes_for_a_run(self) -> None:
        end = procedures(self.text)["EndRun"]
        self.assertTrue(end.index("Say mLastResult") > end.index('Say "RECOVERY='))
        self.assertEqual(len(re.findall(r"Say mLastResult", end)), 1)

    def test_the_harness_writes_no_clock_machine_or_user(self) -> None:
        literals = "\n".join(re.findall(r'"([^"]*)"', "\n".join(code_lines(self.text))))
        for field in ("started", "ENVIRONMENT", "host=", "user=", "machine=", "path="):
            self.assertNotIn(field, literals, field)

    def test_the_public_surface_listed_in_the_header_exists(self) -> None:
        bodies = procedures(self.text)
        header = self.text.split("Option Explicit")[0]
        for name in ("BeginRun", "BeginCase", "RecordCaseError", "EndRun", "AssertEqualDouble",
                     "AssertNear", "AssertEqualText", "AssertTrue", "AssertRaised",
                     "WithinTolerance", "Say", "LogText", "LastResult", "ResetTests"):
            with self.subTest(name=name):
                self.assertIn(name, header)
                self.assertTrue(re.search(rf"Public (?:Sub|Function) {name}\(", self.text) or name in bodies)

    def test_the_guide_lists_both_modules(self) -> None:
        for path in (HARNESS, EXAMPLES):
            self.assertIn(f"tests/unit/{path.name}", self.guide)


if __name__ == "__main__":
    unittest.main()
