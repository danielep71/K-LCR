#!/usr/bin/env python3
"""Build the prototype's macro-enabled workbook from the template and the exported VBA.

1. LibreOffice (headless, UNO) loads the template, switches the document to
   VBA compatibility mode, inserts every .bas module of src/ and tests/modules/ and
   the document modules (ThisWorkbook, sh*), and saves a scratch .xlsm;
   its xl/vbaProject.bin carries the VBA source (Excel compiles it on the
   first open).
2. That vbaProject.bin is injected into a byte copy of the template, so that
   every format of the template is kept exactly; the package is switched to
   the macro-enabled content type.

The workbook is written under the ignored test-results/ by default; it is
never source. LibreOffice is an optional build host: a workbook it produced
is not evidence that the VBA compiles or runs in Excel.

Usage: python tools/build_xlsm.py [template.xlsx] [output.xlsm]
"""

from __future__ import annotations

import importlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "src" / "workbook" / "LCR_Template.xlsx"
OUTPUT = ROOT / "test-results" / "K-LCR.xlsm"
PORT = 2002
FILTER_XLSM = "Calc MS Excel 2007 VBA XML"
MAIN_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"
MACRO_TYPE = "application/vnd.ms-excel.sheet.macroEnabled.main+xml"
BIN_DEFAULT = '<Default Extension="bin" ContentType="application/vnd.ms-office.vbaProject"/>'
VBA_RELATIONSHIP = ('<Relationship Id="rIdVBA" Type="http://schemas.microsoft.com/office/2006/relationships/'
                    'vbaProject" Target="vbaProject.bin"/>')


def modules(root: Path = ROOT) -> list[Path]:
    """The standard modules: every .bas of src/ and the self-test of tests/modules/, in a fixed order.

    The neutral harness of tests/unit/ is not part of the prototype workbook.
    """
    return sorted((root / "src").rglob("*.bas")) + sorted((root / "tests" / "modules").glob("*.bas"))


def documents(root: Path = ROOT) -> list[Path]:
    """The document modules (ThisWorkbook and the sheets)."""
    return sorted((root / "src" / "workbook").glob("*.cls"))


def source_body(path: Path) -> tuple[str, str]:
    """Module name and code without the export header and Attribute lines."""
    text = path.read_text(encoding="cp1252")
    found = re.search(r'Attribute VB_Name = "([^"]+)"', text)
    if found is None:
        raise ValueError(f"{path}: no Attribute VB_Name")
    lines = text.splitlines()
    if lines and lines[0].startswith("VERSION 1.0 CLASS"):
        lines = lines[lines.index("END") + 1:]
    body = [line for line in lines if not line.startswith("Attribute VB_")]
    return found.group(1), "\n".join(body).strip("\n") + "\n"


def uno_module() -> Any:
    """LibreOffice's Python bridge; it exists only in the Python that LibreOffice ships with."""
    return importlib.import_module("uno")


def connect() -> Any:
    """The component context of the LibreOffice listening on PORT."""
    uno = uno_module()
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    for _ in range(60):
        try:
            return resolver.resolve(f"uno:socket,host=localhost,port={PORT};urp;StarOffice.ComponentContext")
        except Exception:  # noqa: BLE001 - the bridge raises its own exception types while LibreOffice starts
            time.sleep(0.5)
    raise RuntimeError("LibreOffice did not start")


def pv(name: str, value: object) -> Any:
    """A com.sun.star.beans.PropertyValue."""
    prop = uno_module().createUnoStruct("com.sun.star.beans.PropertyValue")
    prop.Name, prop.Value = name, value
    return prop


@contextmanager
def office() -> Iterator[Any]:
    """A headless LibreOffice with a throw-away profile; yields its component context."""
    with tempfile.TemporaryDirectory(prefix="lo-profile-") as profile:
        proc = subprocess.Popen(["soffice", "--headless", "--norestore", "--nologo",
                                 "-env:UserInstallation=" + Path(profile).as_uri(),
                                 f"--accept=socket,host=localhost,port={PORT};urp;"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            yield connect()
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                proc.kill()


HELPER = """
Function InsertDocModule(oDoc As Object, sName As String, sCode As String) As String
    Dim oLib As Object
    Dim oProv As Object
    Dim oInfo As New com.sun.star.script.ModuleInfo
    oLib = oDoc.BasicLibraries.getByName("VBAProject")
    oProv = oDoc.createInstance("ooo.vba.VBAObjectModuleObjectProvider")
    oInfo.ModuleType = com.sun.star.script.ModuleType.DOCUMENT
    If oProv.hasByName(sName) Then oInfo.ModuleObject = oProv.getByName(sName)
    If oLib.hasModuleInfo(sName) Then oLib.removeModuleInfo(sName)
    oLib.insertModuleInfo(sName, oInfo)
    If oLib.hasByName(sName) Then
        oLib.replaceByName(sName, sCode)
    Else
        oLib.insertByName(sName, sCode)
    End If
    InsertDocModule = sName & IIf(oProv.hasByName(sName), " bound", " UNBOUND")
End Function
"""


def basic_helper(ctx: Any) -> Any:
    """The InsertDocModule helper, installed in the throw-away profile's application library."""
    smgr = ctx.ServiceManager
    container = smgr.createInstanceWithContext("com.sun.star.script.ApplicationScriptLibraryContainer", ctx)
    if not container.hasByName("KLcrBuild"):
        container.createLibrary("KLcrBuild")
    container.loadLibrary("KLcrBuild")
    lib = container.getByName("KLcrBuild")
    if lib.hasByName("Builder"):
        lib.replaceByName("Builder", HELPER)
    else:
        lib.insertByName("Builder", HELPER)
    factory = smgr.createInstanceWithContext("com.sun.star.script.provider.MasterScriptProviderFactory", ctx)
    provider = factory.createScriptProvider("")
    return provider.getScript(
        "vnd.sun.star.script:KLcrBuild.Builder.InsertDocModule?language=Basic&location=application")


def insert_modules(ctx: Any, doc: Any, root: Path) -> None:
    """Every document module through the Basic helper, then every standard module."""
    uno = uno_module()
    libs = doc.BasicLibraries
    libs.VBACompatibilityMode = True
    libs.ProjectName = "VBAProject"
    # PROJECTCODEPAGE 1252 (RTL_TEXTENCODING_MS_1252 = 1), as the VBE writes on
    # Western-European hosts; otherwise LibreOffice writes the thread encoding
    # of the build machine.
    uno.invoke(libs, "setPropertyValue", ("VBATextEncoding", uno.Any("short", 1)))
    lib = libs.getByName("VBAProject") if libs.hasByName("VBAProject") else libs.createLibrary("VBAProject")
    # Document modules go through a Basic helper: LibreOffice writes VB_Base
    # 00020819 (Workbook) only when ModuleInfo.ModuleObject is the VBA workbook
    # object, which the Python bridge cannot carry.
    helper = basic_helper(ctx)
    for path in documents(root):
        name, body = source_body(path)
        helper.invoke((doc, name, "Option VBASupport 1\n" + body), (), ())
    existing = set(lib.getElementNames())
    normal = uno.getConstantByName("com.sun.star.script.ModuleType.NORMAL")
    for path in modules(root):
        name, body = source_body(path)
        code = "Option VBASupport 1\n" + body
        if name in existing:
            lib.replaceByName(name, code)
            continue
        info = uno.createUnoStruct("com.sun.star.script.ModuleInfo")
        info.ModuleType = normal
        if not lib.hasModuleInfo(name):
            lib.insertModuleInfo(name, info)
        lib.insertByName(name, code)


def vba_project(template: Path, root: Path = ROOT) -> bytes:
    """The xl/vbaProject.bin that LibreOffice writes for the template and the source."""
    with office() as ctx, tempfile.TemporaryDirectory(prefix="klcr-build-") as scratch:
        desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        work = Path(scratch) / template.name  # keeps LibreOffice lock files out of src/
        shutil.copyfile(template, work)
        doc = desktop.loadComponentFromURL(work.as_uri(), "_blank", 0, (pv("Hidden", True),))
        if doc is None:
            raise RuntimeError(f"LibreOffice could not load {template}")
        insert_modules(ctx, doc, root)
        saved = Path(scratch) / "scratch.xlsm"
        doc.storeToURL(saved.as_uri(), (pv("FilterName", FILTER_XLSM),))
        doc.close(True)
        with zipfile.ZipFile(saved) as z:
            return z.read("xl/vbaProject.bin")


def macro_enabled(name: str, data: bytes) -> bytes:
    """One part of the template, changed as a macro-enabled package needs."""
    if name == "[Content_Types].xml":
        text = data.decode("utf-8").replace(MAIN_TYPE, MACRO_TYPE)
        if 'Extension="bin"' not in text:
            text = text.replace("<Default ", BIN_DEFAULT + "<Default ", 1)
        return text.encode("utf-8")
    if name == "xl/_rels/workbook.xml.rels":
        return data.decode("utf-8").replace("</Relationships>", VBA_RELATIONSHIP + "</Relationships>").encode("utf-8")
    return data


def inject(template: Path, bin_data: bytes, output: Path) -> None:
    """Copy the template part by part into output, with the VBA project added."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(template) as zin, zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            zout.writestr(info, macro_enabled(info.filename, zin.read(info.filename)))
        zout.writestr("xl/vbaProject.bin", bin_data)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    template = Path(args[0]) if args else TEMPLATE
    output = Path(args[1]) if len(args) > 1 else OUTPUT
    data = vba_project(template)
    inject(template, data, output)
    print("written", output, "vbaProject.bin", len(data), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
