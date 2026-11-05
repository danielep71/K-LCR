# 📦 Installation and developer setup

[![Host: Windows 64-bit target](https://img.shields.io/badge/Host-Windows_64--bit_target-217346?style=flat-square)](#host-matrix)
[![Excel evidence: Not run](https://img.shields.io/badge/Excel_evidence-Not_run-BF8700?style=flat-square)](#host-matrix)
[![Developer setup: Verified](https://img.shields.io/badge/Developer_setup-Verified_2026--11--05-2ea44f?style=flat-square)](#verified-setup)

K-LCR holds repository setup, contracts and static checks. It has **no VBA
source and no workbook** yet, so nothing can be installed into Excel. This
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

Verified. Clone the repository, switch to the active release branch and note
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

Verified on Linux. The repository checks need:

| Tool | Version | Used by |
| --- | --- | --- |
| Git | Any recent version | Every check reads the Git index |
| Python | 3.13 | `tools/check.py` and its gates |
| Ruff, mypy, PyYAML | The hash-locked versions in `tools/requirements-quality-ci.txt` | `ruff`, `mypy`, `issue-config`, `workflow-invariants` |
| Node.js | 22 | The label scripts in `.github/scripts/` |
| actionlint | 1.7.12 | Workflow syntax |

`tools/check.py` itself needs only the Python standard library.

1. Create a virtual environment and install the Python quality tools. The
   hashes cover CPython 3.13 on Linux x86_64, as in CI:

   ```sh
   python3 -m venv .venv
   . .venv/bin/activate
   python -m pip install --only-binary=:all: --require-hashes -r tools/requirements-quality-ci.txt
   ```

2. Install actionlint 1.7.12 and check its archive against the SHA-256 that
   `.github/workflows/repository-integrity.yml` pins. On Linux x86_64:

   ```sh
   curl -fsSL -o actionlint.tar.gz \
     https://github.com/rhysd/actionlint/releases/download/v1.7.12/actionlint_1.7.12_linux_amd64.tar.gz
   printf '%s  %s\n' 8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8 \
     actionlint.tar.gz | sha256sum --check --strict
   tar --no-same-owner -xzf actionlint.tar.gz actionlint
   ```

   Put the extracted `actionlint` on your `PATH`, outside the repository.

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

I ran the steps above from a fresh clone on 2026-11-05 (#19):

| Item | Value |
| --- | --- |
| Commit | `a8784cb0319b8f3f5a9962a5194c801275f2f535` on `release/0.1.0` |
| System | Ubuntu 24.04.5 LTS, Linux x86_64 |
| Tools | Git 2.43.0, Python 3.13.17, Node.js 22.22.0, actionlint 1.7.12, Ruff 0.16.6, mypy 2.3.1, PyYAML 6.0.3 |
| Fresh clone | `git status --short` printed nothing |
| actionlint archive | `sha256sum --check --strict` printed `OK` |
| `python tools/check.py --ci` | All 20 gates PASS; exit code 0; the report names the commit, mode `ci`, `dirty: false`, status `pass` |
| Without actionlint on `PATH` | `actionlint: NOT RUN`, overall FAIL, exit code 1; with `--allow-missing`, INCOMPLETE and exit code 0 |
| With an untracked file and `--ci` | "working tree is dirty: --ci requires a clean checkout", FAIL, exit code 1 |

**Not executed:** the developer setup on Windows or macOS, and every Excel
step below.

## 🧯 Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| `pip` refuses a package with "hashes are required" or finds no matching distribution | The hashes cover CPython 3.13 on Linux x86_64 only. Use Linux, WSL or a Linux container. Installing the same versions without `--require-hashes` works elsewhere, but is not hash-verified: never use it to produce evidence. |
| A gate reports **NOT RUN** | Its tool is missing or not on `PATH` (Ruff, mypy, Node.js or actionlint). Install it as above. Without PyYAML, `issue-config` and `workflow-invariants` are NOT RUN locally and fail in CI. |
| The run ends **INCOMPLETE** | It ran with `--allow-missing`. Install the missing tools and run again without it: INCOMPLETE is never a pass. |
| "working tree is dirty" with `--ci` | A file is modified or untracked. Commit, stash or remove it; generated reports belong in the ignored `test-results/`. |
| `tracked-text` fails on CR, trailing white space or a missing final newline | Fix the file named in the finding. VBA exports are stored with LF and checked out with CRLF by `.gitattributes`: do not change the line-ending settings. |
| `changelog` fails on a shallow checkout | Clone with full history, or run `git fetch --unshallow --tags`. |

## 🔐 Excel prerequisites

Not executed: there is no workbook yet. Once the host template exists (#14),
building and running it on Windows will need:

- desktop Excel 64-bit, with macros allowed only for the workbook you build
  from the candidate, never by lowering the security of other workbooks;
- **Trust access to the VBA project object model**, in Trust Center >
  Macro Settings, only if the import tooling of #14 uses it; switch it off
  again afterwards;
- a downloaded workbook unblocked only after its SHA-256 matches the recorded
  one (File Properties > Unblock), as your organisation's policy allows;
- no add-in, reference or COM library beyond the standard references, unless a
  reviewed exception names it.

## 📥 Importing VBA into Excel

Not executed. #14 defines the macro-free template, the component manifest,
the backup-before-change rule and the repeatable import and export tooling.
Until then, the **manual fallback**, for a developer trying a module by hand,
is:

1. Copy an approved macro-free template to a new file; never work on a user
   workbook.
2. In the VBE (Alt+F11), use File > Import File for each `.bas` and `.cls`
   module; a `.frm` travels with its `.frx`. Map document modules onto the
   existing workbook and sheet components instead of importing them.
3. Debug > Compile VBAProject, then run the neutral harness of #13.
4. Export the components again and compare them with the repository, which
   stays the source: never commit a macro-enabled workbook.

This fallback has not been run and proves nothing about a host.

## 🧾 Recording host evidence

Not executed. A host run records the exact candidate SHA, a clean working
tree, the Excel build and bitness, the Windows version, the locale, the
import and compile results, the case counts and the cleanup result.
`NOT_RUN` stays distinct from `PASS`. #15 defines the evidence and its
validator; until such a run, every host above is an intended target only.
