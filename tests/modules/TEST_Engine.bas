Attribute VB_Name = "TEST_Engine"
'==============================================================================
' MODULE: TEST_Engine
'------------------------------------------------------------------------------
' PURPOSE
'   Self-test of the regulatory aggregates: hand-computed cases for each cap
'   of Annex I and Annex II, the unwind adjustment, the ratio, the domain
'   checks, and the formula-check column of Results when it holds a run.
'
' PUBLIC SURFACE
'   RunSelfTest     Button "Self-test" on Results; shows the report
'   SelfTestReport  Silent run; returns "PASS n/n" or the failures
'
' DEPENDENCIES
'   CORE_Config, CORE_Engine.
'
' STATE OWNERSHIP
'   Reads Results; writes nothing.
'
' ERROR POLICY
'   An unexpected error in a case is a failure of that case, not of the run.
'
' COMPATIBILITY
'   Excel VBA; no references beyond the defaults.
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
    'Require explicit declarations; keep the tests inside this project.
    Option Explicit
    Option Private Module

'------------------------------------------------------------------------------
' MODULE STATE
'------------------------------------------------------------------------------
        Private mPassed            As Long      'Assertions passed
        Private mFailed            As Long      'Assertions failed
        Private mReport            As String    'Failure lines

'------------------------------------------------------------------------------
'                               ENTRY POINTS
'------------------------------------------------------------------------------

Public Sub RunSelfTest()
'------------------------------------------------------------------------------
' PURPOSE
'   Run every case and show the report.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Report             As String    'Outcome

        Report = SelfTestReport()
        MsgBox Report, IIf(mFailed = 0, vbInformation, vbExclamation), "K-LCR self-test"
End Sub


Public Function SelfTestReport() As String
'------------------------------------------------------------------------------
' PURPOSE
'   Run every case silently.
'
' RETURNS
'   "PASS n/n" when every assertion holds, otherwise "FAIL f/n" followed by
'   one line per failed assertion.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        mPassed = 0
        mFailed = 0
        mReport = vbNullString

        CaseLevel1Only
        CaseCap40
        CaseCap15
        CaseCap70
        CaseUnwind
        CaseInflowCaps
        CaseRatio
        CaseIllustrativeEUR
        CaseDomain
        CaseResultsFormulaCheck

        If mFailed = 0 Then
            SelfTestReport = "PASS " & mPassed & "/" & mPassed
        Else
            SelfTestReport = "FAIL " & mFailed & "/" & (mPassed + mFailed) & mReport
        End If
End Function


'------------------------------------------------------------------------------
'                                  CASES
'------------------------------------------------------------------------------

Private Sub CaseLevel1Only()
    'Only level 1: no cap binds, the buffer is the holding.
        AssertBuffer "L1 only", 100, 0, 0, 0, 100, 0, 0, 0, 0#, 100#
End Sub


Private Sub CaseCap40()
    'L2A 50 against L1 50: level 2 limited to 40%, buffer 50 / 0.60.
        AssertBuffer "40% cap", 50, 0, 50, 0, 50, 0, 50, 0, 100# - 50# / 0.6, 50# / 0.6
End Sub


Private Sub CaseCap15()
    'L2B 20 against L1 80: level 2B limited to 15%, buffer 80 / 0.85.
        AssertBuffer "15% cap", 80, 0, 0, 20, 80, 0, 0, 20, 100# - 80# / 0.85, 80# / 0.85
End Sub


Private Sub CaseCap70()
    'EHQCB 80 against L1 20: L1 excl. EHQCB at least 30%, buffer 20 / 0.30.
        AssertBuffer "70% cap", 20, 80, 0, 0, 20, 80, 0, 0, 100# - 20# / 0.3, 20# / 0.3
End Sub


Private Sub CaseUnwind()
    'Cash 50 borrowed in a repo against L2B 50: held L1 150, L2B 0; after the
    'unwind A1 100 and A2B 50, so the 15% cap removes 150 - 100/0.85.
        AssertBuffer "Unwind", 150, 0, 0, 0, 100, 0, 0, 50, 150# - 100# / 0.85, 100# / 0.85
End Sub


Private Sub CaseInflowCaps()
        AssertNear "75% cap", CORE_Engine.NetLiquidityOutflow(100, 0, 0, 90, 0.9, 0.75), 25#
        AssertNear "75% cap not binding", CORE_Engine.NetLiquidityOutflow(100, 0, 0, 40, 0.9, 0.75), 60#
        AssertNear "Exempt inflows", CORE_Engine.NetLiquidityOutflow(100, 120, 0, 0, 0.9, 0.75), 0#
        AssertNear "90% cap", CORE_Engine.NetLiquidityOutflow(100, 0, 95, 0, 0.9, 0.75), 10#
        'TO 100, FEI 10, IHC 45, IC 60: 100 - 10 - 45 - MIN(60, 0.75 x (90 - 50)).
        AssertNear "Mixed classes", CORE_Engine.NetLiquidityOutflow(100, 10, 45, 60, 0.9, 0.75), 15#
End Sub


Private Sub CaseRatio()
    Dim Ratio              As Variant   'Engine result

        AssertNear "Ratio", CDbl(CORE_Engine.CoverageRatio(150, 100)), 1.5
        Ratio = CORE_Engine.CoverageRatio(150, 0)
        AssertTrue "Ratio with zero outflow is Empty", IsEmpty(Ratio)
End Sub


Private Sub CaseIllustrativeEUR()
    'EUR scope of the illustrative inputs (values from tools/lcr_spec.py).
        AssertBuffer "Illustrative EUR", 1375000000#, 465000000#, 595000000#, 800000000#, _
                     1225000000#, 465000000#, 595000000#, 800000000#, _
                     3085000000# - 2285000000# / 0.85, 2838235294.11765
        AssertNear "Illustrative EUR NLO", CORE_Engine.NetLiquidityOutflow(2520000000#, 100000000#, 0, _
                   725000000#, 0.9, 0.75), 1695000000#
End Sub


Private Sub CaseDomain()
    Dim Raised             As Long      'Error number raised

        On Error Resume Next
        Raised = 0
        Call CORE_Engine.ExcessLiquidAssets(-1, 0, 0, 0, 0.3, 0.6, 0.15)
        Raised = Err.Number
        Err.Clear
        On Error GoTo 0
        AssertTrue "Negative amount raises ERR_ENGINE_INPUT", Raised = ERR_ENGINE_INPUT
        On Error Resume Next
        Raised = 0
        Call CORE_Engine.NetLiquidityOutflow(100, 0, 0, 0, 0.9, 1.5)
        Raised = Err.Number
        Err.Clear
        On Error GoTo 0
        AssertTrue "Cap above 100% raises ERR_ENGINE_INPUT", Raised = ERR_ENGINE_INPUT
End Sub


Private Sub CaseResultsFormulaCheck()
    'Every Results row of the last run agrees with the worksheet formulas.
    Dim ws                 As Worksheet 'Results
    Dim r                  As Long      'Row on Results
    Dim Verdict            As String    'Value of the Check column

        Set ws = ThisWorkbook.Worksheets(SH_RESULTS)
        r = RES_FIRST_ROW
        Do While Len(CStr(ws.Cells(r, RES_FIRST_COL).Value)) > 0
            Verdict = CStr(ws.Cells(r, RES_LAST_COL).Value)
            AssertTrue "Results formula check, " & CStr(ws.Cells(r, RES_FIRST_COL).Value), _
                   Verdict = "OK" Or Verdict = "n/a"
            r = r + 1
        Loop
End Sub


'------------------------------------------------------------------------------
'                                ASSERTIONS
'------------------------------------------------------------------------------

Private Sub AssertBuffer( _
    ByVal CaseName As String, _
    ByVal L1 As Double, ByVal L1CB As Double, ByVal L2A As Double, ByVal L2B As Double, _
    ByVal A1 As Double, ByVal A1CB As Double, ByVal A2A As Double, ByVal A2B As Double, _
    ByVal ExpectedExcess As Double, _
    ByVal ExpectedBuffer As Double)
'------------------------------------------------------------------------------
' PURPOSE
'   AssertTrue the excess and the buffer of one composition with the
'   regulatory limits 0.30, 0.60 and 0.15.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Excess             As Double    'Engine excess

        On Error GoTo Failed
        Excess = CORE_Engine.ExcessLiquidAssets(A1, A1CB, A2A, A2B, 0.3, 0.6, 0.15)
        AssertNear CaseName & " excess", Excess, ExpectedExcess
        AssertNear CaseName & " buffer", CORE_Engine.LiquidityBuffer(L1, L1CB, L2A, L2B, Excess), ExpectedBuffer
        Exit Sub
Failed:
        AssertTrue CaseName & " raised " & Err.Description, False
End Sub


Private Sub AssertNear(ByVal CaseName As String, ByVal Actual As Double, ByVal Expected As Double)
'------------------------------------------------------------------------------
' PURPOSE
'   AssertTrue equality within 1E-9 relative (1E-9 absolute near zero).
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Magnitude          As Double    'Scale of the relative test

        Magnitude = Abs(Expected)
        If Magnitude < 1# Then Magnitude = 1#
        If Abs(Actual - Expected) <= 0.000000001 * Magnitude Then
            mPassed = mPassed + 1
        Else
            mFailed = mFailed + 1
            mReport = mReport & vbLf & CaseName & ": expected " & CStr(Expected) & ", got " & CStr(Actual)
        End If
End Sub


Private Sub AssertTrue(ByVal CaseName As String, ByVal Condition As Boolean)
'------------------------------------------------------------------------------
' PURPOSE
'   Count one assertion.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        If Condition Then
            mPassed = mPassed + 1
        Else
            mFailed = mFailed + 1
            mReport = mReport & vbLf & CaseName & ": failed"
        End If
End Sub
