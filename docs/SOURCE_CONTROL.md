# 🗃️ Source control and generated files

[![Text: LF in Git](https://img.shields.io/badge/Text-LF_in_Git-0969da?style=flat-square)](#-verify-a-checkout)
[![VBA: CRLF checkout](https://img.shields.io/badge/VBA-CRLF_checkout-217346?style=flat-square)](#-verify-a-checkout)

These rules implement issue #5 for the selected Excel/VBA architecture. The
tracked source remains text first; a workbook is a host artifact, not the
canonical calculation source.

- Git stores text with LF. Exported `.bas`, `.cls` and `.frm` files check out
  with CRLF for Windows desktop Excel. `.frx` companions and Office packages
  are binary. Documentation, configuration, Python and JavaScript check out
  with LF. `.editorconfig` guides editors; `.gitattributes` controls Git.
- No VBA encoding conversion is configured. The VBE export code page and
  import behavior need a real supported-host round trip under #6/#14. The ASCII-only repository convention in [VBA house style](VBA_HOUSE_STYLE.md)
  is a source-authoring rule, not a validated VBE encoding or code-page claim.
- Ignore generated workbooks, reports, caches, secrets and workstation files.
  Keep exported source, fixtures and repository configuration trackable.
  An approved macro-free template, if introduced in #14, gets one exact
  rooted negation rule in `.gitignore` and a manifest; no generic exception.
- Create `src/`, `tests/` and `templates/` only with meaningful content,
  following [the proposed layout](REPOSITORY_STRUCTURE.md).

## 🧪 Verify a checkout

From a fresh checkout at the exact candidate commit:

```sh
git status --short
git ls-files --eol
git check-attr text eol -- path/to/module.bas
git check-ignore -v -- test-results/sample.json scratch.xlsm
git diff --check
```

The first command should be empty. A future VBA module should show `i/lf`
and `w/crlf` on Windows; repository Markdown should show LF in both locations.
Check generated outputs using `git check-ignore`; source and fixtures should
remain visible. Never run `git add -f` on an ignored workbook without an
explicit reviewed allowlist entry.

For a new `.gitattributes` policy, inspect `git add --renormalize .` and
`git diff --cached --check` before committing a separate mechanical change.
Whitespace gates must read index/commit bytes (for example `git show HEAD:path`),
not flag the CRLF working-tree bytes imposed by `eol=crlf`. Both a clean
checkout and an unchanged export/import round trip are needed before claiming
supported host behavior. The host round trip is tracked in #14/#15.
