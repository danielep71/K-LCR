"""Valid and invalid fixtures for the VBA static checks (tools/check_vba_*.py).

Each fixture is a throw-away Git repository holding synthetic VBA components,
written with CRLF as the VBE exports them and staged under this repository's
.gitattributes. The components are fixtures for the checks only: no LCR
calculation or regulatory value is implied by them.
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from collections.abc import Callable, Iterator, Mapping
from pathlib import Path
from typing import Any

import check_vba_conditionals
import check_vba_dynamic
import check_vba_jumps
from vba_lexer import Finding, logical_units, split_statements, strip_code

ROOT = Path(__file__).resolve().parents[1]
CORE = "src/core/LCR_Core_Fixture.bas"
API = "src/api/LCR_API_Fixture.bas"
ADAPTER = "src/host/excel/LCR_Excel_Fixture.bas"
HOST_TEST = "tests/host/TEST_LCR_Excel_Fixture.bas"
UNIT = "tests/unit/TEST_LCR_Fixture.bas"
EXCEPTIONS = check_vba_dynamic.EXCEPTIONS
OUTSIDE = "not allowed outside src/host/excel/ and tests/host/"


def exceptions(*entries: Any) -> str:
    return json.dumps({"schema": "klcr-vba-exceptions", "version": 1,
                       "exceptions": list(entries)}, indent=2) + "\n"


def exception(path: str = ADAPTER, procedure: str | None = "Work", construct: str = "CreateObject",
              target: str | None = "Shell.Application", **extra: Any) -> dict[str, Any]:
    return {"path": path, "procedure": procedure, "construct": construct, "target": target,
            "issue": 12, "reason": "Opens the output folder for the user.",
            "reviewed_by": "danielep71", "date": "2026-11-04", **extra}


@contextlib.contextmanager
def repository(files: Mapping[str, str | bytes]) -> Iterator[Path]:
    """A Git repository holding ``files``: VBA written with CRLF, then staged."""
    with tempfile.TemporaryDirectory(prefix="vba-check-") as temporary:
        root = Path(temporary)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        shutil.copyfile(ROOT / ".gitattributes", root / ".gitattributes")
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                data = content
            elif relative.endswith((".bas", ".cls", ".frm")):
                data = content.replace("\n", "\r\n").encode("ascii")
            else:
                data = content.encode("utf-8")
            path.write_bytes(data)
        subprocess.run(["git", "-C", str(root), "-c", "core.autocrlf=false", "-c",
                        "core.safecrlf=false", "add", "--all"], check=True)
        yield root


def run_check(check: Callable[[Path], tuple[list[Finding], *tuple[int, ...]]],
              files: Mapping[str, str | bytes]) -> list[str]:
    with repository(files) as root:
        return [str(finding) for finding in check(root)[0]]


def module(body: str, name: str = "TEST_LCR_Fixture") -> str:
    return f'Attribute VB_Name = "{name}"\nOption Explicit\nOption Private Module\n{body}'


def files_at(path: str, body: str, *entries: Mapping[str, Any]) -> dict[str, str | bytes]:
    """One component at ``path`` holding ``body``, plus the exceptions file."""
    return {path: module(body, Path(path).stem), EXCEPTIONS: exceptions(*entries)}


def standalone(body: str) -> dict[str, str | bytes]:
    return files_at(UNIT, body)


def in_procedure(body: str) -> str:
    return f"Public Sub Work()\n{body}\nEnd Sub\n"


class LexerTest(unittest.TestCase):
    def test_comments_end_the_code(self) -> None:
        cases = {
            "x = 1 ' note": "x = 1",
            "Rem whole line": "",
            "  Rem": "",
            "Debug.Print 1: Rem GoTo Missing": "Debug.Print 1:",
            'Debug.Print "a: Rem b"': 'Debug.Print "a: Rem b"',
            "Call Work(Remainder:=1)": "Call Work(Remainder:=1)",
            "Report Name:= Rem": "Report Name:= Rem",
            "Remove 1": "Remove 1",
            "100 Rem GoTo Missing": "100",
            "  10 x = 1 ' note": "  10 x = 1",
            "10: Rem note": "10:",
            "x = ['Sheet 1'!A1] ' note": "x = ['Sheet 1'!A1]",
            "x = 1: Remark = 2": "x = 1: Remark = 2",
            '"it\'s": GoTo Label': '"it\'s": GoTo Label',
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(strip_code(raw), expected)
        self.assertEqual(strip_code('Debug.Print "GoTo x": GoTo y', blank_strings=True),
                         "Debug.Print         : GoTo y")
        self.assertEqual(strip_code("x = ['GoTo z'!A1]: GoTo y", blank_strings=True),
                         "x = [" + " " * len("'GoTo z'!A1") + "]: GoTo y")

    def test_continuations_join_and_continued_comments_stay_comment(self) -> None:
        lines = ["x = 1 ' note _", "  GoTo Missing _", "  MsgBox 1", "y = 2", "' plain _"]
        self.assertEqual(logical_units(lines), [(1, 3, "code", "x = 1"), (4, 4, "code", "y = 2"),
                                                (5, 5, "code", "")])
        self.assertEqual(logical_units(["x = 1 + _", "  2"]), [(1, 2, "code", "x = 1 + 2")])
        self.assertEqual(logical_units(["#If VBA7 Then", "x = 1"]),
                         [(1, 1, "directive", "#If VBA7 Then"), (2, 2, "code", "x = 1")])

    def test_colon_separated_statements(self) -> None:
        cases = {
            "x = 1: y = 2": ["x = 1", "y = 2"],
            'Debug.Print "a:b": y = 2': ['Debug.Print "a:b"', "y = 2"],
            "Work Value:=1: y = 2": ["Work Value:=1", "y = 2"],
            "x = [A1:B2]: y = 2": ["x = [A1:B2]", "y = 2"],
            "x = #12:30:00 PM#: y = 2": ["x = #12:30:00 PM#", "y = 2"],
            "Print #1, x: y = 2": ["Print #1, x", "y = 2"],
            'Print #1, "#": y = 2': ['Print #1, "#"', "y = 2"],
            "Print #1, x: Print #2, y": ["Print #1, x", "Print #2, y"],
            "Close #f: y = 2": ["Close #f", "y = 2"],
            "Close #1, #2: y = #1/2/2026#": ["Close #1, #2", "y = #1/2/2026#"],
            'Open p For Output As #1 Len = 5: y = "#"': ["Open p For Output As #1 Len = 5",
                                                         'y = "#"'],
            "x = #January 1, 2026#: y = 2": ["x = #January 1, 2026#", "y = 2"],
            "x = Total#: y = 2": ["x = Total#", "y = 2"],
            "x = 1: Rem y = 2": ["x = 1"],
        }
        for code, expected in cases.items():
            with self.subTest(code=code):
                self.assertEqual(split_statements(code), expected)


CONDITIONAL_VALID = {
    "nested": '''#If VBA7 Then
    #If Win64 Then
        Private Declare PtrSafe Function F64 Lib "kernel32" () As LongPtr
    #ElseIf Win32 Then
        Private Declare PtrSafe Function F32 Lib "kernel32" () As Long
    #End If
#Else
    Private Declare Function FLegacy Lib "kernel32" () As Long
#End If
''',
    "inactive-legacy": '''#If Not VBA7 Then
    #If Win64 Then
        Private Declare Function Impossible Lib "kernel32" () As Long
    #End If
#End If
''',
    "boolean-expression": '''#If Not VBA7 Then
    Private Declare Function Legacy Lib "kernel32" () As Long
#ElseIf VBA7 And (Win64 Or Win32) Then
    Private Declare PtrSafe Function Modern Lib "kernel32" () As LongPtr
#End If
''',
    "continued-declare": '''#If VBA7 Then
    Private Declare PtrSafe Function Modern Lib "kernel32" _
        () As LongPtr
#Else
    Private Declare Function Legacy Lib "kernel32" _
        () As Long
#End If
''',
    "colon-separated-declares": '''#If VBA7 Then
    Private Const N As Long = 1: Private Declare PtrSafe Function B Lib "kernel32" () As LongPtr
#Else
    Private Const N As Long = 1: Private Declare Function B Lib "kernel32" () As Long
#End If
''',
    "literals": '''#If VBA7 And Not 0 And True Then
    Private Declare PtrSafe Function Modern Lib "kernel32" () As LongPtr
#End If
''',
    "keywords-in-comments-and-strings": '''#If VBA7 Then
    ' Private Declare Function Commented Lib "kernel32" () As Long
#End If
Private Const TEXT As String = "Declare Function Quoted Lib ""kernel32"" () As LongPtr"
''',
    "type-and-enum": '''Private Type Pair
    Low As Double
    High As Double
End Type

Private Enum Slot
    slFirst = 0
End Enum
''',
}
CONDITIONAL_INVALID = {
    "declare-without-ptrsafe": ('''#If VBA7 And Win64 Then
    Private Declare Function Bad Lib "kernel32" () As Long
#End If
''', "without PtrSafe in vba7-win64"),
    "unconditional-declare": ('Private Declare Function Bad Lib "kernel32" () As Long\n',
                              "without PtrSafe in vba7-win32, vba7-win64"),
    "unconditional-ptrsafe": ('Private Declare PtrSafe Function Bad Lib "kernel32" () As Long\n',
                              "Declare with PtrSafe reachable under VBA6 in vba6-win32"),
    "longptr-under-win32": ('''#If Win32 Then
    Private Declare PtrSafe Function Bad Lib "kernel32" () As LongPtr
#End If
''', "reachable under VBA6 in vba6-win32"),
    "win32-is-true-on-win64": ('''#If Win32 Then
    Private Declare Function WrongOrder Lib "kernel32" () As Long
#ElseIf Win64 Then
    Private Declare PtrSafe Function NeverReached Lib "kernel32" () As LongPtr
#End If
''', "vba7-win64"),
    "colon-separated-declare": ('Private Const N As Long = 1: Private Declare Function B Lib "kernel32" '
                                '() As Long\n', "without PtrSafe in vba7-win32, vba7-win64"),
    "vba6-is-true-under-vba7": ('''#If VBA6 Then
    Private Declare Function Legacy Lib "kernel32" () As Long
#End If
''', "without PtrSafe in vba7-win32, vba7-win64"),
    "unknown-symbol": ("#If Mac Then\n#End If\n", "unsupported conditional-compilation symbol"),
    "integer-literal": ("#If 2 Then\n#End If\n", "-1 and 0"),
    "missing-then": ("#If VBA7\n#End If\n", "must end with Then"),
    "project-const": ("#Const FEATURE = True\n", "project #Const"),
    "unclosed": ("#If VBA7 Then\n", "not closed"),
    "stray-elseif": ("#ElseIf VBA7 Then\n", "#ElseIf without #If"),
    "elseif-after-else": ("#If VBA7 Then\n#Else\n#ElseIf Win64 Then\n#End If\n",
                          "#ElseIf after #Else"),
    "duplicate-else": ("#If VBA7 Then\n#Else\n#Else\n#End If\n", "duplicate #Else"),
    "stray-end-if": ("#End If\n", "#End If without #If"),
    "unsupported-directive": ("#Region Main\n", "unsupported conditional-compilation directive"),
}


class ConditionalTest(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for name, body in CONDITIONAL_VALID.items():
            with self.subTest(name=name):
                self.assertEqual(run_check(check_vba_conditionals.check, standalone(body)), [])

    def test_invalid_fixtures_fail(self) -> None:
        for name, (body, text) in CONDITIONAL_INVALID.items():
            with self.subTest(name=name):
                findings = run_check(check_vba_conditionals.check, standalone(body))
                self.assertTrue(any(text in item for item in findings), findings)

    def test_findings_name_file_and_line(self) -> None:
        findings = run_check(check_vba_conditionals.check, standalone(
            "\n" + CONDITIONAL_INVALID["declare-without-ptrsafe"][0]))
        self.assertEqual(findings, [f"{UNIT}:6: Declare reachable under VBA7 without PtrSafe in "
                                    "vba7-win64"])

    def test_reachable_sources_blank_inactive_lines(self) -> None:
        sources, findings = check_vba_conditionals.reachable_sources(
            "x.bas", "A\n#If VBA7 Then\nB\n#ElseIf Win64 Then\nC\n#Else\nD\n#End If")
        self.assertEqual(findings, [])
        self.assertEqual(sources["vba7-win64"].split("\n"), ["A", "", "B", "", "", "", "", ""])
        self.assertEqual(sources["vba7-win32"].split("\n"), ["A", "", "B", "", "", "", "", ""])
        self.assertEqual(sources["vba6-win32"].split("\n"), ["A", "", "", "", "", "", "D", ""])


JUMPS_VALID = {
    "handler-and-cleanup": '''Public Sub First(ByVal Value As Long)
        On Error GoTo Fail
        If Value < 0 Then GoTo Cleanup
        Debug.Print Value
Cleanup:
        Exit Sub
Fail:
        Resume Cleanup
End Sub
''',
    "same-handler-twice": '''Public Sub First()
        On Error GoTo Fail
        Debug.Print 1
        On Error GoTo Fail
        Exit Sub
Fail:
        Resume Next
End Sub
''',
    # Resume 0 is VBA's spelling of Resume: it names no label.
    "resume-zero": '''Public Sub First()
        On Error GoTo Fail
        Exit Sub
Fail:
        Resume 0
End Sub
''',
    "same-label-in-two-procedures": '''Private Sub First()
        GoTo Shared
Shared:
End Sub

Private Sub Second()
        GoTo Shared
Shared:
End Sub
''',
    "continued-comment": '''Private Sub First()
        ' A comment that continues _
          GoSub Missing
        Exit Sub
End Sub
''',
    "numbered-label": '''Private Sub First()
        GoTo 100
100     Exit Sub
End Sub
''',
    "special-error-controls": '''Private Sub First()
        On Error GoTo 0
        On Error Resume Next
        Resume Next
End Sub
''',
    "quoted-jump-text": '''Private Sub First()
        Debug.Print "GoSub Missing", "On Error GoTo -1", "Resume Nowhere"
        Debug.Print "He said ""GoSub Missing""; it's text"
        Debug.Print "GoSub Missing" & _
            "Resume Lost"
        Debug.Print "GoSub Missing": GoTo Done
Done:
End Sub
''',
    "keyword-before-colon": '''Private Sub First(ByVal Flag As Boolean)
        If Flag Then
            Debug.Print 1
        Else: Debug.Print 2
        End If
End Sub
''',
    "rem-after-separator": '''Private Sub First()
        Debug.Print 1: Rem GoTo Missing
        Debug.Print 2:Rem GoSub Lost
End Sub
''',
    "one-line-procedure": '''Private Sub First(): Debug.Print 1: End Sub

Private Sub Second(): Debug.Print 2: End Sub
''',
    "numbered-comment-lines-as-targets": '''Private Sub First()
        GoTo 100
100 Rem target
End Sub

Private Sub Second()
        GoTo 200
200 ' target
End Sub
''',
    "bracketed-sheet-name": '''Private Sub First()
        Debug.Print ['GoSub Missing'!A1], [A1:B2]: GoTo Done
Done:
End Sub
''',
    "colons-in-a-date-literal": '''Private Sub First()
        Debug.Print #12:30:00 PM#: GoTo Done
Done:
End Sub
''',
    "exclusive-branches": '''Private Sub First()
#If VBA7 Then
        GoTo Modern
Modern:
#Else
        GoTo Legacy
Legacy:
#End If
End Sub
''',
    "member-calls-named-like-jumps": '''Private Sub First(ByVal Target As Object)
        Target.Goto Reference:="R1C1", Scroll:=True
        With Target
            .GoTo "R1C1"
            .GoSub
        End With
End Sub
''',
    "type-and-enum": '''Private Type Pair
    Low As Double
    High As Double
End Type

Private Enum Slot
    slFirst = 0
End Enum

Private Sub First()
        GoTo Done
Done:
End Sub
''',
}
JUMPS_INVALID = {
    "cross-procedure": ('''Private Sub First()
        GoTo Shared
End Sub

Private Sub Second()
Shared:
        Exit Sub
End Sub
''', "GoTo target 'Shared' is not a label of procedure First"),
    "duplicate-label": ('''Private Sub First()
Again:
Again:
        Exit Sub
End Sub
''', "duplicate label 'Again' in procedure First; first defined at line"),
    "jump-after-string": ('''Private Sub First()
        Debug.Print "it's ""quoted""": GoTo Missing
End Sub
''', "GoTo target 'Missing'"),
    "resume-to-missing-label": ('''Private Sub First()
        On Error GoTo Fail
        Exit Sub
Fail:
        Resume Retry
End Sub
''', "Resume target 'Retry'"),
    "handler-missing": ("Private Sub First()\n        On Error GoTo Fail\nEnd Sub\n",
                        "On Error GoTo target 'Fail'"),
    "label-in-other-branch": ('''Private Sub First()
#If VBA7 Then
        GoTo Legacy
#Else
Legacy:
#End If
End Sub
''', "[vba7-win32, vba7-win64]"),
    "procedure-not-closed": ("Private Sub First()\n        Exit Sub\n", "is not closed"),
    "procedure-opened-twice": ("Private Sub First()\nPrivate Sub Second()\nEnd Sub\n",
                               "is not closed before Second"),
    "stray-end": ("End Sub\n", "End statement outside any procedure"),
    "jump-outside-procedure": ("GoTo Lost\n", "jump statement outside any procedure"),
    "jump-after-bracketed-sheet-name": ("Private Sub First()\n"
                                        "        Debug.Print ['Sheet 1'!A1]: GoTo Lost\nEnd Sub\n",
                                        "GoTo target 'Lost'"),
    "one-line-procedure-missing-label": ("Private Sub First(): GoTo Lost: End Sub\n",
                                         "GoTo target 'Lost'"),
    "jump-after-member-call": ("Private Sub First(ByVal Target As Object)\n"
                               "        Target.Goto Reference:=\"R1C1\": GoTo Lost\nEnd Sub\n",
                               "GoTo target 'Lost'"),
    "gosub": ('''Private Sub First()
        GoSub Worker
        Exit Sub
Worker:
        Return
End Sub
''', "GoSub is not allowed"),
    "gosub-after-colon": ('''Private Sub First()
        Debug.Print "x": GoSub Worker
Worker:
End Sub
''', "GoSub is not allowed"),
    "continued-gosub": ('''Private Sub First()
        GoSub _
            Worker
Worker:
End Sub
''', "GoSub is not allowed"),
    "computed-goto": ('''Private Sub First(ByVal Choice As Long)
        On Choice GoTo One, Two
One:
Two:
End Sub
''', "On <expression> GoTo is a computed jump"),
    "computed-gosub": ('''Private Sub First(ByVal Choice As Long)
        On Choice GoSub One
One:
End Sub
''', "On <expression> GoSub is a computed jump"),
    "on-error-goto-minus-one": ('''Private Sub First()
        On Error Resume Next
        On Error GoTo -1
End Sub
''', "On Error GoTo -1 is not allowed"),
    "two-handlers": ('''Private Sub First()
        On Error GoTo FailOne
        On Error GoTo FailTwo
        Exit Sub
FailOne:
FailTwo:
End Sub
''', "more than one On Error GoTo handler label"),
    "two-cleanup-labels": ('''Private Sub First(ByVal Flag As Boolean)
        If Flag Then GoTo One
        GoTo Two
One:
Two:
End Sub
''', "jumps to more than one label besides its error handler"),
    "backward-goto": ('''Private Sub First()
Again:
        Debug.Print 1
        GoTo Again
End Sub
''', "GoTo Again jumps backward in procedure First"),
    "same-line-loop": ("Private Sub First()\nAgain: GoTo Again\nEnd Sub\n",
                       "GoTo Again jumps backward"),
}


class JumpTest(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for name, body in JUMPS_VALID.items():
            with self.subTest(name=name):
                self.assertEqual(run_check(check_vba_jumps.check, standalone(body)), [])

    def test_invalid_fixtures_fail(self) -> None:
        for name, (body, text) in JUMPS_INVALID.items():
            with self.subTest(name=name):
                findings = run_check(check_vba_jumps.check, standalone(body))
                self.assertTrue(any(text in item for item in findings), findings)

    def test_findings_name_file_line_and_environments(self) -> None:
        findings = run_check(check_vba_jumps.check, standalone(JUMPS_INVALID["gosub"][0]))
        self.assertEqual(findings, [f"{UNIT}:5: GoSub is not allowed "
                                    "[vba6-win32, vba7-win32, vba7-win64]"])

    def test_counts_procedures(self) -> None:
        with repository(standalone(JUMPS_VALID["same-label-in-two-procedures"])) as root:
            _, components, procedures = check_vba_jumps.check(root)
        self.assertEqual((components, procedures), (1, 2))


CLASS = '''VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "LCR_Core_Book"
Attribute VB_PredeclaredId = False
Option Explicit
'''
HOST_BODY = '''#If VBA7 Then
Private Declare PtrSafe Function GetTickCount Lib "kernel32" () As Long
#Else
Private Declare Function GetTickCount Lib "kernel32" () As Long
#End If

Public Sub Work()
        Dim Shell As Object
        Set Shell = CreateObject("Shell.Application")
        CreateObject "Shell.Application"
        Set Shell = VBA.Interaction.CreateObject( "Shell.Application" )
        Application.Run "LCR_Excel_Fixture.Refresh"
        Dim Seen As Object
        Set Seen = New Scripting.Dictionary
End Sub
'''
HOST_EXCEPTIONS = (exception(), exception(procedure=None, construct="Declare", target="GetTickCount"),
                   exception(construct="Run", target=None),
                   exception(construct="New", target="scripting.dictionary"))
DYNAMIC_VALID: dict[str, dict[str, str | bytes]] = {
    "pure-core": {**files_at(CORE, '''Private Enum Field
    [_First] = 0
    Run = 1
    Evaluate = 2
End Enum

Private Type Quote
    OnTime As Boolean
    [New] As Double
End Type

Public Function Count(ByVal Items As Collection) As Long
        ' CreateObject("Scripting.Dictionary"), Application.Run and [A1] in a comment
        ' continue _
          Set Items = CreateObject("Word.Application")
        Dim Book As LCR_Core_Book
        Set Book = New LCR_Core_Book
        Dim Seen As New Collection
        Set Items = New VBA.Collection
        Debug.Print "CreateObject(""Excel.Application""), GetObject, New Dictionary, [A1]"
        Debug.Print "Application.Run": Debug.Print "CallByName"
        Dim RunDate As Date, Evaluated As Boolean, Renewal As Long, CreateObjects As Long
        Count = Items.Count + RunDate + Renewal
End Function
'''), "src/core/LCR_Core_Book.cls": CLASS},
    "host-adapter-with-reviewed-exceptions": files_at(ADAPTER, HOST_BODY, *HOST_EXCEPTIONS),
    "host-test-with-reviewed-exception": files_at(HOST_TEST, in_procedure(
        '        Debug.Print GetObject(, "Excel.Application").Name'),
        exception(path=HOST_TEST, construct="GetObject", target=None)),
    "procedure-names-ignore-case": files_at(ADAPTER, in_procedure(
        '        Set Shell = CreateObject("shell.application")'), exception(procedure="WORK")),
}


def core_use(body: str) -> dict[str, str | bytes]:
    return files_at(CORE, in_procedure(body))


DYNAMIC_INVALID: dict[str, tuple[dict[str, str | bytes], str]] = {
    "core-declare": (files_at(CORE, '#If VBA7 Then\nPrivate Declare PtrSafe Function GetTickCount '
                                    'Lib "kernel32" () As Long\n#End If\n'),
                     f"Declare GetTickCount (module level): {OUTSIDE}"),
    "create-object-parentheses": (core_use('        Set D = CreateObject("Scripting.Dictionary")'),
                                  f"CreateObject Scripting.Dictionary (procedure Work): {OUTSIDE}"),
    "create-object-spaces": (core_use('        Set D = CreateObject( "Scripting.Dictionary" )'),
                             "CreateObject Scripting.Dictionary"),
    "create-object-statement": (core_use('        CreateObject "Scripting.Dictionary"'),
                                "CreateObject Scripting.Dictionary"),
    "create-object-call": (core_use('        Call CreateObject("Word.Application")'),
                           "CreateObject Word.Application"),
    "create-object-qualified": (core_use('        VBA.Interaction.CreateObject "Word.Application"'),
                                "CreateObject Word.Application"),
    "create-object-variable": (core_use("        Set D = CreateObject(ProgId)"),
                               f"CreateObject (procedure Work): {OUTSIDE}"),
    "create-object-after-colon": (core_use('        X = 1: Set D = CreateObject("A.B")'),
                                  "CreateObject A.B"),
    "run-after-file-output-with-a-quoted-hash": (core_use(
        '        Print #1, "#": Application.Run "Unsafe"'), "Run (procedure Work)"),
    "run-after-a-file-statement-and-a-string": (core_use(
        '        Close #1: Debug.Print "a#b": Run "Unsafe"'), "Run (procedure Work)"),
    "create-object-continued": (core_use('        Set D = _\n            CreateObject("A.B")'),
                                "CreateObject A.B"),
    "create-object-single-line-if": (core_use('        If X Then Set D = CreateObject("A.B")'),
                                     "CreateObject A.B"),
    "create-object-in-else-branch": (core_use('#If VBA7 Then\n        X = 1\n#Else\n'
                                              '        Set D = CreateObject("A.B")\n#End If'),
                                     "CreateObject A.B"),
    "get-object": (core_use('        Set X = GetObject(, "Excel.Application")'),
                   f"GetObject (procedure Work): {OUTSIDE}"),
    "get-object-statement": (core_use('        GetObject "C:\\\\x.xlsx"'), "GetObject (procedure Work)"),
    "standalone-new": (core_use("        Set D = New Scripting.Dictionary"),
                       f"New Scripting.Dictionary (procedure Work): {OUTSIDE}"),
    "standalone-new-unqualified": (core_use("        Set D = New Dictionary"), "New Dictionary"),
    "as-new": (core_use("        Dim Fso As New FileSystemObject"), "New FileSystemObject"),
    "new-after-type-block": (files_at(CORE, "Private Type Holder\n    Value As Double\nEnd Type\n"
                                            "Private Seen As New Dictionary\n"),
                             "New Dictionary (module level)"),
    "statement-after-unclosed-type": (files_at(CORE, "Private Type Holder\n    Value As Double\n"
                                                     + in_procedure('        CreateObject "A.B"')),
                                      "CreateObject A.B (procedure Work)"),
    "procedure-named-like-a-dynamic-call": (files_at(CORE, "Public Sub Run()\nEnd Sub\n"),
                                            "Run (procedure Run)"),
    "call-by-name": (core_use('        Debug.Print CallByName(Me, "X", VbGet)'),
                     f"CallByName (procedure Work): {OUTSIDE}"),
    "application-run": (core_use('        Application.Run "Macro"'), "Run (procedure Work)"),
    "with-member-run": (core_use('        With Application\n            .Run "Macro"\n'
                                 "        End With"), "Run (procedure Work)"),
    "unqualified-run": (core_use('        Run "Macro"'), "Run (procedure Work)"),
    "evaluate": (core_use('        Debug.Print Evaluate("1+1")'), "Evaluate (procedure Work)"),
    "member-evaluate": (core_use('        Debug.Print Sheet.Evaluate("A1")'), "Evaluate"),
    "execute-excel4-macro": (core_use('        ExecuteExcel4Macro "X"'), "ExecuteExcel4Macro"),
    "on-time": (core_use('        Application.OnTime Now, "Macro"'), "OnTime"),
    "address-of": (core_use("        Debug.Print AddressOf Work"), "AddressOf"),
    "bracket-evaluation": (core_use("        Debug.Print [A1]"), "[...] (procedure Work)"),
    "api-call-by-name": (files_at(API, in_procedure('        X = CallByName(Y, "Z", VbGet)')),
                         f"CallByName (procedure Work): {OUTSIDE}"),
    "unit-test-create-object": (files_at(UNIT, in_procedure('        Set D = CreateObject("A.B")')),
                                OUTSIDE),
    "other-home": (files_at("src/Other.bas", in_procedure('        Set D = CreateObject("A.B")')),
                   OUTSIDE),
    "host-without-exception": (files_at(ADAPTER, HOST_BODY, *HOST_EXCEPTIONS[1:]),
                               f"CreateObject Shell.Application (procedure Work): needs a reviewed "
                               f"exception in {EXCEPTIONS}"),
    "host-variable-progid": (files_at(ADAPTER, in_procedure("        Set D = CreateObject(ProgId)")),
                             "the ProgID is not a literal, so no exception can cover it"),
    "host-concatenated-progid": (files_at(ADAPTER, in_procedure(
        '        Set D = CreateObject("Shell." & Suffix)')), "the ProgID is not a literal"),
    "host-test-declare": (files_at(HOST_TEST, '#If VBA7 Then\nPrivate Declare PtrSafe Function '
                                              'GetTickCount Lib "kernel32" () As Long\n#End If\n'),
                          "Declare GetTickCount (module level): a Declare is allowed in "
                          "src/host/excel/ only"),
    "exception-for-another-procedure": (files_at(ADAPTER, in_procedure(
        '        Set D = CreateObject("Shell.Application")'), exception(procedure="Other")),
        "needs a reviewed exception"),
    "stale-exception": (files_at(ADAPTER, in_procedure("        X = 1"), exception()),
                        f"{EXCEPTIONS}: stale exception for CreateObject in {ADAPTER}"),
}
EXCEPTIONS_INVALID: dict[str, tuple[str, str]] = {
    "not-json": ("{", "cannot be read"),
    "duplicate-key": ('{"schema": "klcr-vba-exceptions", "schema": "x", "version": 1, '
                      '"exceptions": []}', "duplicate key(s) schema"),
    "non-finite": ('{"schema": "klcr-vba-exceptions", "version": NaN, "exceptions": []}',
                   "non-finite number NaN"),
    "wrong-schema": ('{"schema": "x", "version": 1, "exceptions": []}', "must be {"),
    "extra-top-level-key": ('{"schema": "klcr-vba-exceptions", "version": 1, "exceptions": [], '
                            '"x": 1}', "must be {"),
    "not-an-object": (exceptions("x"), "exceptions[0]: an exception must be an object"),
    "unknown-field": (exceptions(exception(note="x")), "exceptions[0]: unknown field 'note'"),
    "missing-field": (exceptions({k: v for k, v in exception().items() if k != "reason"}),
                      "exceptions[0]: missing field 'reason'"),
    "unknown-construct": (exceptions(exception(construct="Shell")), "construct must be one of"),
    "outside-host": (exceptions(exception(path=CORE)), "path must be a component in"),
    "declare-in-host-tests": (exceptions(exception(path=HOST_TEST, procedure=None,
                                                   construct="Declare", target="F")),
                              "a Declare is allowed in src/host/excel/ only"),
    "empty-procedure": (exceptions(exception(procedure="")), "procedure must be a name"),
    "missing-target": (exceptions(exception(target=None)), "a CreateObject exception names its target"),
    "target-for-run": (exceptions(exception(construct="Run", target="Macro")),
                       "a Run exception has a null target"),
    "issue-zero": (exceptions(exception(issue=0)), "issue must be a positive issue number"),
    "issue-boolean": (exceptions(exception(issue=True)), "issue must be a positive issue number"),
    "empty-reason": (exceptions(exception(reason=" ")), "reason must be a non-empty text"),
    "no-reviewer": (exceptions(exception(reviewed_by=None)), "reviewed_by must be a non-empty text"),
    "unreal-date": (exceptions(exception(date="2026-02-30")), "date must be a real date"),
    "duplicate-entry": (exceptions(exception(), exception(target="SHELL.APPLICATION")),
                        "exceptions[1]: duplicates an earlier exception"),
}


class DynamicTest(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for name, files in DYNAMIC_VALID.items():
            with self.subTest(name=name):
                self.assertEqual(run_check(check_vba_dynamic.check, files), [])

    def test_invalid_fixtures_fail(self) -> None:
        for name, (files, text) in DYNAMIC_INVALID.items():
            with self.subTest(name=name):
                findings = run_check(check_vba_dynamic.check, files)
                self.assertTrue(any(text in item for item in findings), findings)

    def test_invalid_exceptions_fail(self) -> None:
        for name, (content, text) in EXCEPTIONS_INVALID.items():
            with self.subTest(name=name):
                files = files_at(ADAPTER, in_procedure('        Set D = CreateObject("Shell.Application")'))
                files[EXCEPTIONS] = content
                findings = run_check(check_vba_dynamic.check, files)
                self.assertTrue(any(text in item for item in findings), findings)

    def test_missing_exceptions_file_fails_closed(self) -> None:
        findings = run_check(check_vba_dynamic.check, {UNIT: module("")})
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].startswith(f"{EXCEPTIONS}: cannot be read:"), findings)

    def test_findings_name_file_and_line(self) -> None:
        files = core_use('        Set D = CreateObject("A.B")\n        CreateObject "A.B"')
        self.assertEqual(run_check(check_vba_dynamic.check, files),
                         [f"{CORE}:5: CreateObject A.B (procedure Work): {OUTSIDE}",
                          f"{CORE}:6: CreateObject A.B (procedure Work): {OUTSIDE}"])

    def test_counts_components_and_uses(self) -> None:
        with repository(DYNAMIC_VALID["host-adapter-with-reviewed-exceptions"]) as root:
            findings, components, count = check_vba_dynamic.check(root)
        self.assertEqual((findings, components, count), ([], 1, 7))


class MainTest(unittest.TestCase):
    def test_every_gate_exits_0_when_valid_and_1_when_invalid(self) -> None:
        valid = {**DYNAMIC_VALID["host-adapter-with-reviewed-exceptions"],
                 UNIT: module(JUMPS_VALID["handler-and-cleanup"])}
        invalid = files_at(CORE, "#If Mac Then\n#End If\n" + in_procedure(
            '        GoSub Lost\n        Set D = CreateObject("A.B")\nLost:'))
        mains = (check_vba_conditionals.main, check_vba_jumps.main, check_vba_dynamic.main)
        for files, expected in ((valid, 0), (invalid, 1)):
            with repository(files) as root:
                for main in mains:
                    with self.subTest(main=main.__module__, expected=expected), \
                            contextlib.redirect_stdout(io.StringIO()) as output:
                        self.assertEqual(main(["--root", str(root)]), expected)
                        verdict = output.getvalue().splitlines()[-1]
                        self.assertIn("PASS" if expected == 0 else "FAIL", verdict)
                        self.assertIn("static check, nothing compiled or run", verdict)


if __name__ == "__main__":
    unittest.main()
