# 🧭 Working rules for contributors

These rules apply to everyone who edits this repository, by hand or with a
tool. Editorial and working rules live only in this file; other documents
describe the project and its procedures and link here when needed.
Branching, review and integration procedures are in
[docs/GOVERNANCE.md](docs/GOVERNANCE.md).

## ✍️ Voice

- Write my decisions in the first person: "I decided", "my approval",
  "approved by me". Never write "the maintainer" or "the owner".
- Address instructions to the reader: "Run the checks", "Open a pull request
  against release/0.1.0".

## 📄 What the documentation describes

- Operational documentation (README, `docs/`, `tools/README.md`, workflow
  comments, issue and pull request templates) describes only this repository:
  its files, rules, settings and evidence.
- Do not name other repositories, copy their history or wording about them, or
  record conversation or session context. The one exception is the README's
  section *Where K-LCR belongs*, which names and links the K-Risk Engines
  portfolio that K-LCR belongs to, by my decision of 2026-11-13.
- Attributions of imported or adapted material go only in the license files,
  [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).

## 🌿 Branch names

- Task branches start with `docs/`, `fix/`, `feat/` or `chore/`, followed by
  the issue number and a descriptive slug, for example
  `fix/42-empty-input-report`.
- Release branches are `release/X.Y.Z`, without a `v`.
- No other prefix is allowed, whatever prefix a tool proposes.

## 🧱 Intended defaults

Excel as the host, VBA kept as exported source files, and the domain
conventions in [docs/REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md)
and [docs/VBA_HOUSE_STYLE.md](docs/VBA_HOUSE_STYLE.md) are deliberate
choices, not gaps. Work within them; propose a change to one of them only
through an issue.
