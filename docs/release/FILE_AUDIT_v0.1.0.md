# 🔎 File audit — v0.1.0

**Every tracked file · Purpose, source and licence · Findings and their disposition**

This audit covers every file tracked on `release/0.1.0` for *v0.1.0 - Repo
setup* (#21). It started from `e777984252d46288499ad26581342dc935dd9240` and
covers the tree of the pull request that adds this file, findings fixed. The
merge commit is recorded in the resolution of #21. The files changed after
that commit were audited again at the closeout on 2026-11-07 (#23,
[closeout template](CLOSEOUT.md)); see *Closeout re-audit* below.

## 🧭 Method

On 2026-11-05 I:

- listed every tracked file with `git ls-files`, hidden configuration
  included: 130 files, the 131st, `docs/release/DOC_AUDIT_v0.1.0.md`, being
  written afterwards for K-LCR (#22);
- classified each file as text or binary from `.gitattributes` and its
  bytes, then checked every binary against the new `binaries` gate;
- searched every text file for other repositories' names outside
  `NOTICE.md`, employer or firm names, assistant or vendor names, third-person
  references to me, placeholders (`TODO`, `TBD`, `FIXME`, `OWNER/REPOSITORY`),
  credential patterns (GitHub and cloud tokens, private keys, passwords),
  e-mail addresses, generated or cache files and empty files;
- matched every reference to a closed issue against the words that mark
  pending work (`planned`, `pending`, `remains`, `not yet`, `until`);
- checked the fixtures in `tests/` for real-looking identifiers (ISIN, LEI,
  bank or firm names);
- matched every file against the provenance rows of [NOTICE.md](../../NOTICE.md).

## 📋 Findings and disposition

| # | Finding | Disposition |
| ---: | --- | --- |
| 1 | No check held binary files to an exact allowlist | Fixed: `binaries` gate (`tools/check_binaries.py`, 17 tests) and `.github/binary-allowlist.json`. The two EU source PDFs pass as byte-preserved sources; the social preview PNG is allowlisted with its SHA-256 |
| 2 | `NOTICE.md` referred to me as "the owner" twice | Fixed: first person, as `AGENTS.md` requires |
| 3 | `docs/TRAFFIC.md` showed the badge URL with the placeholder `OWNER/REPOSITORY` | Fixed: `danielep71/K-LCR` |
| 4 | `docs/methodology/APPLICABILITY.md` called both parameter sets "Planned (#10)", but #10 is closed | Fixed: the identifiers and format are fixed by #10; the sourced values follow with the EU and Basel profiles (B002, B001) |
| 5 | `NOTICE.md` did not name `categories.json`, `vba-exceptions.json`, `AGENTS.md`, `docs/WEBSITE.md`, `docs/sitemap.xml` and `docs/.nojekyll` | Fixed: each is now recorded. A text comparison found `AGENTS.md` and `docs/WEBSITE.md` written for K-LCR |
| 6 | Earlier audits (2026-10-31, 2026-11-01) found third-person wording and other repositories named in operational text | Already resolved by earlier pull requests: no occurrence remains |

Accepted as they are:

- `README.md` links the author's portfolio of risk engines: authorship
  branding, kept on purpose.
- `docs/REPOSITORY_SETTINGS_EVIDENCE.md` names *Copilot Autofix*, a GitHub
  setting; `AGENTS.md`, `CONTRIBUTING.md` and `docs/GOVERNANCE.md` name no
  assistant tool since #152.
- `SECURITY.md` publishes my reporting address on purpose; the other e-mail
  addresses are `example.invalid` test values.
- `docs/.nojekyll` is empty on purpose: it makes Pages serve `docs/` as is.
- The issue forms' `placeholder:` keys are form hints, not unfinished text.

No credential, employer or firm name, client or personal data, generated
file or cache was found. Nothing was deleted.

## 🔁 Closeout re-audit

On 2026-11-07 I scanned the 57 files changed after this audit for the closeout
of *v0.1.0 - Repo setup* (#23): no third-person wording, other-repository
name, tool name, employer name, placeholder, credential or new binary; every
Markdown anchor resolves. The inventory below lists all 131 tracked files:
the 130 of the first listing and `docs/release/DOC_AUDIT_v0.1.0.md`. The
consistency review of 2026-11-13 found the two label rows marked *Copied
unchanged* wrongly (their blobs differ from the sources recorded in
`NOTICE.md`) and the missing inventory row; both are fixed (#161).

## 🗃️ Binary files

| File | Why it is allowed |
| --- | --- |
| `docs/methodology/sources/SRC-01_CRR-575-2013_consolidated-2026-06-26_extract.pdf` | Byte-preserved EU source copy; hash in its README |
| `docs/methodology/sources/SRC-02_LCR-Delegated-Regulation-2015-61_consolidated-2022-07-08.pdf` | Byte-preserved EU source copy; hash in its README |
| `docs/assets/K-LCR_social_preview.png` | Allowlisted with its SHA-256; rendered from its HTML source |

## 🧪 Fixtures

The 41 files under `tests/` are synthetic: run and holding identifiers such
as `SYN-EU-01`, `SYN-BANK-A`, `A001` and `H01`, and amounts with no
regulatory value. No ISIN, LEI or real institution appears. Each registered
case declares `"synthetic": true`, and the `test-cases` gate refuses a case
without it.

## 🗂️ Inventory

Licences: MPL-2.0 unless the row says otherwise. *NOTICE* names the source of
an adapted or copied file, with its revision.

| Path | Purpose | Source | Licence |
| --- | --- | --- | --- |
| `.editorconfig` | Editor settings: encoding, line endings, indentation | Adapted (NOTICE) | MPL-2.0 |
| `.gitattributes` | Line endings, binary handling, byte-preserved sources, VBA diff driver | Adapted (NOTICE) | MPL-2.0 |
| `.github/ISSUE_TEMPLATE/bug.yml` | Issue form with assignee, priority, acceptance, dependencies and end date | Adapted (NOTICE) | MPL-2.0 |
| `.github/ISSUE_TEMPLATE/config.yml` | Issue chooser: no blank issues, private vulnerability link | Adapted (NOTICE) | MPL-2.0 |
| `.github/ISSUE_TEMPLATE/documentation.yml` | Issue form with assignee, priority, acceptance, dependencies and end date | Adapted (NOTICE) | MPL-2.0 |
| `.github/ISSUE_TEMPLATE/enhancement.yml` | Issue form with assignee, priority, acceptance, dependencies and end date | Adapted (NOTICE) | MPL-2.0 |
| `.github/PULL_REQUEST_TEMPLATE.md` | Pull request record: changes, validation, final-head review | Adapted (NOTICE) | MPL-2.0 |
| `.github/binary-allowlist.json` | Reviewed binary files with their SHA-256 | Adapted (NOTICE) | MPL-2.0 |
| `.github/dependabot.yml` | Weekly updates of pinned Actions and Python tools into the release branch | Written for K-LCR | MPL-2.0 |
| `.github/labels.json` | Label catalogue, schema 2 | Adapted (NOTICE) | MPL-2.0 |
| `.github/scripts/labels-drift.mjs` | Label synchronization and drift detection | Copied unchanged (NOTICE) | MPL-2.0 |
| `.github/scripts/labels-sync.mjs` | Label synchronization and drift detection | Adapted (NOTICE) | MPL-2.0 |
| `.github/workflows/issue-triage.yml` | Label sync, label drift or issue triage workflow | Adapted (NOTICE) | MPL-2.0 |
| `.github/workflows/labels-drift.yml` | Label sync, label drift or issue triage workflow | Adapted (NOTICE) | MPL-2.0 |
| `.github/workflows/labels-sync.yml` | Label sync, label drift or issue triage workflow | Adapted (NOTICE) | MPL-2.0 |
| `.github/workflows/pr-milestones.yml` | Removes milestones set on pull requests | Copied unchanged (NOTICE) | MIT |
| `.github/workflows/repository-integrity.yml` | The required check: runs tools/check.py --ci | Adapted (NOTICE) | MPL-2.0 |
| `.github/workflows/traffic-history.yml` | Opt-in daily traffic collection and alert (#17) | Adapted (NOTICE) | MPL-2.0 |
| `.gitignore` | Keeps generated files, workbooks and local tools out of Git | Adapted (NOTICE) | MPL-2.0 |
| `AGENTS.md` | Editorial and assistant rules | Written for K-LCR | MPL-2.0 |
| `CHANGELOG.md` | Notable changes; no version released | Adapted (NOTICE) | MPL-2.0 |
| `CODE_OF_CONDUCT.md` | Conduct policy and private reporting | Adapted (NOTICE) | MPL-2.0 |
| `CONTRIBUTING.md` | Contributor workflow and local checks | Adapted (NOTICE) | MPL-2.0 |
| `INSTALLATION.md` | Host matrix, verified developer setup, planned Excel steps | Adapted (NOTICE) | MPL-2.0 |
| `LICENSE` | Mozilla Public License 2.0 text | Standard licence text | MPL-2.0 text |
| `NOTICE.md` | Licence, provenance, EU legal texts and data policy | Written for K-LCR | MPL-2.0 |
| `README.md` | Entry point: purpose, status, quick start, layout, links | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `RELEASING.md` | Versioning, milestones, closeout and release procedure | Adapted (NOTICE) | MPL-2.0 |
| `SECURITY.md` | Vulnerability reporting, scope, automation surface | Adapted (NOTICE) | MPL-2.0 |
| `docs/.nojekyll` | Serves docs/ as a plain static site on Pages | Written for K-LCR | MPL-2.0 |
| `docs/DECISIONS.md` | My accepted decisions and follow-on backlog | Written for K-LCR | MPL-2.0 |
| `docs/GOVERNANCE.md` | Branches, review, integration, issues and labels | Adapted (NOTICE) | MPL-2.0 |
| `docs/REPOSITORY_SETTINGS.md` | Portable register of non-default settings | Adapted (NOTICE) | MPL-2.0 |
| `docs/REPOSITORY_SETTINGS_EVIDENCE.md` | Dated settings read-back and enforcement demonstration | Adapted (NOTICE) | MPL-2.0 |
| `docs/REPOSITORY_STRUCTURE.md` | Scope, architecture and repository layout | Written for K-LCR | MPL-2.0 |
| `docs/SOURCE_CONTROL.md` | Source layout, encoding and generated files | Written for K-LCR | MPL-2.0 |
| `docs/TRAFFIC.md` | Traffic history: enabling, data, alert, recovery | Adapted (NOTICE) | MPL-2.0 |
| `docs/VBA_HOUSE_STYLE.md` | VBA conventions and the static checks | Adapted (NOTICE) | MPL-2.0 |
| `docs/WEBSITE.md` | Website publishing and maintenance | Written for K-LCR | MPL-2.0 |
| `docs/assets/K-LCR_social_preview.html` | Social preview image and its HTML source (#18) | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/assets/K-LCR_social_preview.png` | Social preview image and its HTML source (#18) | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/assets/README.md` | Image provenance, figures and rendering | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/assets/architecture.svg` | Website architecture illustration | Written for K-LCR | MPL-2.0 |
| `docs/assets/site.css` | Website styles | Adapted (NOTICE) | MPL-2.0 |
| `docs/index.html` | Project website | Adapted (NOTICE) | MPL-2.0 |
| `docs/methodology/APPLICABILITY.md` | Requirement map and my applicability decisions | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/methodology/DATA_CONTRACT.md` | Input contract | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/methodology/PARAMETERS_AND_RESULTS.md` | Parameter-set and result contract | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/methodology/README.md` | Methodology index | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/methodology/SOURCES.md` | Regulatory source register | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/methodology/TEST_CASES.md` | Test-case format, oracles, tolerances | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/methodology/VALIDATION_PLAN.md` | Planned validation cases | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/methodology/categories.json` | Machine-readable contract or category taxonomy | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/methodology/data-contract.json` | Machine-readable contract or category taxonomy | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/methodology/parameter-result-contract.json` | Machine-readable contract or category taxonomy | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/methodology/sources/README.md` | Retrieval record and SHA-256 of the stored EU sources | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `docs/methodology/sources/SRC-01_CRR-575-2013_consolidated-2026-06-26_extract.pdf` | Stored EU legal text (SRC-01 extract, SRC-02 full) | EU legal text (NOTICE) | CC BY 4.0 |
| `docs/methodology/sources/SRC-02_LCR-Delegated-Regulation-2015-61_consolidated-2022-07-08.pdf` | Stored EU legal text (SRC-01 extract, SRC-02 full) | EU legal text (NOTICE) | CC BY 4.0 |
| `docs/release/CLOSEOUT.md` | Milestone closeout template | Adapted (NOTICE) | MPL-2.0 |
| `docs/release/DOC_AUDIT_v0.1.0.md` | The documentation audit (#22) | Written for K-LCR | MPL-2.0 |
| `docs/release/FILE_AUDIT_v0.1.0.md` | This file audit (#21) | Written for K-LCR | MPL-2.0 |
| `docs/sitemap.xml` | Website sitemap | Written for K-LCR | MPL-2.0 |
| `pyproject.toml` | Ruff and strict mypy configuration | Adapted (NOTICE) | MPL-2.0 |
| `tests/cases/illustrative-eu-input-totals/assets.csv` | Registered illustrative test case (synthetic) | Written for K-LCR | MPL-2.0 |
| `tests/cases/illustrative-eu-input-totals/case.json` | Registered illustrative test case (synthetic) | Written for K-LCR | MPL-2.0 |
| `tests/cases/illustrative-eu-input-totals/expected.json` | Registered illustrative test case (synthetic) | Written for K-LCR | MPL-2.0 |
| `tests/cases/illustrative-eu-input-totals/flows.csv` | Registered illustrative test case (synthetic) | Written for K-LCR | MPL-2.0 |
| `tests/cases/illustrative-eu-input-totals/run.csv` | Registered illustrative test case (synthetic) | Written for K-LCR | MPL-2.0 |
| `tests/cases/illustrative-eu-rejected-input/assets.csv` | Registered illustrative test case (synthetic) | Written for K-LCR | MPL-2.0 |
| `tests/cases/illustrative-eu-rejected-input/case.json` | Registered illustrative test case (synthetic) | Written for K-LCR | MPL-2.0 |
| `tests/cases/illustrative-eu-rejected-input/expected.json` | Registered illustrative test case (synthetic) | Written for K-LCR | MPL-2.0 |
| `tests/cases/illustrative-eu-rejected-input/flows.csv` | Registered illustrative test case (synthetic) | Written for K-LCR | MPL-2.0 |
| `tests/cases/illustrative-eu-rejected-input/run.csv` | Registered illustrative test case (synthetic) | Written for K-LCR | MPL-2.0 |
| `tests/contract/basel-valid/assets.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/basel-valid/flows.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/basel-valid/run.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/eu-empty-portfolio/assets.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/eu-empty-portfolio/flows.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/eu-empty-portfolio/run.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/eu-valid/assets.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/eu-valid/flows.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/eu-valid/run.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/expected.json` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/invalid-categories/assets.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/invalid-categories/flows.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/invalid-categories/run.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/invalid-fields/assets.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/invalid-fields/flows.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/invalid-fields/run.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/invalid-rules/assets.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/invalid-rules/flows.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/invalid-rules/run.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/invalid-structure/assets.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/invalid-structure/flows.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/invalid-structure/run.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/missing-file/assets.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/contract/missing-file/run.csv` | Synthetic input-contract fixture or its expected findings | Written for K-LCR | MPL-2.0 |
| `tests/derivations/illustrative_input_totals.py` | Standard-library derivation script of an illustrative case | Written for K-LCR | MPL-2.0 |
| `tests/parameters/expected.json` | Synthetic parameter-set or result fixture | Written for K-LCR | MPL-2.0 |
| `tests/parameters/parameter-set-basel-illustrative.json` | Synthetic parameter-set or result fixture | Written for K-LCR | MPL-2.0 |
| `tests/parameters/parameter-set-eu-illustrative.json` | Synthetic parameter-set or result fixture | Written for K-LCR | MPL-2.0 |
| `tests/parameters/parameter-set-invalid.json` | Synthetic parameter-set or result fixture | Written for K-LCR | MPL-2.0 |
| `tests/parameters/result-invalid.json` | Synthetic parameter-set or result fixture | Written for K-LCR | MPL-2.0 |
| `tests/parameters/result-rejected.json` | Synthetic parameter-set or result fixture | Written for K-LCR | MPL-2.0 |
| `tools/README.md` | Tooling guide: gates, triage, traffic, tool versions | Adapted (NOTICE) | MPL-2.0 |
| `tools/check.py` | Runs every gate; writes the integrity report | Adapted (NOTICE) | MPL-2.0 |
| `tools/check_binaries.py` | Gate: tracked binary files | Adapted (NOTICE) | MPL-2.0 |
| `tools/check_changelog.py` | Gate: changelog, VERSION and release state | Adapted (NOTICE) | MPL-2.0 |
| `tools/check_contract.py` | Gate: input contract validator | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `tools/check_files.py` | Gate: tracked text format | Written for K-LCR | MPL-2.0 |
| `tools/check_issues.py` | Issue triage rules and configuration gate | Adapted (NOTICE) | MPL-2.0 |
| `tools/check_parameters.py` | Gate: parameter-set and result validator | Written for K-LCR | MPL-2.0 |
| `tools/check_test_cases.py` | Gate: registered test cases | Written for K-LCR; structure adapted (NOTICE) | MPL-2.0 |
| `tools/check_vba_conditionals.py` | Gate: VBA static check | Adapted (NOTICE) | MPL-2.0 |
| `tools/check_vba_dynamic.py` | Gate: VBA static check | Adapted (NOTICE) | MPL-2.0 |
| `tools/check_vba_jumps.py` | Gate: VBA static check | Adapted (NOTICE) | MPL-2.0 |
| `tools/check_workflows.py` | Gate: workflow and Dependabot invariants | Adapted (NOTICE) | MPL-2.0 |
| `tools/requirements-quality-ci.txt` | Hash-locked Ruff, mypy and PyYAML | Adapted (NOTICE) | MPL-2.0 |
| `tools/test_check.py` | Tests of the gate runner | Adapted (NOTICE) | MPL-2.0 |
| `tools/test_check_binaries.py` | Tests of the binary gate | Adapted (NOTICE) | MPL-2.0 |
| `tools/test_check_changelog.py` | Tests of the changelog gate | Adapted (NOTICE) | MPL-2.0 |
| `tools/test_check_contract.py` | Tests of the matching tool | As the tool it tests (NOTICE) | MPL-2.0 |
| `tools/test_check_issues.py` | Tests of the matching tool | As the tool it tests (NOTICE) | MPL-2.0 |
| `tools/test_check_parameters.py` | Tests of the matching tool | As the tool it tests (NOTICE) | MPL-2.0 |
| `tools/test_check_test_cases.py` | Tests of the matching tool | As the tool it tests (NOTICE) | MPL-2.0 |
| `tools/test_check_vba.py` | Tests of the matching tool | As the tool it tests (NOTICE) | MPL-2.0 |
| `tools/test_check_workflows.py` | Tests of the matching tool | As the tool it tests (NOTICE) | MPL-2.0 |
| `tools/test_traffic_history.py` | Tests of the matching tool | As the tool it tests (NOTICE) | MPL-2.0 |
| `tools/traffic_history.py` | Traffic history merge, badges and alert | Adapted (NOTICE) | MPL-2.0 |
| `tools/vba-exceptions.json` | Reviewed host-boundary VBA exceptions (none yet) | Written for K-LCR | MPL-2.0 |
| `tools/vba_lexer.py` | Shared VBA lexer of the static checks | Adapted (NOTICE) | MPL-2.0 |
