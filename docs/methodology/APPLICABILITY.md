# 🧭 LCR applicability and requirement map

**Register version 1 · Decisions of 2026-11-03 · No parameter values established here**

This map links each LCR topic to its locators in the
[source register](SOURCES.md), for the EU profile (`SRC-01`, `SRC-02`) and the
Basel profile (`SRC-06`). Each entry names the planned requirement, the
parameter set that will hold its values and the tests that will cover it. It
then records what the sources resolve and what they leave to me.

It states no percentage, run-off rate, haircut or threshold. Those values
enter a parameter set only through #10, each with its register ID and
locator, and are tested only through #11.

## 🧩 Planned parameter sets

| Parameter set | Profile | Sources | Status |
| --- | --- | --- | --- |
| `EU-LCR-DA-2022-07-08` | EU | `SRC-02` as consolidated on 2022-07-08, with `SRC-01` as consolidated on 2026-06-26 | Planned (#10) |
| `BASEL-LCR-2019-12-15` | Basel | `SRC-06`, version effective as of 15 December 2019 | Planned (#10) |

A parameter set's identifier names its source edition. A new edition creates
a new parameter set; it never changes an existing one. Each run names its
parameter set explicitly (see [REPOSITORY_STRUCTURE.md](../REPOSITORY_STRUCTURE.md#-regulatory-profiles)).

## 🗺️ Requirement map

Locators are articles of `SRC-02` unless marked `CRR` (`SRC-01`), and
paragraphs of `SRC-06`. A dash means no counterpart has been located in that
profile; it is not a claim that none exists.

| ID | Topic | EU locators | Basel locators | Future tests (#11) |
| --- | --- | --- | --- | --- |
| `REQ-01` | Ratio: liquidity buffer over net liquidity outflows | Art. 4(1); Annex II; CRR Art. 412(1) | LCR20.5; LCR40.1 | Ratio from known numerator and denominator; rejection of an empty denominator |
| `REQ-02` | Horizon of 30 calendar days | Art. 4(1); Art. 17(2) | LCR20.1; LCR20.5; LCR40.1 | Items maturing on the last day inside and the first day outside the horizon |
| `REQ-03` | Minimum requirement, use of the buffer in stress, non-compliance | Art. 4(2) to (4); CRR Art. 412 and 414 | LCR20.5 to LCR20.8 | Reported status below and above the minimum; no automatic remedy |
| `REQ-04` | Stress scenario | Art. 5 | LCR20.2 | None: scenario description only |
| `REQ-05` | Entity scope: individual and consolidated application | Art. 2; CRR Art. 6(4), 8 and 11(3) | LCR10.1 to LCR10.8 | Declared perimeter type; no consolidation performed (A01) |
| `REQ-06` | Currencies: reporting currency and significant currencies | Art. 4(5); Art. 8(6); CRR Art. 415(2) | LCR10.9; LCR30.29 | Converted amounts with their original currency; rejection of a significant-currency LCR (A02) |
| `REQ-07` | Liquid assets: general and operational requirements, valuation | Art. 6 to 9 | LCR30.2 to LCR30.28 | Assets that fail one requirement are excluded, with a diagnostic |
| `REQ-08` | Diversification of the buffer | Art. 8(1) | LCR30.29 | Diagnostic only: no limit is computed |
| `REQ-09` | Level 1 assets | Art. 10 | LCR30.40; LCR30.41 | Classification and valuation per category |
| `REQ-10` | Level 2A assets | Art. 11 | LCR30.42; LCR30.43 | Classification, haircut from the parameter set |
| `REQ-11` | Level 2B assets | Art. 12 | LCR30.44 to LCR30.46 | Classification; Basel inclusion only where the parameter set enables it |
| `REQ-12` | Special asset categories | Art. 13 to 16 | LCR30.47 | Rejection while out of scope (A03) |
| `REQ-13` | Buffer composition by level, with unwind of transactions within the horizon | Art. 17; Annex I | LCR30.31 to LCR30.39 | Each composition limit binding and not binding; unwind of secured transactions |
| `REQ-14` | Breach of composition requirements | Art. 18 | — | Reported breach |
| `REQ-15` | Alternative liquidity approaches | Art. 19 | LCR31; LCR30.32 | Rejection while out of scope (A04) |
| `REQ-16` | Net outflows and netting of derivatives | Art. 20 and 21; Annex II | LCR40.1 to LCR40.4; LCR40.49; LCR40.91 | Netting by counterparty and netting set; no double counting (LCR40.4) |
| `REQ-17` | Retail deposit outflows | Art. 24 and 25 | LCR40.5 to LCR40.18 | Category boundaries from the parameter set |
| `REQ-18` | Unsecured wholesale funding, operational deposits, other liabilities | Art. 27; Art. 28(1), (2) and (5) to (7) | LCR40.19 to LCR40.44 | Counterparty and operational-deposit classification |
| `REQ-19` | Secured funding and collateral swaps | Art. 28(3) and (4) | LCR40.45 to LCR40.48 | Treatment by collateral level |
| `REQ-20` | Additional outflows, credit and liquidity facilities, other contingent and contractual outflows | Art. 23, 30, 31 and 31a | LCR40.49 to LCR40.74 | Each category, with its parameter |
| `REQ-21` | Outflows with inter-dependent inflows | Art. 26 | — | Rejection while out of scope (A06) |
| `REQ-22` | Inflows | Art. 32 | LCR40.75; LCR40.76; LCR40.78 to LCR40.93 | Only performing contractual inflows within the horizon; no contingent inflows |
| `REQ-23` | Cap on inflows and its exemptions | Art. 33 | LCR40.77 | Cap binding and not binding; exemptions rejected while out of scope (A06) |
| `REQ-24` | Intragroup and institutional protection scheme treatments | Art. 29 and 34 | — | Rejection while out of scope (A06) |
| `REQ-25` | Transitional and grandfathering provisions | Art. 35 to 38 | LCR90 | Rejection while out of scope (A05) |
| `REQ-26` | Reporting and disclosure | CRR Art. 415, 416 and 451a; `SRC-05` | LCR20.7; LCR20.8 | None: outside the calculation, informs #10 only |

`LCR99` summarises the Basel factors; the cited chapter paragraphs remain the
source of each value. The tests listed are directions for #11, not fixtures.

## ✅ Resolved by the sources

Each resolution below was read in the located text on 2026-11-03.

| ID | Resolution | EU | Basel |
| --- | --- | --- | --- |
| `R01` | Both profiles measure the buffer against net outflows over the next 30 calendar days. | Art. 4(1) | LCR20.1; LCR40.1 |
| `R02` | Both profiles compute the ratio for all items in one currency: EU in the reporting currency; Basel in a common currency on a consolidated basis. | Art. 4(5), first subparagraph | LCR10.9 |
| `R03` | Inflows are limited relative to outflows by a cap. The EU allows exemptions, or a different cap for specialised institutions, only with the competent authority's prior approval. | Art. 33(1) to (4) | LCR40.77 |
| `R04` | The level composition limits apply after unwinding secured funding, secured lending and collateral swaps that mature within 30 calendar days. | Art. 17(2) | LCR30.34 to LCR30.37 |
| `R05` | Several Basel parameters are set by national authorities, and Level 2B assets are included only at their discretion. | — | LCR40.2; LCR30.44 |
| `R06` | Some EU treatments need the competent authority's prior approval or case-by-case authorisation. | Art. 26; Art. 29(1); Art. 33(2) to (4); Art. 34(1) | — |

## ✅ My applicability decisions — 2026-11-03

I decided these positions on 2026-11-03 (#126). They set the perimeter of
the contracts in #10 and the fixtures in #11; they implement no calculation.
An item outside them is rejected with a diagnostic, never ignored and never
given a default.

| ID | Decision | Consequence for #10 and #11 | EU locators | Basel locators |
| --- | --- | --- | --- | --- |
| `A01` | One perimeter per run, declared in the input as individual or already consolidated. K-LCR does not consolidate. | The input names its perimeter type. No group structure, third-country asset rule or liquidity transfer restriction is modelled. | Art. 2; CRR Art. 6(4), 8 and 11(3) | LCR10.1 to LCR10.8 |
| `A02` | Only the LCR in the reporting currency. Every amount arrives converted, and keeps its original currency. The separate LCR in each significant currency is later work. | Amounts are in the reporting currency, with an original-currency field. A request for a significant-currency LCR is rejected. | Art. 4(5); Art. 8(6) | LCR10.9; LCR30.29 |
| `A03` | Level 1, 2A and 2B assets only. | The special categories are rejected. | Art. 10 to 16 | LCR30.40 to LCR30.47 |
| `A04` | Alternative liquidity approaches are out of scope. | Rejected. | Art. 19 | LCR31 |
| `A05` | Transitional and grandfathering provisions are out of scope. | Rejected. | Art. 35 to 38 | LCR90 |
| `A06` | Treatments that need supervisory approval or authorisation (R06) are out of scope. | Inputs claiming them are rejected. The inflow cap of Art. 33(1) and LCR40.77 always applies. | Art. 26, 29, 33(2) to (6) and 34 | — |
| `A07` | Each Basel national discretion (R05) is a required parameter with no default. The parameter set records the choice, and fixtures use values labelled illustrative. | The Basel parameter schema makes every discretionary entry mandatory. | — | LCR10.4; LCR10.5; LCR30.44; LCR40.2; LCR40.93 |
| `A08` | The contracts cover every standard outflow and inflow category, with the inflow cap. Implementation may come in stages. The treatments excluded by A06 stay out. | The category lists of the data contract are complete for both profiles. | Art. 22 to 25, 27, 28, 30, 31, 31a, 32 and 33(1) | LCR40 |
| `A09` | No copy of BIS material is stored. EU copies (`SRC-02` in full and an extract of `SRC-01`) are stored only after I check the EUR-Lex legal notice on reuse. | I checked the notice on 2026-11-03: the copies are in [sources/](sources/README.md) (#129). | `SRC-01`, `SRC-02` | `SRC-06` |

## 🔍 Unresolved interpretations

| ID | Question | Locators | Follow-up |
| --- | --- | --- | --- |
| `I01` | Article 4(4) of `SRC-02` refers to Implementing Regulation (EU) No 680/2014 for reporting below the minimum. The current reporting standard is `SRC-05`. Which text governs the reporting fields that #10 maps? | Art. 4(4); `SRC-05` | #10 |
| `I02` | CRR Articles 416 to 425 are reporting provisions written "pending the specification of a liquidity requirement in accordance with Article 460" (Article 420(1)). The EU profile calculates under `SRC-02`. Which of those articles, if any, the profile also needs is open. | CRR Art. 416 to 425 and 460 | #10 |
| `I03` | The EU text states its composition requirements as three limits on the buffer. Basel states two caps on Level 2 assets and gives an adjustment formula. The two are compared only on deliberately mapped inputs, with the difference explained. | Art. 17; Annex I; LCR30.31 to LCR30.39 | #11 |
| `I04` | `SRC-05`'s annexes, with the reporting templates, were not retrieved. Whether the data contract follows those templates is open. | `SRC-05` | #10 |

A resolved interpretation moves to the resolutions table, citing the source
or the decision that resolved it.
