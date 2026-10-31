<div align="center">

# 💧 K-LCR

### Liquidity Coverage Ratio reference and independent validation in Excel VBA

**Separate EU and Basel profiles · Traceable inputs and outputs · Synthetic data only**

<br>

[![Excel VBA](https://img.shields.io/badge/Excel_VBA-64--bit_target-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white)](INSTALLATION.md#-host-matrix)
[![Platform](https://img.shields.io/badge/Platform-Windows_target-0078D6?style=for-the-badge&logo=windows&logoColor=white)](INSTALLATION.md#-host-matrix)
[![Profiles](https://img.shields.io/badge/Profiles-EU_%C2%B7_Basel_planned-1f3a5f?style=for-the-badge)](docs/REPOSITORY_STRUCTURE.md#-regulatory-profiles)
[![Status](https://img.shields.io/badge/Status-Repository_setup-BF8700?style=for-the-badge)](#-status)
[![License](https://img.shields.io/badge/License-MPL_2.0-2ea44f?style=for-the-badge)](LICENSE)

<br>

[Website](https://danielep71.github.io/K-LCR/) · [Wiki](https://github.com/danielep71/K-LCR/wiki) ·
[Status](#-status) · [What this project is](#-what-this-project-is) ·
[Get started](#-get-started) · [Architecture](#-architecture) ·
[Documentation](#-documentation) · [Limitations](#-limitations)

---

</div>

## 📍 Status

> [!IMPORTANT]
> **Repository setup.** There is no LCR calculation engine, validated
> workbook, Excel import/compile run or supported host claim yet.
> Windows desktop Excel 64-bit is an **engineering target**, not a tested
> configuration. This project is intended for reference and independent
> validation, not operational reporting or production use.

The selected implementation is Excel/VBA with separate planned EU and Basel
profiles. The current portable **Repository integrity** check covers
repository tooling, tracked text and workflow syntax. It does not validate
regulatory calculations or execute Excel.

## ✨ What this project is

K-LCR is planned as an auditable Liquidity Coverage Ratio reference. The
design separates regulatory source and parameter choices, deterministic
calculation, public API and Excel input/output. Synthetic fixtures and
independent expected values will support validation as those components are
implemented. Exact regulatory editions, inputs, outputs and reconciliation
rules are tracked in the setup issues rather than presumed here.

### Where K-LCR belongs

K-LCR adds liquidity risk to the
[K-Risk Engines](https://github.com/danielep71/K-Risk-Engines) portfolio of
independent risk calculators, whose other projects cover counterparty credit,
market, CVA and interest-rate risk. It is planned, not implemented: no LCR
result exists yet, and the portfolio hub does not list K-LCR yet.

## 📥 Get started

Clone the repository and switch to the active integration branch:

```sh
git clone https://github.com/danielep71/K-LCR.git
cd K-LCR
git switch release/0.1.0
python tools/check.py --ci
```

The check requires the tools listed in [Installation](INSTALLATION.md#-source-and-developer-setup).
It writes a candidate-bound report in `test-results/`. No workbook is
available to install. Do not treat a static PASS as Excel or LCR evidence.

## 🏗️ Architecture

| Boundary | Planned role | Current state |
| --- | --- | --- |
| Pure VBA core | Deterministic calculation, with explicit profile and parameter versions | Contract only |
| Public API | Request validation, named errors and results | Contract only |
| Excel adapter | Host I/O and state restoration | Contract only |
| Validation | Independent fixtures and real host evidence | Planned under #11 and #15 |

See [scope and architecture](docs/REPOSITORY_STRUCTURE.md) and
[VBA house style](docs/VBA_HOUSE_STYLE.md) for the boundaries.

## 🗂️ Documentation

| Topic | Read |
| --- | --- |
| Scope, decisions and follow-on work | [Architecture](docs/REPOSITORY_STRUCTURE.md) · [Decisions](docs/DECISIONS.md) |
| Development, review and checks | [Governance](docs/GOVERNANCE.md) · [Repository tooling](tools/README.md) · [Working rules](AGENTS.md) |
| Settings, evidence, verification gaps | [Repository settings](docs/REPOSITORY_SETTINGS.md) · [Settings evidence](docs/REPOSITORY_SETTINGS_EVIDENCE.md) |
| Source files and generated artifacts | [Source control](docs/SOURCE_CONTROL.md) |
| VBA and Excel target | [House style](docs/VBA_HOUSE_STYLE.md) · [Installation](INSTALLATION.md) |
| License, provenance and safe examples | [Notice](NOTICE.md) · [Security](SECURITY.md) |

## ⚠️ Limitations

No numerical method, regulatory interpretation, host compatibility or
production readiness is certified. EU and Basel rules must remain distinct;
future calculations require source editions, reporting dates and parameter
versions. All examples and test data must be synthetic.

All development first targets `release/0.1.0`. Integration into `main`
requires explicit owner authorization; see [governance](docs/GOVERNANCE.md).

## 👤 Author

**Daniele Penza** — [@danielep71](https://github.com/danielep71). This is an
independent personal project.

## 📄 License

[Mozilla Public License 2.0](LICENSE). Provenance of imported material is
recorded in [NOTICE](NOTICE.md).
