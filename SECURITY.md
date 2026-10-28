# 🔒 Security and confidential data

[![Visibility: Public](https://img.shields.io/badge/Visibility-Public-1f3a5f?style=flat-square)](#-security-features)
[![Reporting: Private](https://img.shields.io/badge/Reporting-Private_on_GitHub-1f3a5f?style=flat-square)](#-report-a-vulnerability)
[![Data: Synthetic only](https://img.shields.io/badge/Data-Synthetic_only-0969da?style=flat-square)](#-data-and-secrets)

K-LCR is a public Excel/VBA reference and independent-validation project at
repository-setup stage. It has no validated LCR engine or production workbook.
Treat its examples and outputs as unverified until independently validated.

## 📌 Supported versions

No version of K-LCR has been released. The active release branch named in
[docs/GOVERNANCE.md](docs/GOVERNANCE.md) and `main` are supported on a
best-effort basis. Reports must identify a full commit SHA. Modified copies are
unsupported unless the problem reproduces in this repository.

## 📨 Report a vulnerability

Do **not** disclose a suspected vulnerability in an issue, pull request,
commit message, sample file or screenshot.

Report it privately on GitHub, through **Security → Report a vulnerability**
(<https://github.com/danielep71/K-LCR/security/advisories/new>).

Include:

- the full commit SHA and the affected file, procedure or workflow;
- the Excel/Office build, bitness and Windows version, where relevant;
- the impact and minimal reproduction steps, with synthetic data only; and
- any workaround you tested.

## ⏱️ Response targets

K-LCR is maintained by one person; the targets are best effort, not a
contractual commitment:

- acknowledgement within 5 business days;
- an initial assessment within 10 business days of receiving enough evidence;
- an update at least every 14 days while the report is investigated.

Remediation and disclosure timing are agreed with the reporter according to
severity.

## 🎯 Scope

In scope are this repository's workflows, scripts, issue forms, configuration
and documentation and, when added, its VBA source and workbook templates.
Vulnerabilities in Excel, Windows, GitHub, Python, Node or other third-party
tools should be reported to their maintainers.

## ⚙️ Automation risk surface

The required Repository integrity workflow runs on pull requests and pushes to
`main` and `release/**` with read-only contents permission. Issue triage audits
open issues with read-only issue and pull-request access. Label drift reads
live labels; label sync writes labels only on trusted `main` events and is
validation-only for pull requests. Actions are pinned to full commit SHAs,
checkouts do not persist credentials, and the Python quality tools are
installed from hash-locked requirements. No traffic credential or workbook
execution workflow is configured. Update this inventory when workflows or
tokens change.

## 🛡️ Security features

Recorded on **2026-10-28**, the day K-LCR became public. The states marked
*API* were read back from the public GitHub API on that date (#66).

| Feature | Status |
| --- | --- |
| Private vulnerability reporting | Enabled (API). Reports are filed on GitHub, as above. |
| Secret scanning | Enabled (API). Non-provider patterns and validity checks are not enabled (API). |
| Push protection | Enabled (API). |
| Dependabot alerts | Enabled, as recorded in [docs/GOVERNANCE.md](docs/GOVERNANCE.md); not readable through the public API. |
| Dependabot security updates | Not enabled (API). |
| Dependabot version updates | Configured in `.github/dependabot.yml` for GitHub Actions and the hash-locked Python quality tools; updates arrive as pull requests for review. |
| Code scanning | Not configured. CodeQL would cover the Python tools and workflows, not the VBA. |

Update this table, with its date, when a feature is enabled or changed.

## 🔑 Data and secrets

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
content, revoke or rotate affected credentials through the owner, and
coordinate remediation privately. Do not paste the sensitive value into a
cleanup issue.

## 🤝 Safe harbor

The project will not initiate or recommend legal action for good-faith
research that follows this policy, stays within this repository's own source,
avoids privacy violations and destructive actions, and is reported privately.
This does not authorize testing third-party systems; no bug bounty is offered.
