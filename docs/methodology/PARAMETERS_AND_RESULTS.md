# 🧮 Parameter sets, results and diagnostics

**Contract version 1 · Layout only: no regulatory value is established here**

This contract defines the two files around a calculation: the **parameter
set** a run uses, and the **result** it produces, with its diagnostics.
[parameter-result-contract.json](parameter-result-contract.json) is its
machine-readable form, and `tools/check_parameters.py` its reference
validator. Inputs follow the [input contract](DATA_CONTRACT.md).

Passing this contract means that a file is complete and well formed. It does
not mean that a value is the right regulatory value, or that a result is
correct: that is for the calculation contracts and the independent cases
planned in [VALIDATION_PLAN.md](VALIDATION_PLAN.md).

## 🧩 Parameter sets

A parameter set holds every value a profile needs, each with its source. Its
identifier names its source edition (`EU-LCR-DA-2022-07-08`,
`BASEL-LCR-2019-12-15`), and a set never changes once a result has used it: a
corrected value or a new edition is a new set, recorded with its own SHA-256
in the result's lineage.

| Field | Content |
| --- | --- |
| `schema`, `parameter_set_version` | `klcr-parameter-set`, version `1` |
| `parameter_set`, `profile` | The set's identifier, which must be the one of its profile |
| `status` | `illustrative`: values chosen for synthetic fixtures only; `sourced`: every value read in its source and verified against its locator |
| `verified_on` | The verification date; required when `sourced`, absent otherwise |
| `source_register_version`, `categories_version` | The versions of [SOURCES.md](SOURCES.md) and [categories.json](categories.json) the set covers |
| `factors` | Exactly one entry per in-scope category of the profile, except the categories whose treatment is `exclusion`, which have none |
| `limits` | Exactly one entry per limit of the profile |

Each **factor** has a `category`, a `kind` (`haircut` for liquid assets,
`outflow_rate` for outflows, `inflow_rate` for inflows), a `value`, a `source`
and a `locator`. The source is `SRC-01` or `SRC-02` for the EU profile, and
`SRC-06` for Basel.

A Basel category marked as a national discretion also has a
`discretion_choice`, which records whose choice the value is (A07). There is
no default value and no fallback to the other profile.

Each **limit** has an `id`, a `value`, and the `source` and `locator` the
contract fixes for it:

| Profile | Limit | Locator |
| --- | --- | --- |
| EU | `LCR-MINIMUM` | `SRC-02` Art. 4(2) |
| EU | `LEVEL1-MINIMUM-SHARE` | `SRC-02` Art. 17(1)(a) |
| EU | `LEVEL1-EXCL-EHQCB-MINIMUM-SHARE` | `SRC-02` Art. 17(1)(b) |
| EU | `LEVEL2B-MAXIMUM-SHARE` | `SRC-02` Art. 17(1)(c) |
| EU | `INFLOW-CAP` | `SRC-02` Art. 33(1) |
| Basel | `LCR-MINIMUM` | `SRC-06` LCR20.5 |
| Basel | `LEVEL2-MAXIMUM-SHARE` | `SRC-06` LCR30.34 |
| Basel | `LEVEL2B-MAXIMUM-SHARE` | `SRC-06` LCR30.33 |
| Basel | `INFLOW-CAP` | `SRC-06` LCR40.77 |

Values are decimal fractions written as JSON strings, such as `"0.25"` for
one quarter. They are never percentages, never floating-point numbers, and
they have at most 15 significant digits. A factor is at most `1`.

No `sourced` parameter set exists yet. The illustrative sets in
`tests/parameters/` serve the fixtures only, and every result calculated with
them carries the `CALC-ILLUSTRATIVE` diagnostic.

## 📤 Results

| Field | Content |
| --- | --- |
| `schema`, `result_version` | `klcr-result`, version `1` |
| `status` | `calculated`, `rejected` (the input contract reported findings) or `failed` (the calculation could not complete) |
| `illustrative` | `true` when the parameter set is illustrative |
| `lineage` | The run's fingerprint, the input contract version, the parameter set and its SHA-256, the categories and register versions, and the commit of the code |
| `figures` | Only when `calculated`: `liquidity_buffer`, `outflows`, `inflows`, `inflows_after_cap`, `net_outflows`, in the reporting currency, and `lcr`, a decimal fraction |
| `components` | Only when `calculated`: one object per category with exactly `category`, `amount`, `factor` (at most `1`) and `weighted`, decimal strings, so that every figure reconciles with the input totals |
| `diagnostics` | Every diagnostic, each with `code`, `severity`, `message` and `refs`, the records or limits it concerns |

A result that is `rejected` or `failed` has no figures and no components, and
names its error diagnostic. A `calculated` result has no error diagnostic.
Earlier outputs are never left as if current.

## 🩺 Diagnostics

| Code | Severity | Meaning |
| --- | --- | --- |
| `CALC-INPUT-REJECTED` | error | The input contract reported findings; their codes are listed |
| `CALC-PARAMETER-SET-INVALID` | error | The parameter set does not pass its contract |
| `CALC-PARAMETER-SET-PROFILE` | error | The parameter set belongs to another profile or edition than the run |
| `CALC-ZERO-NET-OUTFLOWS` | error | Net outflows are zero, so no ratio is given |
| `CALC-INTERNAL` | error | An unexpected condition stopped the calculation |
| `CALC-ILLUSTRATIVE` | warning | The parameter set is illustrative: the result is not a regulatory figure |
| `CALC-BELOW-MINIMUM` | warning | The ratio is below the profile's minimum requirement |
| `CALC-ASSET-EXCLUDED` | info | A holding with `requirements_met` `N` is left out of the buffer |
| `CALC-OUTSIDE-HORIZON` | info | An item maturing after the 30-day horizon is left out |
| `CALC-COMPOSITION-LIMIT` | info | A composition limit of the buffer binds |
| `CALC-INFLOW-CAP` | info | The inflow cap binds |

## 🔐 Immutability and repeatability

- A result is bound to its inputs and configuration by its lineage. The run
  fingerprint covers the input contract, the categories and the input files;
  the parameter set has its own SHA-256; the code commit identifies the
  implementation.
- The same lineage must always give the same result. A result whose lineage
  differs is a different result, never an update of an earlier one.

## 🚦 Validator findings

`tools/check_parameters.py --file <json>` checks a parameter set or a result:

- **Parameter sets:** `PAR-HEADER`, `PAR-FACTOR`, `PAR-FACTOR-CATEGORY`,
  `PAR-FACTOR-DUPLICATE`, `PAR-FACTOR-MISSING`, `PAR-VALUE`, `PAR-SOURCE`,
  `PAR-DISCRETION`, `PAR-LIMIT`.
- **Results:** `RES-HEADER`, `RES-LINEAGE`, `RES-FIGURES`, `RES-DIAGNOSTIC`,
  `RES-STATUS`, `RES-ILLUSTRATIVE`.

`tests/parameters/` holds valid and invalid examples, with the findings each
must give in [expected.json](../../tests/parameters/expected.json). The
`parameter-result-contract` gate of `tools/check.py` runs them.

## 🚫 What this contract does not check

- Whether a value is the one its locator states: that is the verification a
  `sourced` set records.
- Whether a result's figures are arithmetically right, or whether its
  components add up: that belongs to the calculation contracts and the planned
  cases of [VALIDATION_PLAN.md](VALIDATION_PLAN.md).
