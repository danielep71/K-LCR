# 🧾 Milestone closeout

The record for closing a milestone: what was delivered, what evidence shows
it, and what closing it does and does not mean. Copy the template below into
the milestone's closing issue, and close the milestone only when every row
links its evidence or records a deviation. The procedure is
[Closing a milestone](../../RELEASING.md#closing-a-milestone) in
RELEASING.md. Closing a milestone publishes nothing; a release follows the
rest of RELEASING.md separately, by my decision.

## Template

```markdown
## Closeout: vX.Y.Z - <title>

### Sequence

| Step | Needs | Produces |
| ---: | --- | --- |
| 1 | The milestone's remaining issues | Each closed with a Resolution, or moved with a scope-change note |
| 2 | Step 1 and my authorization | The release branch integrated into main and synchronized back |
| 3 | Step 2 | The candidate record, from a fresh clone of the candidate |
| 4 | Step 3 | The audits and settings evidence the milestone requires |
| 5 | Step 4 | The evidence index and the scope statement |
| 6 | Step 5 | My decision: close without a release, or prepare one (RELEASING.md) |

### Checklist

| # | Criterion | Evidence | Done |
| ---: | --- | --- | :---: |
| 1 | Every issue of the milestone is closed with a Resolution, or moved with a reason | Evidence index | ☐ |
| 2 | No open pull request carries the milestone; every open issue elsewhere that names one of its issues as a prerequisite is updated | Milestone and issue links | ☐ |
| 3 | `python tools/check.py --ci` passes from a fresh clone of the candidate | Candidate record | ☐ |
| 4 | Repository integrity is green on the candidate on main | Run link | ☐ |
| 5 | Live labels match the catalogue, and Issue triage passes | Label drift and Issue triage run links | ☐ |
| 6 | The settings evidence is current for the candidate | `docs/REPOSITORY_SETTINGS_EVIDENCE.md` at the candidate | ☐ |
| 7 | The file and documentation audits cover the candidate | Audit issues | ☐ |
| 8 | The changelog's `[Unreleased]` section describes what the milestone delivered | `CHANGELOG.md` at the candidate | ☐ |
| 9 | The scope statement is recorded | This issue | ☐ |

### Candidate record

| Item | Value |
| --- | --- |
| Candidate commit | Full 40-character SHA on main |
| Integration and sync pull requests | #N, #N |
| Fresh clone | `git status --short` printed nothing: yes or no |
| Repository checks | `python tools/check.py --ci`: result, and `test-results/repository-integrity.json` naming the candidate |
| Tool versions | Git, Python, Node.js and actionlint used |
| Hosted CI | Repository integrity run link and result |
| Excel run | The host and the evidence, or "none" |
| Deviations | None, or each criterion not met and my decision to accept it |

### Evidence index

| Issue | Subject | Evidence | Verified at candidate |
| --- | --- | --- | :---: |
| #N | Title | Its Resolution | ☐ |

### Scope statement

vX.Y.Z <title> is closed at commit <SHA>. It delivers <what>. It does not
certify <what it does not cover>; no version is released by this closeout.
Limitations: <list>.
```
