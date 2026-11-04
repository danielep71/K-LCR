# 🧪 LCR test cases

**Registered cases · Independent oracles · Explicit tolerances**

This document defines how K-LCR records a numerical test case: its inputs,
its metadata, the values it expects and where each value comes from. It also
defines how an actual result is compared with an expected one, and when a case
counts as validation. The [validation plan](VALIDATION_PLAN.md) lists the cases
the profiles need. `tools/check_test_cases.py` checks the cases and runs what
can run today.

No LCR calculation exists yet. The cases here are **registered**: their
metadata and expected values are checked, but no LCR figure is executed until
an implementation exists (B001 to B005 in [DECISIONS.md](../DECISIONS.md)).

## 📁 Files of a case

Each case is a folder `tests/cases/<case-id>/`:

| File | Content |
| --- | --- |
| `case.json` | The case's metadata |
| `run.csv`, `assets.csv`, `flows.csv` | The inputs, in the [input contract](DATA_CONTRACT.md) |
| `expected.json` | The expected outputs and their references |

The case ID is lower case, with digits and hyphens. A case whose expected
values are all `illustrative` has an ID starting with `illustrative-`.

## 🏷️ Case metadata — `case.json`

| Field | Content |
| --- | --- |
| `schema`, `case_version` | `klcr-test-case`, `1` |
| `id` | The folder name |
| `synthetic` | `true`: every case holds synthetic data only |
| `description` | What the case shows; for an invalid case, the input or parameter rule it breaks |
| `profile` | `EU` or `BASEL`, the same as `run.csv` (for a readable `run.csv`) |
| `category` | `nominal`, `boundary`, `invalid-input` or `invalid-parameters` |
| `requirements` | The `REQ-` IDs of [APPLICABILITY.md](APPLICABILITY.md) the case covers |
| `parameter_set` | The path of the parameter set the case uses, under `tests/parameters/` |
| `review` | `derived_by`, `reviewed_by` (or `null`), `date`, and `status`: `unreviewed`, or `reviewed` when someone other than the author checked every expected value |

The metadata is always valid, even in an invalid case. Only the input files of
an `invalid-input` case may break the input contract, and only an
`invalid-parameters` case may name a parameter set of another profile or one
that breaks its contract.

## 🎯 Expected outputs — `expected.json`

```json
{
  "schema": "klcr-test-expected",
  "expected_version": 1,
  "case": "illustrative-eu-input-totals",
  "outputs": [
    {"quantity": "input_status", "text": "pass", "reference": {"…": "…"}},
    {"quantity": "illustrative_total_market_value", "value": "56750.50", "unit": "EUR",
     "tolerance": {"absolute": "0", "relative": "0"}, "reference": {"…": "…"}}
  ]
}
```

An output is either **text**, compared exactly, or a **number**:
- `value` is a decimal string;
- `unit` is the reporting currency for an amount, or `1` for a ratio or
  factor;
- `tolerance` has `absolute` and `relative` bounds, both decimal strings.

| Quantity | Kind | Meaning | Executed today |
| --- | --- | --- | --- |
| `input_status` | text | `pass` or `fail`: the [input contract](DATA_CONTRACT.md) verdict | Yes, by the input validator |
| `input_findings` | text | The finding codes, sorted and joined by `,`; empty when the input passes | Yes, by the input validator |
| `result_status` | text | `calculated`, `rejected` or `failed` ([results](PARAMETERS_AND_RESULTS.md)) | No: registered |
| `liquidity_buffer`, `outflows`, `inflows`, `inflows_after_cap`, `net_outflows` | number, currency | The result figures of the same name | No: registered |
| `lcr` | number, `1` | The ratio, as a decimal fraction | No: registered |
| `illustrative_…` | number or text | A quantity that only shows the format; allowed only in an `illustrative-` case | Yes, by its derivation script |

An `invalid-input` case expects `input_status` `fail`, its `input_findings`
and `result_status` `rejected`. An `invalid-parameters` case expects
`input_status` `pass`, empty `input_findings` and `result_status` `failed`.
Neither has a numeric output.

## 🧭 Reference classes

Every output has one `reference`:
- `class`;
- `source` and `locator`;
- `derivation`, explaining how the value was obtained;
- `script`, or `null`;
- `derived_by`, `reviewed_by` and `date`.

| Class | Meaning | Required |
| --- | --- | --- |
| `published` | Printed in a registered source, for example a worked example | `source` is a `SRC-` ID of [SOURCES.md](SOURCES.md) and `locator` names the place |
| `independent` | Computed by an external implementation by another author, registered with an `IMPL-` ID in the source register | `source` is an `IMPL-` ID, `locator` and `derived_by` name it and its version |
| `contract` | A text output fixed by a K-LCR contract rule: an input finding or a status | `source` names the contract file and `locator` the rule |
| `illustrative` | Shows the format or a behaviour; **never** a validated figure | `derivation` |

- **The implementation under test is never the sole oracle.** A number is
  validated only by a `published` or `independent` value. A value K-LCR
  derives itself, even from a registered text and even by a script, stays
  `illustrative`.
- A `script` lives in `tests/derivations/` and must exist. It may import only
  the Python standard library: never K-LCR's tools or code under test. The
  checker refuses any other import.
- A `contract` value applies only to `input_status`, `input_findings` and
  `result_status`.

## 📏 Comparing a result with its expected value

An actual number `a` matches the expected value `e` when

```text
|a − e| ≤ max(absolute, relative × |e|)
```

- **Both bounds are stated** on every number, as finite decimals of at least
  0. There is no hidden default. Both `0` means an exact comparison.
- **Near zero** the absolute bound governs: an expected `0` is matched within
  `absolute` only, so an `absolute` of 0 demands an exact zero.
- **Non-finite values never match:** an expected or actual NaN or infinity is
  a failure, not a tolerance question.
- **Domain rules come first:** a figure that may not be negative fails when it
  is negative, however small.
- **No rounding before comparison,** unless the result contract rounds the
  figure. The comparison itself runs at a precision wide enough for its
  operands, so it never rounds.
- **Deterministic aggregation:** sums are exact decimals, as in the input
  contract's reconciliation, and must not depend on the order of the input
  records. The plan includes cases with records in reverse order.

Default bounds, until an accuracy decision replaces them:

| Reference | `absolute` | `relative` |
| --- | --- | --- |
| `illustrative` or `independent`, at full precision | `0.000001` currency units; `0.000000001` for `lcr` | `0.000000001` |
| `published`, printed rounded | Half a unit of the last printed digit | `0` |

## 🗂️ Categories

| Category | Covers |
| --- | --- |
| `nominal` | Typical inputs within the perimeter |
| `boundary` | A domain edge: a zero amount, a single record, a maturity on the last day of the horizon, a cap or limit exactly binding, zero net outflows |
| `invalid-input` | Input that the input contract or a decision rejects |
| `invalid-parameters` | Valid input with a parameter set of another profile or one that breaks its contract |

## 📋 Registered and executed

A **registered** case is checked for form: its metadata, inputs, expected
outputs and references. An **executed** assertion compares an actual result
with an expected one. `tools/check_test_cases.py` reports both counts:
- it executes `input_status` and `input_findings` with the input validator;
- it executes every output that names a derivation script by running the
  script on the case folder;
- it reports `result_status` and the result figures as **registered, not
  executed**.

A run that leaves an expected assertion unexecuted is incomplete, never a
pass for that assertion.

A rule is **validated** only when at least one `published` or `independent`
case for it executes and passes. `illustrative` cases never count. No rule is
validated yet.

## 🧪 Neutral examples

Two `illustrative` cases show the format only:
- `illustrative-eu-input-totals` sums the synthetic input amounts with
  `tests/derivations/illustrative_input_totals.py`;
- `illustrative-eu-rejected-input` breaks the input contract with a negative
  amount and expects its rejection.

Neither holds a regulatory value.

## 🚫 What the checker does not do

- Calculate an LCR, or check that a planned case exists for every
  requirement: the [validation plan](VALIDATION_PLAN.md) tracks that by hand.
- Prove that a `published` locator prints the value: a reviewer checks it and
  records `reviewed_by`.
