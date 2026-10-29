# Repository settings evidence snapshot

This file preserves the dated repository-specific observations for **K-LCR**.
The portable non-default settings reference is [REPOSITORY_SETTINGS.md](REPOSITORY_SETTINGS.md).
This snapshot is not a current certification and must not be copied as evidence
for another repository.
[Governance](GOVERNANCE.md) defines the working policy;
[SECURITY.md](../SECURITY.md) defines vulnerability reporting and data handling.
GitHub's live settings remain authoritative. This file records observations,
not automatic enforcement or authorization to change a setting.

Snapshot date: **2026-10-29 (Europe/Rome)**. Tracking: [#90](https://github.com/danielep71/K-LCR/issues/90).

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

Evidence: [repository API](https://api.github.com/repos/danielep71/K-LCR), read 2026-10-29.
All rows below were verified on that date unless stated otherwise.

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
| Pages / homepage | Enabled / project URL | Pages enabled; https://danielep71.github.io/K-LCR/ | Owner-reported source: main, `/docs`, enabled 2026-10-29 (#63). Run evidence: [pages build and deployment](https://github.com/danielep71/K-LCR/actions/runs/40836157499) of `0547772`. Environment controls not verified. |
| Topics | Relevant discovery terms | basel, basel-iii | Topic count is not a security measure. |
| License | MPL-2.0 | MPL-2.0 detected | Selected by the owner on 2026-10-28 ([NOTICE](../NOTICE.md)). |

## Branch and tag rulesets

All five rulesets were read in full through the API on **2026-10-29**:
active enforcement, empty bypass lists, and no ref exclusions. This confirms
configuration, not destructive enforcement tests.

| Rule / target | Desired and observed setting | Evidence | Exceptions |
| --- | --- | --- | --- |
| Protect main: default branch | PR required; merge commits only; 0 approvals; conversations resolved; strict up-to-date Repository integrity check from GitHub Actions (integration 15368); deletion and force pushes blocked | [26063609](https://github.com/danielep71/K-LCR/rules/26063609) | No administrator bypass. Check enforced on creation. |
| Protect release branches: release/** | PR required; squash or merge; 0 approvals; conversations resolved; same required check and strict up-to-date rule; deletion and force pushes blocked | [26063663](https://github.com/danielep71/K-LCR/rules/26063663) | Check not enforced on initial branch creation. No bypass. PR requirement off from 2026-10-28 and restored on 2026-10-29 (#88). |
| Prevent release branch deletion: release/** | Deletion blocked independently | [26063689](https://github.com/danielep71/K-LCR/rules/26063689) | No bypass. |
| Protect release tags: v* | Updates, deletion and force pushes blocked | [26063723](https://github.com/danielep71/K-LCR/rules/26063723) | Creation is not blocked by this ruleset. No tag exists. |
| Protect traffic history: traffic-history | Deletion and force pushes blocked | [26063762](https://github.com/danielep71/K-LCR/rules/26063762) | No PR or CI requirement. No traffic-history branch exists yet (#17). |

Both PR rules disable stale-review dismissal, code-owner review and last-push
approval; no required reviewers are configured. Zero approvals accommodates
the sole-owner model; it does not establish independent approval. The rulesets
require only Repository integrity, not a separate CodeQL check or code-scanning rule.

Release synchronization uses a **main-to-release PR with a merge commit**,
not a direct fast-forward or an administrator exception. Follow the ordering
and divergence rules in [Release integration](GOVERNANCE.md#-release-integration-and-synchronization).
Controlled fail/pass enforcement demonstrations remain open in #16.

## Security settings

API rows were read from the public GitHub API on **2026-10-29**; private
vulnerability reporting, secret scanning and push protection were first read
back on 2026-10-28 (#66). The Settings UI was not read for this snapshot, so
UI-only rows are historical or unverified.

| Setting | Desired baseline | Observed state / evidence | Exception or remaining verification |
| --- | --- | --- | --- |
| Private vulnerability reporting | Enabled | Verified enabled, API | Reporting procedure remains in SECURITY.md, with an email channel (#79). |
| Dependency graph | Enabled | Historical: enabled, 2026-10-28 alignment record | Reread in the Settings UI. |
| Automatic dependency submission | Retain current choice | Historical: disabled, 2026-10-28 alignment record | Reassess when build ecosystems change. |
| Dependabot alerts | Enabled | Historical: enabled, 2026-10-28 alignment record; the alerts API returns 403 without admin access | Alert inventory was not audited here. |
| Dependabot security updates | Enabled | Verified enabled, API; enabled by the owner on 2026-10-29 (#85) | Pull requests target main; see [Governance](GOVERNANCE.md). No security-update PR has been opened yet. |
| Grouped security updates | Retain current choice | Historical: disabled, 2026-10-28 alignment record | Does not disable individual security updates. |
| Malware alerts | No change proposed | Unverified | Read in the Settings UI. |
| Secret scanning | Enabled | Verified enabled, API | No secret-injection test performed. |
| Push protection | Enabled | Verified enabled, API | No blocked-push demonstration performed. |
| Non-provider patterns / validity checks | Retain current choice | Verified disabled / disabled, API | Optional controls to evaluate separately. |
| CodeQL | Configured; validate coverage | Verified default setup, API: Actions and Python, default query suite, remote threat model, weekly. Run evidence: [CodeQL Setup](https://github.com/danielep71/K-LCR/actions/runs/40829870792) on `4176184`, [push analysis](https://github.com/danielep71/K-LCR/actions/runs/40836157419) on `0547772` and analysis on PR #87 | Not observed on PRs into release/0.1.0 (#86). Not a required check. No claim of VBA analysis. Alerts return 403 without admin access. |
| Code scanning thresholds | Retain current choice | Unverified | A failure threshold alone does not make the scan a required merge gate. |
| Dependabot auto-triage | Review before standardizing | Unverified | Do not assume low-impact alerts stay visible. |
| AI scans / Copilot Autofix | No change proposed | Unverified | Read in the Settings UI. |

## Actions and dependency automation

Repository-level Actions settings were **not re-read** for this snapshot: the
Actions permissions API is not available to this read-back (HTTP 403). The
values below come from the 2026-10-28 alignment record. Workflow YAML is
evidence of that workflow only, not of the repository-wide defaults.

| Control | Desired baseline | Observed state / date | Evidence / remaining work |
| --- | --- | --- | --- |
| Full-SHA requirement at repository level | Enforce | Historical: required, 2026-10-28 | Reread Actions settings; distinguish policy from pins in YAML. |
| Default GITHUB_TOKEN permissions | Read-only | Historical: read-only, 2026-10-28 | Jobs may explicitly request more permissions. |
| Actions may create/approve PRs | Disabled | Historical: disabled, 2026-10-28 | Reread the repository toggle. |
| Allowed Actions and reusable workflows | Explicit reviewed policy | Unverified | Record allowed publishers/patterns before declaring a standard. |
| External-contributor workflow approval | Explicit reviewed policy | Unverified | Record the selected contributor category. |
| Repository log/artifact retention | Explicit documented period | Historical: 90 days, 2026-10-28 | The integrity workflow uploads its report with 30-day retention ([tools/README.md](../tools/README.md)). |
| Version updates | Weekly grouped updates | File inspected 2026-10-29: GitHub Actions and pip (`/tools`, 14-day cooldown); Monday 05:00 Europe/Rome; target release/0.1.0; limit 5; ci/P3; assignee danielep71 | [.github/dependabot.yml](../.github/dependabot.yml); main's definition controls activation. Run evidence: the first pip update opened #82, closed on 2026-10-29 to update K-LCR and K-SFTs together. |
| Integrity / labels / issue triage | Preserve installed gates and read-only audits | Repository integrity, label sync and drift, and issue triage workflows installed | [Tooling](../tools/README.md); this documentation change does not audit all workflow executions. |
| Traffic analytics | Not configured | No traffic workflow, branch or credential | Activation is tracked in #17. |
| Environments, collaborators, deploy keys | Not cloned from other projects | Unverified (environments API not available to this read-back) | 2026-10-28 alignment record: repository-specific credentials, collaborators, deployments and environments are not cloned. |

## Open verification and maintenance

Before promoting this snapshot as fully verified, read the Settings UI for the
historical and unverified security rows, the Actions settings, the Pages
source and environment controls, and confirm CodeQL coverage of release-branch
pull requests. Controlled enforcement demonstrations and fresh settings
verification remain in #16; final baseline certification is #23.

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
| 2026-10-28 | The owner turned off the release-branch pull-request requirement after it refused a fast-forward synchronization (#59, #61). |
| 2026-10-28 | The owner made K-LCR public and enabled private vulnerability reporting, secret scanning and push protection (#66). |
| 2026-10-29 | The owner enabled GitHub Pages (main, `/docs`; #63), Dependabot security updates and CodeQL default setup (#85), and restored the release-branch pull-request requirement with squash or merge only (#88). |
