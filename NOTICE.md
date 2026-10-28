# 📜 Licensing, provenance and data

[![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-2ea44f?style=flat-square)](LICENSE)
[![Data: Synthetic only](https://img.shields.io/badge/Data-Synthetic_only-0969da?style=flat-square)](#-data-and-privacy)

Copyright 2026 Daniele Penza and contributors.

The owner selected the Mozilla Public License 2.0 on 2026-10-28 for K-LCR.
Code, documentation, workflows and configuration contributed to K-LCR are
covered by [LICENSE](LICENSE), unless an individual file states otherwise.
This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at https://mozilla.org/MPL/2.0/.

This is a public, independent reference project. The license decision does
not change repository visibility or grant permission to disclose client,
employer or third-party material. Distribution and publication remain separate
owner decisions.

## 📚 Imported material

The initial repository setup included files adapted from
[danielep71/K-SFTs](https://github.com/danielep71/K-SFTs). Source revision
`e6bae6df272083ba596c9eb866b14e6f9152bc15` was inspected on
2026-10-28. That repository carries MPL-2.0. Git blob identity was verified for `.github/labels.json`,
`.github/label-policy.json`, `.github/scripts/labels-sync.mjs` and
`.github/scripts/labels-drift.mjs` (rechecked on 2026-10-28). The other
imported files were adapted and require this provenance record rather than
an assertion of byte-for-byte identity.

| K-LCR paths | Source and relationship | Local adaptation |
| --- | --- | --- |
| `.editorconfig`, `.gitattributes`, `.gitignore` | K-SFTs at the source revision; adapted under #5 | K-LCR paths, no preselected VBA encoding, no regulatory-copy or workbook-template exception, Markdown trailing whitespace trimmed to match the tracked-text gate; same normalization, binary and ignore policy. |
| `.github/labels.json`, `.github/label-policy.json` | K-SFTs files at the source revision; same blobs | Selected application profile with no domain overlay. |
| `.github/scripts/labels-sync.mjs`, `.github/scripts/labels-drift.mjs` | K-SFTs files at the source revision; same blobs | Used with K-LCR repository variables and policy. |
| `.github/ISSUE_TEMPLATE/` | K-SFTs issue forms/configuration, adapted | K-LCR descriptions, assignee, links and platform-neutral guidance. |
| `.github/workflows/labels-sync.yml`, `labels-drift.yml`, `issue-triage.yml` | K-SFTs workflow patterns, adapted | K-LCR triggers, permissions and current issue-triage script. |
| `tools/check.py`, `tools/test_check.py`, `.github/workflows/repository-integrity.yml` | K-SFTs runner, tests and workflow structure at the source revision, adapted under #7 | K-LCR gates for current tooling, text fixtures, workflow lint and candidate report; no SFT calculation or Excel evidence. |
| `pyproject.toml`, `tools/requirements-quality-ci.txt` | K-SFTs Ruff/mypy configuration and hash-locked pins at the source revision, adapted under #52 | Python 3.13 target matching the CI runtime; identical package pins and hashes; K-LCR installation reference. |
| `tools/README.md` | K-SFTs `tools/README.md` structure at the source revision, adapted under #68 | K-LCR gates, tracked-text checker, tool versions and dependency-update procedure; no VBA, Excel-evidence or traffic tooling described before it exists. |
| `tools/check_issues.py`, `tools/test_check_issues.py` | K-SFTs triage logic/tests, adapted | K-LCR repository identity and relevant regression cases. |
| `docs/VBA_HOUSE_STYLE.md`, `INSTALLATION.md` | K-SFTs style and installation structure at the source revision, adapted | K-LCR naming, EU/Basel profile boundary and untested host status; no copied SFT formulas, tested-host claims or workbook paths. |
| Markdown presentation and badges in this documentation set | K-SFTs structure and glyph/badge vocabulary, adapted under the documentation polish PR | K-LCR-specific status and links; no borrowed execution or release claims. |
| `docs/index.html`, `docs/assets/site.css` | K-SFTs `docs/index.html` structure and `docs/assets/site.css` at the source revision, adapted under #63; MPL-2.0 | K-LCR scope, profiles, setup status, public-repository links and static publishing; no copied product or validation claims. The architecture SVG is original K-LCR source. |
| `SECURITY.md` | K-SFTs security-policy structure at the source revision, adapted | Private reporting without assuming public-only reporting features or a published version; K-LCR workflow and data boundaries. |
| `docs/GOVERNANCE.md` | K-SFTs label/governance patterns, rewritten | K-LCR branch state, owner approval and configured controls. |

`.github/dependabot.yml`, `tools/check_files.py` and `docs/SOURCE_CONTROL.md`
were written for this repository; Dependabot uses standard GitHub Actions
configuration and pinned upstream actions. `README.md`,
`docs/REPOSITORY_STRUCTURE.md` and `docs/DECISIONS.md` describe K-LCR
decisions. This register does not assign copyright in source files to someone
else or claim ownership of third-party tools.

When importing more source, record its origin, immutable revision, applicable
license and local changes here in the importing PR. Do not copy proprietary
workbooks, regulatory document text, third-party code or imagery merely
because they are accessible. A citation/link to an official regulatory source
is preferable to redistributing its full text.

## 🧰 External tools

The workflows use `actions/checkout`, `actions/setup-python`,
`actions/setup-node` and `actions/upload-artifact` pinned by commit SHA; they
are dependencies fetched by GitHub Actions, not vendored files in K-LCR. The
Repository integrity workflow downloads the
[actionlint](https://github.com/rhysd/actionlint) 1.7.12 release binary and
verifies it against a pinned SHA-256 before use; it is not redistributed.
It also installs Ruff, mypy and their dependencies from PyPI at the versions
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
