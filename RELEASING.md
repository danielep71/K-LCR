# 🚀 Releasing

How a milestone is closed and how a version is prepared and published. The
branches and the integration and synchronization pull requests are in
[GOVERNANCE.md](docs/GOVERNANCE.md#-release-integration-and-synchronization);
the version and changelog rules are in
[CHANGELOG.md](CHANGELOG.md#date-and-version-rules).

> [!IMPORTANT]
> Nothing is versioned, tagged or published unless I decide it. Closing a
> milestone, or integrating a release branch into `main`, publishes nothing.
> Unreleased work stays under `## [Unreleased]`.

<a id="current-status"></a>

## 🧭 Current status

| Item | State |
| --- | --- |
| Released versions | None |
| `VERSION` | Does not exist yet; it is created when the first release is prepared |
| Active release branch | `release/0.1.0` |
| Open milestones | *v0.2.0 - Prototype setup*, due 2026-12-31 |
| v0.1.0 outcome | Closed without a release, by my decision of 2026-11-07 (#23): no tag, no published version, and the changelog stays under `[Unreleased]`; I closed the milestone *v0.1.0 - Repo setup* on 2026-11-13 |

<a id="what-a-version-means"></a>

## 🎯 What a version means

A K-LCR version states what the repository holds at one commit. It never
certifies a regulatory interpretation, a numerical result or a host.

| Version | What it can contain |
| --- | --- |
| **v0.1.0 - Repo setup** | Governance, tooling, checks, the source register, the contracts, the test-case format and the static VBA rules. **No VBA source, no workbook, no LCR calculation and no Excel run.** I closed it on 2026-11-13 without a release, so it has no release notes and no asset. |
| Later `0.y.z` | Implementation work. Each release lists which rules are implemented, which are validated by `published` or `independent` cases ([VALIDATION_PLAN.md](docs/methodology/VALIDATION_PLAN.md#-evidence-for-a-validated-rule)), under which source edition and parameter set, and which host was tested. |
| `1.0.0` and later | Only once I decide that calculation results, the input and output contracts and the public VBA API are stable enough to promise compatibility. |

<a id="versioning"></a>

## 🏷️ Versioning

| Item | Convention |
| --- | --- |
| Version | Semantic Versioning, `MAJOR.MINOR.PATCH`; `0.y.z` during initial development ([rules](CHANGELOG.md#date-and-version-rules)) |
| Release branch | `release/X.Y.Z`, without `v`, opened only when I decide to ([GOVERNANCE.md](docs/GOVERNANCE.md#-ownership-and-development-target)) |
| Milestone | `vX.Y.Z - <title>`, on issues only ([Milestones](#milestones)) |
| `VERSION` | One `X.Y.Z` line at the root. Created in the release preparation pull request, never before; afterwards it always names the newest released version |
| Changelog | Work stays under `## [Unreleased]`; preparation moves it to `## [X.Y.Z] - YYYY-MM-DD` |
| Tag | Annotated `vX.Y.Z` on the candidate commit on `main`. The **Protect release tags** ruleset blocks its deletion, updates and force pushes ([settings](docs/REPOSITORY_SETTINGS.md#rulesets)); it does not block creation |
| GitHub Release | Created from the tag, with the changelog section and the evidence summary as notes; no asset until a workbook is packaged |

The `changelog` gate of `python tools/check.py` ties `CHANGELOG.md`,
`VERSION`, the *Current status* above and the README together: no `VERSION`
before a dated release, and from then on `VERSION` equal to the newest one.

<a id="milestones"></a>

## 🗓️ Milestones

- **Issues only.** A milestone is set on issues, never on pull requests; the
  **Keep milestones issue-only** workflow removes one set on a pull request
  (#107). Pull requests carry the labels of their issue.
- **Due date and end dates.** Every milestone has a due date. Every issue in
  it has a target end date earlier than that due date, as
  [GOVERNANCE.md](docs/GOVERNANCE.md#-issues) describes; Issue triage reports
  an issue whose date is missing or not earlier.
- **Overdue work.** When an issue passes its target end date, I either set a
  new date, with a dated line in its Planning section (`Rescheduled on
  YYYY-MM-DD from <old> to <new>: <reason>`), still earlier than the due
  date, or move it as below. Its dependent issues are reviewed on the same
  day. A milestone due date is changed only by my decision, recorded in the
  milestone description.
- **Deferred work.** An issue leaves a milestone only by my decision: it moves
  to a later milestone with a dated *Scope change* section giving the reason
  and the new target end date, and every issue that named it as a
  prerequisite is updated. Silence is not a deferral.
- **Closure.** A milestone is closed only when every issue in it is closed
  with a Resolution section or moved with a scope-change note, and its
  closeout record is complete ([below](#closing-a-milestone)). Closing it
  publishes nothing.

<a id="closing-a-milestone"></a>

## 🧾 Closing a milestone

Copy the [closeout template](docs/release/CLOSEOUT.md) into the milestone's
closing issue (#23 for v0.1.0) and fill it from runs on the candidate:

1. Every remaining issue is closed or moved.
2. The release branch is integrated into `main` and synchronized back
   ([GOVERNANCE.md](docs/GOVERNANCE.md#-release-integration-and-synchronization)).
   The integration merge commit is the **candidate**: record its full SHA.
3. From a fresh clone of the candidate, run the checks of
   [step 3](#3-run-the-checks) below, and confirm that Repository integrity,
   label drift and Issue triage are green.
4. Record the file audit, the documentation audit and the settings evidence
   the milestone requires (for v0.1.0: #21, #22 and #16).
5. Write the scope statement: what the milestone delivers and what it does
   not certify.
6. I decide whether the milestone is also released. If not, close it: the
   changelog stays under `## [Unreleased]`, and a later release includes it.
   If so, continue with the preparation below.

<a id="release-invariants"></a>

## 🔒 Release invariants

A version may be published only when:

1. one exact candidate commit is frozen: the merge commit that integrates the
   release branch into `main`;
2. the changelog section for the version is dated and matches what the
   candidate contains;
3. `python tools/check.py --ci` passes from a fresh clone of the candidate,
   and the hosted Repository integrity check is green on it;
4. when the candidate contains VBA, it is imported, compiled and run in Excel
   on the supported host, with the evidence bound to the candidate as
   [INSTALLATION.md](INSTALLATION.md#-importing-vba-into-excel) describes for
   the import (#14) and #15 will define for the evidence; a version
   without VBA, such as v0.1.0, records "no Excel run" as a deviation;
5. the annotated tag targets the candidate; and
6. the checks after publication pass.

If the source changes after steps 3 and 4, the evidence is stale and is
produced again for the new candidate.

## 🪜 Preparing and publishing a version

Preparation (steps 1 to 4) changes only the repository and publishes
nothing; it can stop at any point. Publication (steps 5 and 6) needs my
separate decision.

### 1. Finalize the changelog and `VERSION`

In a task pull request into the release branch:

- move the `[Unreleased]` entries into `## [X.Y.Z] - YYYY-MM-DD`, and add its
  link reference, `[X.Y.Z]: https://github.com/danielep71/K-LCR/releases/tag/vX.Y.Z`;
- keep an empty `## [Unreleased]` section, with its link reference changed to
  `https://github.com/danielep71/K-LCR/compare/vX.Y.Z...HEAD`;
- create `VERSION`, or update it, to `X.Y.Z`;
- update *Current status* above, and remove the changelog's "No version has
  been released" sentence for the first release.

The `changelog` gate fails until these agree. It also fails on a placeholder
line, such as `TBD`, in a version section, and on a "Release Candidate"
mention or an unchecked task-list item in `README.md`.

### 2. Integrate and freeze the candidate

Integrate the release branch into `main` and synchronize it back, as
[GOVERNANCE.md](docs/GOVERNANCE.md#-release-integration-and-synchronization)
describes; the integration needs my authorization for that candidate. The
integration merge commit is the candidate: record its full SHA. Until the
tag exists, the release branch takes only fixes for a gate that failed on the
candidate; each is integrated again, and the new merge commit becomes the
candidate.

### 3. Run the checks

From a fresh clone of the candidate:

```sh
git switch --detach FULL_SHA
git status --short
python tools/check.py --ci
```

`git status --short` prints nothing, and
`test-results/repository-integrity.json` names `FULL_SHA` with every gate
passing; keep it with the evidence. Confirm that Repository integrity is
green on the same SHA on `main`, and review the open alerts under
**Security > Code scanning** and **Dependabot**.

### 4. Record the host evidence

When the candidate contains VBA, record the Excel run as #15 defines. Until
then, record "no Excel run" in the evidence and the tag message.

### 5. Create the annotated tag

Only once I decide to publish, from the command line so that the tag is
annotated:

```sh
git fetch origin
git tag -a vX.Y.Z FULL_SHA -F ../tag-message-vX.Y.Z.txt
git cat-file -t vX.Y.Z        # must print: tag
git push origin vX.Y.Z
```

The tag message is the release's permanent record:

```text
vX.Y.Z - <milestone title>

Candidate <full 40-character SHA>.
Repository integrity: run <run id> PASS.
Excel: <host, build, bitness>, or none.
Closeout: #<issue>.
Deviations: none.
```

`Deviations:` is mandatory: write `none`, or list each invariant that was not
met. Copy the results from the runs themselves.

### 6. Publish and verify

Create the GitHub Release from the tag. Title it `vX.Y.Z - <milestone
title>`; its notes are the changelog section and the evidence summary, and
for a version without a calculation they start by saying so. Then check that:

- `git cat-file -t vX.Y.Z` prints `tag`, and the tag points at the commit its
  `Candidate` line names;
- Repository integrity succeeded on that commit;
- the release is published, not a draft, its notes name that commit, and it
  has no asset other than the source archives GitHub adds;
- the milestone is closed and has no open issue;
- a fresh clone of the tag passes the commands of step 3.

Record the results in the closeout issue.

## 🗂️ Evidence record

Keep with the release, in its closeout issue and the release notes:

- the candidate SHA and the integration and sync pull requests;
- the Repository integrity run and `test-results/repository-integrity.json`;
- the code-scanning and Dependabot review;
- the Excel run and its host, or "none";
- the tag name and its target;
- the checks of step 6;
- every deviation.

Logs and artifacts expire: copy the decisive lines.

<a id="recovery"></a>

## 🧯 Recovery

- **A wrong change on the release branch:** revert or fix it through a
  reviewed task pull request. Shared history is never rewritten.
- **A wrong integration into `main`, before the tag:** fix it on the release
  branch through a task pull request and integrate again; the new merge
  commit is the candidate. `main` takes only integration pull requests,
  never a direct push; the one exception is a Dependabot security-update pull
  request, which GitHub opens against `main` ([GOVERNANCE.md](docs/GOVERNANCE.md#dependabot-security-updates)).
- **A protected branch moved unexpectedly:** stop, record the divergence and
  get my decision, as
  [GOVERNANCE.md](docs/GOVERNANCE.md#-release-integration-and-synchronization)
  describes.
- **After the tag, before the Release:** stop and record the problem. A
  pushed tag is never moved or deleted: the **Protect release tags** ruleset
  blocks both and has no bypass. Fix the problem in a new patch version.
- **After publication:** never move the tag or replace the notes'
  evidence. Publish a corrected patch version and record the problem in the
  changelog; report a vulnerability as [SECURITY.md](SECURITY.md) describes.
  Only a demonstrable error in a released changelog section, such as a wrong
  link, is corrected there, in a reviewed pull request that adds
  `Corrected after release on YYYY-MM-DD: <reason>`.

## ⏳ Not yet in place

| Practice | State | Follow-on |
| --- | --- | --- |
| Tag-triggered release workflow that checks the tag and builds an attested source bundle and checksums | Deferred: no asset is published before a workbook exists | #137 |
| Command that verifies a published release (tag, candidate, assets, milestone) | Deferred: the checks of step 6 are manual | #137 |
| Excel run bound to the candidate | Deferred to *v0.2.0 - Prototype setup* | #14, #15 |
| Workbook asset and its packaging | Deferred: no workbook is released | B004 and B006 in [DECISIONS.md](docs/DECISIONS.md) |
| User manual and distribution review | Deferred: no workbook is released | None recorded |

## ✅ Checklist

| # | Gate | Done |
| ---: | --- | :---: |
| 1 | I decided to prepare the version | ☐ |
| 2 | Changelog section dated and `VERSION` created or updated | ☐ |
| 3 | Release branch integrated into `main`, and synchronized back | ☐ |
| 4 | Candidate frozen: the integration merge commit's full SHA | ☐ |
| 5 | `python tools/check.py --ci` and Repository integrity pass on the candidate; alerts reviewed | ☐ |
| 6 | Host evidence recorded for the candidate, or "no Excel run" recorded as a deviation | ☐ |
| 7 | I decided to publish | ☐ |
| 8 | Annotated tag on the candidate | ☐ |
| 9 | GitHub Release published from the tag, and the checks of step 6 pass | ☐ |
