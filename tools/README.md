# 🧰 Repository tooling

`check.py` is the single entry point for the repository's checks. The same
command runs locally and in the `Repository integrity` workflow. It checks the
repository tooling, Python lint and types, the label and issue-form
configuration, the format of tracked text, the workflows, the contracts, the
registered test cases, the static VBA rules, the binary files and the
changelog. It never compiles or runs VBA in Excel and never validates an
LCR calculation.

## ▶️ Running the checks

Requirements: Git, Python 3.13, Node.js 22 and actionlint 1.7.12 on `PATH`,
plus the quality tools below. `check.py` itself needs only the standard
library. The setup is in [INSTALLATION.md](../INSTALLATION.md#developer-setup).

```sh
python tools/check.py --ci
```

| Mode | Behaviour |
| --- | --- |
| *(default)* | Runs every gate. A gate whose tool is missing is **NOT RUN** and fails the run. |
| `--allow-missing` | Reports missing tools as **NOT RUN** and exits 0 with status **INCOMPLETE**. An incomplete run is never a pass; use it only to diagnose a local setup. |
| `--ci` | Requires every tool and a clean checkout (no modified or untracked files). Used by the workflow. |

Exit code 0 means PASS (or INCOMPLETE with `--allow-missing`); 1 means a gate
failed, a tool was missing, or `--ci` found a dirty tree.

The checkers share one convention: 0 means no finding, 1 means at least one
finding, and 2 means the check could not run (an unreadable or invalid input
file, a script that timed out, or a missing optional tool locally). A check
that could not run is never a pass.

Reports go to the ignored `test-results/` directory:
`repository-integrity.json` and `repository-integrity.md` record the candidate
commit, the mode, whether the tree was dirty, each gate's result and the tool
versions; each gate also writes `<gate>.log`.

## ✅ Gates

| Gate | Checks |
| --- | --- |
| `tool-tests` | Unit tests of the tooling (`tools/test_*.py`): this runner's status, report and missing-tool rules, the issue-triage rules, the workflow invariants, the contract and case checkers, the binary-file, changelog and traffic-history rules, the VBA checks' valid and invalid fixtures (`test_check_vba.py`), the static consistency of the VBA test harness and its example suite (`test_vba_harness.py`: counts, identifiers, documented records, no host object), the prototype's Python model and source check (`test_lcr_spec.py`, `test_check_source.py`), and its build tools: a rebuild of the template equals the tracked file part by part, with fixed dates and no author (`test_build_template.py`, which needs openpyxl: skipped locally without it, run on GitHub Actions), and the parts of the workbook builder and the LibreOffice smoke test that need no LibreOffice (`test_build_xlsm.py`). |
| `labels-sync-self-test` | The label synchronizer's validation and reconciliation fixtures. |
| `labels-manifest` | `.github/labels.json` is a valid schema-2 catalogue: one `labels` list, no overlays. |
| `labels-drift-self-test` | The read-only drift detector's fixtures. |
| `issue-config` | The catalogue passes `labels-sync.mjs --mode validate`; the issue forms assign the person named in `bug.yml` and set exactly their default priority (bug `P2`, enhancement and documentation `P3`), use only catalogue labels and have the acceptance, validation, dependencies and target end date fields; blank issues are disabled; `blocked` is the only dependency status label; the label tables of the Issues section of `docs/GOVERNANCE.md` explain every catalogue label exactly once; every Dependabot update, read with PyYAML, uses only catalogue labels and assigns exactly the same person (`check_issues.py --check-config`). It needs PyYAML and Node.js: without PyYAML it fails on GitHub Actions and is NOT RUN locally, and without Node.js it is NOT RUN. |
| `format-fixtures` | The tracked-text checker's own fixtures: valid samples pass, malformed ones fail (`check_files.py --self-test`). |
| `tracked-text` | Every tracked text file, read from the Git index rather than the working tree: valid UTF-8, no NUL or CR byte, a final newline and no trailing white space (`check_files.py`). Markdown, Python, YAML, JSON, JavaScript modules (`.mjs`), TOML, CSV, plain text, HTML, CSS, SVG, XML, VBA exports and the Git/editor configuration files are covered; `LICENSE` and the byte-for-byte regulatory source copies in `docs/methodology/sources/` (not its README) are excluded. |
| `ruff` | Lint of `tools/` with the rules in `pyproject.toml`. |
| `ruff-complexity-probe` | The complexity ceiling is active: a synthetic complexity-15 function passes and one at 16 is rejected. |
| `mypy` | `mypy --strict` over `tools/`, tests included. |
| `mypy-strict-probe` | Strict mode is active: an annotated function passes and the same function without annotations is rejected. |
| `actionlint` | Syntax, expressions and shell scripts of every workflow. |
| `workflow-invariants` | The project rules for every workflow (`.yml` and `.yaml`) and Dependabot (`check_workflows.py`, PyYAML): every `uses:` pinned to a 40-character SHA; checkouts with `persist-credentials: false`; workflow-level `permissions` without write access; `timeout-minutes` on every job; write permissions only for `labels-sync.yml`/`reconcile` (issues), `pr-milestones.yml`/`reconcile` (pull-requests), `traffic-history.yml`/`collect` (contents) and `traffic-history.yml`/`alert` (issues); the `Repository integrity` job matches the required check in `docs/GOVERNANCE.md` and `docs/REPOSITORY_SETTINGS.md`, with no `if`, `strategy` or extra trigger filter; the label reconcile job keeps its exact condition (not a pull request and the default branch); `pr-milestones.yml` keeps its events, permissions, condition and single inline script; `traffic-history.yml` keeps its two jobs, the `analytics` environment and opt-in default-branch condition of `collect`, the App key in its two steps and the App token in the fetch step only, which runs no repository code, and an `alert` job with no environment or secret that reads the commit its collection wrote; Dependabot covers GitHub Actions (`/`) and pip (`/tools`) once each, sets no milestone and exactly `P3`. Without PyYAML it fails on GitHub Actions and is NOT RUN locally. `test_check_workflows.py` mutates each rule and runs the milestone script against a fake API. |
| `data-contract` | Every synthetic run in `tests/contract/` gives exactly the findings, and the passing runs exactly the reconciliation, recorded in `tests/contract/expected.json`; each run is validated twice and must give the same report (`check_contract.py --check-fixtures`). The input contract is [docs/methodology/DATA_CONTRACT.md](../docs/methodology/DATA_CONTRACT.md). |
| `test-cases` | Every registered case in `tests/cases/` follows [TEST_CASES.md](../docs/methodology/TEST_CASES.md): metadata, expected outputs, reference classes, tolerances and derivation scripts, which may import the standard library only. It executes the input-contract assertions and the derivation scripts, and reports the result figures as registered, not executed (`check_test_cases.py`). |
| `parameter-result-contract` | Every parameter-set and result example in `tests/parameters/` gives exactly the findings recorded in `tests/parameters/expected.json` (`check_parameters.py --check-fixtures`). The contract is [docs/methodology/PARAMETERS_AND_RESULTS.md](../docs/methodology/PARAMETERS_AND_RESULTS.md). |
| `vba-conditionals` | Every `#If` block of the tracked VBA components evaluates in each compilation environment (VBA6 Win32, VBA7 Win32, VBA7 Win64); every `Declare` reachable under VBA7 is `PtrSafe` and none reachable under VBA6 uses `PtrSafe` or `LongPtr` (`check_vba_conditionals.py`). |
| `vba-jumps` | Every jump target is a label of the same procedure, in each environment; jumps serve one error/cleanup handler: no `GoSub`, computed `On ... GoTo`, `On Error GoTo -1` or backward `GoTo` (`check_vba_jumps.py`). |
| `vba-dynamic` | No `Declare`, `CreateObject`, `GetObject`, `New` automation object, `CallByName`, `Run`, `Evaluate` or other dynamic call outside the host homes; there, each use needs a reviewed entry in `tools/vba-exceptions.json` (a `Declare` only in `src/host/excel/`, a `CreateObject` only with a literal ProgID), and stale entries fail (`check_vba_dynamic.py`). |
| `binaries` | Every tracked binary file, by `.gitattributes` or by a NUL byte anywhere in it, is a byte-preserved regulatory source under `docs/methodology/sources/`, a UserForm `.frx` beside its `.frm`, or listed in `.github/binary-allowlist.json` with its current SHA-256 and a reason; an allowlisted file whose content changed fails, and so does an Office package with macros or personal metadata (`check_binaries.py`). |
| `changelog` | `CHANGELOG.md` and `VERSION` follow the [date and version rules](../CHANGELOG.md#date-and-version-rules): headings, real dates, order, link references into this repository, no `VERSION` before the first dated release and the newest release afterwards; the changelog introduction and the *Current status* of [RELEASING.md](../RELEASING.md#current-status) agree on the release state, with no placeholder line; the README mentions no "Release Candidate" and holds no unchecked task item (it is not compared with the release state); a released section equals its content at its tag, and a shallow checkout fails once a release exists, which is why the workflow checks out the full history and tags (`check_changelog.py --repository danielep71/K-LCR`). It never tags or publishes. |

The label gates run on every pull request here, although the label workflows
run on a pull request only when it changes label files. Live label
reconciliation and drift detection stay in those workflows.

## 🗂️ Issue triage

`check_issues.py` applies the issue rules of
[docs/GOVERNANCE.md](../docs/GOVERNANCE.md#-issues) to every open issue and
reports findings; it never changes an issue. The `Issue triage` workflow runs
it on issue events with a read-only token. Pull requests are not audited, but
their numbers are loaded so that a dependency section may name one as a
reference; it never counts as a prerequisite. The token therefore needs
`pull-requests: read` as well: without it the issues API omits pull requests.

```sh
GITHUB_TOKEN=<token with issues:read and pull-requests:read> python tools/check_issues.py --repository danielep71/K-LCR
python tools/check_issues.py --input issues.json --repo-name danielep71/K-LCR   # issues exported as GitHub REST JSON
python tools/check_issues.py --check-config        # forms, catalogue, label guide and Dependabot
```

The target end date is read from the Planning lines `Target end date:
YYYY-MM-DD` (an optional ` (Europe/Rome)` may follow; a list marker and bold
are allowed). Only when there is none is it read from the first line under the
forms' "Target end date" heading. Every date read must be a real calendar date,
all must be the same date, and it must be earlier than the due date of the
issue's milestone. The due date is the date part of the
milestone's `due_on`, in UTC. A closed milestone and a milestone without a due
date are findings. A target end date that has already passed is not.

Exit code 0 means no findings, 1 means findings, 2 means the audit could not
run. Its rules are tested by `test_check_issues.py` in `tool-tests`.

## 📈 Traffic history

`traffic_history.py` keeps the repository's traffic beyond GitHub's 14-day
window, on the data-only `traffic-history` branch. The opt-in **Traffic
history** workflow runs it; operation, credentials and recovery are in
[docs/TRAFFIC.md](../docs/TRAFFIC.md). It reads only local files and needs no
token:

```sh
python tools/traffic_history.py init --data data
python tools/traffic_history.py merge --raw RAW --data data --collected-at 2026-11-05T06:17:00Z
python tools/traffic_history.py alert --data data --milestone-due 2026-11-20 --output alert.json
```

`init` creates missing history files with their headers; `merge` validates the
API responses and the stored files, then merges one collection idempotently
and rewrites the badge files; `alert` writes one alert issue when traffic
stands out. `test_traffic_history.py` covers the merge rules, refusals,
badges and alerts, and checks that an alert issue passes Issue triage.

## 🔧 Tool versions

| Tool | Version | Source |
| --- | --- | --- |
| Python | 3.13 | `actions/setup-python` |
| Node.js | 22 | `actions/setup-node` |
| Ruff, mypy, PyYAML, openpyxl, types-openpyxl | 0.17.3, 2.4.1, 6.0.3, 3.1.5, 3.1.5.20261017 | `tools/requirements-quality-ci.txt`, hash-locked for CPython 3.13 on Linux x86_64 |
| actionlint | 1.7.12 | Release archive verified by SHA-256 in the workflow |

Install the same quality tools locally, on CPython 3.13 and Linux x86_64:

```sh
python -m pip install --only-binary=:all: --require-hashes -r tools/requirements-quality-ci.txt
```

On another platform, install the same versions without the lock
(`pip install ruff==0.17.3 mypy==2.4.1 pyyaml==6.0.3 openpyxl==3.1.5 types-openpyxl==3.1.5.20261017`);
CI remains the reference run.
actionlint is available from its
[1.7.12 release](https://github.com/rhysd/actionlint/releases/tag/v1.7.12).

## ☁️ Continuous integration

`.github/workflows/repository-integrity.yml` runs `python tools/check.py --ci`
on every pull request into `main` or `release/**`, on every push to them and
on manual dispatch. It has no path filter, so its `Repository integrity` job
reports on every pull request and is the required check of both rulesets.

- The job checks out the exact commit under review without persisting
  credentials and verifies that `HEAD` is that commit. For a pull request this
  is GitHub's test merge of the head into the base.
- The token is read-only (`contents: read`); the job has no write permission,
  secret, approval or merge step.
- Every action is pinned to a full commit SHA.
- The Markdown report is added to the job summary, and `test-results/` is
  uploaded as the artifact `repository-integrity-<sha>-<run>-<attempt>`,
  **retained for 30 days**.
- Its only downloads are the pinned actions, the locked Python wheels and the
  actionlint archive.

## 📦 Dependency updates

`.github/dependabot.yml` proposes weekly updates to the pinned GitHub Actions
and, separately, to the hash-locked Ruff/mypy/PyYAML/openpyxl requirements
(`tools/requirements-quality-ci.txt`, releases at least 14 days old). Each
ecosystem's updates are grouped into one pull request against the active
release branch, with the `ci` and `P3` labels and danielep71 as assignee. Dependabot reads this file
from the default branch, `main`, so a change to it takes effect once it is
integrated into `main`. When a new release branch is opened, update its
`target-branch`.

Dependabot security updates ignore `target-branch`: their pull requests target
`main` and arrive without the `ci`/`P3` labels and the assignee above. I label
and assign them by hand during triage, review the final head myself and merge
into `main` only with my approval, then sync the release branch
([docs/GOVERNANCE.md](../docs/GOVERNANCE.md), Repository settings).

Nothing merges automatically. Before merging an update:

1. Read the release notes between the old and new versions of each action
   or package.
2. For an action, check that each new pin is a full SHA that the upstream tag
   points to. For a Python package, check that every new `--hash` matches the
   wheel published on PyPI and that the file still installs with
   `--only-binary=:all: --require-hashes`.
3. Wait for `Repository integrity` to pass on the pull request: it installs
   the updated requirements and runs Ruff and mypy, and actionlint checks the
   updated workflows.
4. Review the final diff and head SHA yourself: the automated code reviewer
   does not review bot-authored pull requests
   ([docs/GOVERNANCE.md](../docs/GOVERNANCE.md#-task-integration-and-review)).

Dependabot does not update the actionlint version or checksum in
`.github/workflows/repository-integrity.yml`. Update it by hand: choose a
release at least two weeks old and compare its SHA-256 with the release's
checksums file. Dependabot's pip updates list a hash for every published
wheel, not only the CPython 3.13 Linux x86_64 wheel this file pins. To keep
that format, update the Python requirements by hand: download the wheels for
CPython 3.13 on Linux x86_64 and compare every SHA-256 with PyPI.
