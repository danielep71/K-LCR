# 🧪 VBA test harness

**Neutral · Deterministic · Source only, not yet run in Excel**

The harness runs the VBA test suites of K-LCR and writes a complete,
line-based log of each run. It is **neutral**: it holds no regulatory rule and
no LCR calculation, and it needs no workbook, file, clock or Excel object, so
a suite that uses it behaves the same in any host. It proves infrastructure
only; a green run of its example suite says nothing about a Liquidity Coverage
Ratio.

**Status.** The two modules below are source text. They have been read by the
[static checks](../VBA_HOUSE_STYLE.md#-static-checks) and by
`tools/test_vba_harness.py`, and listed in the development workbook of
`tools/vba-projects.json`; in LibreOffice they have only been imported into
that workbook by `tools/build_xlsm.py`, never run. They have **not been
compiled or run in Excel**. The first import, compile and run on a supported host is
planned in #14 and #15; until then, every statement here about how a run ends
is what the source says it does, not an observation.

## Modules

| Module | Holds |
| --- | --- |
| `tests/unit/TEST_LCR_Harness.bas` | The run lifecycle (`BeginRun`, `BeginCase`, `RecordCaseError`, `EndRun`), the assertions (`AssertEqualDouble`, `AssertNear`, `AssertEqualText`, `AssertTrue`, `AssertRaised`), the comparison rule `WithinTolerance`, the log (`Say`, `LogText`, `LastResult`) and `ResetTests` |
| `tests/unit/TEST_LCR_Examples.bas` | The example suite: one case per kind of assertion, four modes, and `VerifyExampleModes`, which checks that each mode ends as it must |

Both use `Option Private Module`, so they never become part of the workbook's
external surface. A production workbook contains neither. The names follow the
[VBA house style](../VBA_HOUSE_STYLE.md#%EF%B8%8F-naming-and-component-boundaries)
(`TEST_LCR_<Name>` in `tests/unit/`).

A project suite follows the example suite: one `Case` procedure per case, each
starting with `BeginCase` and ending in an error handler that calls
`RecordCaseError`; a runner that calls every case once, between `BeginRun` and
`EndRun`; and the expected case and assertion counts as constants. The expected
values of a numerical case come from its [test case](TEST_CASES.md), with the
tolerance that the case states.

## What is neutral and what is not

| Concern | Where it lives |
| --- | --- |
| Counting cases and assertions, identifiers, tolerance rule, completeness, the log | `tests/unit/` (this harness): independent of workbook state and of any host I/O |
| Saving a log to a file, the environment record (host, version, Office bitness) | `tests/host/`, with the host run of #14 and #15 |
| Checking that the host state is as it was (calculation mode, alerts, events, screen updating, open workbooks) | `tests/host/`: the host test passes what it found to `EndRun` as `CleanupProblems` |
| Evidence bound to one commit and the rejection of stale or mismatched evidence | #15 |

The `vba-dynamic` check of Repository integrity forbids native, dynamic and COM
constructs in `tests/unit/`, and `tools/test_vba_harness.py` forbids the names
that would tie the harness to a host, a file, the clock or chance.

## Run outcomes

`EndRun` reports four outcomes separately:

| Outcome | Values | Meaning |
| --- | --- | --- |
| `operation` | `PASS`, `FAIL`, `ERROR` | What ran: every assertion passed, an assertion or a case identifier failed, or an unexpected error occurred |
| `completeness` | `COMPLETE`, `INCOMPLETE` | `COMPLETE` only when both expected counts were met exactly. A skipped or an extra case or assertion is `INCOMPLETE`, whatever the cases that ran did ([registered and executed](TEST_CASES.md#-registered-and-executed)) |
| `cleanup` | `PASS`, `FAIL` | `FAIL` when the caller passed a non-empty `CleanupProblems`: the host state changed. A cleanup failure is not an assertion failure, and the operation outcome does not hide it |
| `recovery` | `NONE`, `REQUIRED` | `REQUIRED` when cleanup failed, or when a run was interrupted |

`RESULT=PASS` needs `operation=PASS`, `COMPLETE`, cleanup `PASS` and no
recovery. Any other run raises `ERR_TEST_FAILED`, or the unexpected error that
escaped the runner, only after its summary is logged. The runner's error is
never replaced by a cleanup failure: both are reported.

A run that starts while another is active, or while recovery is required, is
refused with `ERR_TEST_DIRTY_START`. Check the host state by hand, then call
`TEST_LCR_Harness.ResetTests`; it restores nothing itself.

## The example suite and its modes

The example suite has 3 cases and 9 assertions: `exact-comparison` (an exact
Double, a text and a condition), `tolerance-comparison` (an absolute bound, a
relative bound, the absolute bound near zero and a value the rule rejects) and
`expected-error` (an error raised and the same call raising nothing). It runs
in four modes:

| Mode | Must end | One failure |
| --- | --- | --- |
| `NORMAL` | `RESULT=PASS`; `operation=PASS`, `COMPLETE`, `cases=3; assertions=9; failures=0`, cleanup `PASS` | none |
| `INJECTED_FAILURE` | `RESULT=FAIL`; `operation=FAIL`, `COMPLETE`, `cases=3; assertions=9; failures=1`, cleanup `PASS` | the designated assertion, `exact-comparison/half-of-one` |
| `SKIPPED_CASE` | `RESULT=FAIL`; `operation=PASS`, `INCOMPLETE`, `cases=2; assertions=7; failures=1`, cleanup `PASS` | `harness.completeness` |
| `CLEANUP_PROBLEM` | `RESULT=FAIL`; `operation=PASS`, `COMPLETE`, `cases=3; assertions=9; failures=0`, cleanup `FAIL`, recovery `REQUIRED` | none: the cleanup outcome fails on its own |

Each deliberate mode must reach its caller as `ERR_TEST_FAILED`: this is the
self-test that a failed run is never silent. `VerifyExampleModes` runs the four
modes in order and returns a report with the required and the actual `RESULT`
of each; `CheckExampleModes` prints it and raises `ERR_TEST_FAILED` when a mode
did not end as required. The cleanup problem of the last mode is simulated, so
the verification acknowledges it with `ResetTests`, but only when that mode ran
in the same call and ended as required. If a run was active or recovery was
already required, every start is refused, the verification reports the
deviations and leaves that state as it found it: the manual check of the host
state that `ResetTests` stands for is never bypassed.

To run the suite in Excel (planned, #14 and #15), build a development workbook
with `tools/Sync-KLCR-VBA.ps1` (not yet run on a host) or import the two
modules from `tests/unit/` into a scratch workbook by hand, open the Immediate
window and run
`TEST_LCR_Examples.CheckExampleModes`. That run has **not** been made.

## Log format

One record per line, `KEY=value`, with further fields separated by `; `. `RUN`
comes first; `CASE`, `ASSERT`, `ERROR` and `FAILURE` follow as the run reaches
them; the summary records come last, in the order of the table:

| Record | Fields |
| --- | --- |
| `RUN=<suite>` | `mode` (`NORMAL` or a deliberate mode), `expected_cases`, `expected_assertions` |
| `CASE=<case-id>` | One per case, in run order |
| `ASSERT=<case-id>/<name>` | `status` (`PASS` or `FAIL`); on failure, the expected and actual values |
| `FAILURE=<id>` | One per failure: an assertion, `<case-id>.unexpected-error`, `runner.unexpected-error`, `harness.case-id`, `harness.no-case` or `harness.completeness`, with its detail |
| `ERROR=<case-id>` or `ERROR=run` | `number`, `source`, `description` of an unexpected error |
| `CASES=<n>`, `ASSERTIONS=<n>` | `expected` |
| `FAILURES=<n>` | `errors` |
| `PRIMARY_FAILURE=<id>` | The first failure of the run, when there is one |
| `CLEANUP=PASS` or `FAIL` | `detail`: `no change reported`, or what the caller found changed |
| `RECOVERY=NONE` or `REQUIRED` | `reason`, `action`, when required |
| `RESULT=PASS` or `FAIL` | `suite`, `operation`, `completeness`, `cases`, `assertions`, `failures`, `cleanup`, `recovery` |

`RESULT` is always the last record of a run. A refused start writes a
`RECOVERY=REQUIRED` record and a `RESULT=FAIL` with `operation=NOT_RUN`, and
`ResetTests` writes `RESET=DONE`.

## Reproducibility

The log holds no time, machine, user or path, and the harness reads no clock,
file or random generator. Two runs of the same suite in the same mode therefore
write the same log byte for byte, and `LogText` returns it with line feeds as
separators. Case identifiers and assertion names are fixed in the suite's
source, so two logs can be compared line by line. A number is written with
`Str$`, which uses a period whatever the regional settings.

Reproducibility on a host is a claim of #15, not of this page: it needs a real
run on the supported profile, the Office build and bitness, and the log saved
by `tests/host/`.
