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
| `fix/<issue>-<slug>`, `docs/<slug>`, `test/<slug>` | Short-lived task branches cut from the active release branch; PRs target release/0.1.0. |
| `release/X.Y.Z` | Release branch naming: version digits only, without a `v` prefix. |
| traffic-history | Reserved data-only branch; not yet created. Never a task base or merged into source branches. |

A new active release branch requires an owner decision. A release branch name,
completed issue, green check or closed milestone does not authorize integration
into main, tagging, publication or a visibility change.

## 🔀 Task integration and review

1. Read the issue, branch from the current release/0.1.0 head and keep the change
   within the authorized task.
2. Open a PR explicitly targeting release/0.1.0 and fill in
   [the PR template](../.github/PULL_REQUEST_TEMPLATE.md). Link the issue,
   describe the resulting behavior, validation and limitations. Add the labels
   of the linked issue; milestones belong to issues only.
3. Review the final diff and record the exact head SHA, reviewer identity,
   findings and their resolution in the PR description or review. Keep author
   attribution truthful; an agent review must not be described as owner approval.
4. Require a passing Repository integrity check for the current candidate and
   current base, an up-to-date task branch and resolved review conversations.
   Path-specific label checks supplement the universal required check.
5. Squash-merge the task PR into release/0.1.0 within the owner's task
   authorization. Use a subject ending in the PR number and a body stating what
   changed, what was validated and what was not, ending with `Refs #<issue>`.
   Verify the release push check, then record issue completion evidence.

The sole owner cannot approve their own PR, so the main and release-branch
rulesets require a PR with zero approving reviews
([settings](REPOSITORY_SETTINGS.md#rulesets)); this does not waive review or
the separate owner authorization required for main. CI and review are
separate evidence. After any
head change, repeat the affected validation and review and record the new SHA.
The automated code reviewer reviews PRs opened by people, not bot-authored PRs,
and does not re-run after a fix push. Wait for its review to complete before
merging; requesting a re-run needs the owner's approval each time. Record
whether a review actually completed for that SHA, including findings; do not
infer coverage from a previous review.
Automated code review was observed on 2026-10-28 for exact PR heads,
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
   until synchronization completes. After the main push check passes, open a
   main -> release/0.1.0 sync PR and merge it with a merge commit after
   Repository integrity passes. The release ruleset requires a PR, so a direct
   fast-forward push is refused.
5. For a sync PR whose file diff is genuinely empty, record the compared SHAs
   and CI result; content review need not be repeated. A non-empty sync
   requires normal review. Resume task merges only after the release push check
   passes.

Do not push directly to main or a protected release branch, and never
force-push or use Update branch on them. Do not
rebase or amend shared history. If either protected branch moves unexpectedly
during integration/sync, stop integration, record the divergence and obtain
an owner decision on recovery; use reviewed PRs without weakening protections.

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
its body. The target end date of a new issue must be earlier than the due date
of its milestone. End-date validation, including this comparison, is planned
in issue #8; it is not yet automated.
Forms default bugs to P2 and enhancements/documentation to P3.

- P1: confirmed calculation bug producing wrong results for valid inputs; requires bug.
- P2: material correctness, robustness or maintainability defect.
- P3: non-blocking quality, testing, documentation, setup or technical-debt work.

Every issue includes a Dependencies and blocking status section. Write None
if ready, name prerequisite issues with #number, or use a line beginning
External condition: for an external blocker. Apply blocked only while a
named prerequisite is unresolved. Review dependent issues when a prerequisite
closes. Pull-request references do not count as blocking prerequisites.

The read-only Issue triage workflow audits open issues on issue events and
manual dispatch. Findings require maintainer triage; the workflow never edits
issues. Its mechanical P1 check requires bug; confirming a calculation defect
remains a maintainer decision.

PRs into the active release branch, bot PRs included, carry labels matching
their tracking issue but no milestone: milestones belong to issues only, and
the Keep milestones issue-only workflow removes a milestone set on a pull
request. Integration and sync PRs
link the issues and PRs they carry. Close an issue only after its
criteria are evidenced on the release branch; add a Resolution section with PR,
commit, actual checks/results and limitations. A release-targeted PR does not
automatically close its linked issue on the default branch, so verify closure
explicitly. Issue completion on release does not imply integration into main.
After closure, review dependent issues and remove blocked only when all named
prerequisites are resolved.

## 🏷️ Labels

### When to use each label

Every issue carries exactly one priority label, defined under
[Issues](#-issues): `P1` (confirmed calculation bug; requires `bug`), `P2` or
`P3`. The forms default to `P2` for bugs and `P3` for enhancements and
documentation; Dependabot update PRs get `P3`. Triage confirms or changes it.

Type labels say what kind of work an issue or PR is. The forms set `bug`,
`enhancement` or `documentation`; add others where they apply.

| Label | Use for |
| --- | --- |
| `bug` | Confirmed defect in behavior, correctness, error handling, or a documented contract |
| `enhancement` | New capability or meaningful improvement to supported behavior |
| `documentation` | Documentation for users or for my repository maintenance |
| `tests` | Regression coverage, test harnesses, fixtures, or manual validation |
| `refactor` | Internal restructuring intended to preserve supported behavior |
| `behavior-change` | Intentional externally observable behavior change |
| `ci` | Automated quality checks, workflow maintenance, or release certification |
| `repository` | Repository structure, governance, metadata, tooling, or maintenance |
| `release` | Release preparation, certification, evidence, packaging, or publication |
| `security` | Security boundary, vulnerability handling, supply chain, or hardening; never for an undisclosed vulnerability, which follows [SECURITY.md](../SECURITY.md) |

Status and triage labels:

| Label | Use when |
| --- | --- |
| `blocked` | A named open prerequisite or an `External condition:` line prevents progress; remove it when none remains |
| `question` | I need further information or need to make a decision |
| `help wanted` | I welcome external investigation, implementation, validation, or review |
| `good first issue` | Well-scoped task suitable for a first contribution |
| `duplicate` | An existing issue or pull request already covers this work |
| `invalid` | The report is incomplete, unsupported, or not actionable as submitted |
| `wontfix` | I have decided not to implement or continue this work |

Labels do not assign priorities or milestones automatically.

### Label workflows

- Sync issue labels validates and self-tests changes on pull requests into
  main and release/**. Relevant pushes to main, or manual dispatch on the
  default branch, reconcile the live catalogue and verify an exact match.
  Labels outside the selected catalogue are removed (prune is enabled).
- Detect issue-label drift runs offline fixtures on relevant pull requests
  and compares live labels daily at 05:17 UTC or on manual dispatch.
  It reports differences without changing labels and retains evidence for 30 days.
- Issue triage checks assignee, priority, milestone, catalogue membership
  and dependency status.
- Keep milestones issue-only removes a milestone from any pull request. It
  runs on pull request events through `pull_request_target`, which always
  uses the default-branch copy of the workflow, daily at 03:17 UTC, and on
  manual dispatch or a change of the workflow on the default branch. It never
  checks out or runs pull request contents; only its job can write pull
  requests.

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

## ⚙️ Repository settings

The dated settings, evidence, historical snapshots and unverified controls are
maintained in [REPOSITORY_SETTINGS_EVIDENCE.md](REPOSITORY_SETTINGS_EVIDENCE.md).
The portable non-default settings reference is
[REPOSITORY_SETTINGS.md](REPOSITORY_SETTINGS.md). GitHub's live settings remain
authoritative. Do not restate current settings here or in
[SECURITY.md](../SECURITY.md); update the evidence snapshot, with its date and
evidence, whenever a setting is configured, verified or changed.

Working rules that depend on those settings:

- The Repository integrity check runs on every pull request and push to main
  and release/** and is the required check of both PR rulesets. It produces
  candidate-bound reports; it does not compile VBA, execute Excel or validate
  LCR calculations ([tools/README.md](../tools/README.md)).
- Dependabot reads `.github/dependabot.yml` from the default branch. Version
  updates target the active release branch; update `target-branch` when a new
  release branch is opened.
- Dependabot security updates ignore `target-branch` and open pull requests
  against `main`. Review them as described in
  [tools/README.md](../tools/README.md#-dependency-updates); merging one into
  main needs the owner's approval, like any main integration. Then synchronize
  the release branch with main through a sync PR, as for any integration.
- GitHub Pages publishes main `/docs`; site changes follow
  [WEBSITE.md](WEBSITE.md).

## 🔎 Activation boundaries and remaining verification

Issue-event and scheduled workflows use their default-branch definitions.
Live label reconciliation is deliberately restricted to main. Release-branch
changes to these definitions/policies are staged until an authorized integration;
do not bypass that boundary to activate them early.

Settings observations, their dates and the controls still to verify are kept
in the [evidence snapshot](REPOSITORY_SETTINGS_EVIDENCE.md).
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
PRs; [SECURITY.md](../SECURITY.md) defines private vulnerability reporting
through GitHub or by email, response targets and synthetic examples.
Licensing and visibility are separate owner decisions.
