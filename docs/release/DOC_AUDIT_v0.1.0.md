# 📝 Documentation audit — v0.1.0

**Every document, comment and docstring · Compared with the implemented behaviour · Findings and their disposition**

This audit covers the documentation of `release/0.1.0` for *v0.1.0 - Repo
setup* (#22): every Markdown and HTML page, the comments of every workflow,
script and configuration file, and the docstrings and comments of every Python
tool. It started from `fc98b1756115cec0c8a873e7feb6a83edba2bf81` and covers
the tree of the pull request that adds this file, findings fixed. The merge
commit is recorded in the resolution of #22. A file changed after that commit
is audited again at the closeout (#23, [closeout template](CLOSEOUT.md)). The
file-level audit of provenance, licences and confidentiality is the
[file audit](FILE_AUDIT_v0.1.0.md) (#21).

## 🧭 Method

On 2026-11-05 I split the documentation into four groups and compared every
claim with the code, the workflows and the repository's state, never with
another document alone:

| Group | Files | Compared with |
| --- | --- | --- |
| Governance and root documents | `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `INSTALLATION.md`, `RELEASING.md`, `SECURITY.md`, `CHANGELOG.md`, `AGENTS.md`, `NOTICE.md`, `docs/*.md` except `TRAFFIC.md` and `VBA_HOUSE_STYLE.md`, the website, `docs/assets/`, `docs/release/`, the pull request template and the issue forms | `tools/check.py`, the Git history (`git hash-object`, `git log`), issue and milestone states, the integration of #141 |
| Methodology | `docs/methodology/`, `docs/methodology/sources/README.md`, `tests/derivations/` and the docstrings of `check_contract.py`, `check_parameters.py` and `check_test_cases.py` | The validators run on their fixtures and on variants of them, `sha256sum` of the stored sources, `categories.json` counts |
| Tooling | `tools/README.md`, `docs/VBA_HOUSE_STYLE.md`, `pyproject.toml`, `tools/requirements-quality-ci.txt`, `tools/vba-exceptions.json` and the docstrings and comments of every other tool and test | The `GATES` of `check.py`, `--help` of every tool, the 267 tool tests, the wheel hashes on PyPI |
| Workflows and configuration | `.github/workflows/`, `.github/scripts/`, `.github/dependabot.yml`, `.github/labels.json`, `docs/TRAFFIC.md`, `.gitignore`, `.gitattributes`, `.editorconfig` | The YAML, the label scripts' self-tests, `tools/traffic_history.py` and the `traffic-history` branch |

In every group I looked for claims that contradict the code or the current
state, stale "planned" or "not yet" text for delivered work, incorrect host or
support claims, obsolete commands, validation that was never executed, broken
links and anchors, inconsistent terms, paths, dates or provenance,
third-person references to me, and other repositories named outside
`LICENSE` and `NOTICE.md`. I checked each finding again before fixing it.

I also repeated the *Verified setup* of [INSTALLATION.md](../../INSTALLATION.md)
on a fresh clone of `fc98b17`, because the recorded run predated the
`binaries` gate: all 21 gates pass.

## 📋 Findings and disposition

### Governance and root documents

| # | Finding | Disposition |
| ---: | --- | --- |
| G1 | `docs/GOVERNANCE.md` and the pull request template said that every re-run of the automated review needs my approval; I gave a standing permission on 2026-11-05 | Fixed: both describe the standing permission, without naming the tool |
| G2 | `SECURITY.md` said no App credential is configured, and dated the settings evidence 2026-10-29 | Fixed: credentials in `analytics` since 2026-11-05 (#17); evidence of 2026-11-05 (#16) |
| G3 | `NOTICE.md` recorded `docs/REPOSITORY_SETTINGS.md` and `tools/check_changelog.py` as the same blob as their source; #112 and the shallow-checkout fix of #20 changed them (`da3785c`, `85a45ea`) | Fixed: adopted, then adapted; the file audit rows say *Adapted* |
| G4 | `NOTICE.md`: the pull request template has a changelog item, the workflows also use `actions/create-github-app-token`, the #21 audit is done, and "owner approval" was third person | Fixed |
| G5 | `docs/DECISIONS.md` and `docs/GOVERNANCE.md` named me in the third person | Fixed: first person |
| G6 | `docs/DECISIONS.md` called #13 to #15 remaining setup decisions; they moved to v0.2.0 | Fixed: *Remaining decisions (v0.2.0 - Host execution)* |
| G7 | `docs/GOVERNANCE.md` left out the `External condition:` rule for `blocked` that Issue triage applies | Fixed, also in `issue-triage.yml` and in the `blocked` description of `labels.json` |
| G8 | `docs/GOVERNANCE.md` spoke of "these future gates" after every listed item was delivered | Fixed: the closeout certification |
| G9 | `docs/REPOSITORY_STRUCTURE.md`: perimeter and currency still "to resolve" (A01, A02 decide them); methodology "later, contracts"; the layout table lacked `tests/contract/`, `tests/parameters/`, `tests/cases/` and `tests/derivations/` | Fixed |
| G10 | `docs/SOURCE_CONTROL.md` left out the UserForm `.frx` that the `binaries` gate accepts | Fixed |
| G11 | The website still called sources, contracts and tolerances setup work, linked closed #9 and #11, and listed an old scope of Repository integrity; `README.md` also left out binary files and the changelog | Fixed: current scope; links to the methodology and the validation plan. The site changes when this reaches `main` |
| G12 | `docs/WEBSITE.md` asked to record deployments in the closed #63 | Fixed: in the pull request that changes the site |
| G13 | `INSTALLATION.md`: the probes need Ruff and mypy too; the *Verified setup* recorded 20 gates at `a8784cb` | Fixed: probes listed; setup repeated at `fc98b17`, 21 gates PASS, first attempt's HTTP 504 recorded; `--allow-missing` and `--ci` exclude each other |

### Methodology

| # | Finding | Disposition |
| ---: | --- | --- |
| M1 | `docs/methodology/README.md`, `DATA_CONTRACT.md`, `PARAMETERS_AND_RESULTS.md` and `APPLICABILITY.md` named #10 and #11 as future work on contracts and independent fixtures | Fixed: delivered; independent cases are planned in `VALIDATION_PLAN.md` |
| M2 | `DATA_CONTRACT.md` listed the findings in an order that is not the validator's, said the run-dependent checks need a valid `run.csv`, and did not document the `text` type behind `LCR-LENGTH` | Fixed: the validator's order; the exact condition; `text` documented, unused by version 1 |
| M3 | `DATA_CONTRACT.md` did not say that `integer` and `amount` forbid a sign and leading zeros and need digits on both sides of `.` | Fixed |
| M4 | `data-contract.json` left out the carriage return outside a quoted field from `LCR-SYNTAX` | Fixed |
| M5 | `DATA_CONTRACT.md` said every A03 to A06 exclusion is a listed category; EU A04 and A05, Basel A05 and the significant-currency LCR of A02 have no input field or category | Fixed: stated; no input can claim them |
| M6 | `PARAMETERS_AND_RESULTS.md` and `parameter-result-contract.json` asked for a factor for every in-scope category; exclusion categories have none | Fixed |
| M7 | `VALIDATION_PLAN.md` said every `contract` value is executed; `result_status` is registered only. Its EU-only rows did not say so | Fixed |
| M8 | `TEST_CASES.md`: `input_findings` holds distinct codes; the domain rule is not part of today's comparison; the checker's `CASE-*` codes were undocumented | Fixed |
| M9 | `SOURCES.md` called every stored file a byte-for-byte copy with its hash in the retrieval record; the SRC-01 file is an extract with its hash in `sources/README.md` | Fixed |
| M10 | `categories.json` places Art. 12(1)(f) under A03, which names Art. 13 to 16 | Open: my decision, #148 |
| M11 | `categories.json` notes cite CRR articles that are not registered locators of `SRC-01` | Open: #148 |

### Tooling

| # | Finding | Disposition |
| ---: | --- | --- |
| T1 | `tools/vba_lexer.py` named a `vba-source` gate that does not exist | Fixed: no gate rejects non-ASCII VBA yet; the rule is checked in review |
| T2 | `check_vba_conditionals.py` said `check_vba_dynamic.py` shares its reachable-source model | Fixed |
| T3 | `docs/VBA_HOUSE_STYLE.md` and `check_vba_jumps.py` limited labels; the check limits jump targets | Fixed |
| T4 | `docs/VBA_HOUSE_STYLE.md` showed an exception entry that read as a recorded review, citing #42, a pull request | Fixed: the file lists none; the entry is marked illustrative |
| T5 | `docs/VBA_HOUSE_STYLE.md` sent field schemas and tolerances to the closed #10 and #11 | Fixed: links to the contract and the test-case rules |
| T6 | `pyproject.toml` and `requirements-quality-ci.txt` understated the PyYAML use | Fixed: `workflow-invariants` and `issue-config` |
| T7 | Docstrings of `check_changelog.py`, `check_workflows.py` (`*.yaml`), `check_issues.py --check-config` and `test_check_changelog.py` described less or other than the code does | Fixed |
| T8 | `tools/README.md` claimed that the tests mutate each workflow rule; the Dependabot directory, ruleset branch line and reconcile-job rules had no test | Fixed: three tests added, each failing when its rule is removed |
| T9 | `tools/README.md`: the tracked-text check skipped HTML, CSS, SVG and XML without saying so; the summary and the tool-tests row were incomplete; the `vba-dynamic` row omitted two limits | Fixed: those suffixes are now checked (every tracked file passes); rows completed |

### Workflows and configuration

| # | Finding | Disposition |
| ---: | --- | --- |
| W1 | `.gitattributes` and `.editorconfig` said no source copy is committed, and called every stored file a copy | Fixed |
| W2 | `.gitattributes` sent host encoding evidence to the closed #6 | Fixed: #14 and #15 |
| W3 | `docs/GOVERNANCE.md` and `labels.json` gave the `invalid` description in two wordings | Fixed: the catalogue's |
| W4 | `docs/TRAFFIC.md` placed an uninstalled App at the *Fetch* step; it fails at the token step, as the run of 2026-11-05 shows | Fixed |
| W5 | `docs/TRAFFIC.md` chose the alert milestone after the collection day; the workflow compares with the day the job runs | Fixed |
| W6 | `docs/TRAFFIC.md` gave repair commands that cannot run from either checkout | Fixed: a worktree beside the default branch, as the workflow does |

Accepted as they are:

- `README.md` links the author's portfolio of risk engines: my decision in
  #121, as the file audit records.
- `tools/README.md` and `INSTALLATION.md` link the actionlint release: the
  download source of a pinned tool, verified by its SHA-256.
- The social preview and its alt text say *v0.1.0 · Repository setup*: the
  milestone, not a released version; `RELEASING.md` gives the release state.
- `check_issues.py` reads the assignee from the issue form; "repository owner"
  in its docstring meant GitHub's field and now says repository metadata.
- `TEST_CASES.md` keeps its default tolerance bounds; the illustrative cases
  state an exact comparison, which the rules allow.

Open: `AGENTS.md` and `CONTRIBUTING.md` forbid two branch prefixes by naming
the tools that propose them. Whether to rephrase that is my decision.

## 🧪 Checks after the fixes

- `python tools/check.py --ci`: every gate PASS, on the head recorded in the
  pull request.
- `python -m unittest` in `tools/`: 270 tests, three more than at `fc98b17`.
- Every heading anchor and relative link of the tracked Markdown resolves.
- *Verified setup* of `INSTALLATION.md` on a fresh clone of `fc98b17`: 21
  gates PASS; the missing-tool and dirty-tree rows behave as recorded.

## ⚠️ Not validated

- The audit compares documents with code and state; it does not prove a
  document complete where the code is silent.
- Basel locators, the full CRR page count and the retrieved files that are not
  stored were not checked against their sources: the Basel text is not stored
  (A09).
- `categories.json` was checked for structure, counts, collateral, derivative
  and exclusion rules and by spot checks of locators, not entry by entry
  against the legal texts.
- Action SHAs were checked for consistency with their version comments, not
  against the tags upstream.

## 🗂️ Coverage

131 tracked files.

| File | Group | Result |
| --- | --- | --- |
| `.editorconfig` | Workflows | Fixed |
| `.gitattributes` | Workflows | Fixed |
| `.github/ISSUE_TEMPLATE/bug.yml` | Governance | No finding |
| `.github/ISSUE_TEMPLATE/config.yml` | Governance | No finding |
| `.github/ISSUE_TEMPLATE/documentation.yml` | Governance | No finding |
| `.github/ISSUE_TEMPLATE/enhancement.yml` | Governance | No finding |
| `.github/PULL_REQUEST_TEMPLATE.md` | Governance | Fixed |
| `.github/binary-allowlist.json` | Governance | No finding |
| `.github/dependabot.yml` | Workflows | No finding |
| `.github/labels.json` | Workflows | Fixed |
| `.github/scripts/labels-drift.mjs` | Workflows | No finding |
| `.github/scripts/labels-sync.mjs` | Workflows | No finding |
| `.github/workflows/issue-triage.yml` | Workflows | Fixed |
| `.github/workflows/labels-drift.yml` | Workflows | No finding |
| `.github/workflows/labels-sync.yml` | Workflows | No finding |
| `.github/workflows/pr-milestones.yml` | Workflows | No finding |
| `.github/workflows/repository-integrity.yml` | Workflows | No finding |
| `.github/workflows/traffic-history.yml` | Workflows | No finding |
| `.gitignore` | Workflows | No finding |
| `AGENTS.md` | Governance | No finding |
| `CHANGELOG.md` | Governance | Fixed |
| `CODE_OF_CONDUCT.md` | Governance | No finding |
| `CONTRIBUTING.md` | Governance | No finding |
| `INSTALLATION.md` | Governance | Fixed |
| `LICENSE` | — | Standard licence text, not reviewed |
| `NOTICE.md` | Governance | Fixed |
| `README.md` | Governance | Fixed |
| `RELEASING.md` | Governance | No finding |
| `SECURITY.md` | Governance | Fixed |
| `docs/.nojekyll` | — | Empty marker file |
| `docs/DECISIONS.md` | Governance | Fixed |
| `docs/GOVERNANCE.md` | Governance | Fixed |
| `docs/REPOSITORY_SETTINGS.md` | Governance | No finding |
| `docs/REPOSITORY_SETTINGS_EVIDENCE.md` | Governance | No finding |
| `docs/REPOSITORY_STRUCTURE.md` | Governance | Fixed |
| `docs/SOURCE_CONTROL.md` | Governance | Fixed |
| `docs/TRAFFIC.md` | Workflows | Fixed |
| `docs/VBA_HOUSE_STYLE.md` | Tooling | Fixed |
| `docs/WEBSITE.md` | Governance | Fixed |
| `docs/assets/K-LCR_social_preview.html` | Governance | No finding |
| `docs/assets/K-LCR_social_preview.png` | — | Binary: file audit (#21) |
| `docs/assets/README.md` | Governance | No finding |
| `docs/assets/architecture.svg` | Governance | No finding |
| `docs/assets/site.css` | Governance | No finding |
| `docs/index.html` | Governance | Fixed |
| `docs/methodology/APPLICABILITY.md` | Methodology | Fixed |
| `docs/methodology/DATA_CONTRACT.md` | Methodology | Fixed |
| `docs/methodology/PARAMETERS_AND_RESULTS.md` | Methodology | Fixed |
| `docs/methodology/README.md` | Methodology | Fixed |
| `docs/methodology/SOURCES.md` | Methodology | Fixed |
| `docs/methodology/TEST_CASES.md` | Methodology | Fixed |
| `docs/methodology/VALIDATION_PLAN.md` | Methodology | Fixed |
| `docs/methodology/categories.json` | Methodology | Structure, counts and spot checks; findings open in #148 |
| `docs/methodology/data-contract.json` | Methodology | Fixed |
| `docs/methodology/parameter-result-contract.json` | Methodology | Fixed |
| `docs/methodology/sources/README.md` | Methodology | No finding |
| `docs/methodology/sources/SRC-01_CRR-575-2013_consolidated-2026-06-26_extract.pdf` | — | Binary: file audit (#21) |
| `docs/methodology/sources/SRC-02_LCR-Delegated-Regulation-2015-61_consolidated-2022-07-08.pdf` | — | Binary: file audit (#21) |
| `docs/release/CLOSEOUT.md` | Governance | No finding |
| `docs/release/DOC_AUDIT_v0.1.0.md` | Governance | This record |
| `docs/release/FILE_AUDIT_v0.1.0.md` | Governance | Fixed (two provenance rows) |
| `docs/sitemap.xml` | Governance | No finding |
| `pyproject.toml` | Tooling | Fixed |
| `tests/cases/illustrative-eu-input-totals/assets.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/cases/illustrative-eu-input-totals/case.json` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/cases/illustrative-eu-input-totals/expected.json` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/cases/illustrative-eu-input-totals/flows.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/cases/illustrative-eu-input-totals/run.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/cases/illustrative-eu-rejected-input/assets.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/cases/illustrative-eu-rejected-input/case.json` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/cases/illustrative-eu-rejected-input/expected.json` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/cases/illustrative-eu-rejected-input/flows.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/cases/illustrative-eu-rejected-input/run.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/basel-valid/assets.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/basel-valid/flows.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/basel-valid/run.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/eu-empty-portfolio/assets.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/eu-empty-portfolio/flows.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/eu-empty-portfolio/run.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/eu-valid/assets.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/eu-valid/flows.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/eu-valid/run.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/expected.json` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/invalid-categories/assets.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/invalid-categories/flows.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/invalid-categories/run.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/invalid-fields/assets.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/invalid-fields/flows.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/invalid-fields/run.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/invalid-rules/assets.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/invalid-rules/flows.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/invalid-rules/run.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/invalid-structure/assets.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/invalid-structure/flows.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/invalid-structure/run.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/missing-file/assets.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/contract/missing-file/run.csv` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/derivations/illustrative_input_totals.py` | Methodology | No finding |
| `tests/parameters/expected.json` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/parameters/parameter-set-basel-illustrative.json` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/parameters/parameter-set-eu-illustrative.json` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/parameters/parameter-set-invalid.json` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/parameters/result-invalid.json` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tests/parameters/result-rejected.json` | — | Synthetic fixture data: file audit (#21); exercised by the validators |
| `tools/README.md` | Tooling | Fixed |
| `tools/check.py` | Tooling | No finding |
| `tools/check_binaries.py` | Tooling | No finding |
| `tools/check_changelog.py` | Tooling | Fixed |
| `tools/check_contract.py` | Methodology | No finding |
| `tools/check_files.py` | Tooling | Fixed |
| `tools/check_issues.py` | Tooling | Fixed |
| `tools/check_parameters.py` | Methodology | No finding |
| `tools/check_test_cases.py` | Methodology | No finding |
| `tools/check_vba_conditionals.py` | Tooling | Fixed |
| `tools/check_vba_dynamic.py` | Tooling | No finding |
| `tools/check_vba_jumps.py` | Tooling | Fixed |
| `tools/check_workflows.py` | Tooling | Fixed |
| `tools/requirements-quality-ci.txt` | Tooling | Fixed |
| `tools/test_check.py` | Tooling | No finding |
| `tools/test_check_binaries.py` | Tooling | No finding |
| `tools/test_check_changelog.py` | Tooling | Fixed |
| `tools/test_check_contract.py` | Tooling | No finding |
| `tools/test_check_issues.py` | Tooling | No finding |
| `tools/test_check_parameters.py` | Tooling | No finding |
| `tools/test_check_test_cases.py` | Tooling | No finding |
| `tools/test_check_vba.py` | Tooling | No finding |
| `tools/test_check_workflows.py` | Tooling | Fixed |
| `tools/test_traffic_history.py` | Tooling | No finding |
| `tools/traffic_history.py` | Tooling | No finding |
| `tools/vba-exceptions.json` | Tooling | No finding |
| `tools/vba_lexer.py` | Tooling | Fixed |
