# Security and confidential data

K-LCR is a private Excel/VBA reference and independent-validation project at
repository-setup stage. It has no validated LCR engine or production workbook.
Treat its examples and outputs as unverified until independently validated.

## Supported scope and reporting

No version has been published. The protected release branch and main receive
best-effort fixes. Report the exact commit; modified copies are outside this
repository's support. In scope are its workflows, scripts, issue forms and,
when added, VBA source and workbook templates. Vulnerabilities in Excel,
Windows, GitHub, Python or Node themselves should be reported upstream.

## Report a vulnerability

Do not open a public issue or include exploit steps, tokens, client details or
private workbooks in a PR. Contact the maintainer, @danielep71, through an
already established private channel and include a minimal synthetic
reproduction and affected commit. If a GitHub private vulnerability-reporting
option is visible and enabled for this repository, it may be used; its
availability has not been verified here. The maintainer will coordinate scope,
fix and disclosure. Do not assume public security advisory workflows are enabled.

## Contributions and examples

- Use synthetic, non-identifying inputs and independently derived expected
  values. Avoid copies of client portfolios, trades, collateral, account
  identifiers and internal documents, including in logs, screenshots and
  issue attachments.
- Keep access tokens, credentials and environment files out of source,
  fixtures, GitHub issue bodies and build logs. Use GitHub secrets only after
  an owner-approved access decision and limit their permissions and lifetime.
- Review imported workbooks, formulas, macros and artifacts for external links,
  hidden sheets, connections, names, embedded files and metadata before any
  commit. A workbook extension or a clean text scan does not establish safety.
- Do not execute an untrusted macro or enable active content to inspect it.
  Host execution evidence must use an approved, isolated test environment and
  a candidate-bound synthetic fixture.
- Follow the repository's branch protections and check results. A passing
  portable check does not certify numerical correctness or host safety.

If a secret or sensitive record is accidentally committed, stop sharing the
content, revoke or rotate affected credentials through the owner, and coordinate
remediation privately. Do not paste the sensitive value into a cleanup issue.
Security-feature availability and any future reporting policy changes are
recorded in [governance](docs/GOVERNANCE.md).

## Current automation boundary

The required Repository integrity workflow runs on PRs and pushes to main and
release/** with read-only contents permission. Issue triage audits open issues
with read-only issue and PR access. Label drift reads live labels; label sync
writes labels only on trusted main events and is validation-only for PRs.
Actions use pinned full commit SHAs and checkouts do not persist credentials.
No traffic credential or workbook execution workflow is configured yet.
See [governance](docs/GOVERNANCE.md) for the observed control state. Update
this inventory when workflows or tokens change.
