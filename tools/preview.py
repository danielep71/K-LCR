#!/usr/bin/env python3
"""Render every sheet of a workbook to PNG for a visual check (LibreOffice + pdftoppm).

Shapes are made printable and each sheet is fitted to one page wide, landscape,
on a copy; the workbook itself is not changed.
Usage: python tools/preview.py workbook.xlsx outdir [rows]
"""
import re
import subprocess
import sys
import zipfile
from pathlib import Path


def main() -> int:
    """Render the sheets of sys.argv[1] into sys.argv[2]; return the exit code."""
    src, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    rows = int(sys.argv[3]) if len(sys.argv) > 3 else 45
    outdir.mkdir(parents=True, exist_ok=True)
    copy = outdir / ("preview" + src.suffix.replace("xlsm", "xlsx"))
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(copy, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            name = info.filename
            if name.startswith("xl/drawings/drawing"):
                data = data.replace(b'fPrintsWithSheet="0"', b'fPrintsWithSheet="1"')
            if re.match(r"xl/worksheets/sheet\d+\.xml$", name):
                t = data.decode("utf-8")
                t = re.sub(r"<pageSetup[^>]*/>", "", t)
                t = t.replace("<pageMargins", '<pageMargins', 1)
                t = re.sub(r"(<pageMargins[^>]*/>)",
                           r'\1<pageSetup paperSize="8" orientation="landscape" fitToWidth="1" fitToHeight="0"/>', t)
                t = re.sub(r"<pageSetUpPr[^>]*/>", '<pageSetUpPr fitToPage="1"/>', t)
                if "<pageSetUpPr" not in t:
                    t = re.sub(r"(<sheetPr[^>]*?)(/>)", r'\1><pageSetUpPr fitToPage="1"/></sheetPr>', t, count=1)
                    t = re.sub(r"(<sheetPr[^>]*>)(?!<pageSetUpPr)", r'\1<pageSetUpPr fitToPage="1"/>', t, count=1)
                # print only the first rows
                dim = re.search(r'<dimension ref="A1:([A-Z]+)\d+"', t)
                if dim and name.startswith("xl/worksheets/"):
                    pass
                data = t.encode("utf-8")
            if name == "xl/workbook.xml":
                t = data.decode("utf-8")
                names = re.findall(r'<sheet [^>]*name="([^"]+)"', t)
                areas = "".join('<definedName name="_xlnm.Print_Area" localSheetId="%d">\'%s\'!$A$1:$AD$%d</definedName>'
                                % (i, n, rows) for i, n in enumerate(names))
                t = re.sub(r'<definedName name="_xlnm.Print_Area"[^>]*>[^<]*</definedName>', "", t)
                t = t.replace("<definedNames>", "<definedNames>" + areas, 1) if "<definedNames>" in t else \
                    t.replace("</sheets>", "</sheets><definedNames>" + areas + "</definedNames>", 1)
                data = t.encode("utf-8")
            if name == "xl/vbaProject.bin":
                continue
            if name == "[Content_Types].xml":
                data = data.replace(b"application/vnd.ms-excel.sheet.macroEnabled.main+xml",
                                    b"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml")
            zout.writestr(info, data)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(copy)],
                   check=True, capture_output=True, timeout=180)
    pdf = copy.with_suffix(".pdf")
    subprocess.run(["pdftoppm", "-png", "-r", "70", str(pdf), str(outdir / "page")], check=True)
    print(sorted(p.name for p in outdir.glob("page*.png")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
