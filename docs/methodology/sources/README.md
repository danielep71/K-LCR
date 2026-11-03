# 📄 Stored source copies

Copies of EU texts listed in the [source register](../SOURCES.md), stored so
that every locator can be checked against the exact edition that was read.
They are documentation copies, not authentic texts: the authentic versions are
those published in the Official Journal of the European Union. No Basel
Committee material is stored here (decision A09 in
[APPLICABILITY.md](../APPLICABILITY.md)).

**Do not edit, reformat or replace these files.** Git does not normalize them
(`.gitattributes`), and the tracked-text check skips them. A new edition is a
new file with its own row; the old file stays.

## 🗂️ Files

| File | Register ID | Document | CELEX | ELI | Language | Consolidated version | Retrieved |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `SRC-02_LCR-Delegated-Regulation-2015-61_consolidated-2022-07-08.pdf` | `SRC-02` | Commission Delegated Regulation (EU) 2015/61 of 10 October 2014 to supplement Regulation (EU) No 575/2013 with regard to liquidity coverage requirement for credit institutions, consolidated text, 60 pages | `02015R0061-20220708` | <http://data.europa.eu/eli/reg_del/2015/61/2022-07-08> | English | 08.07.2022, version 002.001 | 2026-11-03 |
| `SRC-01_CRR-575-2013_consolidated-2026-06-26_extract.pdf` | `SRC-01` | Regulation (EU) No 575/2013 (CRR), consolidated text: **extract** of 37 of its 895 pages (see below) | `02013R0575-20260626` | <http://data.europa.eu/eli/reg/2013/575/2026-06-26> | English | 26.06.2026, version 021.001 | 2026-11-03 |

Both files were retrieved from the Publications Office, which serves the same
consolidated texts as EUR-Lex:
<https://publications.europa.eu/resource/celex/02015R0061-20220708> and
<https://publications.europa.eu/resource/celex/02013R0575-20260626>.

## 🔐 Integrity

| File | Relationship to the retrieved file | SHA-256 |
| --- | --- | --- |
| `SRC-02_…_consolidated-2022-07-08.pdf` | Byte for byte the retrieved PDF | `b9af0bdf6f65df258cb4b0f807159f0391d824c4c4bfd295e79bd3d0c138e8dd` |
| `SRC-01_…_extract.pdf` | Derived extract, not a copy of the retrieved file | `e581dd2fcaf327c2f02d90dad5f69c613d54db45db5da3bbefe3387978fd96d1` |
| Full CRR PDF/A-2a, 895 pages, not stored | The original the extract was cut from | `6796302ed4213bcba4d4b9b17dc48aefcaf7ef586b875c30c8c71a7689288ecf` |

A hash shows that a file has not changed since it was recorded. It does not
make the file legally authentic, and it does not show that the text is still
current: check the register for a later edition.

## ✂️ How the CRR extract was made

The extract is a **selection of pages** of the full consolidated text. No page
was edited, and no text, formula or notice was changed:

| Pages of the full text | Content |
| --- | --- |
| 1 | Title page with the Publications Office notice on the legal status of consolidated texts, and the start of the list of amending acts, which continues on pages not selected |
| 36 to 38 | Article 6 |
| 39 and 40 | Article 8 |
| 42 to 44 | Article 11 |
| 636 to 658 | Part Six, Articles 411 to 426 |
| 740 to 742 | Article 451a |
| 752 and 753 | Article 460 |

Page numbers are those printed on the pages. Because whole pages were taken,
some pages also show the end of the preceding article or the start of the next
one; only the articles listed above are selected. The extract cites nothing
outside them as complete.

Method: pypdf 6.17.0 copied the listed pages in order, unchanged, into a new
PDF. Checked on 2026-11-03:

- the text of every extracted page (`pdftotext -layout`) equals the text of
  the same page of the full file;
- rebuilding the extract with the same pages and version gives the same
  SHA-256.

## ⚖️ Reuse terms

The reuse terms, the attribution of these documents and their licence, which
is not K-LCR's MPL-2.0, are recorded in
[NOTICE.md](../../../NOTICE.md#-eu-legal-texts).

## ✅ Checking a file

To check a file against its hash, from the repository root:

```sh
sha256sum docs/methodology/sources/*.pdf
```

On Windows: `certutil -hashfile <file> SHA256`.
