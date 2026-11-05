# Repository settings evidence snapshot

This file preserves the dated repository-specific observations for **K-LCR**.
The portable non-default settings reference is [REPOSITORY_SETTINGS.md](REPOSITORY_SETTINGS.md).
This snapshot is not a current certification and must not be copied as evidence
for another repository.
[Governance](GOVERNANCE.md) defines the working policy;
[SECURITY.md](../SECURITY.md) defines vulnerability reporting and data handling.
GitHub's live settings remain authoritative. This file records observations,
not automatic enforcement or authorization to change a setting.

Snapshot date: **2026-11-05 (Europe/Rome)**. Tracking: [#16](https://github.com/danielep71/K-LCR/issues/16);
the first snapshot of 2026-10-29 was made under [#90](https://github.com/danielep71/K-LCR/issues/90).

## Reading the register

- **Verified**: read from the live GitHub API or Settings UI on the stated date.
- **Run evidence**: a particular workflow completed; this is not proof of future coverage.
- **Historical**: retained earlier evidence, not a fresh confirmation.
- **Unverified**: no conclusive current read-back. Never interpret this as disabled.
- **Desired**: existing policy or a proposed baseline explicitly marked as such.

No settings were changed to prepare this document. An enabled scanner is not
proof that its findings block merges, and static checks are not Excel or
numerical validation.

## General settings

Evidence: [repository API](https://api.github.com/repos/danielep71/K-LCR), read 2026-11-05.
All rows below were verified on that date unless stated otherwise. They match
the general rows of the [portable register](REPOSITORY_SETTINGS.md#general),
including the legacy downloads flag (off).

| Setting | Desired baseline | Observed setting | Exceptions / interpretation |
| --- | --- | --- | --- |
| Visibility / default branch | Public / main | Public / main | Public since 2026-10-28. Development targets release/0.1.0, not main. |
| Issues / Wiki | Enabled | Enabled / enabled | Wiki editing access was not reverified. |
| Projects / Discussions | Retain current choice | Disabled / disabled | Repository feature flags; not an inventory of user-level projects. |
| Merge methods | Subject to branch rules | Merge, squash, rebase enabled | Protected branches restrict the methods below. |
| Auto-merge | Disabled | Disabled | Passing checks do not authorize integration into main. |
| Delete merged head branches | Enabled | Enabled | Release and traffic branches remain protected by rulesets. Branches of closed, unmerged pull requests are not deleted. |
| Update-branch suggestions | Enabled | Enabled | Governance prohibits using this on protected integration branches. |
| Web commit sign-off | No change proposed | Not required | Separate from reviews and signed-commit requirements. |
| Pages / homepage | Enabled / project URL | Homepage https://danielep71.github.io/K-LCR/; Pages verified, UI, read by me 2026-11-05: deploy from branch main, folder `/docs`, HTTPS enforced | The Pages API returns 403 to the API read-back. Enabled 2026-10-29 (#63); run evidence: [pages build and deployment](https://github.com/danielep71/K-LCR/actions/runs/40836157499) of `0547772`. Environment controls not verified. |
| Description / topics | LCR-specific | Description and 12 topics set by me on 2026-11-04 (#18): basel, basel-iii, crr, crr3, excel, excel-vba, lcr, liquidity-coverage-ratio, liquidity-risk, model-validation, risk, risk-management | The social preview is the PNG of `docs/assets/`; its served copy matched the recorded SHA-256 on 2026-11-04. Topic count is not a security measure. |
| License | MPL-2.0 | MPL-2.0 detected | Selected by me on 2026-10-28 ([NOTICE](../NOTICE.md)). |

## Branch and tag rulesets

All five rulesets were read in full through the API on **2026-11-05**:
active enforcement, empty bypass lists (`current_user_can_bypass`: never), no
ref exclusions, and no change since 2026-10-29 (their `updated_at`). They
match the [portable register](REPOSITORY_SETTINGS.md#rulesets). The
[enforcement demonstration](#enforcement-demonstration) below tests the
required check on a pull request.

| Rule / target | Desired and observed setting | Evidence | Exceptions |
| --- | --- | --- | --- |
| Protect main: default branch | PR required; merge commits only; 0 approvals; conversations resolved; strict up-to-date Repository integrity check from GitHub Actions (integration 15368); deletion and force pushes blocked | [26063609](https://github.com/danielep71/K-LCR/rules/26063609) | No administrator bypass. Check enforced on creation. |
| Protect release branches: release/** | PR required; squash or merge; 0 approvals; conversations resolved; same required check and strict up-to-date rule; deletion and force pushes blocked | [26063663](https://github.com/danielep71/K-LCR/rules/26063663) | Check not enforced on initial branch creation. No bypass. PR requirement off from 2026-10-28 and restored on 2026-10-29 (#88). |
| Prevent release branch deletion: release/** | Deletion blocked independently | [26063689](https://github.com/danielep71/K-LCR/rules/26063689) | No bypass. |
| Protect release tags: v* | Updates, deletion and force pushes blocked | [26063723](https://github.com/danielep71/K-LCR/rules/26063723) | Creation is not blocked by this ruleset. No tag exists. |
| Protect traffic history: traffic-history | Deletion and force pushes blocked | [26063762](https://github.com/danielep71/K-LCR/rules/26063762) | No PR or CI requirement. No traffic-history branch exists yet (#17). |

Both PR rules disable stale-review dismissal, code-owner review and last-push
approval; no required reviewers are configured. Both also carry
`require_extra_approval_for_unattributed_changes: true`, a parameter the
portable register does not describe; with zero required approvals it adds no
approval in practice. The rules API, read 2026-11-05, confirms what applies
to each branch: on `main`, ruleset 26063609 only; on `release/0.1.0`,
26063663 and the separate deletion rule 26063689; on `traffic-history`,
26063762. Zero approvals accommodates
the sole-owner model; it does not establish independent approval. The rulesets
require only Repository integrity, not a separate CodeQL check or code-scanning rule.

Release synchronization uses a **main-to-release PR with a merge commit**,
not a direct fast-forward or an administrator exception. Follow the ordering
and divergence rules in [Release integration](GOVERNANCE.md#-release-integration-and-synchronization).

<a id="enforcement-demonstration"></a>

## Enforcement demonstration

Pull request #135 into `release/0.1.0` (#16) showed on 2026-11-05 that the
required check blocks a merge and that a passing run then permits it. The
rulesets were not changed for the demonstration.

| Step | Commit | Observation |
| --- | --- | --- |
| 1. Deliberate defect | `f798a0f` | A trailing space in this section. `Repository integrity` [failed](https://github.com/danielep71/K-LCR/actions/runs/41985309189): only `tracked-text`, on that line; every other gate passed. |
| 2. Merge attempt | `f798a0f` | The pull request's merge state was `blocked`. A squash merge through the REST API at 07:11 UTC, with the expected head SHA, was refused: HTTP 405, "Repository rule violations found. Required status check "Repository integrity" is failing." Nothing reached `release/0.1.0`. |
| 3. Correction | the next commit | Removes the trailing space and records steps 1 and 2. |
| 4. Merge | the final head | Permitted only once `Repository integrity` passes on the final head and the review threads are resolved; the run and the merge commit are recorded in the resolution of #16. |

The demonstration covers the release-branch ruleset (26063663). The `main`
ruleset (26063609) requires the same check with the same strict policy; it
was not exercised with a failing commit, since a change to `main` needs my
approval of an integration.

## Required-check coverage and branch cleanup

The workflow runs on every pull request into `main` and `release/**`, with no
path filter, so documentation-only and synchronization pull requests are
covered; `workflow-invariants` rejects a trigger filter. Run evidence:

| Pull request kind | Example | `Repository integrity` |
| --- | --- | --- |
| Task, code | #133 into release/0.1.0 | [passed on `ca6c9a2`](https://github.com/danielep71/K-LCR/actions/runs/41849521520) |
| Task, documentation and image only | #134 into release/0.1.0 | [passed on `b1c5e49`](https://github.com/danielep71/K-LCR/actions/runs/41897453637) |
| Release integration, release/0.1.0 into main | #123 | [passed on `05d72eb`](https://github.com/danielep71/K-LCR/actions/runs/41705368390) |
| Synchronization, main into release/0.1.0 | #124 | [passed on `12269d9`](https://github.com/danielep71/K-LCR/actions/runs/41705938716) |
| Dependabot version update | #118 into release/0.1.0, open | [passed on `3d1b981`](https://github.com/danielep71/K-LCR/actions/runs/41701226141) |

**Head-branch deletion,** read 2026-11-05: the head branches of the merged
#133 and #134 no longer exist. Branches of closed, unmerged pull requests
stay: `dependabot/pip/tools/release/0.1.0/python-quality-tools-67e7a4b5de`
(#82, closed) remains. CodeQL analyses `main` on push and on its weekly
schedule; it did not report on #133 or #134, so it does not cover pull requests
into `release/0.1.0`.

## Security settings

API rows were read from the public GitHub API on **2026-11-05**; private
vulnerability reporting, secret scanning and push protection were first read
back on 2026-10-28 (#66). I read the UI-only rows in **Settings > Advanced
Security** on 2026-11-05.

| Setting | Desired baseline | Observed state / evidence | Exception or remaining verification |
| --- | --- | --- | --- |
| Private vulnerability reporting | Enabled | Verified enabled, API | Reporting procedure remains in SECURITY.md, with an email channel (#79). |
| Dependency graph | Enabled | Verified enabled, UI, read by me 2026-11-05 | — |
| Automatic dependency submission | Retain current choice | Verified disabled, UI, read by me 2026-11-05 | Reassess when build ecosystems change. |
| Dependabot alerts | Enabled | Verified enabled, UI, read by me 2026-11-05; the alerts API returns 403 to the API read-back | Alert inventory was not audited here. |
| Dependabot security updates | Enabled | Verified enabled, API and UI 2026-11-05; enabled by me on 2026-10-29 (#85) | Pull requests target main; see [Governance](GOVERNANCE.md). No security-update PR has been opened yet. |
| Grouped security updates | Retain current choice | Verified disabled, UI, read by me 2026-11-05 | Does not disable individual security updates. |
| Malware alerts | No change proposed | Verified disabled, UI, read by me 2026-11-05 | Dependabot does not alert on malicious packages; the pinned, hash-locked tool requirements remain the control. |
| Secret scanning | Enabled | Verified enabled, API | No secret-injection test performed. |
| Push protection | Enabled | Verified enabled, API | No blocked-push demonstration performed. |
| Non-provider patterns / validity checks | Retain current choice | Verified disabled / disabled, API | Optional controls to evaluate separately. |
| CodeQL | Configured; validate coverage | Verified default setup, API 2026-11-05: Actions and Python, default query suite, remote threat model, weekly, last updated 2026-10-29. Run evidence: [CodeQL Setup](https://github.com/danielep71/K-LCR/actions/runs/40829870792) on `4176184`, [push analysis](https://github.com/danielep71/K-LCR/actions/runs/40836157419) on `0547772` and analysis on PR #87 | Not observed on PRs into release/0.1.0 (#86; again absent on #133 and #134). Not a required check. No claim of VBA analysis. Alerts return 403 without admin access. |
| Code scanning thresholds | Retain current choice | Verified, UI, read by me 2026-11-05: security alerts High or higher; standard alerts errors only | A failure threshold alone does not make the scan a required merge gate, and CodeQL does not report on pull requests into release/0.1.0. |
| Dependabot auto-triage | Review before standardizing | Verified, UI, read by me 2026-11-05: two GitHub presets; "Dismiss low-impact alerts for development-scoped dependencies" enabled, "Dismiss package malware alerts" disabled; no custom rule | Low-impact alerts for development-scoped dependencies are dismissed automatically: do not assume they stay visible. |
| Copilot Autofix | No change proposed | Verified enabled, UI, read by me 2026-11-05 | It suggests fixes on code-scanning alerts; a suggestion is reviewed like any other change. |

## Actions and dependency automation

The Actions permissions API is not available to the API read-back (HTTP 403),
so I read the repository-level Actions settings in **Settings > Actions >
General** on 2026-11-05. Workflow YAML is evidence of that workflow only, not
of the repository-wide defaults.

| Control | Desired baseline | Observed state / date | Evidence / remaining work |
| --- | --- | --- | --- |
| Full-SHA requirement at repository level | Enforce | Verified required, UI, read by me 2026-11-05 | Repository policy, separate from the pins that `workflow-invariants` checks in the YAML. |
| Default GITHUB_TOKEN permissions | Read-only | Verified read-only ("Read repository contents and packages permissions"), UI, read by me 2026-11-05 | Jobs may explicitly request more permissions; `workflow-invariants` limits which may. |
| Actions may create/approve PRs | Disabled | Verified disabled, UI, read by me 2026-11-05 | — |
| Allowed Actions and reusable workflows | Explicit reviewed policy | Verified "Allow all actions and reusable workflows", UI, read by me 2026-11-05; no allow list | Gap against the desired baseline: any action may run, limited only by the full-SHA requirement and review of workflow changes. Restricting the list is my decision, not part of this record. |
| External-contributor workflow approval | Explicit reviewed policy | Verified "Require approval for first-time contributors", UI, read by me 2026-11-05 | Later pull requests of a contributor run without approval. |
| Repository log/artifact retention | Explicit documented period | Verified 90 days, UI, read by me 2026-11-05 | The integrity workflow uploads its report with 30-day retention ([tools/README.md](../tools/README.md)). |
| Version updates | Weekly grouped updates | File inspected 2026-10-29: GitHub Actions and pip (`/tools`, 14-day cooldown); Monday 05:00 Europe/Rome; target release/0.1.0; limit 5; ci/P3; assignee danielep71 | [.github/dependabot.yml](../.github/dependabot.yml); main's definition controls activation. Run evidence: the first pip update opened #82, which I closed on 2026-10-29 to update the tool pins by hand. |
| Integrity / labels / issue triage / PR milestones | Preserve installed gates and read-only audits | Repository integrity, label sync and drift, issue triage and Keep milestones issue-only workflows installed | [Tooling](../tools/README.md); this documentation change does not audit all workflow executions. |
| Traffic analytics | Not configured | No traffic workflow on main or release/0.1.0, no `traffic-history` branch and no credential; the `analytics` environment exists (below) | Activation is tracked in #17 (PR #92, open). |
| Environments, collaborators, deploy keys | Not cloned from other projects | Verified, UI, read by me 2026-11-05: environments `analytics` (created for #17) and `github-pages` (Pages); no deploy key; no repository or environment secret or variable. Collaborators read through the authenticated API on 2026-11-05: danielep71 (admin) only | Secret values were never accessed. Pending invitations were not read. |

## Open verification and maintenance

Every row above was verified on 2026-11-05, through the API or in the
Settings UI (#16), except where a row says otherwise. Open points:
- CodeQL does not report on pull requests into release/0.1.0;
- the Actions allow list is open ("Allow all actions");
- the alert inventories (Dependabot, code scanning) and the environment
  protection rules were not audited;
- the `main` ruleset was not exercised with a failing commit.

Final baseline certification is #23.

After a settings change, update its observed value, date, evidence and exception
in this file through the normal documentation workflow. Keep desired policy
separate from observations; mark unavailable checks unverified. Link changes
to their issue/PR and preserve useful dated evidence. Do not reproduce current
settings tables in governance or security policy.

## Historical configuration record

Historical snapshot, superseded by the dated rows above where they differ.
Do not treat pending items or disabled features below as current facts.

| Date | Observation |
| --- | --- |
| 2026-10-28 | Settings aligned and recorded while K-LCR was private: five active rulesets, no bypass actors. Main required a pull request, resolved review conversations, an up-to-date branch and Repository integrity, with merge commits only. Projects disabled; merge, squash and rebase enabled; auto-merge disabled; update suggestions and head-branch deletion enabled. Actions required full-length SHA pins, used read-only default token permissions, could not create or approve pull requests and retained logs/artifacts for 90 days. Dependency graph and Dependabot alerts enabled; automatic dependency submission, security updates and grouped security updates disabled. Repository integrity's first main run passed: [40740544583](https://github.com/danielep71/K-LCR/actions/runs/40740544583). |
| 2026-10-28 | I turned off the release-branch pull-request requirement after it refused a fast-forward synchronization (#59, #61). |
| 2026-10-28 | I made K-LCR public and enabled private vulnerability reporting, secret scanning and push protection (#66). |
| 2026-10-29 | I enabled GitHub Pages (main, `/docs`; #63), Dependabot security updates and CodeQL default setup (#85), and restored the release-branch pull-request requirement with squash or merge only (#88). |
| 2026-11-04 | I set the About description and topics and uploaded the social preview (#18). |
