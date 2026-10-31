# 🏗️ K-LCR scope and architecture

[![Architecture: VBA + Excel host](https://img.shields.io/badge/Architecture-VBA_%2B_Excel_host-217346?style=flat-square)](#-implementation-and-host-profile)
[![Maturity: Setup](https://img.shields.io/badge/Maturity-Setup-BF8700?style=flat-square)](#-purpose-and-maturity)

## ✨ Purpose and maturity

K-LCR is an Excel/VBA reference implementation of the Liquidity Coverage Ratio
for learning, research and independent validation. Intended users are risk
analysts, validators, researchers and educators working with synthetic examples
and independently sourced expected results.

The owner selected Excel/VBA, separate EU and Basel profiles, and reference and
validation use on 2026-10-28 in issue #3. The repository currently contains setup
tooling and documentation: it has no LCR calculation engine or validated workbook.
This document defines the intended design, not functionality already delivered.

v0.1.0 establishes governance, source conventions, contracts, test scaffolding
and evidence requirements. It does not certify regulatory compliance or readiness
for operational bank reporting. Production use would require a separate scope
decision, data controls, independent validation and operational acceptance.

## 📚 Regulatory profiles

EU and Basel are distinct planned profiles, not interchangeable labels for one
parameter set. Neither profile is implemented or numerically validated yet.

Every future run must identify the profile, regulatory source edition, parameter
version and reporting date explicitly. Missing or unsupported combinations must
fail validation rather than silently selecting a default or substituting the
other profile. Shared code is permitted only where the documented semantics agree;
profile-specific classification, parameters and rules remain explicit.

Issue #9 establishes the authoritative source register and exact applicability
decisions before formula work starts. Issue #10 defines schemas and issue #11
defines independently derived validation fixtures. No percentages, thresholds,
eligibility rules or effective-date claims are established by this architecture
document. Compare profiles only on deliberately mapped inputs with explained
differences.

Planned analytical scope includes asset/liquidity-buffer classification, inflow
and outflow treatment, intermediate reconciliations, diagnostics and ratio
outputs. The precise perimeter, currency and entity aggregation rules are
requirements to resolve through those source and data-contract issues.

## 🖥️ Implementation and host profile

The calculation implementation is VBA. Excel provides input/output and the user
interface; Python and Node scripts in this repository are development/CI tooling,
not an alternative production calculation engine.

Initial engineering target: desktop Excel for Microsoft 365 on Windows, 64-bit.
This is a planning baseline, not tested support. Record the actual Excel build,
Windows version, architecture and locale in host evidence. The host/API
conventions settled in #6 are in [VBA house style](VBA_HOUSE_STYLE.md); issue
#15 provides genuine import, compile and test evidence before any
supported-host claim.

| Host | Current status |
| --- | --- |
| Windows desktop Excel, 64-bit | Initial target; not tested or certified. |
| Windows desktop Excel, 32-bit | Outside the initial test target; add only by an explicit compatibility decision. |
| macOS, web and mobile Excel | Outside the initial target; no compatibility claim. |

The portable core must not rely on operating-system APIs, COM automation,
worksheet state or Excel object-model calls. Host-specific functionality belongs
behind explicit adapters and follows [VBA house style](VBA_HOUSE_STYLE.md).
Do not infer support from the absence of known failures.

## 🔀 Boundaries and data flow

1. The Excel adapter reads explicitly identified workbook inputs and converts
   them to the versioned input contract.
2. The public VBA API validates the request, including the explicit profile and
   parameter/source versions, then invokes deterministic core calculations.
3. The core returns results and structured diagnostics without reading or
   changing worksheets, files, the network, clock, random state or global settings.
4. The adapter writes outputs and presentation separately; it restores any host
   state it changes and reports host failures distinctly from calculation errors.

The core receives all required input and configuration explicitly and treats
them as immutable. Identical validated inputs and versions must produce identical
results. Workbook layout, formatting and application state cannot change the
meaning of the calculation. Do not duplicate regulatory logic in worksheet
formulas or host adapters.

The API owns the contract boundary, validation orchestration and stable error
categories. The core owns calculations; the host adapter owns workbook mapping,
presentation and user interaction. Numeric types follow
[VBA house style](VBA_HOUSE_STYLE.md). Input schemas are specified in #10 and
rounding and tolerances in #11 before implementation; concrete function
signatures are fixed with the first API implementation.

An independent validation fixture must not obtain its sole expected value from
the code it tests. Record its source or derivation and distinguish registered,
executed, passed, failed and not-run cases. A green portable CI run is not Excel
execution evidence or numerical certification.

## 🗂️ Repository layout

Create a directory only with its first meaningful file. Proposed paths below
are not claims that those components exist today.

| Path | Purpose | Status |
| --- | --- | --- |
| README.md | Entry point, maturity and navigation | Present |
| docs/ | Governance, repository settings, scope, decisions, contracts and evidence guidance | Present |
| .github/ | Labels, issue forms, pull request template, dependency configuration and workflows | Present |
| tools/ | Portable checks and developer utilities | Present |
| src/core/ | Host-independent VBA calculations and profile rules | Planned |
| src/api/ | Public VBA entry points, validation orchestration and contracts | Planned |
| src/host/excel/ | Workbook input/output and user-interface adapters | Planned |
| tests/unit/ | Core/API tests independent of workbook layout | Planned |
| tests/fixtures/eu/ | EU fixtures with independent expected results | Planned |
| tests/fixtures/basel/ | Basel fixtures with independent expected results | Planned |
| tests/host/ | Excel import, compile, adapter and cleanup checks | Planned |
| templates/ | Explicitly allowlisted source workbook template | Planned |
| test-results/ | Reports generated by `tools/check.py`; not source content | Ignored by Git |

Dependency direction is host -> API -> core. The core never imports a host
component; tests may exercise each layer. Keep profile identifiers explicit in
fixtures and diagnostics. Use descriptive filenames and stable case IDs.

VBA exported component names use the K-LCR namespace without a hyphen:
`LCR_Core_<Name>`, `LCR_API_<Name>`, `LCR_Excel_<Name>`; tests use `TEST_LCR_<Name>`.
Keep component names within VBA's limits. Profile-specific names include EU or
Basel. Module/class prefixes, exported extensions and the ASCII source rule are
defined in [VBA house style](VBA_HOUSE_STYLE.md); VBE import behavior is
verified in #14/#15. Repository paths use consistent lowercase directory names;
do not create generic placeholder modules solely to fill the layout.

## 🗺️ Setup exclusions and follow-on work

v0.1.0 does not deliver production formulas, a completed calculation workbook,
regulatory reporting submission, bank-system integration, real customer data,
automated regulatory updates, deployment, public hosting or numerical certification.
A neutral test scaffold or template proves infrastructure only.

The [decision log and follow-on backlog](DECISIONS.md) records accepted direction,
remaining decisions and the work to schedule after setup. Work moves through
release/0.1.0 first; integration into main follows explicit owner authorization
under [governance](GOVERNANCE.md).
