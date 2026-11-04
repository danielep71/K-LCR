# 🧾 LCR input contract

**Contract version 1 · Three CSV files per run · Form only, not regulatory correctness**

This contract defines the input of one K-LCR run: its files, their format, the
fields and their units, what makes the input invalid, and how a run is traced.
[data-contract.json](data-contract.json) is its machine-readable form, and
[categories.json](categories.json) lists the categories of each profile.
`tools/check_contract.py` is the reference validator: the future workbook
importer follows the same contract and must give the same findings.

The contract follows my applicability decisions A01 to A09
([APPLICABILITY.md](APPLICABILITY.md)). Passing the contract means that the
input is well formed and inside the v0.1 perimeter. It says nothing about
whether a figure calculated from it would be correct: that is the work of the
calculation contracts and of the independent fixtures (#11).

## 📁 Files of a run

A run is one folder holding three files:

| File | Records | Key | Content |
| --- | --- | --- | --- |
| `run.csv` | Exactly one | — | Profile, parameter set, reporting date and currency, perimeter |
| `assets.csv` | Zero or more | `asset_id` | Holdings that may count as liquid assets |
| `flows.csv` | Zero or more | `flow_id` | Outflow and inflow items |

## 🧾 File format

- **Encoding:** UTF-8, with or without a byte-order mark. A NUL character or
  an invalid byte rejects the file.
- **Records:** separated by LF or CRLF. A carriage return elsewhere outside a
  quoted field is a syntax error.
- **Fields:** delimited by `;` and quoted with `"` when needed. A quote
  inside a quoted field is doubled.
- **Header:** required. It names every column of the contract once; column
  order is free.
- **Missing values:** an empty field is missing, never zero. A record whose
  fields are all blank is rejected.
- **Numbers:** `.` as decimal separator, no thousands separator, no exponent,
  at most 15 significant digits. `NaN` and infinities are rejected.
- **Dates:** ISO 8601, `YYYY-MM-DD`, from 2000-01-01 to 2199-12-31.
- **Limits:** at most 64 MiB and 1,000,000 records per file.

## 🔤 Value types

| Type | Form |
| --- | --- |
| `id` | Letters, digits, `.`, `_` and `-`, starting with a letter or digit; at most 64 characters; compared case-insensitively as a key |
| `code` | One of the values the column allows, or a category of the run's profile |
| `flag` | `Y` or `N` |
| `currency` | Three capital letters (ISO 4217) |
| `integer` | Digits only, from 1 to 999 |
| `amount` | A decimal number, zero or more, in the reporting currency |
| `date` | `YYYY-MM-DD`, a real calendar date |

Text never starts with `=`, `+`, `-`, `@`, a tab or a carriage return, so
that a spreadsheet does not read it as a formula.

## 📋 run.csv

| Column | Type | Required | Content |
| --- | --- | --- | --- |
| `run_id` | id | Yes | Identifier of the run, chosen by the provider |
| `profile` | code | Yes | `EU` or `BASEL` (D002); there is no default |
| `parameter_set` | code | Yes | `EU-LCR-DA-2022-07-08` for `EU`, `BASEL-LCR-2019-12-15` for `BASEL` |
| `source_register_version` | integer | Yes | `1`, the register version this contract cites |
| `reporting_date` | date | Yes | The date at which the LCR is measured; the 30-day horizon follows it (R01) |
| `reporting_currency` | currency | Yes | The currency of every amount in the run (A02) |
| `perimeter_type` | code | Yes | `INDIVIDUAL` or `CONSOLIDATED`, as declared by the provider; K-LCR does not consolidate (A01) |
| `perimeter_id` | id | Yes | The institution or group the data describe |
| `synthetic` | flag | Yes | `Y` only: the repository holds synthetic data only |

## 📋 assets.csv

| Column | Type | Required | Content |
| --- | --- | --- | --- |
| `asset_id` | id | Yes | Unique identifier of the holding |
| `category` | code | Yes | A liquid-asset category of the run's profile |
| `market_value` | amount | Yes | Market value before any haircut, in the reporting currency |
| `original_currency` | currency | Yes | The currency the asset is denominated in (A02) |
| `requirements_met` | flag | Yes | `Y` when the holding meets the general and operational requirements of its profile (`SRC-02` Art. 7 and 8; `SRC-06` LCR30.13 to LCR30.28), as the provider asserts |

## 📋 flows.csv

| Column | Type | Required | Content |
| --- | --- | --- | --- |
| `flow_id` | id | Yes | Unique identifier of the item |
| `direction` | code | Yes | `OUTFLOW` or `INFLOW` |
| `category` | code | Yes | An outflow or inflow category of the run's profile, matching `direction` |
| `amount` | amount | Yes | Outstanding balance, committed amount or contractual amount, in the reporting currency; `direction` gives the sign |
| `original_currency` | currency | Yes | The currency the item is denominated in (A02) |
| `maturity_date` | date | Inflows | Contractual maturity or next contractual payment; blank for an outflow without one |
| `collateral_category` | code | Secured categories | The liquid-asset category of the collateral of a secured transaction or collateral swap |
| `netting_set_id` | id | No | The netting set of a derivative item |

## 🏷️ Categories

[categories.json](categories.json) lists, for each profile, the liquid-asset,
outflow and inflow categories in scope (A03, A08), at the granularity at which
the source gives a distinct treatment: 23 liquid-asset, 67 outflow and 28
inflow categories for the EU profile, and 12, 57 and 22 for Basel. Each
category has its locator in `SRC-02` or `SRC-06`, a short description, and its
treatment: a haircut, outflow rate or inflow rate, an inclusion rule, or an
exclusion. An exclusion category, such as a retail term deposit outside the
horizon, lets the provider classify an item that the source leaves out of
the calculation. Basel categories also say whether they are a national
discretion (A07). The categories hold no parameter value.

A flow category also states its collateral rule:
- **required:** `collateral_category` must be one of the categories it lists,
  for example the Level 2A categories for funding secured by Level 2A assets;
- **optional:** any liquid-asset category, or none, for example a collateral
  swap;
- **absent:** `collateral_category` must be blank.

A derivative category may carry `netting_set_id`.

The file also lists the excluded categories (A03 to A06), so that input naming
one is rejected rather than ignored. This includes the secured flows whose
collateral is an excluded asset class, such as securitisations or CIUs.

## 🚦 Findings

Each finding has a stable code, the file, the physical line, the record
number (0 for the header) and the column. The codes and their meanings are
in [data-contract.json](data-contract.json). In order of checking:

1. **File:** `LCR-FILE-MISSING`, `LCR-ENCODING`, `LCR-TOO-LARGE`,
   `LCR-SYNTAX`, `LCR-EMPTY`, `LCR-DELIMITER`, `LCR-HEADER-DUPLICATE`,
   `LCR-HEADER-MISSING`, `LCR-HEADER-UNKNOWN`, `LCR-FIELD-COUNT`. After one of
   these, the file is not read as records.
2. **Field:** `LCR-BLANK-RECORD`, `LCR-REQUIRED`, `LCR-FORMULA`, `LCR-TYPE`,
   `LCR-NON-FINITE`, `LCR-PRECISION`, `LCR-RANGE`, `LCR-ALLOWED`,
   `LCR-LENGTH`, `LCR-DUPLICATE-KEY`. A field reports its first finding only.
3. **Run:** `LCR-RECORD-COUNT`, `LCR-PARAMETER-SET`, `LCR-REGISTER-VERSION`.
4. **Records against the run:** `LCR-CATEGORY-UNKNOWN`, `LCR-OUT-OF-SCOPE`,
   `LCR-COLLATERAL`, `LCR-NETTING-SET`, `LCR-MATURITY`. These run only when
   `run.csv` is valid, and only on records without field findings.

Treatment:

- **Any finding rejects the whole run.** No figure is calculated, and no
  earlier result is shown as current.
- **Invalid input is never corrected,** rounded or given a default.
- **Duplicates** are keys that repeat, compared case-insensitively; the later
  record is reported.
- **Non-finite numbers,** too many digits and negative amounts are reported,
  never coerced.
- **Inconsistent input,** such as a category of the wrong direction or a
  maturity before the reporting date, is reported with its own code.

## 🧮 Reconciliation

The report gives, for every readable file:
- the number of records, and the number with findings;
- exact decimal totals over the records without findings: market value by
  asset category and in total, and flow amounts by direction and category,
  and by direction.

Totals are sums of the input as given, before any haircut, rate or cap. They
reconcile the input with its source; they are not LCR figures. They are
computed in exact decimal arithmetic, so the same input always gives the same
totals.

## 🔐 Lineage, immutability and repeatability

- The validator never modifies an input file. The report records the
  SHA-256 of each file as read.
- The run's **fingerprint** is a SHA-256 over the SHA-256 of
  `data-contract.json`, of `categories.json` and of each input file, in a
  fixed order. A change to any of them changes the fingerprint.
- Validating the same files with the same contract always gives the same
  report. The fixture check validates every case twice and compares the
  results.

## 🧪 Fixtures

`tests/contract/` holds one folder per synthetic case: valid runs for each
profile, and invalid runs that each trigger chosen findings.
[expected.json](../../tests/contract/expected.json) lists the findings each
case must give, as `[code, file, record, column]`, and the reconciliation of
the valid cases. The `data-contract` gate of `tools/check.py` runs
`tools/check_contract.py --check-fixtures`, and `tools/test_check_contract.py`
tests the parser and the rules on inline cases, including CRLF and BOM input.

## 🚫 What the contract does not check

- Whether a category is the right one for a real item, or whether
  `requirements_met` is true: those are the provider's assertions.
- Any parameter value, haircut, rate or cap, and the LCR itself.
- Currency conversion: amounts arrive already in the reporting currency.
- Real data: the repository holds synthetic data only.
