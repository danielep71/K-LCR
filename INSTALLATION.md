# Installation and host evidence

K-LCR currently contains repository setup and planned contracts, with no
Excel/VBA calculation components or workbook to install. This page adapts
the established installation guidance to K-LCR's present state; it does not
describe a procedure already executed.

## Host matrix

| Host | Intended status | Tested status |
| --- | --- | --- |
| Windows desktop Microsoft 365 Excel, 64-bit | Initial engineering target | No import, compile or harness evidence yet |
| Windows desktop Excel, 32-bit | Outside initial target | Not tested |
| macOS, web, mobile or older Excel | Outside initial target | Not tested |

Exact build and locale support will be recorded after genuine host runs in
#15. No version is certified. The intended baseline uses the standard VBA,
Excel and Office references available in a new desktop workbook; any added
library or COM dependency needs a reviewed inventory and host test.

## Source and developer setup

Fetch the current `release/0.1.0` candidate and verify its full commit SHA.
Read [source-control conventions](docs/SOURCE_CONTROL.md),
[VBA style](docs/VBA_HOUSE_STYLE.md) and
[architecture](docs/REPOSITORY_STRUCTURE.md). The current portable checks
are:

```sh
node .github/scripts/labels-sync.mjs --self-test
node .github/scripts/labels-sync.mjs --mode validate
node .github/scripts/labels-drift.mjs --self-test
python tools/check_issues.py --check-config
python -m unittest discover -s tools -p 'test_check_issues.py'
```

These checks do not require Excel and do not demonstrate VBA behavior.
Generated reports belong in `test-results/`, which Git ignores.

## Future Excel import/export contract

Issue #14 will define the actual macro-free template, component manifest,
backup-before-change rule and repeatable import/export tooling. Standard
`.bas`/`.cls` modules are imported into a temporary copy of an approved
workbook; document modules are mapped into existing workbook/sheet components;
`.frm` travels with its `.frx`. Verify component names and encoding, compile,
run the neutral harness, export again and compare source/behavior. Do not
overwrite a user workbook or rely on a macro-enabled artifact as source.

The host run logs exact candidate SHA, clean worktree, Excel build/bitness,
Windows version, locale, imports/compile result, case counts and cleanup.
`NOT_RUN` remains distinct from `PASS`. The recorded evidence and
candidate validator are specified in #15. Until that run, host support is
an intended target only.
