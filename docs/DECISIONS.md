# 🧭 Architecture decisions and follow-on backlog

[![Stack: Excel VBA](https://img.shields.io/badge/Stack-Excel_VBA-217346?style=flat-square)](#-my-accepted-decisions--2026-10-28)
[![Profiles: EU + Basel planned](https://img.shields.io/badge/Profiles-EU_%2B_Basel_planned-1f3a5f?style=flat-square)](#-my-accepted-decisions--2026-10-28)

## ✅ My accepted decisions — 2026-10-28

These decisions were supplied by @danielep71 while implementing issue #3.

| ID | Decision | Consequence |
| --- | --- | --- |
| D001 | Excel/VBA | VBA core with a separate Excel adapter; existing Python/Node remain developer tooling. |
| D002 | EU and Basel profiles | Explicit, independently versioned profiles and source mappings; no implicit fallback between them. |
| D003 | Reference and independent validation | Prioritize traceable calculations, synthetic examples, independent oracles and diagnostics; no operational certification claim. |

The [scope and architecture](REPOSITORY_STRUCTURE.md) implements these decisions.
The initial Windows desktop Excel 64-bit target is an engineering baseline;
exact supported builds and tested configurations remain subject to #15.

## ✅ Completed setup decisions

| Decision or deliverable | Tracking issue | Evidence |
| --- | --- | --- |
| Licensing, imported-code provenance and confidentiality policy | #4 | [NOTICE](../NOTICE.md), [LICENSE](../LICENSE) and [SECURITY](../SECURITY.md) |
| Source layout, encoding and generated-file handling | #5 | [Source control](SOURCE_CONTROL.md), `.editorconfig`, `.gitattributes` and `.gitignore` |
| General host, API, numeric-type and source-authoring conventions | #6 | [VBA house style](VBA_HOUSE_STYLE.md) and [Installation](../INSTALLATION.md); actual host execution remains #14/#15 |
| EU/Basel source editions, requirement map, source-based resolutions and interpretation register | #9 | [Source register](methodology/SOURCES.md) and [applicability map](methodology/APPLICABILITY.md) |
| EU and Basel applicability positions for v0.1 | #126 | My decisions A01 to A09 of 2026-11-03 in the [applicability map](methodology/APPLICABILITY.md#-my-applicability-decisions--2026-11-03) |
| Input, parameter-set and result contracts; units, reconciliation, fingerprints and diagnostics | #10 | [Input contract](methodology/DATA_CONTRACT.md), [parameter sets and results](methodology/PARAMETERS_AND_RESULTS.md), their validators and synthetic fixtures |
| Test-case format, oracle and comparison rules, validation plan | #11 | [Test cases](methodology/TEST_CASES.md), [validation plan](methodology/VALIDATION_PLAN.md), `tools/check_test_cases.py` and two neutral examples |
| VBA static checks: conditional compilation, jumps, native, dynamic and COM constructs, reviewed host exceptions | #12 | [Static checks](VBA_HOUSE_STYLE.md#-static-checks), the `vba-conditionals`, `vba-jumps` and `vba-dynamic` gates and their fixtures in `tools/test_check_vba.py` |

## 📋 Remaining setup decisions

| Decision or deliverable | Tracking issue | Completion evidence |
| --- | --- | --- |
| Neutral scaffold, workbook synchronization and real host evidence | #13, #14, #15 | Executed evidence bound to the tested candidate |

Do not silently turn an unresolved item into a default. Record my decision
or the source-based resolution in its tracking issue and update the relevant document.

## 🗺️ Follow-on backlog after repository setup

These are planning entries, not implemented features or scheduled promises.
Before starting an entry, create a scoped issue with owner, priority, milestone,
target end date, dependencies and checkable acceptance criteria. I select
the next milestone; these entries do not expand v0.1.0.

| ID | Work | Entry conditions and acceptance direction |
| --- | --- | --- |
| B001 | Basel calculation profile | Source register, schemas and fixture rules complete; map each implemented rule to source sections and independent fixtures. |
| B002 | EU calculation profile | Same foundations plus explicit EU applicability decisions; implement and test differences without silently inheriting Basel behavior. |
| B003 | Shared calculation and reconciliation core | Demonstrated common semantics only; deterministic intermediate totals, errors and repeatability tests. |
| B004 | Public VBA API and Excel analytical workbook | Stable contracts and approved host conventions; test input mapping, diagnostics, output lineage and host-state cleanup. |
| B005 | Independent numerical validation | Cover each implemented rule and applicable boundary/invalid cases with independently derived expected values; explain EU/Basel differences. |
| B006 | Reproducible reference examples and packaging | Real supported-host evidence, validated examples, versioned provenance and installation instructions; packaging approved by me. |
| B007 | Operational-use assessment, only if requested | Separate scope approved by me, legal/licensing review, data/security controls, operational testing and independent acceptance before production use. |

Sequencing is governed by actual dependencies: no formula implementation before
its sources/contracts are resolved, and no numerical certification before
independent validation and host evidence. Scope changes need a new dated decision;
preserve earlier decisions as history rather than rewriting what was approved.
