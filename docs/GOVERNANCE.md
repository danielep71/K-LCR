# Issue and label governance

K-LCR adopts the 20-label catalogue and issue-triage rules from K-SFTs.
Names, colors and descriptions are versioned in [.github/labels.json](../.github/labels.json).
The application profile has no additional labels.

## Issues

Use the Bug report, Enhancement or Documentation form. Each issue is assigned
to danielep71, has exactly one priority and belongs to a milestone selected
during triage. Forms default bugs to P2 and enhancements/documentation to P3.

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

## Label workflows

- Sync issue labels validates and self-tests changes on pull requests into
  main and release/**. Relevant pushes to main, or manual dispatch on the
  default branch, reconcile the live catalogue and verify an exact match.
  Labels outside the selected catalogue are removed (prune is enabled).
- Detect issue-label drift runs offline fixtures on relevant pull requests
  and compares live labels daily at 05:17 UTC or on manual dispatch.
  It reports differences without changing labels and retains evidence for 30 days.
- Issue triage checks assignee, priority, milestone, catalogue membership
  and dependency status.

## Local validation

```sh
node .github/scripts/labels-sync.mjs --self-test
node .github/scripts/labels-sync.mjs --mode validate
node .github/scripts/labels-drift.mjs --self-test
python tools/check_issues.py --check-config
python -m unittest discover -s tools -p 'test_check_issues.py'
```

## Source

Initial configuration copied from K-SFTs on 2026-10-28 and adapted for K-LCR.
K-SACCR has the same 20 names and colors; K-SFTs supplies the P1 and wontfix
descriptions. This document covers issue and label governance only.

## Repository settings (2026-10-28)

The five active rulesets were read back and match K-SFTs exactly:
Protect main, Protect release branches, Prevent release branch deletion,
Protect release tags and Protect traffic history. No bypass actors are configured.

Main requires a pull request, resolved review conversations, an up-to-date
branch and the passing Repository integrity check from GitHub Actions.
Only merge commits are permitted into main; release/** permits squash or merge.
Deletion and force pushes are blocked. Release branches may be created before
their first status check. The separate release deletion rule is retained.
Tags v* cannot be updated, deleted or force-pushed. Traffic-history branches
cannot be deleted or force-pushed.

No release or traffic-history branch has been created. Until the maintainer
designates a release branch, setup pull requests target main. The integrity
check runs on every pull request and push to main and release/** and currently
validates the label scripts, label manifest, issue forms and triage tests.
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
Europe/Rome, with ci/P3 labels and danielep71 assigned, matching K-SFTs.
It targets main because K-LCR has no designated release branch.

K-LCR remains private. Public hosting, private vulnerability reporting and
public-repository-only security options are not copied. Repository-specific
credentials, collaborators, deployments and environments are not cloned.
