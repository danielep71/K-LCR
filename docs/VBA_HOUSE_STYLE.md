# ✍️ VBA house style and contracts

[![Scope: VBA exports](https://img.shields.io/badge/Scope-VBA_exports-217346?style=flat-square)](#-module-rules)
[![Contracts: Explicit](https://img.shields.io/badge/Contracts-Explicit-6f42c1?style=flat-square)](#-procedure-contracts)
[![Host: Untested](https://img.shields.io/badge/Host-Untested-BF8700?style=flat-square)](../INSTALLATION.md#-host-matrix)

This is the K-LCR adaptation of the established VBA style structure: naming,
module rules, procedure contracts, cleanup, layout, export compatibility and
review. [Architecture](REPOSITORY_STRUCTURE.md) owns layer boundaries;
[host and import guidance](../INSTALLATION.md) owns execution evidence.
The project has no VBA source or validated workbook yet. The
[static checks](#-static-checks) enforce the mechanical rules; the Excel run in
#15 is still pending.

## 🏷️ Naming and component boundaries

| Layer | Path | Component naming | Visibility |
| --- | --- | --- | --- |
| Pure core | `src/core/` | `LCR_Core_<Name>` | `Option Private Module`; internal public members only |
| Public API | `src/api/` | `LCR_API_<Name>` | Only reviewed entry points externally callable |
| Excel adapter | `src/host/excel/` | `LCR_Excel_<Name>` | Host-only procedures; no regulatory arithmetic |
| Neutral tests | `tests/unit/` | `TEST_LCR_<Name>` | Project-private |
| Host tests | `tests/host/` | `TEST_LCR_Excel_<Name>` | Project-private |

A module's `Attribute VB_Name` matches its filename and component name.
Procedures use PascalCase verb phrases; constants use uppercase descriptive
names. Distinct EU and Basel implementations include their profile in names
and fixtures. Avoid identical public procedure names in different modules,
hidden defaults and a generic `Calculate` entry point without profile/version.

## ⚙️ Module rules

- Every module starts with `Option Explicit`. Core/test standard modules
  use `Option Private Module`. Explicitly declare array bounds; do not use
  `Option Base 1` or a `Variant` where a specific type is adequate.
- Use `ByVal` for inputs; use `ByRef` only for documented outputs or
  necessary object references. Do not mutate caller-owned input arrays or
  configuration records.
- Pure core code does not access `Application`, `Workbook`, `Worksheet`,
  `Range`, files, network, clock, random generator or global mutable state.
  Host reads and writes occur only in the Excel adapter. API validates and
  invokes the core, then returns results and diagnostics.
- References beyond the standard Excel/VBA project references or native
  declarations require an issue and explicit host-compatibility review.
  Avoid platform calls in core/API. If a host adapter needs a declaration,
  use conditional compilation appropriate to the tested Office architecture,
  `PtrSafe` and pointer-sized types; compile every declared branch on its
  applicable host before claiming support.
- Do not use `GoTo` except a single explicit error/cleanup handler.
  No `GoSub`, `On Error GoTo -1`, undeclared dynamic calls or
  `Application.Run`/late-bound `CallByName` in calculation code.
  Host-only late binding must be named, bounded, error-checked and reviewed:
  each use is recorded in `tools/vba-exceptions.json` (see
  [Static checks](#-static-checks)). Static checking is a complement to
  actual compilation.

## 📜 Procedure contracts

Every substantive procedure documents PURPOSE, INPUTS (units, domain and
ownership), RETURNS/OUTPUTS, ERROR POLICY, DEPENDENCIES, STATE OWNERSHIP,
REFERENCE (source register ID/locator where a regulatory rule is implemented)
and UPDATED date. Omit a section only when truly inapplicable. Comments match
behavior; fixture or workbook state is not evidence of a regulatory source.

### Numeric types and units

- Use VBA `Double` for calculation amounts and intermediate ratios, with the
  currency and unscaled unit stated in each contract. Do not use `Currency`,
  `Decimal` or implicit `Variant` conversion for regulatory arithmetic without
  a reviewed, tested exception; their precision and conversion behavior must
  be justified for that field.
- Use `Double` for rates, factors and proportions as decimals (`0.05` means
  5%), and state valid domains. Use `Long` for counts and indexes, `Boolean`
  for flags, `Date` for dates and `String` for identifiers and version keys.
  A duration uses a `Double` in years unless its name and contract state
  another unit. Avoid `Single`, floating-point equality and silent coercion.
- Profile, reporting date, parameter version and regulatory source edition
  are explicit inputs; configuration is caller-owned and never mutated.
  Validate missing, non-finite or out-of-domain values before calculation.
  Do not silently choose a default profile or substitute an invalid input.
- Issue #10 defines field-level schemas, currency conversion, date semantics
  and missing-value representation. Issue #11 defines rounding and comparison
  tolerances. Neither issue changes these general type rules implicitly.
  Do not conflate EU and Basel sources or infer a profile from workbook names.

The public API exposes a deliberate inventory of named entry points. It
validates the entire request, returns a deterministic result or an actionable
error, and does not partially overwrite output on failure. Core procedures
raise a documented named error with component/procedure source and sanitized
description; the Excel adapter maps errors for users and restores its state.
If worksheet functions are added, their error-value mapping is specified
separately and tested. Exact error numbers and signatures are fixed with the
first API implementation, before callers depend on them.

## 🧹 Operation and cleanup

Capture only the Excel settings an adapter changes; restore them on success
and failure. Preserve the original error when cleanup also fails and report
both outcomes. Never save or close a user workbook implicitly. Avoid
`On Error Resume Next` except around one checked statement, followed by
normal error handling. Do not leak client data through error text or logs.

## 🗂️ Module layout and source presentation

Keep modules focused on one responsibility. A header states role, exports,
dependencies and source status. Indent VBA with four spaces, no tabs or
trailing whitespace. Separate declarations from procedures, use explicit
visibility, and wrap long expressions for reviewability. A format-only PR
does not change signatures, semantics or expected results. Keep comments and
their UPDATED dates current.

## 📦 Export compatibility and host evidence

Git stores VBA text with LF and checks it out with CRLF. Use an ASCII-only
repository source convention for future exported VBA (`ChrW` for deliberate
non-ASCII characters); do not configure a Git working-tree encoding or
assume VBE code-page behavior has already been demonstrated. A real export,
import, compile and byte/semantic round trip on the selected host is required
in #14/#15 before claiming support. `.frm` and `.frx` remain paired and
the latter binary. Workbook/sheet document modules cannot be imported as
ordinary standard modules; map them to the corresponding host components.

The portable Repository integrity gate validates tooling, tracked text,
workflow syntax and the static VBA rules below, not VBA syntax, compilation or
LCR calculations. A candidate-bound Excel run in #15 is a separate gate. Record
the exact tested commit, Excel build/bitness, locale, fixture count and
cleanup result.

## 🔍 Static checks

**Repository integrity** runs three static checks on every tracked `.bas`,
`.cls` and `.frm` file. Each also runs on its own, for example
`python tools/check_vba_jumps.py`. Each finding names the file and, where it
has one, the line. With no VBA source, each passes and says it examined no
component.

| Check | Enforces |
| --- | --- |
| `tools/check_vba_conditionals.py` | Well-formed `#If`, `#ElseIf`, `#Else` and `#End If` blocks over `VBA6`, `VBA7`, `Win32`, `Win64`, `True`, `False`, `-1` and `0`, evaluated in each compilation environment (`vba6-win32`, `vba7-win32`, `vba7-win64`); no project `#Const`. Every `Declare` reachable under VBA7 is `PtrSafe`; one reachable under VBA6 uses neither `PtrSafe` nor `LongPtr`, so a declaration sits in `#If VBA7` branches. |
| `tools/check_vba_jumps.py` | In each environment: every `GoTo`, `Resume` and `On Error GoTo` target is a label of the same procedure; no label is defined twice in a procedure; every procedure is closed. Jumps serve one error/cleanup handler: no `GoSub`, no computed `On <expression> GoTo`, no `On Error GoTo -1`, at most one `On Error GoTo` label and one other label per procedure, and no backward `GoTo`. |
| `tools/check_vba_dynamic.py` | Native, dynamic and COM constructs: `Declare`; `CreateObject` and `GetObject`, with or without parentheses; `New` of a type that is neither a component of this project nor `Collection` (as in `New Scripting.Dictionary`); `CallByName`, `AddressOf`, `Run`, `Evaluate`, `ExecuteExcel4Macro`, `OnTime`, `OnKey` and `MacroOptions`, unqualified or as a member; `[...]` expressions. None is allowed in `src/core/`, `src/api/`, `tests/unit/` or elsewhere. In `src/host/excel/` and `tests/host/` each needs a reviewed exception; a `Declare` only in `src/host/excel/`. |

### Reviewed exceptions

`tools/vba-exceptions.json` lists the host-boundary uses I reviewed:

```json
{
  "schema": "klcr-vba-exceptions",
  "version": 1,
  "exceptions": [
    {"path": "src/host/excel/LCR_Excel_Output.bas", "procedure": "OpenFolder",
     "construct": "CreateObject", "target": "Shell.Application", "issue": 42,
     "reason": "Opens the output folder for the user.", "reviewed_by": "danielep71",
     "date": "2026-11-04"}
  ]
}
```

- `construct` is one of the constructs above, spelled as in the table;
  `[...]` stands for a bracketed expression.
- `procedure` is the procedure the use is in, or `null` at module level, as
  for a `Declare`. Names compare ignoring case.
- `target` is the declared name of a `Declare`, the literal ProgID of
  `CreateObject` and the type of `New`; it is `null` for the others. A
  `CreateObject` whose ProgID is not a single string literal cannot be
  excepted.
- An entry covers every use of its construct and target in that procedure.
  An entry that matches no use is stale and fails the check, as does an entry
  outside the host homes, a malformed field or a duplicate.
- Add an entry in the pull request that adds the use, with its issue, and
  have it reviewed there.

### What the checks cannot prove

- They neither compile nor run VBA, and resolve no call. The rules are
  name-based: a construct reached through a variable, an object or another
  project is not seen, and a variable, Type field or procedure named like a
  listed construct, such as `Run` or `Evaluate`, is reported: choose another
  name.
- `check_vba_dynamic.py` reads every `#If` branch at once; the other two
  evaluate the three environments statically, not on a 32-bit or 64-bit host.
- Strings, comments (including continued comments), `Rem`, colon-separated
  statements, line continuations, numeric labels, date literals, bracketed
  sheet names and the members of `Type` and `Enum` blocks are handled by a
  lexer, not a parser: an unusual construct it does not model can hide a use
  or report one that is not there.
- They do not check naming, module options, layer dependencies other than the
  constructs above, or Excel object-model access in the core; review covers
  the rest of this guide.

Changed VBA is imported, compiled and run on the supported host (#14, #15)
before its behaviour is accepted. Repository checks are not compilation.
