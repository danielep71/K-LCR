# 📐 Methodology

**Sources first · Explicit profiles · No unsourced regulatory claims**

This folder holds the regulatory basis of K-LCR's EU and Basel profiles. No
formula is implemented or validated yet. The data, parameter and output
contracts come in #10, and the independent fixtures in #11.

| Document | Content |
| --- | --- |
| [SOURCES.md](SOURCES.md) | Source register: each regulatory text with its edition, retrieval record, status and the locators used |
| [APPLICABILITY.md](APPLICABILITY.md) | Requirement map from LCR topics to EU and Basel locators, planned parameter sets and tests; what the sources resolve; my applicability decisions and the unresolved interpretations |

Rules for every document, parameter set and fixture:

- A regulatory statement cites a register ID and a locator, for example
  `SRC-02` Art. 4(1) or `SRC-06` LCR40.77. Without one, it is labelled as an
  assumption.
- The EU and Basel profiles never borrow each other's rules or values.
- An open decision or interpretation is never replaced by a default: the
  profile rejects the item with a diagnostic until it is resolved.
