# 🛠️ Contributing

Thank you for helping. This guide is the entry point; the detailed rules live
in the documents it links, and it does not repeat them.

By taking part you agree to the [code of conduct](CODE_OF_CONDUCT.md). Report
a suspected vulnerability privately, as [SECURITY.md](SECURITY.md) describes,
never in an issue or pull request. The working rules for everyone who edits
the repository are in [AGENTS.md](AGENTS.md).

## 🐞 Issues

Open an issue with one of the issue forms. Issue triage checks every open
issue: it needs the assignee, exactly one priority label, an open milestone,
a target end date earlier than the milestone's due date, and a dependency
section ([issues](docs/GOVERNANCE.md#-issues)). `P1` is only for a confirmed
calculation bug. An issue is closed with a *Resolution* section: the change,
the checks run and what was not validated.

## 🌿 Branches and pull requests

- Start a task branch from the active release branch, `release/0.1.0`, and
  name it `docs/`, `fix/`, `feat/` or `chore/` plus the issue number and a
  slug, for example `fix/42-empty-input-report`. No other prefix is allowed.
- Open the pull request against `release/0.1.0`, never `main`: `main` takes
  only release integrations that I authorize, apart from the Dependabot
  security-update exception
  ([task integration](docs/GOVERNANCE.md#-task-integration-and-review);
  [exception](docs/GOVERNANCE.md#dependabot-security-updates)).
- Fill in the [pull request template](.github/PULL_REQUEST_TEMPLATE.md). Its
  *Validated* section lists the checks you ran; write NOT RUN or NOT
  APPLICABLE with a reason instead of claiming evidence that was not
  produced. Give the pull request the labels of its issue and no milestone.
- Add the `CHANGELOG.md` entry under `[Unreleased]` in the same pull request
  ([maintenance policy](CHANGELOG.md#-maintenance-policy)).
- A pull request needs a passing **Repository integrity** check, resolved
  review threads and a recorded review of its final head. Task pull requests
  are squash-merged.

## ✍️ Commit messages

- The subject says what changed, after a type prefix such as `feat:`,
  `fix:`, `docs:`, `ci:` or `chore:`.
- The body says why, what was validated at that commit, and plainly what was
  not, such as an Excel run.
- The last line references the issue: `Refs #N`.

A squashed pull request becomes one commit, with a message that follows the
same rule and ends its subject with the pull request number.

## 📏 Rules of evidence

- Expected values come from outside the code under test: a `published` value
  of a registered source or an `independent` implementation. A value derived
  in this repository stays `illustrative` and validates nothing
  ([reference classes](docs/methodology/TEST_CASES.md#-reference-classes)).
- A registered case is not an executed one, and a skipped assertion is not a
  pass.
- A static check is not an Excel run. Record only evidence that was
  produced, on the commit it was produced for.

## 📐 Contract changes

A contract change alters what a documented contract promises:

- a file, column, category, unit or rule of the
  [input contract](docs/methodology/DATA_CONTRACT.md);
- a field or diagnostic of the
  [parameter sets and results](docs/methodology/PARAMETERS_AND_RESULTS.md);
- the format, reference classes or comparison rule of the
  [test cases](docs/methodology/TEST_CASES.md);
- a source, edition, requirement or decision of the
  [source register](docs/methodology/SOURCES.md) or the
  [applicability map](docs/methodology/APPLICABILITY.md).

The pull request that makes it updates the contract, its validator, its
fixtures and the documents that describe it together, and its changelog entry
says what changed and what a user must do.

## 🧪 Local checks

Set up the tools as [INSTALLATION.md](INSTALLATION.md#developer-setup)
describes, then run every gate before opening a pull request:

```sh
python tools/check.py --ci
```

It runs the same gates as the **Repository integrity** check
([gates](tools/README.md#-gates)) and fails on a missing tool or a dirty
working tree. To run one gate, use its own command, for example
`python tools/check_contract.py --check-fixtures`.

## 📄 Data and licensing

- Use synthetic data only: no real portfolio, client, counterparty, personal
  or credential data in code, fixtures, issues, screenshots or workbooks.
- Do not copy regulatory text, third-party code or workbooks merely because
  they are accessible; record any imported material and its licence in
  [NOTICE.md](NOTICE.md) in the pull request that imports it.
- Contributions are licensed under the repository's [LICENSE](LICENSE),
  MPL-2.0.
