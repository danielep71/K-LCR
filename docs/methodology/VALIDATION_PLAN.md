# ✅ LCR validation plan

**Planned cases for both profiles · Oracles before implementation**

This plan lists the cases each profile needs before its rules can be called
validated. A case is registered in `tests/cases/` in the format of
[TEST_CASES.md](TEST_CASES.md) when its inputs and expected values are ready.
Each planned case follows my decisions A01 to A09 and the requirement map in
[APPLICABILITY.md](APPLICABILITY.md). Every case runs once for the EU profile
and once for Basel, unless its row names one profile.

## 🧭 Oracles

- **Expected values come from outside the code under test.** Each numeric
  expectation needs a `published` value from a registered source, or an
  `independent` value from a registered external implementation.
- Values derived in this repository stay `illustrative` and validate nothing.
- No `published` worked LCR example has been registered yet, and no
  independent implementation is registered as `IMPL-`. Finding them is the
  first task of numerical validation (B005).
- `contract` values for `input_status` and `input_findings` are executed today
  against the input validator; `result_status` is registered only.

## 🗺️ Planned cases

Status: `registered` (in `tests/cases/`) or `planned`.

| ID | Category | Requirements | What the case shows | Status |
| --- | --- | --- | --- | --- |
| `PC-01` | nominal | REQ-01, REQ-09 to REQ-11, REQ-17, REQ-22 | A small mixed portfolio: buffer, outflows, inflows and ratio | planned |
| `PC-02` | boundary | REQ-01 | Net outflows of zero: `result_status` `failed` with `CALC-ZERO-NET-OUTFLOWS`, no ratio | planned |
| `PC-03` | boundary | REQ-02, REQ-22 | Items maturing on the last day of the 30-day horizon and on the next day | planned |
| `PC-04` | boundary | REQ-23 | The inflow cap exactly binding, just binding and not binding | planned |
| `PC-05` | boundary | REQ-13 | Each composition limit exactly binding and not binding, before and after the unwind of secured transactions | planned |
| `PC-06` | boundary | REQ-07, REQ-14 | A holding with `requirements_met` `N`, left out with `CALC-ASSET-EXCLUDED`; the 30 calendar days of Art. 18(1) are not modelled | planned |
| `PC-07` | boundary | REQ-03 | A ratio just below and just at the minimum: `CALC-BELOW-MINIMUM` only below | planned |
| `PC-08` | boundary | REQ-16 | Derivatives netted within a netting set and not across sets | planned |
| `PC-09` | boundary | REQ-19 | Secured funding, lending and collateral swaps for each collateral level | planned |
| `PC-10` | nominal | REQ-06 | Amounts converted from several original currencies; totals in the reporting currency only (A02) | planned |
| `PC-11` | nominal | REQ-05 | The same portfolio declared `INDIVIDUAL` and `CONSOLIDATED`: identical figures, since K-LCR does not consolidate (A01) | planned |
| `PC-12` | nominal | REQ-01 | The records of `PC-01` in reverse order: identical figures | planned |
| `PC-13` | invalid-input | REQ-11, REQ-12, REQ-15 (Basel), REQ-17, REQ-21, REQ-24 | Each excluded category of `categories.json` rejected with `LCR-OUT-OF-SCOPE` (A03, A04 and A06) | planned |
| `PC-14` | invalid-input | — | One case per input-contract finding group: structure, field, run and category rules | planned |
| `PC-15` | invalid-parameters | — | A parameter set of the other profile, or an incomplete one: `CALC-PARAMETER-SET-PROFILE` or `CALC-PARAMETER-SET-INVALID` | planned |
| `PC-16` | nominal | REQ-11 | Basel only: Level 2B included or not by the parameter set's discretion choice (A07) | planned |
| `PC-17` | nominal | REQ-13 | The same mapped inputs under both profiles, with the composition difference explained (I03) | planned |
| `PC-18` | boundary | REQ-18 | Unsecured wholesale funding: counterparty classification and the operational-deposit boundary, with the parameter set's rates | planned |
| `PC-19` | boundary | REQ-20 | Each additional-outflow, facility and other contingent category, with its parameter | planned |
| `illustrative-eu-input-totals` | nominal | — | EU only. Format example: synthetic input totals from a derivation script | registered |
| `illustrative-eu-rejected-input` | invalid-input | — | EU only. Format example: a negative amount rejected by the input contract | registered |

Requirements with no planned case, and why:

- `REQ-04`, `REQ-26`: no test direction; the scenario and the reporting are
  outside the calculation.
- `REQ-08`: diversification is a diagnostic only and no diagnostic code is
  registered for it, so there is nothing to execute; a case follows with the
  code.
- `REQ-15` (EU), `REQ-23` exemptions, `REQ-25` and the significant-currency
  LCR of A02: no input represents them (A02, A04 to A06), so no input can
  claim them and no rejection can be tested.

## 📊 Evidence for a validated rule

A rule of a profile is validated when:
1. at least one `published` or `independent` case covering it executes and
   passes against the implementation of the rule;
2. its `boundary`, `invalid-input` and `invalid-parameters` cases from this
   plan are registered and pass;
3. the case's `review.status` is `reviewed`.

Each release lists which rules are validated, under which source edition and
parameter set, and every rule that is implemented but not validated.

## ⏳ Not in this plan

- Excel host behaviour: import, compile and cleanup are the evidence of #14
  and #15.
- Production numerical validation with sourced parameter sets: it follows the
  implementation (B001 to B005) and is linked from it.
