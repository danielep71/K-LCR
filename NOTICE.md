# 📜 Licensing, provenance and data

[![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-2ea44f?style=flat-square)](LICENSE)
[![Data: Synthetic only](https://img.shields.io/badge/Data-Synthetic_only-0969da?style=flat-square)](#-data-and-privacy)

Copyright 2026 Daniele Penza and contributors.

I selected the Mozilla Public License 2.0 on 2026-10-28 for K-LCR.
Code, documentation, workflows and configuration contributed to K-LCR are
covered by [LICENSE](LICENSE), unless an individual file states otherwise.
This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at https://mozilla.org/MPL/2.0/.

This is a public, independent reference project. The license decision does
not change repository visibility or grant permission to disclose client,
employer or third-party material. Distribution and publication remain separate
decisions of mine.

## 📚 Imported material

The initial repository setup included files adapted from
[danielep71/K-SFTs](https://github.com/danielep71/K-SFTs). Source revision
`e6bae6df272083ba596c9eb866b14e6f9152bc15` was inspected on
2026-10-28. That repository carries MPL-2.0. Git blob identity was verified for `.github/labels.json`,
`.github/label-policy.json`, `.github/scripts/labels-sync.mjs` and
`.github/scripts/labels-drift.mjs` (rechecked on 2026-10-28). The label files
were later replaced by the schema-2 versions from revision
`dfed6bc079cb83f751a0778684e2d436378398b7` (#93). The other imported files were adapted and require this
provenance record rather than an assertion of byte-for-byte identity.

| K-LCR paths | Source and relationship | Local adaptation |
| --- | --- | --- |
| `.editorconfig`, `.gitattributes`, `.gitignore` | K-SFTs at the source revision; adapted under #5 | K-LCR paths, no preselected VBA encoding, no workbook-template exception, the byte-for-byte rule for regulatory source copies taken from `dfed6bc` (#97), Markdown trailing whitespace trimmed to match the tracked-text gate; same normalization, binary and ignore policy. |
| `.github/labels.json` | K-SFTs schema-2 catalogue at `dfed6bc`; same blob since #101 (#93) | Single `labels` list, no overlays, first-person descriptions; the separate selection policy file is removed. |
| `.github/scripts/labels-drift.mjs` | [danielep71/MyTemplate](https://github.com/danielep71/MyTemplate) at `d5622433b6a50a41513e2d129cebf036e4bb974d`, MPL-2.0; same blob, adopted under #8 (earlier the K-SFTs file at `dfed6bc`, #93) | Used with the K-LCR catalogue and repository variables. |
| `.github/scripts/labels-sync.mjs` | [danielep71/MyTemplate](https://github.com/danielep71/MyTemplate) at `d5622433b6a50a41513e2d129cebf036e4bb974d`, MPL-2.0, adopted under #8 (earlier the K-SFTs file at `dfed6bc`, #93) | Used with the K-LCR catalogue and repository variables; the self-test also covers descriptions containing pipes and backticks. |
| `.github/PULL_REQUEST_TEMPLATE.md` | K-SFTs `.github/PULL_REQUEST_TEMPLATE.md` at `dfed6bc`, adapted under #95 | release/0.1.0 base, `python tools/check.py --ci`, review record matching this governance; no changelog step and no tool vendor named. |
| `.github/ISSUE_TEMPLATE/` | K-SFTs issue forms/configuration, adapted | K-LCR descriptions, assignee and links; Excel/VBA environment and area fields after the stack decision (#69); a required Target end date field, with the id and label used in [danielep71/MyTemplate](https://github.com/danielep71/MyTemplate) at `d5622433b6a50a41513e2d129cebf036e4bb974d`, MPL-2.0 (#8). |
| `.github/workflows/labels-sync.yml`, `labels-drift.yml`, `issue-triage.yml` | K-SFTs workflow patterns, adapted | K-LCR triggers, permissions and current issue-triage script. |
| `tools/check.py`, `tools/test_check.py`, `.github/workflows/repository-integrity.yml` | K-SFTs runner, tests and workflow structure at the source revision, adapted under #7 | K-LCR gates for current tooling, text fixtures, workflow lint and candidate report; no SFT calculation or Excel evidence. |
| `tools/check_workflows.py`, `tools/test_check_workflows.py` | K-SFTs files at `dfed6bc`, adapted under #109 | Write allowlist limited to the label reconcile and PR milestone jobs. |
| `pyproject.toml`, `tools/requirements-quality-ci.txt` | K-SFTs Ruff/mypy configuration and hash-locked pins at the source revision, adapted under #52; PyYAML pin added under #109 | Python 3.13 target matching the CI runtime; identical package pins and hashes; K-LCR installation reference. |
| `tools/README.md` | K-SFTs `tools/README.md` structure at the source revision, adapted under #68 | K-LCR gates, tracked-text checker, tool versions and dependency-update procedure; no VBA, Excel-evidence or traffic tooling described before it exists. |
| `tools/check_issues.py`, `tools/test_check_issues.py` | K-SFTs files at `dfed6bc`, adapted under #105 and #8 | Assignee read from the issue forms; every Dependabot update entry must assign that person; K-LCR identity only in the forms and governance; target end date, open milestone and milestone due-date checks following [danielep71/MyTemplate](https://github.com/danielep71/MyTemplate) at `d5622433b6a50a41513e2d129cebf036e4bb974d`, MPL-2.0, with conflicting Planning dates also reported (#8). |
| `docs/VBA_HOUSE_STYLE.md`, `INSTALLATION.md` | K-SFTs style and installation structure at the source revision, adapted; `INSTALLATION.md` restructured under #19 after the host, setup and evidence sections of `INSTALLATION.md` in [danielep71/MyTemplate](https://github.com/danielep71/MyTemplate) at `9489d12b2f4463c0e567c9631e10a43220f0f291`, MPL-2.0 | K-LCR naming, EU/Basel profile boundary and untested host status; a developer setup verified from a fresh clone; Excel steps marked as not executed; no copied SFT formulas, tested-host claims or workbook paths. |
| Markdown presentation and badges in this documentation set | K-SFTs structure and glyph/badge vocabulary, adapted under the documentation polish PR | K-LCR-specific status and links; no borrowed execution or release claims. |
| `docs/index.html`, `docs/assets/site.css` | K-SFTs `docs/index.html` structure and `docs/assets/site.css` at the source revision, adapted under #63; MPL-2.0 | K-LCR scope, profiles, setup status, public-repository links and static publishing; no copied product or validation claims. The architecture SVG is original K-LCR source. |
| `docs/assets/K-LCR_social_preview.html`, `docs/assets/K-LCR_social_preview.png`, `docs/assets/README.md` | HTML-to-PNG social preview method and image-README layout modelled on `docs/assets/SACCR_social_preview.html` and `docs/assets/README.md` of K-SACCR at `0e123ac`, adapted under #18; palette and `K` mark from this repository's `docs/assets/site.css` | Original K-LCR content and layout; regulatory figures checked against `SRC-02` and the Basel LCR chapters. The PNG renders Inter and JetBrains Mono (SIL Open Font License 1.1) from local installations; no font file is redistributed. |
| `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` | `CONTRIBUTING.md` of [danielep71/MyTemplate](https://github.com/danielep71/MyTemplate) at `9489d12b2f4463c0e567c9631e10a43220f0f291`, MPL-2.0, and `CODE_OF_CONDUCT.md` of K-SFTs at `0d994f7818c49439610f6ec6f418001852b1db71`, adapted under #19 | K-LCR's branches, pull request template, commit rules, evidence rules, contracts and checks; conduct reports by email to the address of `SECURITY.md`; no Contributor Covenant text copied. |
| `.github/workflows/traffic-history.yml`, `tools/traffic_history.py`, `tools/test_traffic_history.py`, `docs/TRAFFIC.md` | `.github/workflows/traffic-history.yml`, `tools/traffic_history.py`, `tests/test_traffic_history.py` and `docs/repo_governance/TRAFFIC.md` of [danielep71/MyTemplate](https://github.com/danielep71/MyTemplate) at `9489d12b2f4463c0e567c9631e10a43220f0f291`, MPL-2.0, adopted under #17; they replace the earlier K-LCR implementation of PR #92 | The script unchanged except for its documentation path; the workflow with K-LCR's Python version and documentation path; the tests with K-LCR's imports and Issue triage interface; the guide with K-LCR's paths, activation state and badge status. The workflow invariants of the traffic jobs are written for K-LCR's `check_workflows.py`. |
| `tools/check_binaries.py`, `tools/test_check_binaries.py`, `.github/binary-allowlist.json` | `tools/check_binaries.py`, `tests/test_check_binaries.py` and `.github/binary-allowlist.json` of [danielep71/MyTemplate](https://github.com/danielep71/MyTemplate) at `9489d12b2f4463c0e567c9631e10a43220f0f291`, MPL-2.0, adopted under #21 | Approved paths limited to the regulatory source copies and UserForm `.frx` files; the workbook template is to be allowlisted; tests adapted to those paths and to K-LCR's imports; K-LCR's own allowlist entry for the social preview. |
| `SECURITY.md` | K-SFTs `SECURITY.md` structure at the source revision, adapted under #4 and #66 | K-LCR scope and automation surface; private reporting through GitHub or by email (#79); same best-effort response targets and safe harbor; current security-feature states kept in the settings evidence (#90); no published version. |
| `docs/REPOSITORY_SETTINGS.md` | K-SFTs `docs/REPOSITORY_SETTINGS.md` at `3a6ed87388cd0f65c4665c84f2c41f59ff688715` (K-SFTs #163); same blob `a938d56`, adopted under #90 | Portable register without repository identifiers; every row checked against K-LCR's live settings on 2026-10-29. |
| `docs/REPOSITORY_SETTINGS_EVIDENCE.md` | K-SFTs `docs/REPOSITORY_SETTINGS_EVIDENCE.md` structure at the same revision, adapted under #90 | K-LCR's own dated read-backs, rule IDs, run evidence and historical record; no K-SFTs observations. |
| `docs/methodology/SOURCES.md`, `docs/methodology/APPLICABILITY.md`, `docs/methodology/README.md` | Register structure (stable IDs, statuses, verification steps, rules for local copies) adapted from `docs/methodology/SOURCES.md` of [danielep71/MyTemplate](https://github.com/danielep71/MyTemplate) at `d5622433b6a50a41513e2d129cebf036e4bb974d`, MPL-2.0; retrieval record and version notes modelled on `docs/methodology/sources/README.md` of K-SFTs at `3fea4e9`, adapted under #9 | K-LCR's own EU and Basel sources, editions, hashes, locators, requirement map, resolutions, decisions and interpretations; no source text copied. |
| `docs/methodology/DATA_CONTRACT.md`, `data-contract.json`, `categories.json`, `PARAMETERS_AND_RESULTS.md`, `parameter-result-contract.json`, `tools/check_contract.py`, `tools/check_parameters.py` and their tests and fixtures | Contract and validator pattern (semicolon CSV with header, typed columns, stable finding codes with file, line, record and column, inline and folder fixtures with an expected file) adapted from `docs/csv/contract.json` and `tools/csv_contract.py` of K-SACCR at `22edfc8`; dataset, validation, point-in-time and lineage headings adapted from `docs/methodology/DATA_CONTRACT.md` and `CALCULATION_CONTRACTS.md` of [danielep71/MyTemplate](https://github.com/danielep71/MyTemplate) at `d5622433b6a50a41513e2d129cebf036e4bb974d`, MPL-2.0; adapted under #10 | K-LCR's own files, columns, LCR categories, rules, reconciliation, fingerprint, parameter-set and result layouts and diagnostics; code written for K-LCR. |
| `docs/methodology/TEST_CASES.md`, `VALIDATION_PLAN.md`, `tools/check_test_cases.py`, `tools/test_check_test_cases.py`, `tests/cases/`, `tests/derivations/` | Case, expected-output and reference-class format, tolerance rule, derivation-script check and completeness policy adapted from `docs/methodology/TEST_CASES.md`, `VALIDATION_PLAN.md` and `tools/check_derivations.py` of [danielep71/MyTemplate](https://github.com/danielep71/MyTemplate) at `d5622433b6a50a41513e2d129cebf036e4bb974d`, MPL-2.0; adapted under #11 | K-LCR's case layout over its input contract, quantities, the contract reference class, the standard-library-only rule for derivations, the planned LCR cases and the neutral examples; code written for K-LCR. |
| `tools/vba_lexer.py`, `tools/check_vba_conditionals.py`, `tools/check_vba_jumps.py`, `tools/check_vba_dynamic.py`, `tools/test_check_vba.py` | `tools/vba_lexer.py`, `check_vba_conditionals.py` and `check_vba_jumps.py` of [danielep71/MyTemplate](https://github.com/danielep71/MyTemplate) at `d5622433b6a50a41513e2d129cebf036e4bb974d`, MPL-2.0, adapted under #12; the `CreateObject`/`GetObject`, dynamic-call, `Type`/`Enum` member and statement-normalization patterns of its `check_vba_dependencies.py`; lexer, conditional and jump fixtures of its `tests/test_check_vba.py` | No facade-prefix helpers; `PtrSafe` and `LongPtr` rejected under VBA6; jump rules for one error/cleanup handler (no `GoSub`, computed jump, `On Error GoTo -1` or backward `GoTo`); `check_vba_dynamic.py` and its reviewed-exceptions file written for K-LCR's homes; K-LCR fixtures. |
| `CHANGELOG.md`, `RELEASING.md`, `docs/release/CLOSEOUT.md`, `tools/check_changelog.py`, `tools/test_check_changelog.py` | `CHANGELOG.md`, `RELEASING.md` and `docs/release/CLOSEOUT.md` of [danielep71/MyTemplate](https://github.com/danielep71/MyTemplate) at `4a4554703709dd0f3be306e4ef1f443268de2a22`, MPL-2.0, adapted under #20; `tools/check_changelog.py` and `tests/test_check_changelog.py` of the same revision: the checker unchanged (same blob `7e5bfcc`), the tests with only their import adapted; the release-status table and the closing of a setup milestone without a release follow `RELEASING.md` of K-SFTs at `0d994f7818c49439610f6ec6f418001852b1db71` | **Adopted:** Keep a Changelog and Semantic Versioning, `VERSION` only from the first release, annotated tags with a `Deviations:` line, frozen released sections, the recovery rules and the closeout record. **Adapted:** K-LCR's branches, milestones and checks; what a setup version may and may not claim; a closeout that can end without a release; no Excel run before #15. **Deferred:** the tag-triggered release workflow, attested source bundle and published-release verifier (#137), the Excel run binding (#14, #15), and the workbook asset, user manual and distribution review (B004, B006). |
| `docs/GOVERNANCE.md` | K-SFTs label/governance patterns, rewritten | K-LCR branch state, owner approval and working rules; settings are kept in the settings register and evidence (#90). |

`.github/dependabot.yml`, `tools/check_files.py`, `docs/SOURCE_CONTROL.md`,
`AGENTS.md`, `docs/WEBSITE.md`, `docs/sitemap.xml`, `docs/.nojekyll` and
`tools/vba-exceptions.json` were written for this repository; Dependabot uses standard GitHub Actions
configuration and pinned upstream actions. `README.md`,
`docs/REPOSITORY_STRUCTURE.md` and `docs/DECISIONS.md` describe K-LCR
decisions. This register does not assign copyright in source files to someone
else or claim ownership of third-party tools.

When importing more source, record its origin, immutable revision, applicable
license and local changes here in the importing PR. Do not copy proprietary
workbooks, regulatory document text, third-party code or imagery merely
because they are accessible. A citation/link to an official regulatory source
is preferable to redistributing its full text.

## ⚖️ MIT-licensed material

`.github/workflows/pr-milestones.yml` is copied unchanged (same Git blob
`91f45e6`) from `.github/workflows/pr-milestones.yml` in
[danielep71/K-FRTB-SA](https://github.com/danielep71/K-FRTB-SA) at revision
`80495bebf4cf300660c2fdf386bee6bbad83eed6`, inspected on 2026-10-31 (#107).
That file is distributed under the MIT License, reproduced here:

> MIT License
>
> Copyright (c) 2026 Daniele Penza
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.

## 🇪🇺 EU legal texts

`docs/methodology/sources/` stores two EU documents; their provenance,
extraction method and SHA-256 are in its
[README](docs/methodology/sources/README.md):

| File | Document | Changes |
| --- | --- | --- |
| `SRC-02_LCR-Delegated-Regulation-2015-61_consolidated-2022-07-08.pdf` | Commission Delegated Regulation (EU) 2015/61, consolidated text of 08.07.2022 | None: stored as retrieved |
| `SRC-01_CRR-575-2013_consolidated-2026-06-26_extract.pdf` | Regulation (EU) No 575/2013, consolidated text of 26.06.2026 | Extract: 37 of 895 pages selected (page 1 and the pages of Articles 6, 8, 11, 411 to 426, 451a and 460); the selected pages are unchanged |

- **Source and attribution:** EUR-Lex, <https://eur-lex.europa.eu>, and the
  Publications Office of the European Union; © European Union. Each file keeps
  its own notices, including the statement that a consolidated text is a
  documentation tool without legal effect.
- **Reuse terms:** I checked the EUR-Lex legal notice
  (<https://eur-lex.europa.eu/content/legal-notice/legal-notice.html>) on
  2026-11-03. It allows reuse, including commercial reuse, of the legal
  documents published on EUR-Lex, unless a document states otherwise, and it
  places consolidated texts under the Creative Commons Attribution 4.0
  International licence (CC BY 4.0), which requires attribution of the source
  and an indication of changes. The underlying rules are Commission Decision
  2011/833/EU of 12 December 2011 on the reuse of Commission documents, which
  also requires that reuse does not distort the original meaning.
- **Licence:** these documents are **not** covered by the MPL-2.0 licence of
  K-LCR, which applies to K-LCR's own code and documentation.

## 🧰 External tools

The workflows use `actions/checkout`, `actions/setup-python`,
`actions/setup-node` and `actions/upload-artifact` pinned by commit SHA; they
are dependencies fetched by GitHub Actions, not vendored files in K-LCR. The
Repository integrity workflow downloads the
[actionlint](https://github.com/rhysd/actionlint) 1.7.12 release binary and
verifies it against a pinned SHA-256 before use; it is not redistributed.
It also installs Ruff, mypy, PyYAML and their dependencies from PyPI at the versions
and wheel hashes pinned in `tools/requirements-quality-ci.txt`; they are not
vendored. Python and Node runtimes used for repository checks are not bundled. Verify
upstream license/version metadata when adding or changing a dependency;
preserve any required notices.

## 🔒 Data and privacy

Fixtures, bug reports, examples and documentation use synthetic data only.
Do not commit client, employer, counterparty, customer, personal or proprietary
information, credentials, private workbooks, non-public regulatory material or
unapproved artwork. See [SECURITY.md](SECURITY.md). A file audit and a narrow
credential/organization-name pattern check of the files tracked on
`release/0.1.0` when this policy was adopted (#4, PR #32, 2026-10-28) found
no such material; files added later were not part of that audit. Pattern
checks do not prove that future contributions or unrecognizable confidential
data are safe; review provenance and contents at every import and in the
final #21 audit.
