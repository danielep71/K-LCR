# Architecture decisions and follow-on backlog

## Accepted owner decisions — 2026-10-28

These decisions were supplied by @danielep71 while implementing issue #3.

| ID | Decision | Consequence |
| --- | --- | --- |
| D001 | Excel/VBA | VBA core with a separate Excel adapter; existing Python/Node remain developer tooling. |
| D002 | EU and Basel profiles | Explicit, independently versioned profiles and source mappings; no implicit fallback between them. |
| D003 | Reference and independent validation | Prioritize traceable calculations, synthetic examples, independent oracles and diagnostics; no operational certification claim. |

The [scope and architecture](REPOSITORY_STRUCTURE.md) implements these decisions.
The initial Windows desktop Excel 64-bit target is an engineering baseline;
exact supported builds and tested configurations remain subject to #6 and #15.

## Remaining setup decisions

| Decision or deliverable | Tracking issue | Completion evidence |
| --- | --- | --- |
| Licensing, imported-code provenance and confidentiality policy | #4 | Owner decision and applicable notices/policies |
| Source layout, encoding and generated-file handling | #5 | Conventions and fresh-checkout evidence |
| Host matrix, API/error/type conventions and import/export rules | #6 | Documented in VBA_HOUSE_STYLE.md and INSTALLATION.md; supported-host evidence remains in #14/#15 |
| Exact EU/Basel source editions, applicability and interpretation register | #9 | Authoritative sources and resolved requirements |
| Data, parameter and output schemas; units and reconciliation | #10 | Versioned contracts and synthetic examples |
| Independent fixture schema and comparison/rounding rules | #11 | Independently derived examples and validation criteria |
| Neutral scaffold, workbook synchronization and real host evidence | #13, #14, #15 | Executed evidence bound to the tested candidate |

Do not silently turn an unresolved item into a default. Record the owner decision
or source-based resolution in its tracking issue and update the relevant document.

## Follow-on backlog after repository setup

These are planning entries, not implemented features or scheduled promises.
Before starting an entry, create a scoped issue with owner, priority, milestone,
target end date, dependencies and checkable acceptance criteria. The owner selects
the next milestone; these entries do not expand v0.1.0.

| ID | Work | Entry conditions and acceptance direction |
| --- | --- | --- |
| B001 | Basel calculation profile | Source register, schemas and fixture rules complete; map each implemented rule to source sections and independent fixtures. |
| B002 | EU calculation profile | Same foundations plus explicit EU applicability decisions; implement and test differences without silently inheriting Basel behavior. |
| B003 | Shared calculation and reconciliation core | Demonstrated common semantics only; deterministic intermediate totals, errors and repeatability tests. |
| B004 | Public VBA API and Excel analytical workbook | Stable contracts and approved host conventions; test input mapping, diagnostics, output lineage and host-state cleanup. |
| B005 | Independent numerical validation | Cover each implemented rule and applicable boundary/invalid cases with independently derived expected values; explain EU/Basel differences. |
| B006 | Reproducible reference examples and packaging | Real supported-host evidence, validated examples, versioned provenance and installation instructions; owner-approved packaging. |
| B007 | Operational-use assessment, only if requested | Separate owner-approved scope, legal/licensing review, data/security controls, operational testing and independent acceptance before production use. |

Sequencing is governed by actual dependencies: no formula implementation before
its sources/contracts are resolved, and no numerical certification before
independent validation and host evidence. Scope changes need a new dated decision;
preserve earlier decisions as history rather than rewriting what was approved.
