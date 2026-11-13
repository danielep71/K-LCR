# 📚 LCR source register

**Register version 1 · 2026-11-03 · EU and Basel profiles kept apart**

Every regulatory statement in K-LCR's documentation, parameter sets or
fixtures cites an entry of this register by its ID and a locator: an article
and paragraph, a Basel paragraph, or a printed page. A statement without a
registered source is an assumption, and the document that makes it says so.
The [applicability map](APPLICABILITY.md) links each LCR topic to these
locators. Decision D002 in [DECISIONS.md](../DECISIONS.md) keeps the two
profiles separate: an EU rule never fills a gap in the Basel profile, nor the
reverse.

## 🗂️ Register

| ID | Profile | Role | Document | Issuer | Version | Locators used | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `SRC-01` | EU | Normative | Regulation (EU) No 575/2013 (CRR), consolidated text | European Parliament and Council; consolidated by the Publications Office | 26.06.2026, version 021.001 (CELEX `02013R0575-20260626`) | Articles 6(4), 8 and 11(3); Articles 412, 414, 415(2) and 416 of Part Six; Article 451a. The stored extract also holds the rest of Articles 411 to 426 and Article 460, which no requirement cites | `located` |
| `SRC-02` | EU | Normative | Commission Delegated Regulation (EU) 2015/61 (LCR Delegated Regulation), consolidated text | European Commission; consolidated by the Publications Office | 08.07.2022, version 002.001 (CELEX `02015R0061-20220708`), including `SRC-03` and `SRC-04` | Articles 1 to 39; Annexes I and II | `located` |
| `SRC-03` | EU | Amending act, consolidated in `SRC-02` | Commission Delegated Regulation (EU) 2018/1620 of 13 July 2018 amending Delegated Regulation (EU) 2015/61 | European Commission | As published (CELEX `32018R1620`) | Cited through `SRC-02` | `identified` |
| `SRC-04` | EU | Amending act, consolidated in `SRC-02` | Commission Delegated Regulation (EU) 2022/786 of 10 February 2022 amending Delegated Regulation (EU) 2015/61 | European Commission | As published (CELEX `32022R0786`) | Cited through `SRC-02` | `identified` |
| `SRC-05` | EU | Ancillary: supervisory reporting | Commission Implementing Regulation (EU) 2024/3117 laying down implementing technical standards on supervisory reporting | European Commission | Adopted 29 November 2024 (CELEX `32024R3117`); consolidated versions 2024-12-27 and 2025-12-29 exist | Its LCR reporting provisions and templates; not yet read | `identified` |
| `SRC-06` | Basel | Normative | Basel Framework, standard LCR *Liquidity Coverage Ratio*: chapters LCR10, LCR20, LCR30, LCR31, LCR40, LCR90 and LCR99, with their FAQs | Basel Committee on Banking Supervision | Every chapter: version effective as of 15 December 2019. Updates included: LCR20 FAQs published 8 December 2022, LCR30.1 FAQ1 (published 5 June 2020), LCR40 FAQ published 30 March 2023 | Paragraphs LCR10.1 to LCR99.1 | `located` |
| `SRC-07` | Basel | Explanatory: origin of `SRC-06` | *Basel III: The Liquidity Coverage Ratio and liquidity risk monitoring tools* | Basel Committee on Banking Supervision | January 2013 | None: `SRC-06` is cited instead | `identified` |
| `SRC-08` | EU | Interpretive, not binding | EBA Single Rulebook Q&A on the liquidity coverage requirement | European Banking Authority | Each Q&A is registered separately, with its own ID, when a requirement relies on it | None yet | `identified` |

### 🔎 Retrieval record

| ID | Retrieved from | Retrieved | Format | SHA-256 of the retrieved file |
| --- | --- | --- | --- | --- |
| `SRC-01` | <https://publications.europa.eu/resource/celex/02013R0575-20260626> | 2026-11-03 | PDF/A-2a, 895 pages | `6796302ed4213bcba4d4b9b17dc48aefcaf7ef586b875c30c8c71a7689288ecf` |
| `SRC-01` | same address | 2026-11-03 | XHTML | `2d041b5b32d4020fa1decb3bb64e835d6fcb747c5274a61f785b195a9dc9e6ad` |
| `SRC-02` | <https://publications.europa.eu/resource/celex/02015R0061-20220708> | 2026-11-03 | PDF, 60 pages | `b9af0bdf6f65df258cb4b0f807159f0391d824c4c4bfd295e79bd3d0c138e8dd` |
| `SRC-02` | same address | 2026-11-03 | XHTML | `5270ce33e79f271a14c60437d5f2c448ed7ee741364193c0e9d380a8fd710e14` |
| `SRC-05` | <https://publications.europa.eu/resource/celex/32024R3117> | 2026-11-03 | XHTML of the enacting terms, without annexes | `46f32e9d4c58e2d2a1f20911d885558aa1d6b8587d6202efeff835ecd1333b58` |
| `SRC-06` | <https://www.bis.org/committees/bcbs/basel-framework/LCR/standard.pdf> | 2026-11-03 | PDF, 94 pages, generated on 03/11/2026 | `e13f4a864772c8b938ce7bc0f81decc607f4b4d16b4f8ef1fc0a5464bb3ab947` |
| `SRC-07` | <https://www.bis.org/publ/bcbs238.htm> | 2026-11-03 | Publication page only | — |

- **EU versions.** On 2026-11-03 the Publications Office SPARQL endpoint
  (<https://publications.europa.eu/webapi/rdf/sparql>) listed three
  consolidated versions of `SRC-02` (2015-01-17, 2020-04-30, 2022-07-08) and
  two acts amending it (`SRC-03`, `SRC-04`). `SRC-02` is therefore the latest
  consolidation, and it includes both amendments. For `SRC-01` the same
  endpoint listed 2026-06-26 as the latest consolidated version.
- **Consolidated texts have no legal effect.** Each EU consolidated text says
  that it is a documentation tool; the authentic texts are those published in
  the Official Journal of the European Union. A requirement that depends on
  the exact wording is checked against the Official Journal acts as well.
- **CRR pages.** Page numbers are those printed on the pages of `SRC-01`
  (for example *02013R0575 — EN — 26.06.2026 — 021.001 — 636*).
- **Basel identity.** bis.org generates the PDF on each download, with the
  download date on its second page, so a new download does not reproduce the
  hash above. Its identity is the version line of each chapter (*Version
  effective as of 15 December 2019*) and the update notes listed in the
  register.
- **`SRC-05`.** The enacting terms repeal Implementing Regulation (EU)
  2021/451 with effect from 31 December 2025 and cover reporting of the
  liquidity coverage requirement under Article 412 of `SRC-01`. Its annexes,
  which hold the templates, were not retrieved.

## 🏷️ Statuses and roles

- `identified`: registered, but not retrieved, or retrieved and not read.
- `located`: the edition was retrieved from the issuer, its version line was
  read, and the heading of every cited article, chapter or paragraph was
  checked against it.
- `read`: the cited provisions were read in full for a requirement, which
  links the entry.
- `verified`: every locator that a contract (#10) or a fixture (#11) cites
  was checked against the text, on the date recorded with the requirement.
- `superseded by SRC-NN`: replaced; the row stays.

A **normative** source defines a profile's rules. **Ancillary** and
**explanatory** sources inform data contracts and history but never override
a normative source. An **interpretive** source, such as an EBA Q&A, is
applied only through a requirement that names it.

## 📄 Local copies

Two EU copies are stored in [sources/](sources/README.md), with their
provenance and hashes; their reuse terms are in
[NOTICE.md](../../NOTICE.md#-eu-legal-texts):
- `SRC-02`, byte for byte as retrieved;
- an extract of `SRC-01` with the pages of the articles it cites.

I checked the EUR-Lex legal notice on 2026-11-03 (#129). No BIS material is
stored: bis.org permits users to reproduce only "a limited extract" of BIS
material, with the BIS cited as the source
(<https://www.bis.org/terms_conditions.htm>, read on 2026-11-03), so a full
copy of `SRC-06` is not covered (decision A09 in
[APPLICABILITY.md](APPLICABILITY.md)).

A stored file goes under `docs/methodology/sources/` and is kept byte for
byte: Git does not normalize those files and the tracked-text check skips
them. It is either the retrieved file or a page extract made as
[sources/README.md](sources/README.md) describes. It is named
`<ID>_<short-title>.<extension>`, and its SHA-256 is recorded in
[sources/README.md](sources/README.md); the retrieval record above keeps the
hash of the retrieved file.

## ✅ Verifying an entry

1. Open the source from the issuer's own publication, not from a copy.
2. Confirm the version line, and that it applies on the reporting dates the
   profile supports.
3. Recompute the SHA-256 of a retrieved or stored file and compare it with
   the retrieval record (`sha256sum`, or `certutil -hashfile FILE SHA256` on
   Windows).
4. Check each locator that a requirement cites against the text.
5. Raise the status and record the date with the requirement.

## 🔁 Changing the register

- An ID is never reused. A replaced source keeps its row and becomes
  `superseded by` its successor.
- A new edition, or a change to a row's version or locators, raises the
  register version. The same change updates every document, parameter set
  and fixture that cites the row.
- Do not add a regulatory statement to the README, the website, parameter
  sets or fixtures unless it cites a register ID and a locator.
