#!/usr/bin/env python3
"""Build src/workbook/LCR_Template.xlsx, the macro-free K-LCR workbook.

The layout: black K-LCR wordmark band in row 1, blue title band in row 2, italic note in
row 3, navy input headers, blue output headers, yellow input cells, grey
regulatory values, Aptos throughout, gridlines off, and a sheet navigation bar
of linked shapes in column A whose Inputs block sits in the frozen rows 1-3.

The package is deterministic: openpyxl's standard-library XML writer even when
lxml is installed (tools/plain_openpyxl.py), fixed entry dates, a fixed entry
order and no author or dates in docProps/core.xml, so that rebuilding with the hash-locked
openpyxl gives the same parts as the tracked template
(tools/test_build_template.py compares them).

Usage: python tools/build_template.py [output.xlsx]
"""
from __future__ import annotations

import posixpath
import re
import sys
import zipfile
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Literal, TypedDict
from xml.sax.saxutils import escape

import lcr_spec as spec
import plain_openpyxl  # noqa: F401 - before openpyxl: its standard-library XML writer
from openpyxl import Workbook
from openpyxl.cell.cell import Cell, MergedCell
from openpyxl.formatting.rule import Rule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.dimensions import ColumnDimension
from openpyxl.worksheet.hyperlink import Hyperlink
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.xml import LXML

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src" / "workbook" / "LCR_Template.xlsx"

# ------------------------------------------------------------ palette ----
FONT = "Aptos"
BLACK, GOLD, BAND = "000000", "FFC000", "265A99"
HDR_IN, HDR_OUT = "1F3864", "2E75B6"
INPUT, FIXED, DERIVED = "FFF2CC", "D9D9D9", "F2F2F2"
GRID, NOTE, STATUS, LINK = "BFBFBF", "595959", "7F6000", "0563C1"
TAB_HOME, TAB_IN, TAB_OUT = "1F3864", "BF9000", "2E75B6"

THIN = Side(style="thin", color=GRID)
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
DASHED = Border(bottom=Side(style="dashed", color=GRID))
SECTION = Border(bottom=Side(style="medium", color=HDR_IN))

INPUT_ROWS = 200       # pre-formatted input rows per input sheet
OUTPUT_ROWS = 200      # pre-formatted output rows

# Sheet order, kind and navigation tooltip
SHEETS = [
    ("Home", "home", "Start here: what K-LCR calculates, how to run it, every sheet."),
    ("Params", "in", "Reporting date, currency, caps, the category catalogue and FX rates."),
    ("HQLA", "in", "Liquid assets: one row per holding."),
    ("Outflows", "in", "Liabilities and commitments: one row per line."),
    ("Inflows", "in", "Contractual inflows: one row per line."),
    ("Results", "out", "LCR per currency and in total, with the buffer and net outflow trail."),
    ("LineCalc", "out", "Every input line with its factor, weighted amount and status."),
    ("Checks", "out", "Errors, warnings and information lines of the last run."),
    ("README", "home", "Conventions, methodology, scope and limitations."),
]
NAV_SECTIONS = [("Start", ["Home"]), ("Inputs", ["Params", "HQLA", "Outflows", "Inflows"]),
                ("Outputs", ["Results", "LineCalc", "Checks"]), ("Reference", ["README"])]
CODE_NAMES = {name: "sh" + ("Readme" if name == "README" else name) for name, _, _ in SHEETS}

# A column of an input sheet: (label, width, "in" or "calc", number format).
InputColumn = tuple[str, float, str, str]
# A column of an output sheet: (label, width, number format).
OutputColumn = tuple[str, float, str]


class InputLayout(TypedDict):
    note: str
    cols: list[InputColumn]
    catalog: str


# ------------------------------------------------------------ helpers ----
def font(size: float = 9, bold: bool = False, italic: bool = False, color: str | None = None,
         underline: Literal["single"] | None = None) -> Font:
    return Font(name=FONT, size=size, bold=bold, italic=italic, color=color, underline=underline)


def fill(rgb: str) -> PatternFill:
    return PatternFill("solid", fgColor=rgb)


def style(cell: Cell | MergedCell, *, f: Font | None = None, fl: PatternFill | None = None,
          b: Border | None = None, nf: str | None = None, al: Alignment | None = None) -> None:
    if f is not None:
        cell.font = f
    if fl is not None:
        cell.fill = fl
    if b is not None:
        cell.border = b
    if nf is not None:
        cell.number_format = nf
    if al is not None:
        cell.alignment = al


CENTER = Alignment(vertical="center")
CENTER_WRAP = Alignment(vertical="center", wrap_text=True)
HCENTER = Alignment(horizontal="center", vertical="center")
HCENTER_WRAP = Alignment(horizontal="center", vertical="center", wrap_text=True)


def bands(ws: Worksheet, title: str, last_col: int, note: str = "") -> None:
    """Rows 1-3 of every sheet: wordmark band, title band, note."""
    ws.row_dimensions[1].height = 24
    ws.row_dimensions[2].height = 26.1
    ws.row_dimensions[3].height = 37
    for c in range(2, last_col + 1):
        style(ws.cell(1, c), f=font(11, color=GOLD), fl=fill(BLACK), al=CENTER)
        style(ws.cell(2, c), f=font(11, color="FFFFFF"), fl=fill(BAND), al=CENTER)
    ws["B1"] = "K-LCR"
    style(ws["B1"], f=font(14, color=GOLD), al=Alignment(horizontal="left", vertical="center"))
    ws["B2"] = title
    style(ws["B2"], f=font(18, bold=True, color="FFFFFF"), al=Alignment(horizontal="left", vertical="center"))
    if note:
        ws["C3"] = note
        style(ws["C3"], f=font(10, italic=True, color=NOTE), al=CENTER)


def widths(ws: Worksheet, mapping: Mapping[str, float]) -> None:
    ws.column_dimensions["A"].width = 21.7
    ws.column_dimensions["A"].fill = fill(BLACK)
    ws.column_dimensions["B"].width = 4
    for col, w in mapping.items():
        ws.column_dimensions[col].width = w


def hide_after(ws: Worksheet, last_col: int) -> None:
    """Hide every column after last_col (the Home, Params and README look)."""
    first = last_col + 1
    ws.column_dimensions[get_column_letter(first)] = ColumnDimension(
        ws, index=get_column_letter(first), min=first, max=16384, width=9, hidden=True)


def header(ws: Worksheet, row: int, col: int, labels: Sequence[str], color: str, size: float = 11,
           height: float = 30) -> None:
    ws.row_dimensions[row].height = height
    for i, label in enumerate(labels):
        cell = ws.cell(row, col + i, label)
        style(cell, f=font(size, bold=True, color="FFFFFF"), fl=fill(color), b=BOX, al=CENTER_WRAP)


def section(ws: Worksheet, row: int, text: str, last_col: int = 4) -> None:
    ws.row_dimensions[row].height = 30
    ws.cell(row, 3, text)
    for c in range(3, last_col + 1):
        style(ws.cell(row, c), f=font(14, bold=True, color=HDR_IN), b=SECTION, al=CENTER)


def name(wb: Workbook, label: str, ref: str) -> None:
    wb.defined_names[label] = DefinedName(label, attr_text=ref)


def formula_rule(formula: str, font: Font, fill: PatternFill | None = None) -> Rule:
    """A conditional format on an expression, as openpyxl's FormulaRule builds it."""
    rule = Rule(type="expression", formula=[formula])
    rule.dxf = DifferentialStyle(font=font, fill=fill)
    return rule


# ------------------------------------------------------------- sheets ----
def build_home(wb: Workbook, ws: Worksheet) -> None:
    bands(ws, "Home", 5, "Start here: what K-LCR calculates, the steps of a run and a link to "
          "every sheet. The commands are the buttons on the input and output sheets.")
    widths(ws, {"C": 30, "D": 130, "E": 4.75})
    hide_after(ws, 5)
    ws.row_dimensions[4].height = 9.95
    row = 5
    blocks = [
        ("What K-LCR does", [
            ("Calculates", "The Liquidity Coverage Ratio of a credit institution under Delegated Regulation (EU) "
             "2015/61 as amended by Delegated Regulation (EU) 2018/1620: the liquidity buffer after haircuts and "
             "the Annex I composition caps, the net liquidity outflow after the Annex II inflow caps, and the "
             "ratio in total and per currency, with the trail of every line."),
            ("Does not cover", "Article 17 operational requirements, CIU look-through (Art. 15), the alternative "
             "liquidity approaches (Art. 19), the classification of products into categories, significant-currency "
             "tests, supervisory reporting templates C 72-C 76, NSFR and intraday liquidity."),
            ("Status", "Prototype. Factors are taken from the regulation and are editable on Params; the "
             "illustrative inputs are not real data."),
        ]),
        ("How to run", [
            ("1. Check Params", "Set the reporting date, the reporting currency and the FX rates. Review the "
             "institution-specific factors (yellow) in the category catalogue."),
            ("2. Enter the inputs", "One row per holding on HQLA, one row per line on Outflows and Inflows. Pick "
             "the category from the list; the grey columns show the factor and the weighted amount."),
            ("3. Validate", "Validate inputs lists every finding on Checks without calculating."),
            ("4. Run", "Run LCR validates, calculates and writes Results, LineCalc and Checks."),
            ("5. Read the results", "Results gives the LCR per currency and in total, the buffer composition "
             "and the inflow cap; the last columns recompute buffer and net outflow with worksheet formulas."),
            ("Macros", "The commands need macros enabled. With macros disabled the workbook can still be read, "
             "and the navigation bar in column A still works."),
        ]),
    ]
    for title, items in blocks:
        section(ws, row, title)
        row += 1
        for i, (label, text) in enumerate(items):
            last = i == len(items) - 1
            ws.cell(row, 3, label)
            ws.cell(row, 4, text)
            bd = Border(bottom=Side(style="thin" if last else "dashed", color=GRID))
            style(ws.cell(row, 3), f=font(10, bold=True), b=bd, al=CENTER_WRAP)
            style(ws.cell(row, 4), f=font(9), b=bd, al=CENTER_WRAP)
            ws.row_dimensions[row].height = 46 if len(text) > 160 else 30
            row += 1
        row += 1
    section(ws, row, "Sheets")
    row += 1
    kinds = {"in": "Inputs. ", "out": "Outputs. ", "home": "Reference. "}
    listed = [s for s in SHEETS if s[0] != "Home"]
    for i, (sheet, kind, tip) in enumerate(listed):
        last = i == len(listed) - 1
        cell = ws.cell(row, 3, sheet)
        cell.hyperlink = Hyperlink(ref=cell.coordinate, location=f"'{sheet}'!A1", display=sheet)
        bd = Border(bottom=Side(style="thin" if last else "dashed", color=GRID))
        style(cell, f=font(9, color=LINK, underline="single"), b=bd, al=CENTER_WRAP)
        ws.cell(row, 4, kinds[kind] + tip)
        style(ws.cell(row, 4), f=font(9), b=bd, al=CENTER_WRAP)
        ws.row_dimensions[row].height = 20.1
        row += 1
    ws.freeze_panes = "B4"


def build_params(wb: Workbook, ws: Worksheet) -> dict[str, int]:
    bands(ws, "Parameters", 9, "Codes in column C are read by the engine; only the yellow values are "
          "meant to be changed. Grey values are regulatory and change only with the regulation.")
    widths(ws, {"C": 25.625, "D": 62.625, "E": 15.625, "F": 11.625, "G": 9.625, "H": 36.625, "I": 4})
    hide_after(ws, 9)
    ws.row_dimensions[4].height = 9.95
    header(ws, 5, 3, ["Code", "Description", "Value", "Reference", "", ""], HDR_IN, size=12)
    ws.cell(5, 5).alignment = HCENTER_WRAP
    row = 6
    for code, desc, value, nf, editable, ref in spec.PARAMS:
        ws.cell(row, 3, code)
        ws.cell(row, 4, desc)
        ws.cell(row, 5, value)
        ws.cell(row, 6, ref)
        style(ws.cell(row, 3), f=font(10, bold=True), al=CENTER)
        style(ws.cell(row, 4), f=font(9), al=CENTER)
        style(ws.cell(row, 5), f=font(9), fl=fill(INPUT if editable else FIXED), b=BOX, nf=nf,
              al=Alignment(horizontal="right" if nf != "@" else "center", vertical="center"))
        style(ws.cell(row, 6), f=font(9, color=NOTE), al=CENTER)
        ws.row_dimensions[row].height = 20.1
        name(wb, code, f"Params!$E${row}")
        row += 1
    param_last = row - 1

    row += 1
    section(ws, row, "Category catalogue (Delegated Regulation (EU) 2015/61)", 8)
    row += 1
    ws.cell(row, 3, None)
    header(ws, row, 3, ["Category", "Description", "Factor", "Type", "Class", "Reference"], HDR_IN)
    ws.cell(row, 5).alignment = HCENTER_WRAP
    ws.cell(row, 6).alignment = HCENTER_WRAP
    ws.cell(row, 7).alignment = HCENTER_WRAP
    cat_header = row
    row += 1
    first = row
    type_rows: dict[str, list[int]] = {}
    for code, typ, cls, desc, factor, editable, ref in spec.CATALOGUE:
        values: list[str | float] = [code, desc, factor, typ, cls, "DR 2015/61 " + ref]
        for i, v in enumerate(values):
            ws.cell(row, 3 + i, v)
        style(ws.cell(row, 3), f=font(10, bold=True), b=BOX, al=CENTER)
        style(ws.cell(row, 4), f=font(9), b=BOX, al=CENTER)
        style(ws.cell(row, 5), f=font(9), fl=fill(INPUT if editable else FIXED), b=BOX, nf="0%",
              al=Alignment(horizontal="right", vertical="center"))
        style(ws.cell(row, 6), f=font(9), b=BOX, al=HCENTER)
        style(ws.cell(row, 7), f=font(9), b=BOX, al=HCENTER, nf="@")
        style(ws.cell(row, 8), f=font(9, color=NOTE), b=BOX, al=CENTER)
        ws.row_dimensions[row].height = 18
        type_rows.setdefault(typ, []).append(row)
        row += 1
    last = row - 1
    ws.cell(row, 4, "Factor = haircut for HQLA, outflow rate for OUTFLOW, inflow rate for INFLOW. "
            "Class = level for HQLA (L1, L1CB, L2A, L2B), cap class for INFLOW (75, 90, EXEMPT).")
    style(ws.cell(row, 4), f=font(9, italic=True, color=NOTE), al=CENTER)
    name(wb, "Cat_Code", f"Params!$C${first}:$C${last}")
    name(wb, "Cat_Factor", f"Params!$E${first}:$E${last}")
    name(wb, "Cat_Type", f"Params!$F${first}:$F${last}")
    name(wb, "Cat_Class", f"Params!$G${first}:$G${last}")
    name(wb, "Cat_Ref", f"Params!$H${first}:$H${last}")
    for typ, label in (("HQLA", "Cat_HQLA"), ("OUTFLOW", "Cat_Outflow"), ("INFLOW", "Cat_Inflow")):
        rows = type_rows[typ]
        name(wb, label, f"Params!$C${rows[0]}:$C${rows[-1]}")

    row += 2
    section(ws, row, "FX rates (illustrative - replace with market rates)", 5)
    row += 1
    header(ws, row, 3, ["FX_Ccy", "Currency", "Units of reporting ccy per 1 unit"], HDR_IN)
    ws.cell(row, 5).alignment = HCENTER_WRAP
    row += 1
    fx_first = row
    for ccy, label, rate in spec.FX:
        ws.cell(row, 3, ccy)
        ws.cell(row, 4, label)
        ws.cell(row, 5, rate)
        for c in (3, 4, 5):
            style(ws.cell(row, c), f=font(10 if c == 3 else 9, bold=c == 3), fl=fill(INPUT), b=BOX, al=CENTER)
        ws.cell(row, 5).number_format = "0.0000##"
        ws.row_dimensions[row].height = 18
        row += 1
    # spare FX rows
    for _ in range(5):
        for c in (3, 4, 5):
            style(ws.cell(row, c), f=font(9), fl=fill(INPUT), b=BOX, al=CENTER)
        ws.cell(row, 5).number_format = "0.0000##"
        row += 1
    name(wb, "FX_Ccy", f"Params!$C${fx_first}:$C${row - 1}")
    ws.cell(row, 4, "Add currencies directly below the last row (no blank rows in column C).")
    style(ws.cell(row, 4), f=font(9, italic=True, color=NOTE), al=CENTER)
    ws.freeze_panes = "B4"
    return dict(param_first=6, param_last=param_last, cat_header=cat_header)


INPUT_LAYOUTS: dict[str, InputLayout] = {
    "HQLA": InputLayout(
        note="One row per holding at market value in its currency. Unwind adjustment: the change in "
             "holdings if every secured transaction maturing within 30 days unwound (Annex I).",
        cols=[("AssetID", 15.625, "in", "@"), ("Description", 40.625, "in", "@"),
              ("Category", 20.625, "in", "@"), ("Ccy", 8.625, "in", "@"),
              ("Market value", 18.625, "in", "#,##0"), ("Unwind adjustment", 18.625, "in", "#,##0"),
              ("Level", 9.625, "calc", "@"), ("Haircut", 9.625, "calc", "0%"),
              ("Value post-haircut (ccy)", 18.625, "calc", "#,##0"),
              ("Adjusted post-haircut (ccy)", 18.625, "calc", "#,##0"),
              ("Reference", 30.625, "calc", "@")],
        catalog="Cat_HQLA"),
    "Outflows": InputLayout(
        note="One row per line: the outstanding balance, or the undrawn amount that can be drawn within "
             "30 days, in its currency.",
        cols=[("LineID", 15.625, "in", "@"), ("Description", 44.625, "in", "@"),
              ("Category", 20.625, "in", "@"), ("Ccy", 8.625, "in", "@"),
              ("Amount", 18.625, "in", "#,##0"), ("Outflow rate", 10.625, "calc", "0%"),
              ("Weighted outflow (ccy)", 18.625, "calc", "#,##0"), ("Reference", 30.625, "calc", "@")],
        catalog="Cat_Outflow"),
    "Inflows": InputLayout(
        note="One row per line: the contractual amount due within 30 days from exposures that are "
             "performing, in its currency.",
        cols=[("LineID", 15.625, "in", "@"), ("Description", 44.625, "in", "@"),
              ("Category", 20.625, "in", "@"), ("Ccy", 8.625, "in", "@"),
              ("Amount", 18.625, "in", "#,##0"), ("Inflow rate", 10.625, "calc", "0%"),
              ("Cap class", 9.625, "calc", "@"), ("Weighted inflow (ccy)", 18.625, "calc", "#,##0"),
              ("Reference", 30.625, "calc", "@")],
        catalog="Cat_Inflow"),
}


def lookup(range_name: str, r: int) -> str:
    return f'IFERROR(INDEX({range_name},MATCH($E{r},Cat_Code,0)),"?")'


def derived_formulas(sheet: str, r: int) -> dict[int, str]:
    guard = f'$E{r}=""'
    if sheet == "HQLA":
        return {
            9: f'=IF({guard},"",{lookup("Cat_Class", r)})',
            10: f'=IF({guard},"",{lookup("Cat_Factor", r)})',
            11: f'=IF(OR({guard},$G{r}=""),"",IFERROR($G{r}*(1-$J{r}),""))',
            12: f'=IF(OR({guard},$G{r}=""),"",IFERROR(($G{r}+N($H{r}))*(1-$J{r}),""))',
            13: f'=IF({guard},"",{lookup("Cat_Ref", r)})',
        }
    if sheet == "Outflows":
        return {
            8: f'=IF({guard},"",{lookup("Cat_Factor", r)})',
            9: f'=IF(OR({guard},$G{r}=""),"",IFERROR($G{r}*$H{r},""))',
            10: f'=IF({guard},"",{lookup("Cat_Ref", r)})',
        }
    return {
        8: f'=IF({guard},"",{lookup("Cat_Factor", r)})',
        9: f'=IF({guard},"",{lookup("Cat_Class", r)})',
        10: f'=IF(OR({guard},$G{r}=""),"",IFERROR($G{r}*$H{r},""))',
        11: f'=IF({guard},"",{lookup("Cat_Ref", r)})',
    }


def build_input(wb: Workbook, ws: Worksheet, sheet: str, rows: Sequence[Sequence[str | float]]) -> int:
    layout = INPUT_LAYOUTS[sheet]
    cols = layout["cols"]
    last_col = 2 + len(cols)
    bands(ws, sheet, last_col)
    widths(ws, {get_column_letter(3 + i): w for i, (_, w, _, _) in enumerate(cols)})
    ws["C3"] = layout["note"]
    ws.merge_cells("C3:D3")
    style(ws["C3"], f=font(8, italic=True, color=NOTE), al=Alignment(vertical="center", wrap_text=True))
    hr = 4
    ws.row_dimensions[hr].height = 50.1
    for i, (label, _, kind, _) in enumerate(cols):
        cell = ws.cell(hr, 3 + i, label)
        style(cell, f=font(11, bold=True, color="FFFFFF"), fl=fill(HDR_IN if kind == "in" else HDR_OUT),
              b=BOX, al=HCENTER_WRAP if i > 1 else CENTER_WRAP)
    first = hr + 1
    for k in range(INPUT_ROWS):
        r = first + k
        ws.row_dimensions[r].height = 20.1
        values = rows[k] if k < len(rows) else None
        formulas = derived_formulas(sheet, r)
        for i, (label, _, kind, nf) in enumerate(cols):
            c = 3 + i
            target = ws.cell(r, c)
            assert isinstance(target, Cell)
            if kind == "in":
                if values is not None and i < len(values):
                    v = values[i]
                    target.value = v if not (label == "Unwind adjustment" and v == 0) else None
                style(target, f=font(9), fl=fill(INPUT), b=BOX, nf=nf,
                      al=HCENTER if label in ("Ccy", "Category") else CENTER)
            else:
                target.value = formulas.get(c)
                style(target, f=font(9, color=NOTE), fl=fill(DERIVED), b=BOX, nf=nf,
                      al=HCENTER if nf in ("@", "0%") and label != "Reference" else CENTER)
    last = first + INPUT_ROWS - 1
    dv_cat = DataValidation(type="list", formula1=layout["catalog"], allow_blank=True,
                            showErrorMessage=False)
    dv_cat.add(f"E{first}:E{last}")
    dv_ccy = DataValidation(type="list", formula1="FX_Ccy", allow_blank=True, showErrorMessage=False)
    dv_ccy.add(f"F{first}:F{last}")
    ws.add_data_validation(dv_cat)
    ws.add_data_validation(dv_ccy)
    ws.auto_filter.ref = f"C{hr}:{get_column_letter(last_col)}{last}"
    red = Font(color="9C0006")
    ws.conditional_formatting.add(f"I{first}:{get_column_letter(last_col)}{last}",
                                  formula_rule(f'$I{first}="?"' if sheet == "HQLA" else f'$H{first}="?"',
                                              font=red))
    ws.freeze_panes = "E5"
    return last_col


RESULTS_COLS: list[OutputColumn] = [
    ("Scope", 14.75, "@"), ("Lines used / total", 11.75, "@"),
    ("Level 1 excl. EHQCB", 15.75, "#,##0"), ("Level 1 EHQCB", 15.75, "#,##0"),
    ("Level 2A", 15.75, "#,##0"), ("Level 2B", 15.75, "#,##0"),
    ("Adjusted L1 excl. EHQCB", 15.75, "#,##0"), ("Adjusted L1 EHQCB", 15.75, "#,##0"),
    ("Adjusted L2A", 15.75, "#,##0"), ("Adjusted L2B", 15.75, "#,##0"),
    ("Excess liquid assets", 15.75, "#,##0"), ("Liquidity buffer", 16.75, "#,##0"),
    ("Total outflows", 15.75, "#,##0"), ("Inflows fully exempt", 15.75, "#,##0"),
    ("Inflows 90% cap", 15.75, "#,##0"), ("Inflows 75% cap", 15.75, "#,##0"),
    ("Reduction for inflows", 15.75, "#,##0"), ("Net liquidity outflow", 16.75, "#,##0"),
    ("LCR", 10.75, "0.0%"), ("Surplus / (shortfall)", 16.75, "#,##0;(#,##0)"),
    ("Status", 40.75, "@"), ("Buffer (formula check)", 15.75, "#,##0"),
    ("NLO (formula check)", 15.75, "#,##0"), ("Check", 9.75, "@"),
]


def build_results(wb: Workbook, ws: Worksheet) -> int:
    last_col = 2 + len(RESULTS_COLS)
    bands(ws, "Results", last_col)
    widths(ws, {get_column_letter(3 + i): w for i, (_, w, _) in enumerate(RESULTS_COLS)})
    ws["C4"] = "No results yet: press Run LCR."
    ws["C5"] = "Amounts in the reporting currency. Scope = currency of the lines, or TOTAL."
    for a in ("C4", "C5"):
        style(ws[a], f=font(10, italic=True, color=STATUS), al=CENTER)
    hr = 6
    ws.row_dimensions[hr].height = 42
    for i, (label, _, _) in enumerate(RESULTS_COLS):
        cell = ws.cell(hr, 3 + i, label)
        check = label.endswith("(formula check)") or label == "Check"
        style(cell, f=font(11, bold=True, color="FFFFFF"), fl=fill(HDR_IN if check else HDR_OUT), b=BOX,
              al=HCENTER_WRAP if i else CENTER_WRAP)
    for k in range(OUTPUT_ROWS):
        r = hr + 1 + k
        for i, (label, _, nf) in enumerate(RESULTS_COLS):
            style(ws.cell(r, 3 + i), f=font(10), nf=nf,
                  al=HCENTER if label in ("Lines used / total", "Check") else
                  Alignment(vertical="center", indent=1) if label == "Status" else CENTER)
    rng = f"C{hr + 1}:{get_column_letter(last_col)}{hr + OUTPUT_ROWS}"
    red = Font(color="9C0006")
    ws.conditional_formatting.add(rng, formula_rule(f'LEFT($W{hr + 1},10)="INCOMPLETE"', font=red))
    ws.conditional_formatting.add(f"U{hr + 1}:U{hr + OUTPUT_ROWS}",
                                  formula_rule(f'AND(ISNUMBER($U{hr + 1}),$U{hr + 1}<LCRRequirement)',
                                              font=Font(color="9C0006", bold=True)))
    ws.conditional_formatting.add(f"Z{hr + 1}:Z{hr + OUTPUT_ROWS}",
                                  formula_rule(f'$Z{hr + 1}="DIFF"', font=red,
                                              fill=PatternFill("solid", fgColor="FFC7CE", bgColor="FFC7CE")))
    ws.freeze_panes = "D7"
    ws.sheet_view.zoomScale = 90
    return last_col


LINECALC_COLS: list[OutputColumn] = [
    ("Sheet", 10.75, "@"), ("Row", 6.75, "0"), ("LineID", 12.75, "@"), ("Category", 20.75, "@"),
    ("Class", 8.75, "@"), ("Ccy", 6.75, "@"), ("Amount (ccy)", 16.75, "#,##0"),
    ("Unwind adj. (ccy)", 15.75, "#,##0"), ("FX rate", 9.75, "0.0000##"),
    ("Amount (rep. ccy)", 16.75, "#,##0"), ("Factor", 8.75, "0%"), ("Factor type", 11.75, "@"),
    ("Weighted (rep. ccy)", 16.75, "#,##0"), ("Adjusted weighted (rep. ccy)", 16.75, "#,##0"),
    ("Status", 44.75, "@"),
]


def build_table_output(wb: Workbook, ws: Worksheet, title: str, cols: Sequence[OutputColumn], note: str,
                       hr: int = 5) -> int:
    last_col = 2 + len(cols)
    bands(ws, title, last_col, note)
    widths(ws, {get_column_letter(3 + i): w for i, (_, w, _) in enumerate(cols)})
    ws.row_dimensions[4].height = 9.95
    ws.row_dimensions[hr].height = 42
    for i, (label, _, _) in enumerate(cols):
        style(ws.cell(hr, 3 + i, label), f=font(11, bold=True, color="FFFFFF"), fl=fill(HDR_OUT), b=BOX,
              al=CENTER_WRAP if i in (0, len(cols) - 1) else HCENTER_WRAP)
    for k in range(OUTPUT_ROWS):
        for i, (label, _, nf) in enumerate(cols):
            style(ws.cell(hr + 1 + k, 3 + i), f=font(10), nf=nf,
                  al=HCENTER if label in ("Row", "Class", "Ccy", "Factor", "Severity") else
                  Alignment(vertical="center", indent=1) if label in ("Status", "Message", "Code") else CENTER)
    return last_col


CHECKS_COLS: list[OutputColumn] = [("Severity", 12.75, "@"), ("Sheet", 12.75, "@"), ("Row", 6.75, "0"),
               ("Reference", 22.75, "@"), ("Message", 100.75, "@"), ("Code", 16.75, "@")]


def build_checks(wb: Workbook, ws: Worksheet) -> int:
    last_col = build_table_output(
        wb, ws, "Checks", CHECKS_COLS,
        "ERROR: input rejected; the line is excluded and the LCR of its scope is withheld (INCOMPLETE). "
        "WARNING: accepted with an assumption. INFO: information only.")
    red, amber = Font(color="9C0006"), Font(color="9C5700")
    rng = f"C6:{get_column_letter(last_col)}{5 + OUTPUT_ROWS}"
    ws.conditional_formatting.add(rng, formula_rule('$C6="ERROR"', font=red))
    ws.conditional_formatting.add(rng, formula_rule('$C6="WARNING"', font=amber))
    ws.freeze_panes = "D6"
    return last_col


def build_linecalc(wb: Workbook, ws: Worksheet) -> int:
    last_col = build_table_output(
        wb, ws, "LineCalc", LINECALC_COLS,
        "One row per input line, in input order. Weighted = amount x (1 - haircut) for HQLA, "
        "amount x rate for flows; adjusted weighted includes the unwind adjustment (HQLA only).")
    ws.conditional_formatting.add(f"C6:{get_column_letter(last_col)}{5 + OUTPUT_ROWS}",
                                  formula_rule('LEFT($Q6,8)="EXCLUDED"', font=Font(color="9C0006")))
    ws.freeze_panes = "F6"
    return last_col


def build_readme(wb: Workbook, ws: Worksheet) -> None:
    bands(ws, "README", 5, "Conventions, methodology summary, scope and limitations of the K-LCR prototype.")
    widths(ws, {"C": 30, "D": 130, "E": 4.75})
    hide_after(ws, 5)
    ws.row_dimensions[4].height = 9.95
    blocks = [
        ("Conventions", [
            ("Amounts", "Unscaled amounts in the currency of the line on the input sheets; in the reporting "
             "currency (Params, ReportingCcy) on Results and LineCalc, converted with the FX table on Params."),
            ("Rates", "Haircuts, outflow and inflow rates are decimals shown as percentages."),
            ("Colours", "Yellow: input. Grey on Params: regulatory value. Light grey on the input sheets: "
             "derived for display only; the engine recomputes everything from the inputs and Params."),
            ("Scopes", "Each currency used by a line is a scope, and TOTAL covers every line. Per-currency "
             "figures apply the same formulas to the lines of that currency only."),
        ]),
        ("Methodology", [
            ("Liquidity buffer", "Annex I (as amended by DR 2018/1620): buffer = L1 + L2A + L2B - MIN(L1 + L2A + "
             "L2B; excess), with L1 including EHQCB, every amount post-haircut."),
            ("Excess liquid assets", "Excess = S - MIN(S; A1/0.30; (A1 + A1CB)/0.60; (A1 + A1CB + A2A)/0.85), "
             "S = A1 + A1CB + A2A + A2B: the adjusted amounts after the unwind of secured transactions, "
             "asset exchanges and collateralised derivatives maturing within 30 days. A negative adjusted level "
             "amount is floored at zero and reported as a warning."),
            ("Net liquidity outflow", "Annex II: NLO = TO - MIN(FEI; TO) - MIN(IHC; 0.90 x MAX(TO - FEI; 0)) - "
             "MIN(IC; 0.75 x MAX(TO - FEI - IHC/0.90; 0)), with FEI, IHC and IC the weighted inflows of cap "
             "class EXEMPT, 90 and 75."),
            ("Ratio", "LCR = liquidity buffer / NLO; surplus = buffer - LCRRequirement x NLO. No ratio when NLO is "
             "zero."),
            ("Completeness", "A line with an error is excluded and listed on Checks; with WithholdIncomplete = "
             "TRUE the buffer, NLO and LCR of every scope it belongs to are withheld (status INCOMPLETE)."),
            ("Formula check", "The last columns of Results recompute the buffer and NLO with worksheet formulas "
             "from the component columns; Check = OK when both agree with the engine within 0.01."),
        ]),
        ("Scope and limitations", [
            ("Classification", "The user assigns each line to a category; the workbook does not test the "
             "eligibility conditions of Articles 7-16 or the operational requirements of Article 8."),
            ("Not modelled", "CIU look-through (Art. 15), inflows and outflows within a group or IPS beyond the "
             "EXEMPT and 90 classes (Art. 29, 34), collateral swaps (Art. 28(4)), alternative liquidity "
             "approaches (Art. 19), significant-currency thresholds (CRR Art. 415(2))."),
            ("Data", "The inputs are illustrative. Results are for analysis and do not replace the supervisory "
             "reporting of templates C 72-C 76."),
        ]),
        ("Sources", [
            ("Regulation", "Commission Delegated Regulation (EU) 2015/61, consolidated text as amended by "
             "Commission Delegated Regulation (EU) 2018/1620 (applicable from 30 April 2020)."),
            ("Standard", "Basel Committee, consolidated framework LCR30-LCR40, the basis of the EU rules; the EU "
             "adds the level 1 covered bond class (70% cap) and the 90% and exempt inflow cap classes."),
        ]),
    ]
    row = 5
    for title, items in blocks:
        section(ws, row, title)
        row += 1
        for i, (label, text) in enumerate(items):
            last = i == len(items) - 1
            ws.cell(row, 3, label)
            ws.cell(row, 4, text)
            bd = Border(bottom=Side(style="thin" if last else "dashed", color=GRID))
            style(ws.cell(row, 3), f=font(10, bold=True), b=bd, al=CENTER_WRAP)
            style(ws.cell(row, 4), f=font(9), b=bd, al=CENTER_WRAP)
            ws.row_dimensions[row].height = 46 if len(text) > 170 else 30
            row += 1
        row += 1
    ws.freeze_panes = "B4"


# ------------------------------------------------------- drawing layer ----
PX = 9525
BAR_X, BAR_W = 8, 141
PAD_TOP, PAD_BOTTOM, HEAD_H, BTN_H, BTN_GAP, SECTION_GAP, STRIP_W = 6, 3, 17, 21, 2, 7, 3
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_DRAWING = NS_R + "/drawing"
REL_HYPERLINK = NS_R + "/hyperlink"

BUTTONS = {
    "HQLA": [("Run LCR", "RunLCR"), ("Validate inputs", "ValidateInputs"), ("Clear outputs", "ClearOutputs")],
    "Outflows": [("Run LCR", "RunLCR"), ("Validate inputs", "ValidateInputs"), ("Clear outputs", "ClearOutputs")],
    "Inflows": [("Run LCR", "RunLCR"), ("Validate inputs", "ValidateInputs"), ("Clear outputs", "ClearOutputs")],
    "Results": [("Run LCR", "RunLCR"), ("Clear outputs", "ClearOutputs"), ("Self-test", "RunSelfTest")],
}
BUTTON_COL = {"HQLA": 4, "Outflows": 4, "Inflows": 4, "Results": 3}


def shape(sid: int, nm: str, x: int, y: int, w: int, h: int, fill_rgb: str | None, text: str = "",
          color: str = "", bold: bool = False, size: int = 900, link: str | None = None, tip: str = "",
          anchor: str = "ctr", inset: int = 0, spacing: int = 0, macro: str = "", line: str | None = None,
          align: str = "l") -> str:
    click = ""
    if link:
        click = '<a:hlinkClick xmlns:r="%s" r:id="%s" tooltip="%s"/>' % (NS_R, link, escape(tip, {'"': "&quot;"}))
    fill_xml = '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % fill_rgb if fill_rgb else "<a:noFill/>"
    line_xml = ('<a:ln w="9525"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:ln>' % line
                if line else "<a:ln><a:noFill/></a:ln>")
    body = ""
    if text:
        run = ('<a:rPr lang="en-GB" sz="%d" b="%d"%s><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
               '<a:latin typeface="%s"/><a:cs typeface="%s"/></a:rPr>') % (
                   size, 1 if bold else 0, ' spc="%d"' % spacing if spacing else "", color, FONT, FONT)
        body = ('<xdr:txBody><a:bodyPr vertOverflow="clip" horzOverflow="clip" wrap="none" lIns="%d" tIns="0" '
                'rIns="0" bIns="%d" rtlCol="0" anchor="%s"/><a:lstStyle/><a:p><a:pPr algn="%s"/>'
                '<a:r>%s<a:t>%s</a:t></a:r></a:p></xdr:txBody>') % (
                    inset * PX, 2 * PX if anchor == "b" else 0, anchor, align, run, escape(text))
    return ('<xdr:sp macro="%s" textlink=""><xdr:nvSpPr><xdr:cNvPr id="%d" name="%s">%s</xdr:cNvPr>'
            '<xdr:cNvSpPr/></xdr:nvSpPr><xdr:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>%s%s</xdr:spPr>%s</xdr:sp>') % (
                escape(macro, {'"': "&quot;"}), sid, nm, click, x, y, w, h, fill_xml, line_xml, body)


def strip_colour(rgb: str) -> str:
    r, g, b = (int(rgb[i:i + 2], 16) for i in (0, 2, 4))
    return "8FAADC" if 0.2126 * r + 0.7152 * g + 0.0722 * b < 70 else rgb


def nav_group(gname: str, block: Sequence[tuple[str, list[str]]], sheet: str, ids: Iterator[int],
              links: Mapping[str, str], tabs: Mapping[str, str], tips: Mapping[str, str], row: int) -> str:
    x0, children, y = BAR_X * PX, [], PAD_TOP
    for index, (title, items) in enumerate(block):
        if index:
            y += SECTION_GAP
        children.append(shape(next(ids), "Nav_Section_" + title, x0, y * PX, BAR_W * PX, HEAD_H * PX, None,
                              title.upper(), GOLD, True, 700, anchor="b", inset=4, spacing=60))
        y += HEAD_H
        for target in items:
            current = target == sheet
            children.append(shape(next(ids), "Nav_" + target, x0, y * PX, BAR_W * PX, BTN_H * PX,
                                  BAND if current else "262626", target, "FFFFFF" if current else "D9D9D9",
                                  current, 900, None if current else links[target], tips[target], inset=12))
            children.append(shape(next(ids), "Nav_" + target + "_Mark", x0, y * PX, STRIP_W * PX, BTN_H * PX,
                                  GOLD if current else strip_colour(tabs[target])))
            y += BTN_H + BTN_GAP
    height = (y - BTN_GAP + PAD_BOTTOM) * PX
    xml = ('<xdr:grpSp><xdr:nvGrpSpPr><xdr:cNvPr id="%d" name="%s" descr="Sheet navigation"/><xdr:cNvGrpSpPr/>'
           '</xdr:nvGrpSpPr><xdr:grpSpPr><a:xfrm><a:off x="%d" y="0"/><a:ext cx="%d" cy="%d"/>'
           '<a:chOff x="%d" y="0"/><a:chExt cx="%d" cy="%d"/></a:xfrm></xdr:grpSpPr>%s</xdr:grpSp>') % (
               next(ids), gname, x0, BAR_W * PX, height, x0, BAR_W * PX, height, "".join(children))
    return ('<xdr:oneCellAnchor><xdr:from><xdr:col>0</xdr:col><xdr:colOff>%d</xdr:colOff><xdr:row>%d</xdr:row>'
            '<xdr:rowOff>0</xdr:rowOff></xdr:from><xdr:ext cx="%d" cy="%d"/>%s'
            '<xdr:clientData fPrintsWithSheet="0"/></xdr:oneCellAnchor>') % (x0, row, BAR_W * PX, height, xml)


def button_anchor(ids: Iterator[int], label: str, macro: str, col: int, offset_px: int, row3_pt: float) -> str:
    w, h = 128, 24
    row_px = row3_pt * 96 / 72
    y_off = int(max(0, (row_px - h) / 2)) * PX
    sp = shape(next(ids), "Btn_" + macro, 0, 0, w * PX, h * PX, "F2F2F2", label, "000000", False, 1000,
               anchor="ctr", macro="[0]!" + macro, line="ADADAD", align="ctr")
    return ('<xdr:oneCellAnchor><xdr:from><xdr:col>%d</xdr:col><xdr:colOff>%d</xdr:colOff><xdr:row>2</xdr:row>'
            '<xdr:rowOff>%d</xdr:rowOff></xdr:from><xdr:ext cx="%d" cy="%d"/>%s'
            '<xdr:clientData fPrintsWithSheet="0"/></xdr:oneCellAnchor>') % (
                col, offset_px * PX, y_off, w * PX, h * PX, sp)


RELS_EMPTY = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.'
              'openxmlformats.org/package/2006/relationships"></Relationships>')
# docProps/core.xml without author, editor or dates, so that a rebuild gives the same bytes.
CORE_PROPERTIES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<cp:coreProperties xmlns:cp="http://'
                   'schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/'
                   'elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/'
                   'XMLSchema-instance"/>')
ENTRY_DATE = (1980, 1, 1, 0, 0, 0)


def sheet_parts(entries: Mapping[str, bytes]) -> list[tuple[str, str]]:
    """(sheet name, worksheet part) in workbook order."""
    rels = entries["xl/_rels/workbook.xml.rels"].decode("utf-8")
    targets = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels))
    targets.update({k: v for v, k in re.findall(r'Target="([^"]+)"[^>]*Id="([^"]+)"', rels)})
    parts = []
    workbook = entries["xl/workbook.xml"].decode("utf-8")
    for nm, rid in re.findall(r'<sheet [^>]*name="([^"]+)"[^>]*r:id="([^"]+)"', workbook):
        t = targets[rid]
        parts.append((nm, posixpath.normpath(posixpath.join("xl", t)) if not t.startswith("/") else t[1:]))
    return parts


def drawing_xml(sheet: str, frozen_row: int) -> tuple[str, str]:
    """The drawing part of one sheet (navigation bar and buttons) and its relationships."""
    tabs = {n: (TAB_IN if k == "in" else TAB_OUT if k == "out" else TAB_HOME) for n, k, _ in SHEETS}
    tips = {n: t for n, _, t in SHEETS}
    ids = iter(range(2, 10000))
    drel: list[str] = []
    links: dict[str, str] = {}
    for target in [t for _, items in NAV_SECTIONS for t in items]:
        rid = "rId%d" % (len(drel) + 1)
        drel.append('<Relationship Id="%s" Type="%s" Target="#\'%s\'!A1"/>' % (rid, REL_HYPERLINK, target))
        links[target] = rid
    anchors = [nav_group("NavBarTop", [NAV_SECTIONS[1]], sheet, ids, links, tabs, tips, 0),
               nav_group("NavBar", NAV_SECTIONS[2:] + [NAV_SECTIONS[0]], sheet, ids, links, tabs, tips,
                         frozen_row)]
    for i, (label, macro) in enumerate(BUTTONS.get(sheet, [])):
        anchors.append(button_anchor(ids, label, macro, BUTTON_COL[sheet], 8 + i * 140, 37))
    drawing = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<xdr:wsDr xmlns:xdr="http://schemas.'
               'openxmlformats.org/drawingml/2006/spreadsheetDrawing" xmlns:a="http://schemas.openxmlformats.org/'
               'drawingml/2006/main">%s</xdr:wsDr>') % "".join(anchors)
    return drawing, RELS_EMPTY.replace("</Relationships>", "".join(drel) + "</Relationships>")


def default_font(styles: str) -> str:
    """The first font of styles.xml in Aptos, without a theme scheme, whatever the XML writer's spacing."""
    def aptos(match: re.Match[str]) -> str:
        inner = match.group(1).replace('val="Calibri"', 'val="Aptos"')
        return "<font>" + re.sub(r'<scheme val="minor"\s*/>', "", inner) + "</font>"
    return re.sub(r"<font>(.*?)</font>", aptos, styles, count=1, flags=re.S)


def write_package(path: Path, entries: Mapping[str, bytes]) -> None:
    """Write the parts in the given order with fixed entry dates and attributes."""
    tmp = path.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w") as z:
        for n, data in entries.items():
            info = zipfile.ZipInfo(n, date_time=ENTRY_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0
            info.external_attr = 0
            z.writestr(info, data)
    tmp.replace(path)


def add_drawings(path: Path, frozen_rows: Mapping[str, int]) -> None:
    """Add the navigation drawings, set the default font and normalise the package."""
    with zipfile.ZipFile(path) as z:
        entries = {i.filename: z.read(i.filename) for i in z.infolist()}
    types = entries["[Content_Types].xml"].decode("utf-8")
    for n, (sheet, part) in enumerate(sheet_parts(entries), start=1):
        drawing, drawing_rels = drawing_xml(sheet, frozen_rows[sheet])
        dpart = "xl/drawings/drawing%d.xml" % n
        entries[dpart] = drawing.encode("utf-8")
        entries["xl/drawings/_rels/drawing%d.xml.rels" % n] = drawing_rels.encode("utf-8")
        types = types.replace("</Types>", '<Override PartName="/%s" ContentType="application/vnd.openxmlformats-'
                              'officedocument.drawing+xml"/></Types>' % dpart)
        srels_name = posixpath.join(posixpath.dirname(part), "_rels", posixpath.basename(part) + ".rels")
        srels = entries[srels_name].decode("utf-8") if srels_name in entries else RELS_EMPTY
        srels = srels.replace("</Relationships>", '<Relationship Id="rIdNav" Type="%s" Target="../drawings/'
                              'drawing%d.xml"/></Relationships>' % (REL_DRAWING, n))
        entries[srels_name] = srels.encode("utf-8")
        sx = entries[part].decode("utf-8")
        if 'xmlns:r=' not in sx[:600]:
            sx = sx.replace("<worksheet ", '<worksheet xmlns:r="%s" ' % NS_R, 1)
        m = re.search(r"<legacyDrawing|<tableParts|<extLst|</worksheet>", sx)
        if m is None:
            raise ValueError(part + " has no closing worksheet tag")
        sx = sx[:m.start()] + '<drawing r:id="rIdNav"/>' + sx[m.start():]
        entries[part] = sx.encode("utf-8")
    entries["[Content_Types].xml"] = types.encode("utf-8")
    entries["xl/styles.xml"] = default_font(entries["xl/styles.xml"].decode("utf-8")).encode("utf-8")
    entries["docProps/core.xml"] = CORE_PROPERTIES.encode("utf-8")
    write_package(path, entries)


# ---------------------------------------------------------------- main ----
def build(out: Path = OUT) -> dict[str, int]:
    if LXML:
        raise RuntimeError("openpyxl was imported with lxml before tools/plain_openpyxl.py: the bytes would differ")
    wb = Workbook()
    first = wb.active
    if isinstance(first, Worksheet):
        wb.remove(first)
    wb.code_name = "ThisWorkbook"
    sheets: dict[str, Worksheet] = {}
    for nm, kind, _ in SHEETS:
        ws = wb.create_sheet(nm)
        ws.sheet_properties.codeName = CODE_NAMES[nm]
        ws.sheet_properties.tabColor = "FF" + (TAB_IN if kind == "in" else TAB_OUT if kind == "out" else TAB_HOME)
        ws.sheet_view.showGridLines = False
        sheets[nm] = ws
    build_home(wb, sheets["Home"])
    layout = build_params(wb, sheets["Params"])
    build_input(wb, sheets["HQLA"], "HQLA", spec.HQLA)
    build_input(wb, sheets["Outflows"], "Outflows", spec.OUTFLOWS)
    build_input(wb, sheets["Inflows"], "Inflows", spec.INFLOWS)
    build_results(wb, sheets["Results"])
    build_linecalc(wb, sheets["LineCalc"])
    build_checks(wb, sheets["Checks"])
    build_readme(wb, sheets["README"])
    wb.active = 0
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    frozen: dict[str, int] = {}
    for nm, ws in sheets.items():
        m = re.match(r"([A-Z]+)(\d+)", ws.freeze_panes or "")
        if m is None:
            raise ValueError(nm + " has no frozen panes")
        frozen[nm] = int(m.group(2)) - 1
    add_drawings(out, frozen)
    return layout


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    info = build(target)
    print("written", target, info)
    return 0


if __name__ == "__main__":
    sys.exit(main())
