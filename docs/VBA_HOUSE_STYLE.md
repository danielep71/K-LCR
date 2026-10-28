# VBA house style and contracts

This is the K-LCR adaptation of the established VBA style structure: naming,
module rules, procedure contracts, cleanup, layout, export compatibility and
review. [Architecture](REPOSITORY_STRUCTURE.md) owns layer boundaries;
[host and import guidance](../INSTALLATION.md) owns execution evidence.
The project has no VBA source or validated workbook yet. These are design
rules; the static gates in #12 and the Excel run in #15 are still pending.

## Naming and component boundaries

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

## Module rules

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
  Host-only late binding must be named, bounded, error-checked and reviewed.
  Static checking (#12) is a complement to actual compilation.

## Procedure contracts

Every substantive procedure documents PURPOSE, INPUTS (units, domain and
ownership), RETURNS/OUTPUTS, ERROR POLICY, DEPENDENCIES, STATE OWNERSHIP,
REFERENCE (source register ID/locator where a regulatory rule is implemented)
and UPDATED date. Omit a section only when truly inapplicable. Comments match
behavior; fixture or workbook state is not evidence of a regulatory source.

Amounts use a documented currency and unit; profile, reporting date, parameter
and source versions are explicit arguments. Define numeric representation,
rounding, tolerance, date semantics and missing-value behavior in #10/#11
before implementation. Do not silently replace invalid input with a default,
conflate EU and Basel sources, or infer a profile from workbook names.

The public API exposes a deliberate inventory of named entry points. It
validates the entire request, returns a deterministic result or an actionable
error, and does not partially overwrite output on failure. Core procedures
raise a documented named error with component/procedure source and sanitized
description; the Excel adapter maps errors for users and restores its state.
If worksheet functions are added, their error-value mapping is specified
separately and tested. Exact error numbers and signatures are fixed with the
first API implementation, before callers depend on them.

## Operation and cleanup

Capture only the Excel settings an adapter changes; restore them on success
and failure. Preserve the original error when cleanup also fails and report
both outcomes. Never save or close a user workbook implicitly. Avoid
`On Error Resume Next` except around one checked statement, followed by
normal error handling. Do not leak client data through error text or logs.

## Module layout and source presentation

Keep modules focused on one responsibility. A header states role, exports,
dependencies and source status. Indent VBA with four spaces, no tabs or
trailing whitespace. Separate declarations from procedures, use explicit
visibility, and wrap long expressions for reviewability. A format-only PR
does not change signatures, semantics or expected results. Keep comments and
their UPDATED dates current.

## Export compatibility and host evidence

Git stores VBA text with LF and checks it out with CRLF. Use an ASCII-only
repository source convention for future exported VBA (`ChrW` for deliberate
non-ASCII characters); do not configure a Git working-tree encoding or
assume VBE code-page behavior has already been demonstrated. A real export,
import, compile and byte/semantic round trip on the selected host is required
in #14/#15 before claiming support. `.frm` and `.frx` remain paired and
the latter binary. Workbook/sheet document modules cannot be imported as
ordinary standard modules; map them to the corresponding host components.

The current portable Repository integrity gate validates setup tooling, not
VBA syntax, compilation or LCR calculations. Static checks in #12 and a
candidate-bound Excel run in #15 are separate gates. Record the exact tested
commit, Excel build/bitness, locale, fixture count and cleanup result.
