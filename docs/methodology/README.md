# 📐 Methodology

**Sources first · Explicit profiles · No unsourced regulatory claims**

This folder holds the regulatory basis of K-LCR's EU and Basel profiles. The
[prototype workbook](../PROTOTYPE.md) implements the EU formulas outside these
contracts; no formula is validated yet. The input, parameter and result
contracts (#10) and the test-case format with two illustrative cases (#11)
are in place; no independent or published case exists yet.

| Document | Content |
| --- | --- |
| [SOURCES.md](SOURCES.md) | Source register: each regulatory text with its edition, retrieval record, status and the locators used |
| [DATA_CONTRACT.md](DATA_CONTRACT.md) | Input contract of a run: files, format, fields, findings, reconciliation and fingerprint; machine-readable in [data-contract.json](data-contract.json), with the categories of each profile in [categories.json](categories.json) |
| [PARAMETERS_AND_RESULTS.md](PARAMETERS_AND_RESULTS.md) | Layout of parameter sets and results, and the diagnostic codes; machine-readable in [parameter-result-contract.json](parameter-result-contract.json) |
| [TEST_CASES.md](TEST_CASES.md) | Format of a registered test case: metadata, expected outputs, reference classes, tolerance and comparison rules, registered versus executed |
| [TEST_HARNESS.md](TEST_HARNESS.md) | The neutral VBA test harness: modules, run outcomes, example modes, log format and reproducibility; source only, not yet run in Excel |
| [VALIDATION_PLAN.md](VALIDATION_PLAN.md) | The cases each profile needs, their oracles, and when a rule counts as validated |
| [APPLICABILITY.md](APPLICABILITY.md) | Requirement map from LCR topics to EU and Basel locators, planned parameter sets and tests; what the sources resolve; my applicability decisions and the unresolved interpretations |

Rules for every document, parameter set and fixture:

- A regulatory statement cites a register ID and a locator, for example
  `SRC-02` Art. 4(1) or `SRC-06` LCR40.77. Without one, it is labelled as an
  assumption.
- The EU and Basel profiles never borrow each other's rules or values.
- An open decision or interpretation is never replaced by a default: the
  profile rejects the item with a diagnostic until it is resolved.
