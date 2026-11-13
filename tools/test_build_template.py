"""Tests of the template builder (tools/build_template.py).

They need openpyxl from the hash-locked tool requirements. Without it they are
skipped locally; on GitHub Actions they always run, so a missing openpyxl fails.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import tempfile
import unittest
import zipfile
from pathlib import Path

HAS_OPENPYXL = importlib.util.find_spec("openpyxl") is not None or bool(os.environ.get("GITHUB_ACTIONS"))
ROOT = Path(__file__).resolve().parents[1]
TRACKED = ROOT / "src" / "workbook" / "LCR_Template.xlsx"


def parts(path: Path) -> list[tuple[str, str]]:
    """The entries of a package in order, with the SHA-256 of their uncompressed bytes."""
    with zipfile.ZipFile(path) as z:
        return [(info.filename, hashlib.sha256(z.read(info.filename)).hexdigest()) for info in z.infolist()]


@unittest.skipUnless(HAS_OPENPYXL, "openpyxl is not installed (tools/requirements-quality-ci.txt)")
class TemplateTests(unittest.TestCase):
    def setUp(self) -> None:
        import build_template

        self.builder = build_template
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.scratch = Path(directory.name)

    def build(self, name: str) -> Path:
        target = self.scratch / name
        self.builder.build(target)
        return target

    def test_a_rebuild_gives_the_parts_of_the_tracked_template(self) -> None:
        self.assertEqual(parts(self.build("rebuilt.xlsx")), parts(TRACKED))

    def test_two_builds_give_the_same_bytes(self) -> None:
        first, second = (hashlib.sha256(self.build(n).read_bytes()).hexdigest() for n in ("a.xlsx", "b.xlsx"))
        self.assertEqual(first, second)

    def test_openpyxl_writes_with_the_standard_library(self) -> None:
        import openpyxl.xml

        self.assertFalse(openpyxl.xml.LXML)

    def test_the_package_has_fixed_dates_and_no_author(self) -> None:
        with zipfile.ZipFile(self.build("t.xlsx")) as z:
            self.assertEqual({info.date_time for info in z.infolist()}, {self.builder.ENTRY_DATE})
            core = z.read("docProps/core.xml").decode("utf-8")
            names = z.namelist()
        self.assertNotIn("creator", core)
        self.assertNotIn("dcterms:created", core)
        self.assertFalse([n for n in names if "vbaProject" in n or n.startswith("docMetadata/")])

    def test_the_default_font_drops_the_scheme_whatever_the_spacing(self) -> None:
        for scheme in ('<scheme val="minor"/>', '<scheme val="minor" />'):
            with self.subTest(scheme=scheme):
                styles = f'<fonts><font><name val="Calibri"/>{scheme}</font><font>{scheme}</font></fonts>'
                self.assertEqual(self.builder.default_font(styles),
                                 f'<fonts><font><name val="Aptos"/></font><font>{scheme}</font></fonts>')


if __name__ == "__main__":
    unittest.main()
