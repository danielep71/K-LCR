# 🧪 Prototype workbook

**EU LCR from line-level inputs · Source tracked · Not validated**

> [!IMPORTANT]
> **Prototype.** This workbook calculates an EU Liquidity Coverage Ratio, but
> nothing here validates it. Its figures are cross-checked against
> `tools/lcr_spec.py`, a model written for the prototype, which is **not** an
> independent oracle in the sense of the
> [validation plan](methodology/VALIDATION_PLAN.md). Its regulatory factors have
> **not** been checked against the stored source `SRC-02`. The repository's
> checks read its source and rebuild its template; they do not compile or run
> its VBA. A run in LibreOffice is a smoke test on a second host, not evidence
> for Excel. It is not for reporting or production use.

I brought it in for *v0.2.0 - Prototype setup*, whose purpose is a working
prototype to refine afterwards (#179). It is tracked as I wrote it, with the
corrections listed under *What changed on the way in*.

## What it does

The Liquidity Coverage Ratio compares the stock of high-quality liquid assets
with the net cash outflows of a 30-day stress:

```text
LCR = Liquidity buffer / Net liquidity outflow  >= 100%
```

The workbook reproduces that calculation from line-level inputs: one row per
liquid-asset holding, outflow line and inflow line, each assigned to a category
of a catalogue. The engine applies the haircut or rate of the category,
converts into the reporting currency, applies the Annex I composition caps and
the Annex II inflow caps, and writes the ratio in total and per currency with
the trail of every line.

## Sheets

| Sheet | Role |
| --- | --- |
| `Home` | What the workbook does, how to run it, links to every sheet |
| `Params` | Reporting date and currency, caps, the category catalogue (haircuts, outflow and inflow rates with their article), FX rates |
| `HQLA` | Holdings at market value, with the unwind adjustment of secured transactions maturing within 30 days |
| `Outflows`, `Inflows` | One row per line, category chosen from a list |
| `Results` | Per scope: buffer composition, excess liquid assets, outflows, inflows by cap class, net outflow, LCR, surplus, status, and a worksheet-formula check |
| `LineCalc` | Every input line with factor, weighted amount and status |
| `Checks` | Errors, warnings and information with stable codes (`LCR-P…`, `LCR-L…`, `LCR-S…`) |
| `README` | Conventions, methodology, scope and limitations |

## Calculation as implemented

These are the rules as the prototype implements them, not a validated reading
of the regulation.

| Step | Rule | Reference given by the prototype |
| --- | --- | --- |
| Liquid assets | Market value × (1 − haircut), per level L1, L1 EHQCB, L2A, L2B | DR 2015/61 Art. 9 to 12 |
| Excess liquid assets | S − MIN(S, A1/0.30, (A1 + A1CB)/0.60, (A1 + A1CB + A2A)/0.85) on the adjusted amounts | Annex I para 4 |
| Liquidity buffer | L1 + L2A + L2B − MIN(L1 + L2A + L2B, excess) | Annex I para 2 |
| Outflows | Balance × outflow rate | Art. 22 to 31a |
| Net outflow | TO − MIN(FEI, TO) − MIN(IHC, 0.9 × MAX(TO − FEI, 0)) − MIN(IC, 0.75 × MAX(TO − FEI − IHC/0.9, 0)) | Annex II, Art. 33 |
| Ratio | Buffer / net outflow | Art. 4 |

A line with an error is excluded and listed on `Checks`; with
`WithholdIncomplete = TRUE` the ratio of every scope it belongs to is withheld
(status `INCOMPLETE`).

## Source layout

| Path | Holds |
| --- | --- |
| `src/core/` | `CORE_Config` (constants, error numbers, diagnostic codes) and `CORE_Engine` (pure functions of the aggregation) |
| `src/modules/` | `LCR_Formulas`, the worksheet functions |
| `src/workbook/` | `M_Main` (the macros), the document modules `ThisWorkbook` and `sh<Sheet>`, and `LCR_Template.xlsx`, the macro-free template |
| `tests/modules/` | `TEST_Engine`, the self-test that the `Results` sheet runs |
| `tools/lcr_spec.py` | The Python model: parameters, catalogue, demonstration inputs and `compute()`; `tools/test_lcr_spec.py` pins its figures |
| `tools/check_source.py` | Extra checks of the VBA source (names, `Option Explicit`, `Option Private Module`, ASCII, 120 columns); run it on its own |
| `tools/build_template.py` | Writes `LCR_Template.xlsx` from `lcr_spec.py` with `openpyxl` (through `tools/plain_openpyxl.py`, which selects its standard-library XML writer); `tools/test_build_template.py` rebuilds it and compares every part with the tracked file |
| `tools/build_xlsm.py` | Builds the macro-enabled workbook in LibreOffice from the template and the VBA of `src/` and `tests/modules/`, into the ignored `test-results/` |
| `tools/run_lo_test.py` | Runs the workbook's VBA in LibreOffice and compares `Results` with `compute()` |
| `tools/preview.py` | Renders each sheet of a workbook to PNG for a visual check; needs LibreOffice and `pdftoppm` |

The prototype keeps this layout until it is refactored, by my decision of
2026-11-13 recorded in [DECISIONS.md](DECISIONS.md). The names and layers of
the [VBA house style](VBA_HOUSE_STYLE.md) (`LCR_Core_*`, `src/api/`,
`src/host/excel/`, `tests/unit/`) are the target of that refactoring. The
neutral [test harness](methodology/TEST_HARNESS.md) in `tests/unit/` is separate
from `TEST_Engine`.

## Building the workbook by hand

The macro-enabled workbook is not tracked. To build one:

1. Copy `src/workbook/LCR_Template.xlsx` to a new file outside the checkout,
   or under the ignored `test-results/`.
2. Open it in desktop Excel, open the VBE (Alt+F11) and use File > Import File
   for every `.bas` of `src/core/`, `src/modules/`, `src/workbook/` and
   `tests/modules/`.
3. The document modules (`ThisWorkbook`, `sh<Sheet>`) hold only
   `Option Explicit`: nothing needs to be copied into them.
4. Save as `.xlsm`. Review `Params`, enter lines on `HQLA`, `Outflows` and
   `Inflows`, press **Run LCR**, then read `Results` and `Checks`.
   **Self-test** on `Results` runs `TEST_Engine` and the formula check.

None of these steps has been run as part of this repository's checks; the run
on a supported host is #15.

## Building and smoke-testing it in LibreOffice

The tools below need the hash-locked tool requirements (for `openpyxl`) and,
for the workbook, LibreOffice with its Python bridge (`uno`). LibreOffice is an
optional, untested host here: it runs the VBA in a compatibility mode, so a
pass is a smoke test of the logic, never evidence that the workbook compiles
or runs in Excel.

```sh
python tools/build_template.py     # src/workbook/LCR_Template.xlsx
python3 tools/build_xlsm.py        # test-results/K-LCR.xlsm, with LibreOffice's Python
python3 tools/run_lo_test.py       # runs the VBA in LibreOffice and compares with compute()
```

`build_template.py` writes the same bytes on every run: openpyxl's
standard-library XML writer even where lxml is installed, fixed entry dates and
no author or dates in the document properties. A rebuild therefore gives the
tracked template, which `tools/test_build_template.py` checks part by part.
`build_xlsm.py` and `run_lo_test.py` need LibreOffice, so the repository's
checks test only their parts that do not (`tools/test_build_xlsm.py`).

On 2026-11-13 I ran the three tools with LibreOffice 24.2.7.2 on Linux:
`run_lo_test.py` reported 26 expectations passed and none failed. That run
covers the self-test before and after a run, the 16 values of each scope
against `compute()`, the formula check, rejected lines, validation only and a
stopped run. It is a record of that one run, not a check that the repository
repeats.

## Differences from the repository's decisions

The prototype is wider and simpler than the contracts of
[methodology/](methodology/README.md). I have not reconciled them; each
difference is a point to settle when the prototype is refined.

- **Catalogue against the applicability decisions.** The prototype's catalogue
  has categories that my decisions exclude from the contracts:
  securitisations (`L2B_ABS_25`, `L2B_ABS_35`; Art. 13, excluded by A03), the
  restricted-use committed liquidity facility (`L2B_RCLF`; Art. 12(1)(d) and
  14, excluded by A03), the 3 % stable retail deposits (`OUT_RET_STABLE_3`;
  Art. 24(4), excluded by A06 since #172), and the inflows exempt from the cap
  or under the higher cap (`IN_EXEMPT`, `IN_HIGHER_CAP`; Art. 33(2) to (4),
  excluded by A06). Their category codes also differ from those of
  [categories.json](methodology/categories.json).
- **Inputs.** The prototype reads its lines from worksheets, not from the CSV
  files of the [input contract](methodology/DATA_CONTRACT.md), and its
  diagnostic codes are its own.
- **Parameters.** Its haircuts and rates are in the `Params` sheet and in
  `tools/lcr_spec.py`, not in a parameter set of
  [PARAMETERS_AND_RESULTS.md](methodology/PARAMETERS_AND_RESULTS.md), and none
  carries a source-register ID.
- **Profiles.** Only the EU profile is implemented; the Basel profile is not.
- **Sequencing.** It implements formulas before their contracts are resolved,
  which the follow-on backlog of [DECISIONS.md](DECISIONS.md) otherwise rules
  out; I made that exception for the prototype on 2026-11-13.

## Limitations stated by the prototype

- The user classifies each line; eligibility (Art. 7, 8 and 10 to 16) is not
  tested.
- Not modelled: CIU look-through (Art. 15), collateral swaps (Art. 28(4)),
  group and institutional protection scheme treatments beyond the exempt and
  90 % inflow classes, alternative liquidity approaches (Art. 19), and the
  thresholds of a significant currency.
- Per-currency figures apply the same formulas to the lines of one currency.

## What changed on the way in

- `tools/lcr_spec.py` gained type annotations and a function in place of an
  assigned `lambda`, so that it passes Ruff and strict mypy; its output is the
  same as before, line for line.
- `tools/check_source.py` and `tools/preview.py` are wrapped in a `main()`
  function, so that importing them runs nothing; their checks and output are
  unchanged.
- The template's `docProps/core.xml` had `creator` set to `openpyxl`; I cleared
  it, as the `binaries` gate requires.
- With #180 the build tools came in, typed for strict mypy, and I rebuilt the
  template with them. The rebuilt parts equal the earlier ones after XML
  canonicalization, except `docProps/core.xml`, which no longer holds the
  creation and modification dates. The builder now also removes the theme
  scheme from the default font whatever spacing the XML writer uses, writes
  conditional formats through a typed helper equivalent to openpyxl's
  `FormulaRule`, and drops the reference to another workbook from its
  docstring.
- `build_xlsm.py` and `run_lo_test.py` write under `test-results/` instead of
  `dist/`, use a temporary LibreOffice profile and scratch folder that are
  removed afterwards, and `build_xlsm.py` takes only `tests/modules/` from
  `tests/`, so the neutral harness of `tests/unit/` stays out of the workbook.

## Not tracked yet

- **The macro-enabled workbook.** The copy I made carries a Microsoft
  sensitivity label with an organization identifier and a directory-style
  author name in its properties, and a generated workbook is not source. Build
  one by hand or with `build_xlsm.py` as above.
- **`VERSION`.** No version has been released, and `VERSION` is created only
  when the first release is prepared ([RELEASING.md](../RELEASING.md)).
