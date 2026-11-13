#!/usr/bin/env python3
"""Run the prototype workbook's VBA in LibreOffice and compare it with tools/lcr_spec.py.

LibreOffice runs the VBA in its compatibility mode. This is a smoke test of the
VBA logic on a second host: it is NOT evidence that the workbook compiles or
runs in Excel, and lcr_spec.py is not an independent oracle.

Usage: python tools/run_lo_test.py [test-results/K-LCR.xlsm]
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import lcr_spec as spec
from build_xlsm import OUTPUT, office, pv

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "test-results" / "after_run_preview.xlsx"
FIELDS: list[str | None] = ["L1", "L1CB", "L2A", "L2B", "A1", "A1CB", "A2A", "A2B", "Excess", "Buffer",
                            "TO", "FEI", "IHC", "IC", None, "NLO", "LCR"]
COMPARED = [field for field in FIELDS if field is not None]

Row = dict[str, Any]


class Outcome:
    """Prints each expectation and counts the failures."""

    def __init__(self) -> None:
        self.failures: list[str] = []

    def expect(self, label: str, ok: bool, detail: object = "") -> None:
        print(("PASS " if ok else "FAIL ") + label + ("" if ok else "  " + str(detail)))
        if not ok:
            self.failures.append(label)


def call(doc: Any, module: str, proc: str, args: Sequence[object] = ()) -> Any:
    script = doc.getScriptProvider().getScript(
        f"vnd.sun.star.script:VBAProject.{module}.{proc}?language=Basic&location=document")
    result, _, _ = script.invoke(tuple(args), (), ())
    return result


def sheet(doc: Any, name: str) -> Any:
    return doc.Sheets.getByName(name)


def results(doc: Any) -> dict[str, Row]:
    """The Results rows by scope."""
    sh = sheet(doc, "Results")
    rows: dict[str, Row] = {}
    r = 7
    while scope := sh.getCellByPosition(2, r - 1).getString():
        vals: Row = {}
        for i, field in enumerate(FIELDS):
            if field:
                c = sh.getCellByPosition(4 + i, r - 1)
                vals[field] = None if c.getType().value == "EMPTY" else c.getValue()
        vals["Status"] = sh.getCellByPosition(22, r - 1).getString()
        vals["Lines"] = sh.getCellByPosition(3, r - 1).getString()
        vals["Check"] = sh.getCellByPosition(25, r - 1).getString()
        vals["XBuffer"] = sh.getCellByPosition(23, r - 1).getValue()
        vals["XNLO"] = sh.getCellByPosition(24, r - 1).getValue()
        rows[scope] = vals
        r += 1
    return rows


def checks(doc: Any) -> list[tuple[str, ...]]:
    """The Checks rows: severity, sheet, row, reference, message, code."""
    sh = sheet(doc, "Checks")
    out: list[tuple[str, ...]] = []
    r = 6
    while sh.getCellByPosition(2, r - 1).getString():
        out.append(tuple(sh.getCellByPosition(c, r - 1).getString() for c in range(2, 8)))
        r += 1
    return out


def close(got: object, expected: float) -> bool:
    return isinstance(got, float) and abs(got - expected) <= 1e-6 * max(1.0, abs(expected))


def illustrative_run(doc: Any, out: Outcome) -> None:
    """The self-test, then a run of the demonstration data against the Python model."""
    report = call(doc, "TEST_Engine", "SelfTestReport")
    out.expect("engine self-test: " + report.splitlines()[0], report.startswith("PASS"), report)
    print("  summary:", call(doc, "M_Main", "AutomationRun"))
    got = results(doc)
    out.expect("scopes EUR, USD, TOTAL", list(got) == ["EUR", "USD", "TOTAL"], list(got))
    for scope, expected in spec.compute().items():
        g = got.get(scope, {})
        mismatches = 0
        for field in COMPARED:
            rv = expected[field]
            if rv is None or not close(g.get(field), rv):
                mismatches += 1
                out.expect(f"{scope} {field}", False, f"got {g.get(field)}, expected {rv}")
        out.expect(f"{scope}: {len(COMPARED)} values match the Python model (LCR {(g.get('LCR') or 0):.4%})",
                   mismatches == 0)
        out.expect(f"{scope}: formula check {g.get('Check')}", g.get("Check") == "OK",
                   f"X={g.get('XBuffer')} Y={g.get('XNLO')}")
        out.expect(f"{scope}: status VALID", g.get("Status") == "VALID", g.get("Status"))
    lines = sheet(doc, "LineCalc")
    n = len(spec.HQLA) + len(spec.OUTFLOWS) + len(spec.INFLOWS)
    out.expect(f"LineCalc has {n} lines", lines.getCellByPosition(4, 5 + n - 1).getString() != ""
               and lines.getCellByPosition(4, 5 + n).getString() == "")
    found = checks(doc)
    out.expect("no ERROR on the illustrative run", not any(c[0] == "ERROR" for c in found), found)
    report = call(doc, "TEST_Engine", "SelfTestReport")
    out.expect("self-test after run (incl. Results formula check): " + report.splitlines()[0],
               report.startswith("PASS"), report)
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    doc.storeToURL(SNAPSHOT.as_uri(), (pv("FilterName", "Calc MS Excel 2007 XML"),))


def rejected_lines(doc: Any, out: Outcome) -> None:
    """Invalid category, duplicate identifier, text amount and unknown currency."""
    hq = sheet(doc, "HQLA")
    hq.getCellRangeByName("C21").setString("H099")
    hq.getCellRangeByName("D21").setString("Bad category")
    hq.getCellRangeByName("E21").setString("OUT_FIN")
    hq.getCellRangeByName("F21").setString("EUR")
    hq.getCellRangeByName("G21").setValue(1000)
    of = sheet(doc, "Outflows")
    of.getCellRangeByName("C26").setString("O001")
    of.getCellRangeByName("E26").setString("OUT_RET_OTHER")
    of.getCellRangeByName("F26").setString("EUR")
    of.getCellRangeByName("G26").setString("1000")
    inf = sheet(doc, "Inflows")
    inf.getCellRangeByName("C14").setString("I099")
    inf.getCellRangeByName("E14").setString("IN_FIN")
    inf.getCellRangeByName("F14").setString("SEK")
    inf.getCellRangeByName("G14").setValue(500)
    print("  summary:", call(doc, "M_Main", "AutomationRun"))
    got = results(doc)
    codes = sorted({c[5] for c in checks(doc) if c[0] == "ERROR"})
    out.expect("errors LCR-L002, L004, L005, L006 reported",
               {"LCR-L002", "LCR-L004", "LCR-L005", "LCR-L006"} <= set(codes), codes)
    out.expect("EUR withheld (INCOMPLETE)", got["EUR"]["Status"].startswith("INCOMPLETE: 2 of"),
               got["EUR"]["Status"])
    out.expect("EUR LCR blank when withheld", got["EUR"]["LCR"] is None, got["EUR"]["LCR"])
    out.expect("USD unaffected (VALID)", got["USD"]["Status"] == "VALID", got["USD"]["Status"])
    out.expect("TOTAL withheld, 3 rejected", got["TOTAL"]["Status"].startswith("INCOMPLETE: 3 of"),
               got["TOTAL"]["Status"])
    out.expect("formula check n/a when withheld", got["EUR"]["Check"] == "n/a", got["EUR"]["Check"])


def validate_and_stop(doc: Any, out: Outcome) -> None:
    """Validate only leaves Results alone; a parameter error stops the run."""
    before = sheet(doc, "Results").getCellRangeByName("C5").getString()
    summary = call(doc, "M_Main", "AutomationValidate")
    print("  summary:", summary)
    out.expect("validate leaves Results unchanged",
               sheet(doc, "Results").getCellRangeByName("C5").getString() == before)
    out.expect("validate reports 4 errors", " 4 error(s)" in summary, summary)
    sheet(doc, "Params").getCellRangeByName("E7").setString("XXX")
    summary = call(doc, "M_Main", "AutomationRun")
    print("  summary:", summary)
    out.expect("unknown reporting ccy stops the run", summary.startswith("Run stopped"), summary)
    out.expect("Results empty after a stopped run",
               sheet(doc, "Results").getCellRangeByName("C7").getString() == "")


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    xlsm = Path(args[0]) if args else OUTPUT
    out = Outcome()
    with tempfile.TemporaryDirectory(prefix="klcr-test-") as scratch, office() as ctx:
        work = Path(scratch) / "K-LCR.xlsm"
        shutil.copyfile(xlsm, work)
        desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.loadComponentFromURL(work.as_uri(), "_blank", 0,
                                           (pv("Hidden", True), pv("MacroExecutionMode", 4)))
        illustrative_run(doc, out)
        rejected_lines(doc, out)
        validate_and_stop(doc, out)
        doc.close(True)
    print(f"\n{'FAIL' if out.failures else 'PASS'}: {len(out.failures)} failure(s)")
    return 1 if out.failures else 0


if __name__ == "__main__":
    sys.exit(main())
