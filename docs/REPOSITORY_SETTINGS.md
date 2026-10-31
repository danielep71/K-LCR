# ⚙️ Repository settings · Non-default configuration

[![Scope](https://img.shields.io/badge/Scope-Non--default_settings-00338D?style=flat-square)](#scope)
[![Format](https://img.shields.io/badge/Format-Portable-005EB8?style=flat-square)](#reuse)
[![Comparison](https://img.shields.io/badge/Comparison-Documented_defaults-483698?style=flat-square)](#sources)

**Only deliberate differences · No repository identifiers · Reusable configuration**

<a id="scope"></a>

## 🧭 Comparison basis

This document records only settings that differ from the comparison baseline:
a new standalone GitHub.com repository, without inherited organization rules,
an applied security configuration or copied template customizations. General
options use GitHub's documented REST parameter defaults; those defaults are
not a guarantee of every account's repository-creation UI behavior.

Custom active rulesets are compared with an otherwise unprotected repository,
not with individual checkboxes preselected inside the ruleset editor. In
particular, deletion protection may be preselected when creating a ruleset;
creating and activating that targeted ruleset is still a customization.

Reference documentation checked: **2026-10-31**. Repository-specific evidence,
observation dates and rule IDs belong in the local evidence record, not in this
portable file. Copying this file does not apply settings or verify another repository.

[General differences](#general) · [Custom protection](#rulesets) · [Security features](#security) · [Reuse](#reuse) · [Sources](#sources)

<a id="general"></a>

## 🏷️ General settings — changed values only

| Setting | Documented baseline | Configured value | Effect / qualification |
| --- | --- | --- | --- |
| Automatically delete merged head branches | Off (`delete_branch_on_merge: false`) | **On** | Cleans up eligible task branches; protected retained branches remain subject to their deletion rules. |
| Always suggest updating PR branches | Off (`allow_update_branch: false`) | **On** | Offers updates even without a freshness requirement; local governance still governs use on shared integration branches. |
| Repository Projects feature | On (`has_projects: true`) | **Off** | Disables the repository feature; this does not describe account-level project boards. Organization defaults may differ. |
| Legacy downloads flag | On (`has_downloads: true`) | **Off** | API metadata difference; not a prohibition on release assets or source downloads. |

Source: GitHub's [repository REST documentation][repo-api]. These values are
configuration differences, not blanket recommendations for every project.

<a id="rulesets"></a>

## 🛡️ Custom active protection

The baseline has no corresponding custom active rulesets. The following five
rulesets are explicit additions. All are **Active**, have **no excluded refs**
and **no bypass actors**. Default-valued supporting parameters below are
included only to describe each custom rule completely; they are not counted
as separate deviations from GitHub defaults.

| Custom ruleset | Target | Added restrictions |
| --- | --- | --- |
| Protect main | `~DEFAULT_BRANCH` | Require PR, resolved conversations and strict up-to-date `Repository integrity` from GitHub Actions; allow merge commits only; block deletion and force pushes. |
| Protect release branches | `refs/heads/release/**` | Require PR, resolved conversations and the same strict required check; allow squash or merge commits; block deletion and force pushes. |
| Prevent release branch deletion | `refs/heads/release/**` | Independent deletion restriction. |
| Protect release tags | `refs/tags/v*` | Block updates, deletion and force pushes. |
| Protect traffic history | `refs/heads/traffic-history` | Block deletion and force pushes; allow the intended data-writing automation. |

### 🔬 Supporting parameters for the two PR rulesets

| Parameter | Protect main | Release-branch rule |
| --- | --- | --- |
| Required status context | `Repository integrity` | `Repository integrity` |
| Expected check integration | GitHub Actions (`15368`) | GitHub Actions (`15368`) |
| Up-to-date requirement | Strict | Strict |
| Required check enforced on creation | Yes | No — branch bootstrap exception |
| Required approving reviews | 0 | 0 |
| Required review-thread resolution | Yes | Yes |
| Permitted PR merge methods | Merge | Squash, merge |
| Administrator/app bypass | None | None |

**Operational implications:** zero approvals does not establish independent
review. The release bootstrap exception does not exempt subsequent changes.
Synchronize integration branches through the approved PR process; do not rely
on an administrator bypass. Tag protection does not itself restrict tag creation
or authorize publishing a release.

The check name and branch patterns are reusable conventions, not built-in
GitHub jobs or automatically existing branches. Confirm that the required job
reports on every relevant PR before adopting these rules.

<a id="security"></a>

## 🔐 Security features — intended configuration

Unlike the settings above, these features have no single comparison default:
their initial state depends on the account, the repository's visibility and
any applied security configuration. They are listed as the intended
configuration, not as deviations; record the observed state and date in the
local evidence record.

| Feature | Configured value | Effect / qualification |
| --- | --- | --- |
| Dependabot alerts | **On** | Alerts for vulnerable dependencies in the dependency graph; reviewing the alert inventory is separate work. |
| Dependabot security updates | **On** | Opens a pull request to fix an alert. These pull requests target the default branch and ignore `target-branch`, so they need the same approval as any change to it. Grouped security updates are a separate choice. |
| Private vulnerability reporting | **On** | Lets anyone report a vulnerability privately through the Security tab; the reporting policy itself belongs in the security policy file. |
| Secret scanning | **On** | Alerts for supported provider secrets in the repository history. Non-provider patterns and validity checks are separate options. |
| Push protection | **On** | Blocks pushes that contain a supported secret unless the person pushing bypasses it with a reason. |

Code scanning is not listed: its setup type, languages and whether it gates
merges are repository-specific and belong in the evidence record.

<a id="reuse"></a>

## ♻️ Reuse and maintenance

- Keep repository names, usernames, URLs, issue numbers and rule IDs out of this file.
- Verify the destination's actual default and inherited policies before copying a value.
- Include a setting only when both its configured value and comparison default are known.
- Remove rows that match the destination's default; retain only its actual differences.
- Keep unverified settings and historical evidence in the separate local evidence record.
- Recheck this comparison after platform-default changes or an approved configuration change.

> [!NOTE]
> This is intentionally not a complete settings inventory. Security features
> whose initial state depends on account, visibility or an applied security
> configuration are listed above as intended configuration, not classified as
> non-default without a verified comparator. Omission does not mean a feature
> is disabled or unimportant.

<a id="sources"></a>

## 📚 Default and ruleset references

| Reference | Supports |
| --- | --- |
| [Repository REST API][repo-api] | Declared option defaults and parameter meanings |
| [Creating rulesets][ruleset-create] | Custom targets, bypass configuration and activation; the editor initially uses Disabled enforcement |
| [Available rules][ruleset-rules] | Meaning of selected protection rules, including editor defaults |
| [Security configuration defaults][security-defaults] | Why organization-applied defaults must be distinguished from a standalone baseline |
| [Dependabot security updates][dependabot-security] | What security updates do and which branch their pull requests target |
| [Private vulnerability reporting][pvr] | How private reports are enabled and received |
| [Secret scanning and push protection][secret-scanning] | What secret scanning and push protection cover |

[repo-api]: https://docs.github.com/en/rest/repos/repos
[ruleset-create]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository
[ruleset-rules]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
[security-defaults]: https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/secure-at-scale/configure-enterprise-security/establish-complete-coverage/create-custom-configuration
[dependabot-security]: https://docs.github.com/en/code-security/dependabot/dependabot-security-updates/about-dependabot-security-updates
[pvr]: https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/configuring-private-vulnerability-reporting-for-a-repository
[secret-scanning]: https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning

---

[↑ Back to comparison basis](#scope)
