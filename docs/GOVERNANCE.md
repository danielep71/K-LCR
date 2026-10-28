# 🏛️ Repository governance

[![Branch: release/0.1.0](https://img.shields.io/badge/Branch-release%2F0.1.0-217346?style=flat-square)](#-ownership-and-development-target)
[![Checks: Repository integrity](https://img.shields.io/badge/Checks-Repository_integrity-0969da?style=flat-square)](#-local-validation)

K-LCR uses a 20-label catalogue and the issue-triage rules defined below.
Names, colors and descriptions are versioned in [.github/labels.json](../.github/labels.json).
The application profile has no additional labels.

## 👤 Ownership and development target

Daniele Penza (@danielep71) decides scope, priorities and release integration.
All development goes first into **release/0.1.0**. The GitHub default branch
remains main, but it is not the development target. This includes documentation,
tooling, dependency updates and fixes.

| Branch | Role |
| --- | --- |
| main | Integrated baseline; accepts only a release integration PR after explicit owner authorization for that candidate. |
| release/0.1.0 | Active development/integration branch for v0.1.0 - Repo setup; created from main at ff01720c79633d28ba342a7a1ac2c6836aafdf95 on 2026-10-28. |
| `docs/<issue>-<slug>`, `fix/<issue>-<slug>`, `feat/<issue>-<slug>` | Short-lived task branches cut from the active release branch; PRs target release/0.1.0. |
| traffic-history | Reserved data-only branch; not yet created. Never a task base or merged into source branches. |

A new active release branch requires an owner decision. A release branch name,
completed issue, green check or closed milestone does not authorize integration
into main, tagging, publication or a visibility change.

## 🔀 Task integration and review

1. Read the issue, branch from the current release/0.1.0 head and keep the change
   within the authorized task.
2. Open a PR explicitly targeting release/0.1.0. Link the issue, describe the
   resulting behavior, validation and limitations. Do not assign a PR milestone.
3. Review the final diff and record the exact head SHA, reviewer identity,
   findings and their resolution in the PR description or review. Keep author
   attribution truthful; an agent review must not be described as owner approval.
4. Require a passing Repository integrity check for the current candidate and
   current base, an up-to-date task branch and resolved review conversations.
   Path-specific label checks supplement the universal required check.
5. Squash-merge the task PR into release/0.1.0 within the owner's task
   authorization. Use a subject ending in the PR number and a body linking the
   issue. Verify the release push check, then record issue completion evidence.

The sole owner cannot approve their own PR. Rulesets therefore require a PR
with zero approving reviews; this does not waive review or the separate owner
authorization required for main. CI and review are separate evidence. After any
head change, repeat the affected validation and review and record the new SHA.
If a Codex or other external review is used, record whether it actually completed
for that SHA, including findings; do not infer coverage from a previous review.
Automated Codex code review was observed on 2026-10-28 for exact PR heads,
including [PR #24](https://github.com/danielep71/K-LCR/pull/24#issuecomment-6477467917)
at `6063d866a9bec9bf89a02e4634dd726650ee5f6a` and
[PR #40](https://github.com/danielep71/K-LCR/pull/40#issuecomment-6478923525)
at `2815175929c60cd144fa172bd26517c88b58aec8`, with no reported findings.
These receipts establish code-review completion for those commits only, not
maintainer approval, security-review completion or guaranteed future coverage.
An outstanding requested review or unresolved finding prevents task completion.

## 🌿 Release integration and synchronization

1. Prepare a release/0.1.0 -> main PR with candidate head/base SHAs, carried
   issues and PRs, validation evidence and known limitations.
2. **Wait for explicit authorization from @danielep71 to merge this candidate
   into main.** General development approval, including permission to implement
   an issue, is not authorization. Record the owner's decision and its source
   in the PR; a changed candidate needs renewed authorization.
3. With current required checks passing and review findings resolved, use a
   merge commit (never squash or rebase) for the authorized integration.
4. Freeze task merges into the release branch from opening the integration PR
   until synchronization completes. After the main push checks pass, open a
   main -> release/0.1.0 sync PR and merge it with a merge commit after CI passes.
5. For a genuinely empty file diff, record the compared SHAs and CI result;
   content review need not be repeated. A non-empty sync requires normal review.
   Resume task merges only after the sync and its checks pass.

Do not push directly, force-push or use Update branch when the head is main or
a protected release branch. Do not rebase or amend shared history. If either
protected branch moves unexpectedly during integration/sync, stop integration,
record the divergence and obtain an owner decision on recovery; use reviewed
PRs without weakening protections.

## ⏳ Exceptions and deferred work

Record any exception in the affected issue/PR with the reason, scope, owner
decision, residual risk and follow-on issue/milestone/date. Pending work stays
open or is explicitly rescheduled by the owner; silence is not acceptance.
Policy text is not proof of platform enforcement. In particular, the explicit
owner authorization gate above is procedural: the zero-approval GitHub rule
does not mechanically enforce it.

## 🎫 Issues

Use the Bug report, Enhancement or Documentation form. Each issue is assigned
to danielep71, has exactly one priority and belongs to a milestone selected
during triage, and an explicit Target end date: YYYY-MM-DD (Europe/Rome) in
its body. End-date validation is planned in issue #8; it is not yet automated.
Forms default bugs to P2 and enhancements/documentation to P3.

- P1: confirmed calculation bug producing wrong results for valid inputs; requires bug.
- P2: material correctness, robustness or maintainability defect.
- P3: non-blocking quality, testing, documentation or setup work.

Every issue includes a Dependencies and blocking status section. Write None
if ready, name prerequisite issues with #number, or use a line beginning
External condition: for an external blocker. Apply blocked only while a
named prerequisite is unresolved. Review dependent issues when a prerequisite
closes. Pull-request references do not count as blocking prerequisites.

The read-only Issue triage workflow audits open issues on issue events and
manual dispatch. Findings require maintainer triage; the workflow never edits
issues. Its mechanical P1 check requires bug; confirming a calculation defect
remains a maintainer decision.

Milestones belong only to issues. Task, integration, synchronization and bot PRs
link their tracking issues and have no milestone. Close an issue only after its
criteria are evidenced on the release branch; add a Resolution section with PR,
commit, actual checks/results and limitations. A release-targeted PR does not
automatically close its linked issue on the default branch, so verify closure
explicitly. Issue completion on release does not imply integration into main.
After closure, review dependent issues and remove blocked only when all named
prerequisites are resolved.

## 🏷️ Label workflows

- Sync issue labels validates and self-tests changes on pull requests into
  main and release/**. Relevant pushes to main, or manual dispatch on the
  default branch, reconcile the live catalogue and verify an exact match.
  Labels outside the selected catalogue are removed (prune is enabled).
- Detect issue-label drift runs offline fixtures on relevant pull requests
  and compares live labels daily at 05:17 UTC or on manual dispatch.
  It reports differences without changing labels and retains evidence for 30 days.
- Issue triage checks assignee, priority, milestone, catalogue membership
  and dependency status.

## 🧪 Local validation

```sh
python tools/check.py --ci
```

## 📜 Provenance

The initial label and issue-triage configuration was adapted from K-SFTs on
2026-10-28. This historical source attribution is not an operational dependency
or an instruction to follow another repository's current policy. K-LCR's branch
and review policy is defined above: release first, main only with explicit
owner authorization.

## ⚙️ Repository settings (2026-10-28)

The five active K-LCR rulesets were read back:
Protect main, Protect release branches, Prevent release branch deletion,
Protect release tags and Protect traffic history. No bypass actors are configured.

Main requires a pull request, resolved review conversations, an up-to-date
branch and the passing Repository integrity check from GitHub Actions.
Only merge commits are permitted into main; release/** permits squash or merge.
Deletion and force pushes are blocked. Release branches may be created before
their first status check. The separate release deletion rule is retained.
Tags v* cannot be updated, deleted or force-pushed. Traffic-history branches
cannot be deleted or force-pushed.

release/0.1.0 exists and is the development target. No traffic-history branch
has been created. The integrity check runs on every pull request and push to main and release/** and currently
validates label scripts and manifest, issue forms and triage tests, tracked
text format and workflow syntax. It produces candidate-bound reports; it does
not compile VBA, execute Excel or validate LCR calculations.
Its first main run passed: [40740544583](https://github.com/danielep71/K-LCR/actions/runs/40740544583).
These are configured controls; destructive enforcement probes were not performed.

Projects are disabled; merge, squash and rebase are enabled at repository level
(subject to the branch rules). Auto-merge is disabled. Branch-update suggestions
and automatic deletion of merged head branches are enabled.
Actions require full-length SHA pins, use read-only default token permissions,
cannot create or approve pull requests, and retain logs/artifacts for 90 days.
Dependency graph and Dependabot alerts are enabled; automatic dependency
submission, security updates and grouped security updates are disabled.

Dependabot proposes grouped GitHub Actions updates weekly on Mondays at 05:00
Europe/Rome, with ci/P3 labels and danielep71 assigned.
The configuration integrated into main via PR #45 targets `release/0.1.0`.
Dependabot reads its configuration from the default branch, so future grouped
GitHub Actions update PRs target the active release branch.

K-LCR remains private. Public hosting, private vulnerability reporting and
public-repository-only security options are not copied. Repository-specific
credentials, collaborators, deployments and environments are not cloned.

## 🔎 Activation boundaries and remaining verification

Issue-event and scheduled workflows use their default-branch definitions.
Live label reconciliation is deliberately restricted to main. Release-branch
changes to these definitions/policies are staged until an authorized integration;
do not bypass that boundary to activate them early.

The settings above were recorded during the 2026-10-28 alignment. K-LCR is
private: feature availability depends on its GitHub plan and enabled products,
and features available in public repositories are not evidence of availability here. No account
plan, public hosting or additional security product entitlement is assumed.
Controlled fail/pass protection demonstrations and fresh settings verification
remain in issue #16. Expanded portable CI and dependency retargeting were
delivered in #7; metadata automation is in #8; traffic activation in #17;
release procedure in #20; final baseline certification in #23. Existing green
checks cover only the installed portable gates, not LCR calculations, host
execution or these future gates.

## 🔒 Licensing and data

The owner selected MPL-2.0 for K-LCR on 2026-10-28. See [LICENSE](../LICENSE)
and [NOTICE.md](../NOTICE.md) for the license and imported-file provenance.
Keep vulnerability details and confidential data out of ordinary issues and
PRs; [SECURITY.md](../SECURITY.md) defines private reporting and synthetic
examples. Licensing does not itself change this repository's private visibility.
