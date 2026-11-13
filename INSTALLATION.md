# 📦 Installation and developer setup

[![Host: Windows 64-bit target](https://img.shields.io/badge/Host-Windows_64--bit_target-217346?style=flat-square)](#host-matrix)
[![Excel evidence: Not run](https://img.shields.io/badge/Excel_evidence-Not_run-BF8700?style=flat-square)](#host-matrix)
[![Developer setup: Verified](https://img.shields.io/badge/Developer_setup-Verified_2026--11--09-2ea44f?style=flat-square)](#verified-setup)

K-LCR holds repository setup, contracts, static checks, a neutral test
harness and a [prototype workbook](docs/PROTOTYPE.md) whose source and
macro-free template are tracked. None of its VBA has been **compiled or run**
as part of this repository's checks, and no workbook is released. This
page says which hosts are intended and which are tested, how to set up the
repository checks, and which Excel steps are planned. Every step is marked
**verified** (run and recorded below) or **not executed** (planned, never
run).

<a id="host-matrix"></a>

## 🖥️ Host matrix

| Host | Intended status | Tested status |
| --- | --- | --- |
| Windows desktop Microsoft 365 Excel, 64-bit | Initial engineering target | **Not tested**: no import, compile or harness run yet |
| Windows desktop Excel, 32-bit | Outside the initial target; its `#If` branches are checked statically | Not tested |
| macOS, web, mobile or older Excel | Outside the initial target | Not tested |

A host becomes **supported** only after a recorded run on it (#15). The
intended baseline uses the standard VBA, Excel and Office references of a new
desktop workbook; any other library or COM object needs a reviewed exception
([static checks](docs/VBA_HOUSE_STYLE.md#-static-checks)) and a host test.

## 📥 Get the source

Verified on 2026-11-09 ([Verified setup](#verified-setup)). Clone the
repository, switch to the active release branch and note
the exact commit you are working on:

```sh
git clone https://github.com/danielep71/K-LCR.git
cd K-LCR
git switch release/0.1.0
git rev-parse HEAD
git status --short
```

`git status --short` prints nothing on a fresh clone. Read
[source-control conventions](docs/SOURCE_CONTROL.md),
[governance](docs/GOVERNANCE.md) and [CONTRIBUTING.md](CONTRIBUTING.md)
before changing anything.

<a id="developer-setup"></a>

## 🛠️ Developer setup

Verified on Linux on 2026-11-09 ([Verified setup](#verified-setup)), before
openpyxl, its type stubs and the `vba-manifest` gate were added: those have
passed in CI, not in a new fresh-clone run. The repository checks need:

| Tool | Version | Used by |
| --- | --- | --- |
| Git | Any recent version | Every check reads the Git index |
| Python | 3.13 | `tools/check.py` and its gates |
| Ruff, mypy, PyYAML, openpyxl | The hash-locked versions in `tools/requirements-quality-ci.txt` | `ruff`, `ruff-complexity-probe`, `mypy`, `mypy-strict-probe`, `issue-config`, `workflow-invariants`; openpyxl and its type stubs for `mypy` and the template test in `tool-tests` |
| Node.js | 22 | The label scripts in `.github/scripts/`, and the `issue-config` gate |
| actionlint | 1.7.12 | Workflow syntax |

`tools/check.py` itself needs only the Python standard library. LibreOffice
is optional: only the prototype's workbook builder, its smoke test and
`tools/preview.py` use it ([docs/PROTOTYPE.md](docs/PROTOTYPE.md)), the checks
never do, and a run in it
is not evidence for Excel.

1. Create a virtual environment and install the Python quality tools. The
   hashes cover CPython 3.13 on Linux x86_64, as in CI. Git ignores `.venv/`,
   so it does not make the working tree dirty:

   ```sh
   python3 -m venv .venv
   . .venv/bin/activate
   python -m pip install --only-binary=:all: --require-hashes -r tools/requirements-quality-ci.txt
   ```

2. Install actionlint 1.7.12 in a folder next to the repository, never inside
   it: an archive or binary left in the checkout makes the working tree dirty
   and `--ci` fails. Check the archive against the SHA-256 that
   `.github/workflows/repository-integrity.yml` pins. On Linux x86_64, from
   the repository root:

   ```sh
   mkdir -p ../klcr-tools
   curl -fsSL -o ../klcr-tools/actionlint.tar.gz \
     https://github.com/rhysd/actionlint/releases/download/v1.7.12/actionlint_1.7.12_linux_amd64.tar.gz
   printf '%s  %s\n' 8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8 \
     ../klcr-tools/actionlint.tar.gz | sha256sum --check --strict
   tar --no-same-owner -xzf ../klcr-tools/actionlint.tar.gz -C ../klcr-tools actionlint
   export PATH="$(cd ../klcr-tools && pwd):$PATH"
   ```

3. Check that `node --version` prints `v22`.

4. Run every gate:

   ```sh
   python tools/check.py --ci
   ```

| Mode | Result |
| --- | --- |
| *(default)* | Runs every gate; a missing tool is **NOT RUN** and fails the run |
| `--allow-missing` | Reports missing tools and ends **INCOMPLETE** with exit code 0. An incomplete run is never a pass; use it only to diagnose a setup |
| `--ci` | Also requires a clean checkout, as CI does |

The reports go to `test-results/`, which Git ignores:
`repository-integrity.json` names the candidate SHA, the mode, whether the tree
was dirty, each gate's result and the tool versions. The gates are listed in
[tools/README.md](tools/README.md#-gates). These checks need no Excel and
demonstrate no VBA behaviour and no LCR calculation.

<a id="verified-setup"></a>

## ✅ Verified setup

I ran the shell blocks of *Get the source* and *Developer setup*, extracted verbatim from this page, in a new empty folder: on 2026-11-05 for #19, and again for the documentation audit (#22) after the `binaries` gate was added; on 2026-11-09 for the update of Ruff and mypy (#156). The table records the third run:

| Item | Value |
| --- | --- |
| Commit | `7afec586713d1a62f3c04679c9ffe293c09b8b5e`, the head of the pull request that updates the tools (#158), checked out in place of the release branch (earlier runs: `a8784cb` with 20 gates, `fc98b17` with 21) |
| System | Ubuntu 24.04.5 LTS, Linux x86_64 |
| Tools | Git 2.43.0, Python 3.13.17, Node.js 22.22.0, actionlint 1.7.12, Ruff 0.17.2, mypy 2.4.0, PyYAML 6.0.3 |
| Fresh clone | `git status --short` printed nothing, before and after the setup; the virtual environment is ignored and actionlint sits in `../klcr-tools` |
| actionlint archive | `sha256sum --check --strict` printed `OK` (on 2026-11-05 a first attempt stopped at the download with HTTP 504, and the repeated run passed) |
| `python tools/check.py --ci` | All 21 gates PASS; exit code 0; the report names the commit, mode `ci`, `dirty: false`, status `pass` |
| Without actionlint on `PATH` | With `--ci`: `actionlint: NOT RUN`, overall FAIL, exit code 1; with `--allow-missing` instead (the two options exclude each other), INCOMPLETE and exit code 0 |
| With an untracked file and `--ci` | "working tree is dirty: --ci requires a clean checkout", FAIL, exit code 1 |

**Not executed:** the developer setup on Windows or macOS, and every Excel
step below.

## 🧯 Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| `pip` refuses a package with "hashes are required" or finds no matching distribution | The hashes cover CPython 3.13 on Linux x86_64 only. Use Linux, WSL or a Linux container. Installing the same versions without `--require-hashes` works elsewhere, but is not hash-verified: never use it to produce evidence. |
| A gate reports **NOT RUN** | Its tool is missing or not on `PATH` (Ruff, mypy, Node.js or actionlint). Install it as above. Without PyYAML, `issue-config` and `workflow-invariants` are NOT RUN locally and fail in CI. |
| The run ends **INCOMPLETE** | It ran with `--allow-missing`. Install the missing tools and run again without it: INCOMPLETE is never a pass. |
| "working tree is dirty" with `--ci` | A file is modified or untracked, such as a downloaded tool archive. Commit, stash or remove it, and keep tools outside the checkout; generated reports belong in the ignored `test-results/`. |
| `tracked-text` fails on CR, trailing white space or a missing final newline | Fix the file named in the finding. VBA exports are stored with LF and checked out with CRLF by `.gitattributes`: do not change the line-ending settings. |
| `changelog` fails on a shallow checkout | Clone with full history, or run `git fetch --unshallow --tags`. |

## 🔐 Excel prerequisites

Not executed here. Building and running the prototype workbook on Windows
needs:

- desktop Excel 64-bit, with macros allowed only for the workbook you build
  from the candidate, never by lowering the security of other workbooks;
- **Trust access to the VBA project object model**, in Trust Center >
  Macro Settings, only for `tools/Sync-KLCR-VBA.ps1` and only as your
  organization's policy allows; switch it off again afterwards;
- a downloaded workbook unblocked only after its SHA-256 matches the recorded
  one (File Properties > Unblock), as your organisation's policy allows;
- no add-in, reference or COM library beyond the standard references, unless a
  reviewed exception names it.

## 📥 Importing VBA into Excel

Not executed here: no step of this section has been run on a Windows Excel
host, so none of it is host evidence yet (#15).

Every workbook is built from the macro-free template
`src/workbook/LCR_Template.xlsx`. The repository stays the source: never
commit a macro-enabled workbook; build it outside the checkout or under the
ignored `test-results/`.

`tools/vba-projects.json` lists the components of each workbook, and the
`vba-manifest` gate keeps it equal to the tracked components:

| Workbook | Components |
| --- | --- |
| Production | Every standard and class module under `src/`. The **Self-test** button on `Results` calls `TEST_Engine`, which only the development workbook holds |
| Development | The production components and every component under `tests/`: the prototype's self-test and the neutral harness with its example suite |
| Both | The document modules of `src/workbook/` (`ThisWorkbook`, `sh<Sheet>`), whose code replaces the code of the existing workbook and sheet objects |

### By hand

This route needs no special Excel setting.

1. Copy the template to a new file; never work on a user workbook.
2. In the VBE (Alt+F11), use File > Import File for each `.bas` and `.cls`
   module of the workbook you are building. For a document module, paste its
   code below the existing `Option Explicit` of the matching object instead
   of importing it; the prototype's document modules hold nothing else.
3. Debug > Compile VBAProject, and save as `.xlsm`.

<a id="synchronizing-vba"></a>

### With the synchronization script (optional)

`tools/Sync-KLCR-VBA.ps1` does step 2 for you. It needs **Trust access to
the VBA project object model** ([Excel prerequisites](#-excel-prerequisites)),
which the manual route does not. With the workbook closed, drag the `.xlsm`
onto `tools/Sync-KLCR-VBA.cmd`, or run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\Sync-KLCR-VBA.ps1 -WorkbookPath "C:\path\K-LCR.xlsm" -Mode Development
```

| It does | Details |
| --- | --- |
| Imports the components of one workbook | `-Mode Production` or `-Mode Development`, as listed in `tools/vba-projects.json`. Without `-Mode` it asks. A component found under a source folder but missing from the manifest stops it before Excel is opened. |
| Replaces document-module code, if you agree | It asks, unless `-IncludeSheets` or `-SkipSheets` answers; the workbook's sheet objects are kept. |
| Builds the workbook | `-FromTemplate` saves the template as an `.xlsm` at `-WorkbookPath`, replacing a file of that name, before the synchronization, so the sheets are the current template's. |
| Imports from a folder | `-SourceDir` (or `tools/Sync-KLCR-VBA-Downloads.cmd`, which asks for one and defaults to `Downloads`) takes only the `.bas` and `.cls` files found there, by their `Attribute VB_Name`, after listing them for confirmation. A new standard module is taken only with a project prefix (`CORE_`, `LCR_`, `M_`, `TEST_`). |
| Protects the workbook | A backup copy first, removed after a successful save; `-NoBackup` skips it, and `-FromTemplate` takes none because it replaces the file at `-WorkbookPath`. It writes no cells, formulas, names or formatting, and before saving it checks that no sheet was added, removed, renamed or reordered. The workbook is closed unsaved on any error. `-Visible` shows the Excel window. |

It never writes to the repository, never runs the VBA and records no run.
After it, compile as in step 3.

**Exit codes and recovery:**

| Exit code | Meaning | What to do |
| --- | --- | --- |
| 0 | Synchronized and saved; the backup is removed | Compile and run what you need |
| 1 | Failed: the workbook was closed without saving | The message names the cause. If a backup was taken, its path is printed and it is kept beside the workbook (`<name>.pre-vba-sync.<timestamp>.xlsm`): the workbook itself is unchanged, so remove the backup once you have checked that. With `-NoBackup` there is no copy. With `-FromTemplate` a workbook that was at that path is gone and the file there is the template saved as `.xlsm`: run again, or rebuild it |
| 2 | Cancelled, or nothing to import: the workbook was not changed | Nothing |

A synchronization that runs twice imports the same components twice and
leaves the same project: standard and class modules are removed and imported
again, document-module code is replaced, and the sheet structure is checked
before saving. That idempotence, and the preservation of cells, formats and
names around it, are what #14 asks a host run to demonstrate; neither has
been observed yet.

<a id="exporting-changes-back"></a>

### Exporting changes back

1. In the VBE, right-click each changed component > **Export File**, and save
   it over its file in the checkout, in the same folder. For a document
   module, copy its code back into the matching `src/workbook/` file below
   the existing `Attribute` lines instead.
2. Review `git diff`. The VBE changes the capitalization of an identifier
   everywhere it appears when one declaration changes case; revert case-only
   changes you did not intend. Check that no non-ASCII character was
   introduced ([export compatibility](docs/VBA_HOUSE_STYLE.md#-export-compatibility-and-host-evidence)).
3. A new component goes into `tools/vba-projects.json` too, or the
   `vba-manifest` gate fails.
4. Run `python tools/check.py`. Its `vba-*` gates check the exported files
   statically; they do not replace compiling in Excel.
5. Commit. Git stores the files with LF; nothing is converted by hand.

Exported files keep the VBE's header lines (`VERSION`, `BEGIN ... END`,
`Attribute`). Never edit or remove them when reformatting.

## 🧾 Recording host evidence

Not executed. A host run records the exact candidate SHA, a clean working
tree, the Excel build and bitness, the Windows version, the locale, the
import and compile results, the case counts and the cleanup result.
`NOT_RUN` stays distinct from `PASS`. #15 defines the evidence and its
validator; until such a run, every host above is an intended target only.
