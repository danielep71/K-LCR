# 📜 Changelog

Notable changes to K-LCR, from a user's point of view. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). It is neither a
commit log nor release evidence. **No version has been released.**

## 🧭 Maintenance policy

- Add a material change under `[Unreleased]` in the pull request that makes
  it. A change nobody would notice, such as a typo or a refactor with no
  effect, needs no entry.
- Describe the observable result: what exists, what a user or contributor
  can now do, what changed in a contract, and what to do about it.
- Link the issue that holds the detail.
- Record only evidence that was produced. A static check is not an Excel run
  and a registered test case is not a validated calculation: say what was and
  was not run.
- Until a version is released, edit an existing entry rather than adding one
  that describes a change to unreleased work: an entry describes what the
  release contains.
- Entries move into a dated section only when a release is prepared, as
  [RELEASING.md](RELEASING.md) describes. A released section is not
  rewritten; a demonstrable error is corrected in review, with a line
  `Corrected after release on YYYY-MM-DD: <reason>` in that section.

<a id="date-and-version-rules"></a>

### Date and version rules

The `changelog` gate of `python tools/check.py` runs
`tools/check_changelog.py`. It checks the headings, dates, order, link
references and `VERSION`; that every link reference points into this
repository; that this introduction and the *Current status* of
[RELEASING.md](RELEASING.md#current-status) describe the same release state;
that the README mentions no Release Candidate and holds no unchecked task
item; and, once a release's tag exists, that its section still
equals the section at the tag, unless it holds the dated correction line
above. What a version number means is checked in review.

| Rule | Standard |
| --- | --- |
| Version | `MAJOR.MINOR.PATCH`, without a leading `v` in headings |
| Release heading | `## [X.Y.Z] - YYYY-MM-DD`, with a real calendar date |
| Order | `[Unreleased]` first, then releases from newest to oldest, by version and date |
| Link references | One for `[Unreleased]` and one for every release; a release's points to `.../releases/tag/vX.Y.Z` |
| `0.y.z` | Initial development: no compatibility is promised between versions |
| Patch, minor, major | From `1.0.0`: a compatible correction, a compatible capability, an incompatible change to a calculation result, an input or output contract, or the public VBA API |

| Category | Use for |
| --- | --- |
| **Added** | New capabilities, files, checks or tests |
| **Changed** | Changes to existing behaviour, contracts, tooling or documentation |
| **Fixed** | Corrected defects |
| **Security** | Safely disclosed security corrections |
| **Validation** | Evidence actually produced |
| **Known limitations** | Deliberate, unresolved boundaries |

Use only the categories an entry needs.

## [Unreleased]

Work of *v0.1.0 - Repo setup*: the repository, its rules and its contracts.
Nothing in it calculates a Liquidity Coverage Ratio.

### Added

- Governance: `release/0.1.0` as the development branch, task, integration
  and synchronization pull requests, the label catalogue and issue forms
  with priorities, milestones and target end dates checked by Issue triage
  (#2, #8, #56, #70, #107).
- Scope and architecture for an Excel VBA engine with separate EU and Basel
  profiles, the VBA house style and the host conventions (#3, #6).
- Licensing, provenance, security and synthetic-data policies under MPL-2.0
  (#4, #66, #79).
- Repository integrity: tooling tests, Ruff and strict mypy, tracked-text,
  workflow and issue-configuration checks, the input and parameter
  contracts, the registered test cases and VBA static checks, run locally by
  `python tools/check.py` and as the required check (#7, #52, #105, #109,
  #12). The validators accept only `YYYY-MM-DD` dates in range and integer
  versions, match patterns against the whole value, and exit 2 when they
  could not run (#159).
- The regulatory source register and applicability map for both profiles,
  with stored EU source copies and my applicability decisions A01 to A09
  (#9, #126, #129).
- The input, parameter-set and result contracts, with validators and
  synthetic fixtures (#10); Art. 12(1)(f) assets are a Level 2B category in
  scope (#148).
- The test-case format, the oracle and tolerance rules and the validation
  plan, with two illustrative cases (#11).
- The project website, README branding and the social preview (#63, #18).
- Repository settings: a portable register and a dated evidence record,
  including a demonstration that the required check blocks a merge (#90,
  #16). The governance documents, the audits and the provenance record describe
  the closeout as delivered: v0.1.0 is closed without a release (#161).
- This changelog and the release and milestone procedure in
  [RELEASING.md](RELEASING.md) (#20).
- The opt-in **Traffic history** workflow and `tools/traffic_history.py`:
  daily traffic, stars, forks, watchers and open issues merged into CSV files
  on the data-only `traffic-history` branch, badge files and a traffic alert
  issue ([TRAFFIC.md](docs/TRAFFIC.md)), with three traffic badges in the
  README. It is active on `main` since 2026-11-05 (#17).
- The `binaries` gate: every tracked binary is a byte-preserved regulatory
  source, a UserForm `.frx` or listed with its SHA-256 in
  `.github/binary-allowlist.json`; and the
  [file audit](docs/release/FILE_AUDIT_v0.1.0.md) of every tracked file, with
  its findings and their disposition (#21).
- The [documentation audit](docs/release/DOC_AUDIT_v0.1.0.md): every
  document, comment and docstring compared with the implemented behaviour, its
  findings fixed or recorded; the tracked-text check now also covers HTML,
  CSS, SVG and XML (#22).
- [CONTRIBUTING.md](CONTRIBUTING.md), a [code of conduct](CODE_OF_CONDUCT.md)
  and [INSTALLATION.md](INSTALLATION.md): the host matrix, the developer
  setup, verified from a fresh clone on Linux, troubleshooting, and the Excel
  steps, marked as not executed (#19).

### Validation

- `python tools/check.py --ci` and the hosted Repository integrity check
  pass on each merged change. They are static checks: they neither compile
  nor run VBA, and they calculate no LCR.
- The Traffic history workflow made its first collection on `main` on
  2026-11-05, and a same-day rerun changed no value (#17).

### Known limitations

- No VBA source, workbook or LCR calculation exists. No rule is validated:
  no `published` or `independent` test case is registered.
- No Excel host has been tested; import, compilation and a real host run
  are planned in *v0.2.0 - Host execution* (#13, #14, #15).

[Unreleased]: https://github.com/danielep71/K-LCR/commits/main
