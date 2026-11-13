"""Tests for the issue triage rules (tools/check_issues.py)."""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import check_issues
import check_workflows
from check_issues import Issue

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "example-org/sample-project"
BLOCKED_LABEL = check_issues.BLOCKED
PLANNING = "## Planning\n\n- Target end date: 2026-11-13 (Europe/Rome)\n\n"
READY = PLANNING + "## Dependencies and blocking status\n\n**Ready to start**: none.\n"
DUE = "2026-11-20"


def issue(number: int, *labels: str, state: str = "open", body: str = READY,
          assignees: tuple[str, ...] = ("triage-person",), milestone: str | None = "v0.1.0",
          milestone_state: str = "open", milestone_due: str | None = DUE) -> Issue:
    return Issue(number, state, labels or ("P3",), assignees, milestone, body,
                 milestone_state, milestone_due)


def dated(value: str) -> str:
    """A ready issue body whose Planning list states the given target end date."""
    return READY.replace("2026-11-13 (Europe/Rome)", value)


def blocked_by(*numbers: int, heading: str = "## Dependencies and blocking status") -> str:
    lines = "\n".join(f"- #{n} — prerequisite" for n in numbers)
    return f"## Objective\n\nx\n\n{PLANNING}{heading}\n\n**blocked**:\n\n{lines}\n\n## Tracking\n\n#99\n"


def rules(issues: list[Issue], states: dict[int, str] | None = None,
          pulls: frozenset[int] = frozenset()) -> list[tuple[int, str]]:
    known = states if states is not None else {i.number: i.state for i in issues}
    return [(f.number, f.rule)
            for f in check_issues.audit(issues, known, REPOSITORY, pulls=pulls, assignee="triage-person")]


class MetadataTests(unittest.TestCase):
    def test_compliant_issue_has_no_findings(self) -> None:
        self.assertEqual(rules([issue(1)]), [])

    def test_assignee_priority_and_milestone_are_required(self) -> None:
        self.assertEqual(rules([issue(1, assignees=())]), [(1, "assignee")])
        self.assertEqual(rules([issue(1, "documentation")]), [(1, "priority")])
        self.assertEqual(rules([issue(1, "P2", "P3")]), [(1, "priority")])
        self.assertEqual(rules([issue(1, milestone=None)]), [(1, "milestone")])

    def test_p1_is_reserved_for_bugs(self) -> None:
        self.assertEqual(rules([issue(1, "P1", "documentation")]), [(1, "p1-reserved")])
        self.assertEqual(rules([issue(1, "P1", "bug")]), [])

    def test_closed_issues_are_not_audited(self) -> None:
        self.assertEqual(rules([issue(1, "documentation", state="closed", assignees=())]), [])

    def test_unknown_labels_are_reported_against_the_catalogue(self) -> None:
        findings = check_issues.audit([issue(1, "P3", "ready")], {1: "open"}, REPOSITORY,
                                      catalogue={"P3"}, assignee="triage-person")
        self.assertEqual([(f.number, f.rule) for f in findings], [(1, "catalogue")])


FORM = "### 🗓️ Target end date (Europe/Rome)\n\n{}\n\n### 🔗 Dependencies and blocking status\n\nNone\n"


class TargetDateTests(unittest.TestCase):
    def test_planning_line_form_field_and_bold_label_are_read(self) -> None:
        bold = "**Target end date:** 2026-11-13\n\n" + READY.replace(PLANNING, "")
        for body in (READY, FORM.format("2026-11-13"), bold, dated("2026-11-13")):
            with self.subTest(body=body):
                self.assertEqual(rules([issue(1, body=body)]), [])

    def test_crlf_bodies_are_read(self) -> None:
        item = {"number": 1, "state": "open", "labels": [{"name": "P3"}],
                "assignees": [{"login": "triage-person"}],
                "milestone": {"title": "v0.1.0", "state": "open", "due_on": "2026-11-20T00:00:00Z"},
                "body": FORM.format("2026-11-13").replace("\n", "\r\n")}
        parsed = check_issues.issue_from_api(item)
        self.assertNotIn("\r", parsed.body)
        self.assertEqual(rules([parsed]), [])
        self.assertEqual(check_issues.target_end_dates("- Target end date: 2026-11-13\r\n"),
                         ["2026-11-13"])

    def test_missing_target_date(self) -> None:
        self.assertEqual(rules([issue(1, body=READY.replace(PLANNING, ""))]), [(1, "target-date")])

    def test_empty_form_field_is_not_a_date(self) -> None:
        self.assertEqual(rules([issue(1, body=FORM.format("_No response_"))]), [(1, "target-date")])
        heading_only = "### 🗓️ Target end date\n\n### 🔗 Dependencies\n\nNone\n"
        self.assertEqual(rules([issue(1, body=heading_only)]), [(1, "target-date")])

    def test_invalid_dates_are_reported(self) -> None:
        for value in ("2026/11/13", "13-11-2026", "2026-11-13 CET", "2026-11-13 (UTC)",
                      "2026-02-30", "2026-13-01", "next week", ""):
            with self.subTest(value=value):
                self.assertEqual(rules([issue(1, body=dated(value))]), [(1, "target-date")])

    def test_planning_line_takes_precedence_over_the_form_even_when_invalid(self) -> None:
        changed = "- Target end date: 2026-11-16 (Europe/Rome)\n\n" + FORM.format("2026-11-13")
        self.assertEqual(check_issues.target_end_dates(changed), ["2026-11-16"])
        self.assertEqual(rules([issue(1, body=changed)]), [])
        invalid = "- Target end date: soon\n\n" + FORM.format("2026-11-13")
        self.assertEqual(rules([issue(1, body=invalid)]), [(1, "target-date")])

    def test_same_date_written_two_ways_is_not_a_conflict(self) -> None:
        # The form answer omits the zone; the Planning line triage adds states it.
        both = dated("2026-11-13") + "- Target end date: 2026-11-13\n" + FORM.format("2026-11-13")
        self.assertEqual(rules([issue(1, body=both)]), [])

    def test_different_planning_dates_are_reported(self) -> None:
        conflicting = dated("2026-11-13") + "\n- Target end date: 2026-11-14\n"
        self.assertEqual(rules([issue(1, body=conflicting)]), [(1, "target-date")])

    def test_target_date_must_be_earlier_than_the_milestone_due_date(self) -> None:
        self.assertEqual(rules([issue(1, body=dated("2026-11-19"))]), [])
        self.assertEqual(rules([issue(1, body=dated(DUE))]), [(1, "milestone-due")])
        self.assertEqual(rules([issue(1, body=dated("2026-11-21"))]), [(1, "milestone-due")])

    def test_milestone_without_due_date_is_reported(self) -> None:
        self.assertEqual(rules([issue(1, milestone_due=None)]), [(1, "milestone-due")])

    def test_closed_milestone_is_reported(self) -> None:
        self.assertEqual(rules([issue(1, milestone_state="closed")]), [(1, "milestone")])

    def test_no_milestone_reports_only_the_missing_milestone(self) -> None:
        self.assertEqual(rules([issue(1, milestone=None, body=dated("2026-12-31"))]),
                         [(1, "milestone")])

    def test_api_milestone_state_and_due_date_are_read(self) -> None:
        item = {"number": 1, "state": "open", "labels": [], "assignees": [], "body": None,
                "milestone": {"title": "v0.1.0", "state": "closed", "due_on": "2026-11-20T00:00:00Z"}}
        parsed = check_issues.issue_from_api(item)
        self.assertEqual((parsed.milestone_state, parsed.milestone_due), ("closed", DUE))
        item["milestone"] = {"title": "v0.1.0", "state": "open", "due_on": None}
        self.assertIsNone(check_issues.issue_from_api(item).milestone_due)


class DependencyTests(unittest.TestCase):
    def test_blocked_by_an_open_prerequisite(self) -> None:
        self.assertEqual(rules([issue(2, "P3", BLOCKED_LABEL, body=blocked_by(1)), issue(1)]), [])

    def test_blocked_with_only_closed_prerequisites_must_be_unblocked(self) -> None:
        closed = issue(1, state="closed")
        self.assertEqual(rules([issue(2, "P3", BLOCKED_LABEL, body=blocked_by(1)), closed]),
                         [(2, "blocked")])

    def test_open_prerequisite_requires_blocked(self) -> None:
        self.assertEqual(rules([issue(2, "P3", body=blocked_by(1)), issue(1)]), [(2, "blocked")])

    def test_external_condition_counts_as_a_blocker(self) -> None:
        body = PLANNING + "### 🔗 Dependencies and blocking status\n\nExternal condition: Excel host access\n"
        self.assertEqual(rules([issue(2, "P3", BLOCKED_LABEL, body=body)]), [])
        self.assertEqual(rules([issue(2, "P3", body=body)]), [(2, "blocked")])

    def test_references_outside_the_section_are_ignored(self) -> None:
        # blocked_by() also mentions #99 under Tracking; it must not count.
        self.assertEqual(rules([issue(2, "P3", BLOCKED_LABEL, body=blocked_by(1)), issue(1)],
                               {1: "open", 2: "open"}), [])

    def test_issue_urls_and_form_headings_are_recognised(self) -> None:
        body = (PLANNING + "### 🔗 Dependencies and blocking status\n\n"
                f"- https://github.com/{REPOSITORY}/issues/1\n")
        self.assertEqual(rules([issue(2, "P3", BLOCKED_LABEL, body=body), issue(1)]), [])

    def test_missing_section_and_unknown_reference(self) -> None:
        self.assertEqual(rules([issue(1, body=PLANNING + "## Objective\n\nx\n")]), [(1, "dependencies")])
        self.assertEqual(rules([issue(2, "P3", BLOCKED_LABEL, body=blocked_by(7))]),
                         [(2, "dependencies"), (2, "blocked")])

    def test_self_reference_is_ignored(self) -> None:
        self.assertEqual(rules([issue(2, "P3", body=blocked_by(2))]), [])

    def test_named_pull_request_is_a_reference_not_a_prerequisite(self) -> None:
        body = PLANNING + "## Dependencies and blocking status\n\nNone. #1 was delivered in #22.\n"
        closed = issue(1, state="closed")
        self.assertEqual(rules([issue(2, "P3", body=body), closed], pulls=frozenset({22})), [])
        # A pull request never justifies blocked, and unknown numbers are still reported.
        self.assertEqual(rules([issue(2, "P3", BLOCKED_LABEL, body=blocked_by(22, 7))],
                               pulls=frozenset({22})),
                         [(2, "dependencies"), (2, "blocked")])



class ConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # The Dependabot rules read .github/dependabot.yml with PyYAML.
        if check_workflows.load_yaml() is None:
            if os.environ.get("GITHUB_ACTIONS"):
                raise RuntimeError("PyYAML is required on GitHub Actions "
                                   "(tools/requirements-quality-ci.txt)")
            raise unittest.SkipTest("PyYAML is not installed; skipped locally only")

    def test_repository_configuration_passes(self) -> None:
        self.assertEqual(check_issues.config_findings(ROOT), [])

    def test_unsupported_overlays_are_rejected_instead_of_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / ".github/scripts", root / ".github/scripts")
            manifest = json.loads((ROOT / ".github/labels.json").read_text())
            manifest["overlays"] = {"selected": [{"name": "extra"}]}
            (root / ".github/labels.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "root must contain exactly"):
                check_issues.catalogue_labels(root)

    def test_assignee_comes_from_configuration_not_repository_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            forms = root / ".github/ISSUE_TEMPLATE"
            forms.mkdir(parents=True)
            (forms / "bug.yml").write_text('assignees: [triage-person]\n')
            self.assertEqual(check_issues.configured_assignee(root), "triage-person")
            (forms / "bug.yml").write_text('assignees: []\n')
            with self.assertRaises(ValueError):
                check_issues.configured_assignee(root)

    @staticmethod
    def copy_configuration(root: Path) -> None:
        """The files config_findings reads, copied from the repository."""
        for folder in (".github/scripts", ".github/ISSUE_TEMPLATE"):
            shutil.copytree(ROOT / folder, root / folder)
        for name in (".github/labels.json", ".github/dependabot.yml", "docs/GOVERNANCE.md"):
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / name, root / name)

    def test_every_form_needs_the_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_configuration(root)
            form = root / ".github/ISSUE_TEMPLATE/documentation.yml"
            text = form.read_text(encoding="utf-8")
            self.assertIn("id: target_end_date", text)
            form.write_text(text.replace("id: target_end_date", "id: target"), encoding="utf-8")
            self.assertEqual(check_issues.config_findings(root),
                             ["documentation.yml has no target_end_date field"])

    def test_label_guide_explains_every_catalogue_label_once(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_configuration(root)
            guide = root / "docs/GOVERNANCE.md"
            text = guide.read_text(encoding="utf-8")
            row = next(line for line in text.splitlines() if line.startswith("| `wontfix` |"))
            guide.write_text(text.replace(row + "\n", ""), encoding="utf-8")
            self.assertIn("docs/GOVERNANCE.md must explain label 'wontfix' exactly once in the label tables "
                          "of Issues, found 0", check_issues.config_findings(root))
            guide.write_text(text.replace(row, row + "\n" + row), encoding="utf-8")
            self.assertIn("docs/GOVERNANCE.md must explain label 'wontfix' exactly once in the label tables "
                          "of Issues, found 2", check_issues.config_findings(root))
            guide.write_text(text.replace(row, row + "\n| `stale` | Not a label. |"), encoding="utf-8")
            self.assertIn("docs/GOVERNANCE.md explains label 'stale', which is not in the catalogue",
                          check_issues.config_findings(root))

    def test_documented_labels_reads_only_the_label_tables_of_issues(self) -> None:
        text = ("## Branches\n\n| Label | Use |\n| --- | --- |\n| `main` | x |\n\n"
                "## 🗂️ Issues\n\n| Priority | Use |\n| --- | --- |\n| `P1` | x |\n\nText `bug`.\n\n"
                "| Other | Use |\n| --- | --- |\n| `ci` | x |\n\n| Label | Use |\n| --- | --- |\n| `bug` | x |\n\n"
                "## Releases\n\n| Label | Use |\n| --- | --- |\n| `release` | x |\n")
        self.assertEqual(check_issues.documented_labels(text), ["P1", "bug"])

    def test_dependabot_labels_and_assignees_are_checked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_configuration(root)
            self.assertEqual(check_issues.config_findings(root), [])
            config = root / ".github/dependabot.yml"
            text = config.read_text(encoding="utf-8")
            config.write_text(text.replace("      - ci\n", "      - no-such-label\n", 1), encoding="utf-8")
            self.assertIn(".github/dependabot.yml sets unknown label 'no-such-label'",
                          check_issues.config_findings(root))
            config.write_text(text.replace("      - danielep71\n", "      - someone-else\n", 1), encoding="utf-8")
            self.assertIn(".github/dependabot.yml assigns 'someone-else', not 'danielep71'",
                          check_issues.config_findings(root))
            config.write_text(text.replace("    labels:\n      - ci\n      - P3\n",
                                           "    labels: [no-such-label] # custom labels\n", 1), encoding="utf-8")
            self.assertIn(".github/dependabot.yml sets unknown label 'no-such-label'",
                          check_issues.config_findings(root))

    def test_dependabot_must_assign_the_person_in_every_update(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_configuration(root)
            config = root / ".github/dependabot.yml"
            text = config.read_text(encoding="utf-8")
            updates = text.count("package-ecosystem:")
            expected = (f".github/dependabot.yml must assign 'danielep71' in each of its {updates} "
                        f"update entries, found {updates - 1}")
            config.write_text(text.replace("    assignees:\n      - danielep71\n", "", 1), encoding="utf-8")
            self.assertIn(expected, check_issues.config_findings(root))
            config.write_text(text.replace("    assignees:\n      - danielep71\n", "    assignees: []\n", 1),
                              encoding="utf-8")
            self.assertIn(expected, check_issues.config_findings(root))

    def test_dependabot_update_that_is_not_a_mapping_assigns_nobody(self) -> None:
        findings = check_issues.dependabot_findings(
            "updates:\n  - just-a-string\n  - assignees: [triage-person]\n", {"P3"}, "triage-person")
        self.assertEqual(findings, [".github/dependabot.yml must assign 'triage-person' in each of its 2 "
                                    "update entries, found 1"])

    def test_dependabot_empty_labels_and_two_assignees(self) -> None:
        text = ("updates:\n"
                "  - labels:\n    assignees: [triage-person]\n"
                "  - labels: [P3]\n    assignees: [triage-person, someone-else]\n")
        self.assertEqual(check_issues.dependabot_findings(text, {"P3"}, "triage-person"),
                         [".github/dependabot.yml assigns 'someone-else', not 'triage-person'",
                          ".github/dependabot.yml must assign 'triage-person' in each of its 2 "
                          "update entries, found 1"])

    def test_dependabot_flow_style_entries_are_read(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_configuration(root)
            config = root / ".github/dependabot.yml"
            config.write_text("version: 2\nupdates:\n"
                              "  - {package-ecosystem: pip, directory: /tools, labels: [no-such-label],"
                              " assignees: [danielep71]}\n", encoding="utf-8")
            self.assertEqual(check_issues.config_findings(root),
                             [".github/dependabot.yml sets unknown label 'no-such-label'"])

    def test_dependabot_needs_pyyaml(self) -> None:
        with unittest.mock.patch.object(check_workflows, "load_yaml", return_value=None):
            findings = check_issues.dependabot_findings("updates: []\n", {"P3"}, "triage-person")
        self.assertEqual(findings, [".github/dependabot.yml cannot be read: PyYAML is not installed "
                                    "(tools/requirements-quality-ci.txt)"])

    def test_dependabot_duplicate_key_and_missing_updates(self) -> None:
        self.assertIn("is not valid YAML", check_issues.dependabot_findings(
            "updates:\n  - labels: [ci]\n    labels: [P3]\n", {"ci", "P3"}, "triage-person")[0])
        self.assertEqual(check_issues.dependabot_findings("version: 2\n", {"P3"}, "triage-person"),
                         [".github/dependabot.yml has no updates list"])

    def test_flow_list(self) -> None:
        text = 'name: x\nlabels: ["bug", "P2"]\nassignees: [triage-person]\n'
        self.assertEqual(check_issues.flow_list(text, "labels"), ["bug", "P2"])
        self.assertEqual(check_issues.flow_list(text, "assignees"), ["triage-person"])
        self.assertEqual(check_issues.flow_list(text, "title"), [])


class MainTests(unittest.TestCase):
    def test_input_mode_reports_and_exits_nonzero_on_findings(self) -> None:
        items = [
            {"number": 1, "state": "open", "labels": [{"name": "P3"}],
             "assignees": [{"login": "triage-person"}], "milestone": None,
             "body": READY + "Delivered in #2, a pull request.\n"},
            {"number": 2, "state": "open", "labels": [], "assignees": [],
             "milestone": None, "body": READY, "pull_request": {}},
        ]
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "issues.json"
            source.write_text(json.dumps(items), encoding="utf-8")
            output = Path(directory) / "report.json"
            with contextlib.redirect_stdout(io.StringIO()) as stdout, \
                    unittest.mock.patch.object(check_issues, "configured_assignee",
                                               return_value="triage-person"):
                code = check_issues.main(["--root", str(ROOT), "--input", str(source),
                                          "--output", str(output), "--repo-name", REPOSITORY])
            self.assertEqual(code, 1)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "fail")
            self.assertEqual([f["rule"] for f in report["findings"]], ["milestone"])
            self.assertIn("open issues audited: 1", stdout.getvalue())

    def test_offline_mode_requires_explicit_repository(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            check_issues.parse_args(["--input", "issues.json"])
        self.assertEqual(error.exception.code, 2)

    def test_live_mode_requires_a_token(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), \
                unittest.mock.patch.dict("os.environ", {"GITHUB_TOKEN": ""}):
            self.assertEqual(check_issues.main(["--repository", REPOSITORY]), 2)


if __name__ == "__main__":
    unittest.main()
