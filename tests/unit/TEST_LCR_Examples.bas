Attribute VB_Name = "TEST_LCR_Examples"
'==============================================================================
' MODULE: TEST_LCR_Examples
'------------------------------------------------------------------------------
' PURPOSE
'   Example suite of the neutral test harness: one case per kind of
'   assertion, and three deliberate modes that show how a run can fail
'   without being silent. It exercises the harness on arithmetic that
'   belongs to no regulation and holds no calculation of the Liquidity
'   Coverage Ratio.
'
' PUBLIC SURFACE
'   Runs: RunExampleTests, RunExampleTestsWithInjectedFailure,
'   RunExampleTestsWithSkippedCase, RunExampleTestsWithCleanupProblem.
'   Self-test: VerifyExampleModes returns the report of all four modes;
'   CheckExampleModes raises when one mode did not end as required.
'   Option Private Module keeps all of them out of the workbook's external
'   surface.
'
' DEPENDENCIES
'   TEST_LCR_Harness only. No workbook, worksheet, fixture file, clock or
'   host state: the suite runs the same in any host.
'
' STATE OWNERSHIP
'   Owns mMode, the mode of the running suite, empty outside a run.
'
' ERROR POLICY
'   A run that does not pass ends in ERR_TEST_FAILED, raised by EndRun after
'   the log is complete. VerifyExampleModes captures each run's error and
'   compares it with the one the mode requires.
'
' STATUS
'   Source only. It has not been compiled or run in Excel: the host run is
'   #14 and #15. The case and assertion counts below are checked against the
'   source by tools/test_vba_harness.py, without Excel.
'
' UPDATED
'   2026-11-13
'
' AUTHOR
'   Daniele Penza
'==============================================================================

'------------------------------------------------------------------------------
' MODULE SETTINGS
'------------------------------------------------------------------------------
    'Require explicit declarations; keep the suite inside the project.
    Option Explicit
    Option Private Module

'------------------------------------------------------------------------------
' MODULE CONSTANTS
'------------------------------------------------------------------------------
    'The suite's identity and the counts of a complete run. A case or an
    'assertion added or removed changes these in the same commit.
        Private Const SUITE_NAME            As String = "examples"
        Private Const EXPECTED_CASES        As Long = 3
        Private Const EXPECTED_ASSERTIONS   As Long = 9
    'Test-only error raised by the example operation, kept apart from the
    'harness range (&H80040FE0 to &H80040FE2).
    'Written as a literal equal to vbObjectError + 4072.
        Private Const ERR_EXAMPLE_INVALID   As Long = &H80040FE8   'vbObjectError + 4072: Negative input

'------------------------------------------------------------------------------
' MODULE STATE
'------------------------------------------------------------------------------
        Private mMode   As String    'NORMAL or a deliberate mode; empty outside a run


'
'------------------------------------------------------------------------------
'
'                                 ENTRY POINTS
'
'------------------------------------------------------------------------------
'

Public Sub RunExampleTests()
'
'==============================================================================
'                               RunExampleTests
'------------------------------------------------------------------------------
' PURPOSE
'   Run the example suite. A passing run ends with
'   RESULT=PASS; suite=examples; operation=PASS; completeness=COMPLETE;
'   cases=3; assertions=9; failures=0; cleanup=PASS; recovery=NONE.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        RunSuite "NORMAL"

End Sub


Public Sub RunExampleTestsWithInjectedFailure()
'
'==============================================================================
'                      RunExampleTestsWithInjectedFailure
'------------------------------------------------------------------------------
' PURPOSE
'   Show the failure path: exact-comparison is given a wrong value. Expected
'   end: RESULT=FAIL; suite=examples; operation=FAIL;
'   completeness=COMPLETE; cases=3; assertions=9; failures=1; cleanup=PASS;
'   recovery=NONE, then the error ERR_TEST_FAILED.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        RunSuite "INJECTED_FAILURE"

End Sub


Public Sub RunExampleTestsWithSkippedCase()
'
'==============================================================================
'                        RunExampleTestsWithSkippedCase
'------------------------------------------------------------------------------
' PURPOSE
'   Show that an incomplete run is never a pass: the last case is skipped.
'   Expected end: RESULT=FAIL; suite=examples; operation=PASS;
'   completeness=INCOMPLETE; cases=2; assertions=7; failures=1, the failure
'   being harness.completeness; cleanup=PASS; recovery=NONE, then
'   ERR_TEST_FAILED.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        RunSuite "SKIPPED_CASE"

End Sub


Public Sub RunExampleTestsWithCleanupProblem()
'
'==============================================================================
'                      RunExampleTestsWithCleanupProblem
'------------------------------------------------------------------------------
' PURPOSE
'   Show that a cleanup failure is reported apart from the operation: every
'   case passes, and EndRun is told that the host state changed. Expected
'   end: RESULT=FAIL; suite=examples; operation=PASS;
'   completeness=COMPLETE; cases=3; assertions=9; failures=0; cleanup=FAIL;
'   recovery=REQUIRED, then ERR_TEST_FAILED. The next run is refused until
'   ResetTests is called, as for a real cleanup failure.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        RunSuite "CLEANUP_PROBLEM"

End Sub


Public Function VerifyExampleModes() _
    As String
'
'==============================================================================
'                              VerifyExampleModes
'------------------------------------------------------------------------------
' PURPOSE
'   Run the four modes in order and check that each ends as it must: the
'   normal run passes, and every deliberate mode reaches its caller as
'   ERR_TEST_FAILED with the RESULT record documented above. This is the
'   self-test that a failed run is never silent.
'
' RETURNS
'   The report, one record per line separated by line feeds: a MODE record
'   per mode with the required and the actual RESULT and error, then
'   VERIFICATION=PASS or VERIFICATION=FAIL with the number of modes and of
'   deviations. The report holds no time, machine or user.
'
' ERROR POLICY
'   Raises nothing for a deviation; CheckExampleModes does. The cleanup
'   problem of the last mode is simulated, so the verification
'   acknowledges it with ResetTests, but only when that mode ran in this
'   call and ended as required. A start refused because a run was active or
'   recovery was already required is a deviation, and the state found is
'   left as it was: the manual check that ResetTests stands for is not
'   bypassed.
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim Modes           As Variant    'Mode names, in run order
    Dim Required        As Variant    'Required RESULT record of each mode
    Dim RequiredError   As Variant    'Error each mode must end with
    Dim i               As Long       'Position in the lists
    Dim Deviations      As Long       'Modes that did not end as required
    Dim RunError        As Long       'Error that ended the run; 0 for none
    Dim Actual          As String     'RESULT record the run wrote
    Dim Simulated       As Boolean    'True when the simulated cleanup problem ran and ended as required
    Dim Report          As String     'Report built so far

'------------------------------------------------------------------------------
' LIST THE MODES
'------------------------------------------------------------------------------
        Modes = Array("NORMAL", "INJECTED_FAILURE", "SKIPPED_CASE", "CLEANUP_PROBLEM")
        RequiredError = Array(0&, TEST_LCR_Harness.ERR_TEST_FAILED, _
            TEST_LCR_Harness.ERR_TEST_FAILED, TEST_LCR_Harness.ERR_TEST_FAILED)
        Required = Array( _
            "RESULT=PASS; suite=examples; operation=PASS; completeness=COMPLETE" & _
                "; cases=3; assertions=9; failures=0; cleanup=PASS; recovery=NONE", _
            "RESULT=FAIL; suite=examples; operation=FAIL; completeness=COMPLETE" & _
                "; cases=3; assertions=9; failures=1; cleanup=PASS; recovery=NONE", _
            "RESULT=FAIL; suite=examples; operation=PASS; completeness=INCOMPLETE" & _
                "; cases=2; assertions=7; failures=1; cleanup=PASS; recovery=NONE", _
            "RESULT=FAIL; suite=examples; operation=PASS; completeness=COMPLETE" & _
                "; cases=3; assertions=9; failures=0; cleanup=FAIL; recovery=REQUIRED")

'------------------------------------------------------------------------------
' RUN AND COMPARE
'------------------------------------------------------------------------------
        For i = LBound(Modes) To UBound(Modes)
            On Error Resume Next
            RunSuite CStr(Modes(i))
            RunError = Err.Number
            On Error GoTo 0
            Actual = TEST_LCR_Harness.LastResult()
            Report = Report & "MODE=" & CStr(Modes(i)) & _
                "; required_error=" & CStr(RequiredError(i)) & "; error=" & CStr(RunError) & _
                "; required=" & CStr(Required(i)) & "; actual=" & Actual & vbLf
            If RunError <> CLng(RequiredError(i)) Or Actual <> CStr(Required(i)) Then
                Deviations = Deviations + 1
            ElseIf CStr(Modes(i)) = "CLEANUP_PROBLEM" Then
                Simulated = True
            End If
        Next i

    'The cleanup problem of the last mode was simulated: no host state
    'changed, so acknowledging it is correct, but only when this call ran it.
    'A refused start leaves the state that was found, for the manual check.
        If Simulated Then
            TEST_LCR_Harness.ResetTests
        End If
        Report = Report & "VERIFICATION=" & IIf(Deviations = 0, "PASS", "FAIL") & _
            "; modes=" & CStr(UBound(Modes) - LBound(Modes) + 1) & _
            "; deviations=" & CStr(Deviations)
        VerifyExampleModes = Report

End Function


Public Sub CheckExampleModes()
'
'==============================================================================
'                               CheckExampleModes
'------------------------------------------------------------------------------
' PURPOSE
'   Print the report of VerifyExampleModes and raise ERR_TEST_FAILED when a
'   mode did not end as required.
'
' ERROR POLICY
'   Raises TEST_LCR_Harness.ERR_TEST_FAILED, after printing, on a deviation.
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim Report   As String    'Report of the four modes

'------------------------------------------------------------------------------
' CHECK
'------------------------------------------------------------------------------
        Report = VerifyExampleModes()
        Debug.Print Report
        If InStr(Report, "VERIFICATION=PASS") = 0 Then
            Err.Raise TEST_LCR_Harness.ERR_TEST_FAILED, "TEST_LCR_Examples.CheckExampleModes", _
                "A mode of the example suite did not end as required; see the report."
        End If

End Sub


'
'------------------------------------------------------------------------------
'
'                                    RUNNER
'
'------------------------------------------------------------------------------
'

Private Sub RunSuite( _
    ByVal Mode As String)
'
'==============================================================================
'                                   RunSuite
'------------------------------------------------------------------------------
' PURPOSE
'   Run every case in a fixed order between BeginRun and EndRun.
'
' INPUTS
'   Mode: NORMAL, INJECTED_FAILURE, SKIPPED_CASE or CLEANUP_PROBLEM.
'
' ERROR POLICY
'   An error escaping a case handler is passed to EndRun, which reports it
'   and re-raises it unchanged. BeginRun's refusal propagates directly.
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim ErrNumber        As Long      'Runner error number; 0 for none
    Dim ErrSource        As String    'Runner error source
    Dim ErrDescription   As String    'Runner error description
    Dim Problems         As String    'Cleanup problem reported to EndRun

'------------------------------------------------------------------------------
' RUN
'------------------------------------------------------------------------------
        TEST_LCR_Harness.BeginRun SUITE_NAME, Mode, EXPECTED_CASES, EXPECTED_ASSERTIONS
        mMode = Mode
        On Error GoTo RunFailed
        CaseExactComparison
        CaseToleranceComparison
        If mMode <> "SKIPPED_CASE" Then
            CaseExpectedError
        End If

Finish:
        On Error GoTo 0
        If mMode = "CLEANUP_PROBLEM" Then
            Problems = "simulated: the host state changed during the run"
        End If
        mMode = vbNullString
        TEST_LCR_Harness.EndRun ErrNumber, ErrSource, ErrDescription, Problems
        Exit Sub

RunFailed:
        ErrNumber = Err.Number
        ErrSource = Err.Source
        ErrDescription = Err.Description
        Resume Finish

End Sub


'
'------------------------------------------------------------------------------
'
'                                    CASES
'
'------------------------------------------------------------------------------
'

Private Sub CaseExactComparison()
'
'==============================================================================
'                             CaseExactComparison
'------------------------------------------------------------------------------
' PURPOSE
'   Exact comparisons of a Double, a text and a condition. 3 assertions. In
'   INJECTED_FAILURE mode the Double comparison gets a wrong value, so that
'   exactly one assertion fails.
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim Whole   As Double    'Value that is halved

'------------------------------------------------------------------------------
' RUN CASE
'------------------------------------------------------------------------------
        On Error GoTo CaseFailed
        TEST_LCR_Harness.BeginCase "exact-comparison"
        Whole = 1#
        If mMode = "INJECTED_FAILURE" Then
            Whole = 1.5
        End If
        TEST_LCR_Harness.AssertEqualDouble "half-of-one", 0.5, ExampleHalf(Whole)
        TEST_LCR_Harness.AssertEqualText "same-text", "K-LCR", "K" & "-" & "LCR"
        TEST_LCR_Harness.AssertTrue "positive", ExampleHalf(4#) > 0#, "half of four is positive"
        Exit Sub

CaseFailed:
        TEST_LCR_Harness.RecordCaseError

End Sub


Private Sub CaseToleranceComparison()
'
'==============================================================================
'                           CaseToleranceComparison
'------------------------------------------------------------------------------
' PURPOSE
'   Tolerance comparisons: an absolute bound, a relative bound, the absolute
'   bound near zero, and a value outside its bound that the rule rejects.
'   4 assertions.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        On Error GoTo CaseFailed
        TEST_LCR_Harness.BeginCase "tolerance-comparison"
        TEST_LCR_Harness.AssertNear "inside-absolute", 100#, 100.004, 0.01, 0#
        TEST_LCR_Harness.AssertNear "inside-relative", 1000000#, 1000050#, 0#, 0.0001
        TEST_LCR_Harness.AssertNear "near-zero", 0#, 0.000001, 0.00001, 0.001
        TEST_LCR_Harness.AssertTrue "outside-is-rejected", _
            Not TEST_LCR_Harness.WithinTolerance(10#, 10.5, 0.1, 0.01), _
            "10.5 is outside the bound around 10"
        Exit Sub

CaseFailed:
        TEST_LCR_Harness.RecordCaseError

End Sub


Private Sub CaseExpectedError()
'
'==============================================================================
'                              CaseExpectedError
'------------------------------------------------------------------------------
' PURPOSE
'   An expected raised error, captured on the line after the call, and the
'   same call with a valid input raising nothing. 2 assertions.
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim Result        As Double    'Value of the checked square root
    Dim RaisedError   As Long      'Err.Number right after the call

'------------------------------------------------------------------------------
' RUN CASE
'------------------------------------------------------------------------------
        On Error GoTo CaseFailed
        TEST_LCR_Harness.BeginCase "expected-error"
        On Error Resume Next
        Result = ExampleSquareRoot(-1#)
        RaisedError = Err.Number
        On Error GoTo CaseFailed
        TEST_LCR_Harness.AssertRaised "negative-input", ERR_EXAMPLE_INVALID, RaisedError
        On Error Resume Next
        Result = ExampleSquareRoot(4#)
        RaisedError = Err.Number
        On Error GoTo CaseFailed
        TEST_LCR_Harness.AssertRaised "valid-input", 0, RaisedError
        Exit Sub

CaseFailed:
        TEST_LCR_Harness.RecordCaseError

End Sub


'
'------------------------------------------------------------------------------
'
'                              EXAMPLE OPERATIONS
'
'------------------------------------------------------------------------------
'

Private Function ExampleHalf( _
    ByVal Value As Double) _
    As Double
'
'==============================================================================
'                                 ExampleHalf
'------------------------------------------------------------------------------
' PURPOSE
'   Half of a Double: an operation of no regulation, exact in binary, that
'   gives the cases something to compare.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        ExampleHalf = Value / 2#

End Function


Private Function ExampleSquareRoot( _
    ByVal Value As Double) _
    As Double
'
'==============================================================================
'                              ExampleSquareRoot
'------------------------------------------------------------------------------
' PURPOSE
'   The square root of a non-negative Double, raising for a negative one: an
'   operation of no regulation that gives the error case something to raise.
'
' INPUTS
'   Value: >= 0.
'
' ERROR POLICY
'   Raises ERR_EXAMPLE_INVALID for a negative Value.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        If Value < 0# Then
            Err.Raise ERR_EXAMPLE_INVALID, "TEST_LCR_Examples.ExampleSquareRoot", _
                "Value must not be negative."
        End If
        ExampleSquareRoot = Sqr(Value)

End Function
