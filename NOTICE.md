# Licensing, provenance and data

Copyright 2026 Daniele Penza and contributors.

The owner selected the Mozilla Public License 2.0 on 2026-10-28 for K-LCR.
Code, documentation, workflows and configuration contributed to K-LCR are
covered by [LICENSE](LICENSE), unless an individual file states otherwise.
This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at https://mozilla.org/MPL/2.0/.

This is a private, independent reference project. The license decision does
not change repository visibility or grant permission to disclose client,
employer or third-party material. Distribution and publication remain separate
owner decisions.

## Imported material

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
| `.editorconfig`, `.gitattributes`, `.gitignore` | K-SFTs at the source revision; adapted under #5 | K-LCR paths, no preselected VBA encoding, no regulatory-copy or workbook-template exception; same normalization, binary and ignore policy. |
| `.github/labels.json`, `.github/label-policy.json` | K-SFTs files at the source revision; same blobs | Selected application profile with no domain overlay. |
| `.github/scripts/labels-sync.mjs`, `.github/scripts/labels-drift.mjs` | K-SFTs files at the source revision; same blobs | Used with K-LCR repository variables and policy. |
| `.github/ISSUE_TEMPLATE/` | K-SFTs issue forms/configuration, adapted | K-LCR descriptions, assignee, links and platform-neutral guidance. |
| `.github/workflows/labels-sync.yml`, `labels-drift.yml`, `issue-triage.yml` | K-SFTs workflow patterns, adapted | K-LCR triggers, permissions and current issue-triage script. |
| `tools/check_issues.py`, `tools/test_check_issues.py` | K-SFTs triage logic/tests, adapted | K-LCR repository identity and relevant regression cases. |
| `docs/VBA_HOUSE_STYLE.md`, `INSTALLATION.md` | K-SFTs style and installation structure at the source revision, adapted | K-LCR naming, EU/Basel profile boundary and untested host status; no copied SFT formulas, tested-host claims or workbook paths. |
| `SECURITY.md` | K-SFTs security-policy structure at the source revision, adapted | Private reporting without assuming public-only reporting features or a published version; K-LCR workflow and data boundaries. |
| `docs/GOVERNANCE.md` | K-SFTs label/governance patterns, rewritten | K-LCR branch state, owner approval and configured controls. |

`.github/workflows/repository-integrity.yml` and `.github/dependabot.yml`
were written for this repository, using standard GitHub Actions configuration
and pinned upstream actions. `README.md`, `docs/REPOSITORY_STRUCTURE.md`
and `docs/DECISIONS.md` describe K-LCR decisions. This register does not
assign copyright in source files to someone else or claim ownership of
third-party tools.

When importing more source, record its origin, immutable revision, applicable
license and local changes here in the importing PR. Do not copy proprietary
workbooks, regulatory document text, third-party code or imagery merely
because they are accessible. A citation/link to an official regulatory source
is preferable to redistributing its full text.

## External tools

The workflows use `actions/checkout`, `actions/setup-python` and
`actions/upload-artifact` pinned by commit SHA; they are dependencies fetched
by GitHub Actions, not vendored files in K-LCR. Python and Node runtimes used
for repository checks are not bundled. Verify upstream license/version metadata
when adding or changing a dependency; preserve any required notices.

## Data and privacy

Fixtures, bug reports, examples and documentation use synthetic data only.
Do not commit client, employer, counterparty, customer, personal or proprietary
information, credentials, private workbooks, non-public regulatory material or
unapproved artwork. See [SECURITY.md](SECURITY.md). A file audit and a narrow
credential/organization-name pattern check of the 19 tracked files at
`release/0.1.0` on 2026-10-28 found no such material. Pattern checks do
not prove that future contributions or unrecognizable confidential data are safe;
review provenance and contents at every import and in the final #21 audit.
