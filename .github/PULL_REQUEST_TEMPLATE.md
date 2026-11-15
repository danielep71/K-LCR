<!--
  Base: release/0.1.0, the active release branch named in docs/GOVERNANCE.md,
  for task PRs. main only for a release integration approved by me; main into
  the release branch only for a sync PR. State which route applies below.
  Write NOT RUN or NOT APPLICABLE with a reason; never claim evidence that
  was not produced. Synthetic data only; no secrets or vulnerability details.
-->

## 🔗 Linked issues

<!-- Link task issues with Resolves #; integration and sync PRs use Refs #
for the issues and preceding PRs they carry. -->

Resolves #

## 🧾 Changes

-

## 💡 Why

## ✅ Validated

<!-- Commands and checks actually run, with results. Hosted checks run on this pull request. -->

- [ ] `python tools/check.py --ci` (all gates PASS; INCOMPLETE is not a pass)
- [ ] Other checks specific to this change:

## 🔎 Final-head review

<!-- Wait for the automated code review of the current head to complete
(docs/GOVERNANCE.md, Task integration and review). It does not re-run after a
push by itself: request a re-run with the reviewer's review comment, under my
standing permission of 2026-11-05. Write the reviewed
SHA and the result here as text: the review summary comment is edited in
place, so its link later shows another commit. For a bot-authored PR, record
my review of the final head and that the automated review was skipped. A sync
PR needs CI only when its head is the integration's merge commit, its diff
against the release branch is empty and the integration's final-head review
covered the same tree: record the empty diff and name that review. A sync that
changes any file is reviewed as usual. -->

- Final PR head SHA:
- Review type (automated review / my review of a bot-authored PR / not required: unchanged sync PR, naming the integration's review):
- Reviewed commit SHA, result (as text) and review link:
- `Repository integrity` result and run link:

- [ ] Review covers the current PR head; all findings are fixed or answered and applicable threads resolved.
- [ ] `Repository integrity` passes for the current revision and GitHub merge requirements are satisfied.
- [ ] Any push after this record is followed by renewed review and CI verification.

## ⚠️ Not validated

<!-- State plainly what was not checked and why. Write "Nothing" only if that is true. -->

## ☑️ Checklist

- [ ] The base follows docs/GOVERNANCE.md: release/0.1.0 for tasks; main only for an approved integration.
- [ ] Each linked issue has the assignee, exactly one priority label and a milestone; this PR has no milestone and carries the labels of its issue.
- [ ] Scope is focused: no unrelated changes, local artifacts or generated output.
- [ ] Documentation affected by the change is updated, and `CHANGELOG.md` has an `[Unreleased]` entry for a material change (or none is needed).
- [ ] No tokens, credentials, real portfolio or client data.
