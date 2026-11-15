"""Positive and negative evidence fixtures for check_excel_run.py.

Each fixture is an evidence folder built in a temporary directory: the
development workbook's components at HEAD as the VBE exports them (CRLF),
candidate.txt, the four logs, verification.txt, environment.txt,
host-state.txt and host.txt. The logs are written here from the run outcomes
of docs/methodology/TEST_HARNESS.md, not derived by the checker and not
recorded in Excel.
"""

from __future__ import annotations

import contextlib
import io
import os
import subprocess
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path

import check_excel_run
from check_excel_run import EXAMPLES, components, git, git_blob, read_suite

ROOT = Path(__file__).resolve().parents[1]
COMMIT = git(ROOT, "rev-parse", "HEAD").decode().strip()
CASES = {
    "exact-comparison": ["half-of-one", "same-text", "positive"],
    "tolerance-comparison": ["inside-absolute", "inside-relative", "near-zero", "outside-is-rejected"],
    "expected-error": ["negative-input", "valid-input"],
}
INJECTED = "exact-comparison/half-of-one"
INJECTED_DETAIL = "expected=0.5; actual=0.75"
COMPLETENESS = "expected cases=3, assertions=9; observed cases=2, assertions=7"
SIMULATED = "simulated: the host state changed during the run"
RECOVERY = "; action=check the host state, then run TEST_LCR_Harness.ResetTests"
RESULTS = {
    "NORMAL": "RESULT=PASS; suite=examples; operation=PASS; completeness=COMPLETE; cases=3; "
              "assertions=9; failures=0; cleanup=PASS; recovery=NONE",
    "INJECTED_FAILURE": "RESULT=FAIL; suite=examples; operation=FAIL; completeness=COMPLETE; "
                        "cases=3; assertions=9; failures=1; cleanup=PASS; recovery=NONE",
    "SKIPPED_CASE": "RESULT=FAIL; suite=examples; operation=PASS; completeness=INCOMPLETE; "
                    "cases=2; assertions=7; failures=1; cleanup=PASS; recovery=NONE",
    "CLEANUP_PROBLEM": "RESULT=FAIL; suite=examples; operation=PASS; completeness=COMPLETE; "
                       "cases=3; assertions=9; failures=0; cleanup=FAIL; recovery=REQUIRED",
}
ERRORS = {"NORMAL": "0", "INJECTED_FAILURE": "-2147217439", "SKIPPED_CASE": "-2147217439",
          "CLEANUP_PROBLEM": "-2147217439"}
ENVIRONMENT = ("host=Microsoft Excel\nversion=16.0\nbuild=19127\nos=Windows (64-bit) NT 10.00\n"
               "office=64-bit\nruntime=VBA7\ndecimal=.\ncountry=39\n")
STATE = "calculation=-4105; alerts=True; events=True; screen=True; workbooks=1"
HOST = ("windows=Windows 11 Pro, version 24H2, OS build 26100.4061\n"
        "references=Visual Basic For Applications; Microsoft Excel 16.0 Object Library; "
        "OLE Automation; Microsoft Office 16.0 Object Library\n"
        "compile=PASS\n")


def run_log(mode: str) -> str:
    """The log the harness writes for one run of the example suite, as the VBA
    recorder saves it (LF between records, CRLF after the last)."""
    lines = [f"RUN=examples; mode={mode}; expected_cases=3; expected_assertions=9"]
    for case, names in CASES.items():
        if mode == "SKIPPED_CASE" and case == "expected-error":
            continue
        lines.append(f"CASE={case}")
        for name in names:
            if mode == "INJECTED_FAILURE" and f"{case}/{name}" == INJECTED:
                lines += [f"ASSERT={INJECTED}; status=FAIL; {INJECTED_DETAIL}",
                          f"FAILURE={INJECTED}; {INJECTED_DETAIL}"]
            else:
                lines.append(f"ASSERT={case}/{name}; status=PASS")
    skipped = mode == "SKIPPED_CASE"
    if skipped:
        lines.append(f"FAILURE=harness.completeness; {COMPLETENESS}")
    failures = 1 if mode in ("INJECTED_FAILURE", "SKIPPED_CASE") else 0
    lines += [f"CASES={2 if skipped else 3}; expected=3",
              f"ASSERTIONS={7 if skipped else 9}; expected=9",
              f"FAILURES={failures}; errors=0"]
    if mode == "INJECTED_FAILURE":
        lines.append(f"PRIMARY_FAILURE={INJECTED}; {INJECTED_DETAIL}")
    if skipped:
        lines.append(f"PRIMARY_FAILURE=harness.completeness; {COMPLETENESS}")
    if mode == "CLEANUP_PROBLEM":
        lines += [f"CLEANUP=FAIL; detail={SIMULATED}", f"RECOVERY=REQUIRED; reason={SIMULATED}{RECOVERY}"]
    else:
        lines += ["CLEANUP=PASS; detail=no change reported", "RECOVERY=NONE"]
    lines.append(RESULTS[mode])
    return "\n".join(lines) + "\r\n"


def verification() -> str:
    lines = [f"MODE={mode}; required_error={ERRORS[mode]}; error={ERRORS[mode]}; "
             f"required={result}; actual={result}" for mode, result in RESULTS.items()]
    return "\n".join([*lines, "VERIFICATION=PASS; modes=4; deviations=0"]) + "\r\n"


def build(folder: Path) -> None:
    """A complete evidence folder for HEAD, files written in run order."""
    exported = folder / "exported"
    exported.mkdir(parents=True)
    for name, (data, _) in components(ROOT, COMMIT).items():
        (exported / name).write_bytes(data.replace(b"\n", b"\r\n"))
    manifest = git_blob(git(ROOT, "show", f"{COMMIT}:{check_excel_run.MANIFEST}"))
    write(folder / "candidate.txt", f"commit={COMMIT}\nworktree=clean\nmanifest={manifest}\n")
    for mode, filename in check_excel_run.LOGS.items():
        write(folder / filename, run_log(mode))
    write(folder / "verification.txt", verification())
    write(folder / "environment.txt", ENVIRONMENT)
    write(folder / "host-state.txt", f"before={STATE}\nafter={STATE}\ncleanup=PASS\r\n")
    write(folder / "host.txt", HOST)


def write(path: Path, text: str) -> None:
    path.write_bytes(text.encode("ascii"))


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_bytes().decode("ascii")
    if old not in text:
        raise AssertionError(f"{old!r} not in {path.name}")
    mtime = path.stat().st_mtime
    write(path, text.replace(old, new, 1))
    os.utime(path, (mtime, mtime))


class EvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.folder = Path(directory.name) / "excel-run"
        build(self.folder)

    def verdict(self, change: Callable[[Path], None] | None = None) -> check_excel_run.Evidence:
        if change is not None:
            change(self.folder)
        return check_excel_run.check(ROOT, COMMIT, self.folder)

    def assert_fails(self, change: Callable[[Path], None], expected: str) -> None:
        evidence = self.verdict(change)
        self.assertEqual(check_excel_run.verdict(evidence), "FAIL")
        self.assertTrue(any(expected in finding for finding in evidence.findings),
                        evidence.findings)

    def test_complete_evidence_passes(self) -> None:
        evidence = self.verdict()
        self.assertEqual(evidence.findings, [])
        self.assertEqual(check_excel_run.verdict(evidence), "PASS")
        self.assertEqual(evidence.modes["NORMAL"], "PASS (RESULT=PASS, as required)")
        self.assertEqual(evidence.modes["CLEANUP_PROBLEM"], "PASS (RESULT=FAIL, as required)")
        self.assertIn(Path(EXAMPLES).name, evidence.hashes)

    def test_no_output_of_a_run_is_not_run(self) -> None:
        for name in (*check_excel_run.RUN_OUTPUTS, "host.txt"):
            (self.folder / name).unlink()
        evidence = self.verdict()
        self.assertEqual(check_excel_run.verdict(evidence), "NOT_RUN")
        self.assertEqual(set(evidence.modes.values()), {"NOT_RUN (no log)"})

    def test_a_missing_folder_is_not_run(self) -> None:
        evidence = check_excel_run.check(ROOT, COMMIT, self.folder / "absent")
        self.assertEqual(check_excel_run.verdict(evidence), "NOT_RUN")

    def test_a_missing_candidate_fails(self) -> None:
        self.assert_fails(lambda folder: (folder / "candidate.txt").unlink(), "candidate.txt: missing")

    def test_evidence_of_another_commit_is_stale(self) -> None:
        self.assert_fails(lambda folder: edit(folder / "candidate.txt", COMMIT, "0" * 40),
                          "stale or mismatched evidence")

    def test_a_dirty_working_tree_fails(self) -> None:
        self.assert_fails(lambda folder: edit(folder / "candidate.txt", "worktree=clean",
                                              "worktree=2 changed file(s)"), "local changes")

    def test_another_manifest_fails(self) -> None:
        self.assert_fails(lambda folder: edit(folder / "candidate.txt", "manifest=", "manifest=0"),
                          "manifest=0")

    def test_a_changed_module_fails(self) -> None:
        self.assert_fails(lambda folder: edit(folder / "exported" / "TEST_LCR_Harness.bas",
                                              "Option Explicit", "Option Base 1"),
                          "TEST_LCR_Harness.bas: differs")

    def test_a_missing_or_extra_module_fails(self) -> None:
        def change(folder: Path) -> None:
            (folder / "exported" / "CORE_Engine.bas").unlink()
            write(folder / "exported" / "Module1.bas", 'Attribute VB_Name = "Module1"\r\n')
        evidence = self.verdict(change)
        self.assertTrue(any("CORE_Engine.bas: not exported" in item for item in evidence.findings))
        self.assertTrue(any("Module1.bas: not a component" in item for item in evidence.findings))

    def test_a_document_module_is_compared_by_its_code(self) -> None:
        self.assertEqual(self.verdict(lambda folder: edit(
            folder / "exported" / "shHome.cls", "Attribute VB_Customizable = True\r\n", "")).findings, [])
        self.assert_fails(lambda folder: edit(folder / "exported" / "shHome.cls", "Option Explicit",
                                              "Option Base 1"), "shHome.cls: differs")

    def test_a_missing_log_is_not_run_and_fails(self) -> None:
        evidence = self.verdict(lambda folder: (folder / "skipped.log").unlink())
        self.assertEqual(evidence.modes["SKIPPED_CASE"], "NOT_RUN (no log)")
        self.assertEqual(check_excel_run.verdict(evidence), "FAIL")

    def test_a_refused_start_is_not_run(self) -> None:
        refused = ("RECOVERY=REQUIRED; reason=run of examples still active (interrupted?)" + RECOVERY +
                   "\nRESULT=FAIL; suite=examples; operation=NOT_RUN; completeness=INCOMPLETE; "
                   "cases=0; assertions=0; failures=0; cleanup=NOT_RUN; recovery=REQUIRED\r\n")
        evidence = self.verdict(lambda folder: write(folder / "normal.log", refused))
        self.assertEqual(evidence.modes["NORMAL"], "NOT_RUN (start refused)")
        self.assertEqual(check_excel_run.verdict(evidence), "FAIL")

    def test_a_normal_run_that_fails_fails(self) -> None:
        def change(folder: Path) -> None:
            write(folder / "normal.log", run_log("INJECTED_FAILURE").replace(
                "mode=INJECTED_FAILURE", "mode=NORMAL"))
        evidence = self.verdict(change)
        self.assertEqual(evidence.modes["NORMAL"], "FAIL (did not end as required)")

    def test_an_injected_run_failing_another_assertion_fails(self) -> None:
        self.assert_fails(lambda folder: edit(
            folder / "injected.log", "ASSERT=exact-comparison/same-text; status=PASS",
            "ASSERT=exact-comparison/same-text; status=FAIL; expected='K-LCR'; actual='K'"),
            "same-text")

    def test_a_non_finite_number_fails(self) -> None:
        def change(folder: Path) -> None:
            path = folder / "injected.log"
            write(path, path.read_bytes().decode("ascii").replace("actual=0.75", "actual=1.#INF"))
        self.assert_fails(change, "actual=1.#INF is not a finite number")

    def test_inconsistent_counts_fail(self) -> None:
        self.assert_fails(lambda folder: edit(folder / "normal.log", "CASES=3; expected=3",
                                              "CASES=4; expected=3"), "inconsistent counts: CASES=4")

    def test_two_runs_in_one_log_fail(self) -> None:
        def change(folder: Path) -> None:
            write(folder / "normal.log", run_log("NORMAL") + run_log("NORMAL"))
        self.assert_fails(change, "after RESULT")

    def test_an_unreported_cleanup_problem_fails(self) -> None:
        self.assert_fails(lambda folder: write(folder / "cleanup.log", run_log("NORMAL").replace(
            "mode=NORMAL", "mode=CLEANUP_PROBLEM")), "cleanup.log")

    def test_a_verification_deviation_fails(self) -> None:
        self.assert_fails(lambda folder: edit(folder / "verification.txt", "deviations=0",
                                              "deviations=1"), "does not end with VERIFICATION=PASS")

    def test_an_unsupported_host_fails(self) -> None:
        self.assert_fails(lambda folder: edit(folder / "environment.txt", "office=64-bit",
                                              "office=32-bit"), "not the supported target: office")
        self.assert_fails(lambda folder: edit(folder / "environment.txt", "decimal=.\n", ""),
                          "no decimal")

    def test_a_changed_host_state_fails(self) -> None:
        self.assert_fails(lambda folder: edit(folder / "host-state.txt", "after=calculation=-4105",
                                              "after=calculation=-4135"), "host-state.txt")

    def test_the_host_record_is_checked(self) -> None:
        self.assert_fails(lambda folder: edit(folder / "host.txt", "compile=PASS",
                                              "compile=Variable not defined"), "compile=")
        self.assert_fails(lambda folder: edit(folder / "host.txt", "OLE Automation; ", ""),
                          "references must be exactly")
        self.assert_fails(lambda folder: (folder / "host.txt").unlink(), "host.txt: missing")

    def test_a_file_older_than_the_build_is_stale(self) -> None:
        def change(folder: Path) -> None:
            built = (folder / "candidate.txt").stat().st_mtime
            os.utime(folder / "normal.log", (built - 60, built - 60))
        self.assert_fails(change, "normal.log: older than candidate.txt")

    def test_a_path_in_the_evidence_fails(self) -> None:
        self.assert_fails(lambda folder: edit(folder / "host.txt", "compile=PASS",
                                              "compile=PASS\nnote=C:\\Users\\someone\\book.xlsm"),
                          "host.txt: holds a file path")


class SuiteTests(unittest.TestCase):
    def test_the_example_suite_is_read_from_the_commit(self) -> None:
        source = components(ROOT, COMMIT)[Path(EXAMPLES).name][0]
        suite = read_suite(source)
        self.assertEqual(suite.cases, list(CASES))
        self.assertEqual(suite.assertions, [f"{case}/{name}" for case, names in CASES.items()
                                            for name in names])
        self.assertEqual(suite.injected, [INJECTED])
        self.assertEqual(suite.skipped, ["expected-error/negative-input", "expected-error/valid-input",
                                         "expected-error"])
        self.assertEqual((suite.expected_cases, suite.expected_assertions), (3, 9))


class MainTests(unittest.TestCase):
    def run_main(self, *args: str) -> tuple[int, str]:
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            status = check_excel_run.main(list(args))
        return status, printed.getvalue()

    def test_exit_status_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            folder = Path(scratch) / "excel-run"
            status, printed = self.run_main(str(folder), "--commit", COMMIT)
            self.assertEqual(status, 2)
            self.assertIn("excel-run: NOT_RUN", printed)
            build(folder)
            status, printed = self.run_main(str(folder), "--commit", COMMIT)
            self.assertEqual(status, 0, printed)
            self.assertIn("excel-run: PASS", printed)
            self.assertIn(f"Built from: {COMMIT} (worktree=clean)", printed)
            (folder / "host.txt").unlink()
            status, printed = self.run_main(str(folder), "--commit", COMMIT)
            self.assertEqual(status, 1)
            self.assertIn("excel-run: FAIL", printed)

    def test_an_unknown_commit_cannot_be_checked(self) -> None:
        status, printed = self.run_main("folder", "--commit", "no-such-commit")
        self.assertEqual(status, 2)
        self.assertIn("not found", printed)

    def test_the_commit_is_resolved_with_git(self) -> None:
        resolved = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True,
                                  check=True, text=True).stdout.strip()
        self.assertEqual(resolved, COMMIT)


if __name__ == "__main__":
    unittest.main()
