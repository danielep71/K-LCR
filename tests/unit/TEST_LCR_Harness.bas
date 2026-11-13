Attribute VB_Name = "TEST_LCR_Harness"
'==============================================================================
' MODULE: TEST_LCR_Harness
'------------------------------------------------------------------------------
' PURPOSE
'   Neutral, deterministic harness for the VBA test suites of K-LCR: one run
'   per suite, stable case identifiers, exact and tolerance assertions,
'   expected raised errors, expected case and assertion counts, and a
'   complete KEY=value log. It proves infrastructure only: it holds no
'   regulatory rule and no calculation of the Liquidity Coverage Ratio.
'
' PUBLIC SURFACE
'   Suite lifecycle: BeginRun, BeginCase, RecordCaseError, EndRun.
'   Assertions: AssertEqualDouble, AssertNear, AssertEqualText, AssertTrue,
'   AssertRaised; WithinTolerance is the comparison rule.
'   Log: Say, LogText, LastResult. Recovery: ResetTests.
'   Option Private Module keeps all of them out of the workbook's external
'   surface.
'
' DEPENDENCIES
'   The VBA language only: no reference, no Application, Workbook or
'   Worksheet object, no file, no clock and no random generator. The host
'   state, when a run changes it, is checked by the caller in tests/host/
'   and passed to EndRun as CleanupProblems.
'
' STATE OWNERSHIP
'   Owns the run counters, the case identifiers, the failure records, the
'   retained log and the active-run and recovery-required flags. It never
'   writes a file; LogText returns the log for a host adapter to save.
'
' ERROR POLICY
'   Assertion failures are recorded and the run continues. EndRun re-raises
'   an unexpected runner error unchanged after reporting, or raises
'   ERR_TEST_FAILED for any other failed outcome. A run that starts while
'   another is active, or while recovery is required, is refused with
'   ERR_TEST_DIRTY_START. Misuse of the lifecycle raises ERR_TEST_USAGE.
'
' LOG FORMAT
'   One record per line, KEY=value; further fields are separated by "; ".
'   The keys and their order are documented in
'   docs/methodology/TEST_HARNESS.md (Log format). The log holds no time,
'   machine or user, so two runs of the same suite and mode write the same
'   log, byte for byte.
'
' STATUS
'   Source only. It has not been compiled or run in Excel: the host run is
'   #14 and #15. The portable checks of tools/ read its text, nothing more.
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
    'Require explicit declarations; keep the harness inside the project.
    Option Explicit
    Option Private Module

'------------------------------------------------------------------------------
' MODULE CONSTANTS
'------------------------------------------------------------------------------
    'Test-only error numbers, kept apart from the production range in use.
    'Written as literals equal to vbObjectError + n so that a constant
    'expression never depends on the host.
        Public Const ERR_TEST_DIRTY_START   As Long = &H80040FE0   'vbObjectError + 4064: Run refused: active or recovery required
        Public Const ERR_TEST_FAILED        As Long = &H80040FE1   'vbObjectError + 4065: Run finished without PASS
        Public Const ERR_TEST_USAGE         As Long = &H80040FE2   'vbObjectError + 4066: Lifecycle used out of order

'------------------------------------------------------------------------------
' MODULE STATE
'------------------------------------------------------------------------------
    'One run at a time. Counters and the log stay readable after EndRun,
    'until the next BeginRun or ResetTests.
        Private mRunActive            As Boolean        'True from BeginRun to EndRun
        Private mRecoveryRequired     As Boolean        'True until ResetTests after an unsafe end
        Private mRecoveryReason       As String         'Why recovery is required
        Private mSuite                As String         'Name of the running or last suite
        Private mExpectedCases        As Long           'Cases a complete run starts
        Private mExpectedAssertions   As Long           'Assertions a complete run evaluates
        Private mCaseCount            As Long           'Cases started in this run
        Private mAssertionCount       As Long           'Assertions evaluated in this run
        Private mFailureCount         As Long           'Failures of any kind in this run
        Private mErrorCount           As Long           'Unexpected errors in this run
        Private mCurrentCase          As String         'Identifier of the running case
        Private mCaseIds              As Collection     'Case identifiers seen in this run
        Private mPrimaryFailure       As String         'First failure recorded in this run
        Private mLastResult           As String         'RESULT record of the last finished run
        Private mLog                  As Collection     'Log since the last BeginRun or ResetTests


'
'------------------------------------------------------------------------------
'
'                               SUITE LIFECYCLE
'
'------------------------------------------------------------------------------
'

Public Sub BeginRun( _
    ByVal SuiteName As String, _
    ByVal Mode As String, _
    ByVal ExpectedCases As Long, _
    ByVal ExpectedAssertions As Long)
'
'==============================================================================
'                                   BeginRun
'------------------------------------------------------------------------------
' PURPOSE
'   Start one suite run: refuse an unsafe start, reset the run state and
'   write the log header.
'
' INPUTS
'   SuiteName: stable suite identifier, written in the RUN and RESULT records.
'   Mode: NORMAL, or the name of a deliberate failure mode of the suite.
'   ExpectedCases, ExpectedAssertions: counts of a complete run, >= 1.
'
' ERROR POLICY
'   Raises ERR_TEST_DIRTY_START, after logging why, when a run is active or
'   recovery is required; raises ERR_TEST_USAGE for counts below 1.
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' REFUSE AN UNSAFE START
'------------------------------------------------------------------------------
    'An interrupted run or an unverified cleanup must be acknowledged with
    'ResetTests before a new run may overwrite its state. A project reset
    '(End or Reset in the VBE) clears this state, so such a stop is not seen.
        If mRunActive Then
            mRecoveryRequired = True
            mRecoveryReason = "run of " & mSuite & " still active (interrupted?)"
        End If
        If mRecoveryRequired Then
            mLastResult = "RESULT=FAIL; suite=" & SuiteName & "; operation=NOT_RUN" & _
                "; completeness=INCOMPLETE; cases=0; assertions=0; failures=0" & _
                "; cleanup=NOT_RUN; recovery=REQUIRED"
            'RESULT is always the last record of a run.
            Say "RECOVERY=REQUIRED; reason=" & mRecoveryReason & _
                "; action=check the host state, then run TEST_LCR_Harness.ResetTests"
            Say mLastResult
            Err.Raise ERR_TEST_DIRTY_START, "TEST_LCR_Harness.BeginRun", _
                "Recovery required: " & mRecoveryReason & ". Run TEST_LCR_Harness.ResetTests."
        End If
        If ExpectedCases < 1 Or ExpectedAssertions < 1 Then
            Err.Raise ERR_TEST_USAGE, "TEST_LCR_Harness.BeginRun", _
                "Expected counts must be at least 1; got cases=" & CStr(ExpectedCases) & _
                ", assertions=" & CStr(ExpectedAssertions) & "."
        End If

'------------------------------------------------------------------------------
' RESET AND CLAIM THE RUN
'------------------------------------------------------------------------------
        ResetRunState
        Set mLog = New Collection
        mSuite = SuiteName
        mExpectedCases = ExpectedCases
        mExpectedAssertions = ExpectedAssertions
        mRunActive = True
        Say "RUN=" & SuiteName & "; mode=" & Mode & _
            "; expected_cases=" & CStr(ExpectedCases) & _
            "; expected_assertions=" & CStr(ExpectedAssertions)

End Sub


Public Sub BeginCase( _
    ByVal CaseId As String)
'
'==============================================================================
'                                  BeginCase
'------------------------------------------------------------------------------
' PURPOSE
'   Count and log the start of one case.
'
' INPUTS
'   CaseId: lower-case kebab-case identifier, unique within the run and
'   stable across runs, so that logs can be compared case by case.
'
' ERROR POLICY
'   Raises ERR_TEST_USAGE outside a run. A malformed or repeated identifier
'   is recorded as a failure; the case still counts and runs.
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' REGISTER THE CASE
'------------------------------------------------------------------------------
        RequireActiveRun "BeginCase"
        mCaseCount = mCaseCount + 1
        mCurrentCase = CaseId
        Say "CASE=" & CaseId
        If Not IsCaseId(CaseId) Then
            RecordFailure "harness.case-id", "malformed case identifier '" & CaseId & "'"
        ElseIf IsKnownCase(CaseId) Then
            RecordFailure "harness.case-id", "repeated case identifier '" & CaseId & "'"
        Else
            mCaseIds.Add CaseId, CaseId
        End If

End Sub


Public Sub RecordCaseError()
'
'==============================================================================
'                               RecordCaseError
'------------------------------------------------------------------------------
' PURPOSE
'   Record the error that ended the running case, so that the remaining
'   cases still run. Call it first thing in the case's error handler.
'
' INPUTS
'   The Err object, read before anything else can reset it.
'
' SIDE EFFECTS
'   Counts an unexpected error and a failure; evaluates no assertion.
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim ErrorNumber        As Long      'Number of the case error
    Dim ErrorSource        As String    'Source of the case error
    Dim ErrorDescription   As String    'Description of the case error

'------------------------------------------------------------------------------
' RECORD
'------------------------------------------------------------------------------
        ErrorNumber = Err.Number
        ErrorSource = Err.Source
        ErrorDescription = Err.Description
        RequireActiveRun "RecordCaseError"
        mErrorCount = mErrorCount + 1
        Say "ERROR=" & mCurrentCase & "; number=" & CStr(ErrorNumber) & _
            "; source=" & ErrorSource & "; description=" & ErrorDescription
        RecordFailure mCurrentCase & ".unexpected-error", _
            "number=" & CStr(ErrorNumber) & "; source=" & ErrorSource

End Sub


Public Sub EndRun( _
    ByVal RunErrorNumber As Long, _
    ByVal RunErrorSource As String, _
    ByVal RunErrorDescription As String, _
    Optional ByVal CleanupProblems As String = vbNullString)
'
'==============================================================================
'                                    EndRun
'------------------------------------------------------------------------------
' PURPOSE
'   Finish the run: check completeness, release the run, write the summary
'   and raise the outcome.
'
' INPUTS
'   RunErrorNumber, RunErrorSource, RunErrorDescription: the error that
'   escaped the suite's runner, or 0 and empty strings when none did.
'   CleanupProblems: what the caller found changed in the host state after
'   the run, as one line of text; empty when the state is as it was. A
'   suite that touches no host state passes nothing.
'
' OUTCOMES
'   operation: what ran: PASS, FAIL (an assertion or a case identifier
'   failed) or ERROR (an unexpected error occurred). completeness: COMPLETE
'   only when both expected counts were met exactly. cleanup: PASS when
'   CleanupProblems is empty, FAIL otherwise; it is reported apart from the
'   operation. recovery: REQUIRED when cleanup failed, or when a start was
'   refused while this run was active.
'   RESULT=PASS needs operation PASS, COMPLETE, cleanup PASS and no recovery.
'
' ERROR POLICY
'   Re-raises the runner error unchanged, after reporting, so that cleanup
'   never replaces the primary failure; otherwise raises ERR_TEST_FAILED
'   unless RESULT=PASS. Raises ERR_TEST_USAGE outside a run.
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim CleanupPassed   As Boolean    'True when the caller found no change
    Dim Completed       As Boolean    'True when both expected counts were met
    Dim Operation       As String     'PASS, FAIL or ERROR
    Dim Verdict         As String     'PASS or FAIL

'------------------------------------------------------------------------------
' COLLECT THE OUTCOMES
'------------------------------------------------------------------------------
        RequireActiveRun "EndRun"
        mCurrentCase = "run"
        If RunErrorNumber <> 0 Then
            mErrorCount = mErrorCount + 1
            Say "ERROR=run; number=" & CStr(RunErrorNumber) & "; source=" & RunErrorSource & _
                "; description=" & RunErrorDescription
            RecordFailure "runner.unexpected-error", _
                "number=" & CStr(RunErrorNumber) & "; source=" & RunErrorSource
        End If

    'The operation outcome covers what ran; completeness and cleanup are
    'judged separately below, so that each is reported on its own.
        If mErrorCount > 0 Then
            Operation = "ERROR"
        ElseIf mFailureCount > 0 Then
            Operation = "FAIL"
        Else
            Operation = "PASS"
        End If

    'Exact counts: a skipped case or assertion, or an extra one, means the
    'run did not execute the suite as written.
        Completed = (mCaseCount = mExpectedCases) And _
                    (mAssertionCount = mExpectedAssertions)
        If Not Completed Then
            RecordFailure "harness.completeness", _
                "expected cases=" & CStr(mExpectedCases) & _
                ", assertions=" & CStr(mExpectedAssertions) & _
                "; observed cases=" & CStr(mCaseCount) & _
                ", assertions=" & CStr(mAssertionCount)
        End If

        CleanupPassed = (Len(CleanupProblems) = 0)
        mRunActive = False
        If Not CleanupPassed Then
            mRecoveryRequired = True
            mRecoveryReason = CleanupProblems
        End If

        If Operation = "PASS" And Completed And CleanupPassed And Not mRecoveryRequired Then
            Verdict = "PASS"
        Else
            Verdict = "FAIL"
        End If

'------------------------------------------------------------------------------
' REPORT
'------------------------------------------------------------------------------
        Say "CASES=" & CStr(mCaseCount) & "; expected=" & CStr(mExpectedCases)
        Say "ASSERTIONS=" & CStr(mAssertionCount) & "; expected=" & CStr(mExpectedAssertions)
        Say "FAILURES=" & CStr(mFailureCount) & "; errors=" & CStr(mErrorCount)
        If Len(mPrimaryFailure) > 0 Then
            Say "PRIMARY_FAILURE=" & mPrimaryFailure
        End If
        If CleanupPassed Then
            Say "CLEANUP=PASS; detail=no change reported"
        Else
            Say "CLEANUP=FAIL; detail=" & CleanupProblems
        End If
        If mRecoveryRequired Then
            Say "RECOVERY=REQUIRED; reason=" & mRecoveryReason & _
                "; action=check the host state, then run TEST_LCR_Harness.ResetTests"
        Else
            Say "RECOVERY=NONE"
        End If
        mLastResult = "RESULT=" & Verdict & "; suite=" & mSuite & _
            "; operation=" & Operation & _
            "; completeness=" & IIf(Completed, "COMPLETE", "INCOMPLETE") & _
            "; cases=" & CStr(mCaseCount) & _
            "; assertions=" & CStr(mAssertionCount) & _
            "; failures=" & CStr(mFailureCount) & _
            "; cleanup=" & IIf(CleanupPassed, "PASS", "FAIL") & _
            "; recovery=" & IIf(mRecoveryRequired, "REQUIRED", "NONE")
        Say mLastResult

'------------------------------------------------------------------------------
' RAISE THE OUTCOME
'------------------------------------------------------------------------------
        If RunErrorNumber <> 0 Then
            Err.Raise RunErrorNumber, RunErrorSource, RunErrorDescription
        End If
        If Verdict <> "PASS" Then
            Err.Raise ERR_TEST_FAILED, "TEST_LCR_Harness.EndRun", _
                "Suite " & mSuite & " did not pass; see the log."
        End If

End Sub


Public Sub ResetTests()
'
'==============================================================================
'                                  ResetTests
'------------------------------------------------------------------------------
' PURPOSE
'   Acknowledge an interrupted run or an unverified cleanup, so that the
'   next run may start.
'
' USAGE
'   Run only after the interrupted run has stopped and the host state has
'   been checked by hand; it restores nothing itself.
'
' SIDE EFFECTS
'   Clears the run state, the recovery flag and the log, then logs the reset.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        ResetRunState
        mRecoveryRequired = False
        mRecoveryReason = vbNullString
        Set mLog = New Collection
        Say "RESET=DONE; run_active=no; recovery=NONE"

End Sub


'
'------------------------------------------------------------------------------
'
'                                  ASSERTIONS
'
'------------------------------------------------------------------------------
'

Public Sub AssertEqualDouble( _
    ByVal AssertionName As String, _
    ByVal Expected As Double, _
    ByVal Actual As Double)
'
'==============================================================================
'                              AssertEqualDouble
'------------------------------------------------------------------------------
' PURPOSE
'   Require exact Double equality, for results that are exact in binary.
'
' INPUTS
'   AssertionName: stable name within the case. Expected, Actual: compared.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        LogAssertion AssertionName, (Actual = Expected), _
            "expected=" & NumberText(Expected) & "; actual=" & NumberText(Actual)

End Sub


Public Sub AssertNear( _
    ByVal AssertionName As String, _
    ByVal Expected As Double, _
    ByVal Actual As Double, _
    ByVal AbsoluteTolerance As Double, _
    ByVal RelativeTolerance As Double)
'
'==============================================================================
'                                  AssertNear
'------------------------------------------------------------------------------
' PURPOSE
'   Require |Actual - Expected| <= max(AbsoluteTolerance, RelativeTolerance
'   * |Expected|), the rule of docs/methodology/TEST_CASES.md (Tolerance).
'
' INPUTS
'   AbsoluteTolerance, RelativeTolerance: >= 0, both always stated. Near
'   zero the absolute bound governs; both 0 demands exact equality.
'
' ERROR POLICY
'   A negative tolerance fails the assertion; nothing is raised.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        If AbsoluteTolerance < 0# Or RelativeTolerance < 0# Then
            LogAssertion AssertionName, False, "tolerances must not be negative"
        Else
            LogAssertion AssertionName, _
                WithinTolerance(Expected, Actual, AbsoluteTolerance, RelativeTolerance), _
                "expected=" & NumberText(Expected) & "; actual=" & NumberText(Actual) & _
                "; absolute=" & NumberText(AbsoluteTolerance) & _
                "; relative=" & NumberText(RelativeTolerance)
        End If

End Sub


Public Sub AssertEqualText( _
    ByVal AssertionName As String, _
    ByVal Expected As String, _
    ByVal Actual As String)
'
'==============================================================================
'                               AssertEqualText
'------------------------------------------------------------------------------
' PURPOSE
'   Require the same text, compared binary: case and spaces count.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        LogAssertion AssertionName, (StrComp(Actual, Expected, vbBinaryCompare) = 0), _
            "expected='" & Expected & "'; actual='" & Actual & "'"

End Sub


Public Sub AssertTrue( _
    ByVal AssertionName As String, _
    ByVal Condition As Boolean, _
    ByVal Detail As String)
'
'==============================================================================
'                                  AssertTrue
'------------------------------------------------------------------------------
' PURPOSE
'   Require a condition the suite evaluated; Detail is logged on failure.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        LogAssertion AssertionName, Condition, Detail

End Sub


Public Sub AssertRaised( _
    ByVal AssertionName As String, _
    ByVal ExpectedNumber As Long, _
    ByVal ActualNumber As Long)
'
'==============================================================================
'                                 AssertRaised
'------------------------------------------------------------------------------
' PURPOSE
'   Require that a call raised a specific error number. The suite captures
'   Err.Number on the line after the call; 0 means nothing was raised.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        LogAssertion AssertionName, (ActualNumber = ExpectedNumber), _
            "expected error=" & CStr(ExpectedNumber) & "; actual error=" & CStr(ActualNumber)

End Sub


Public Function WithinTolerance( _
    ByVal Expected As Double, _
    ByVal Actual As Double, _
    ByVal AbsoluteTolerance As Double, _
    ByVal RelativeTolerance As Double) _
    As Boolean
'
'==============================================================================
'                               WithinTolerance
'------------------------------------------------------------------------------
' PURPOSE
'   The comparison rule of AssertNear, exposed so that suites can test it.
'
' RETURNS
'   True when |Actual - Expected| <= max(AbsoluteTolerance,
'   RelativeTolerance * |Expected|); the bound is inclusive.
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim Bound   As Double    'Larger of the two bounds

'------------------------------------------------------------------------------
' COMPARE
'------------------------------------------------------------------------------
        Bound = RelativeTolerance * Abs(Expected)
        If AbsoluteTolerance > Bound Then
            Bound = AbsoluteTolerance
        End If
        WithinTolerance = (Abs(Actual - Expected) <= Bound)

End Function


'
'------------------------------------------------------------------------------
'
'                                     LOG
'
'------------------------------------------------------------------------------
'

Public Sub Say( _
    ByVal Text As String)
'
'==============================================================================
'                                     Say
'------------------------------------------------------------------------------
' PURPOSE
'   Write one log record to the Immediate window and keep it for LogText.
'
' ERROR POLICY
'   A host without an Immediate window raises on Debug.Print; that failure
'   is ignored, because the kept log, not the window, is the record of a run.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        If mLog Is Nothing Then
            Set mLog = New Collection
        End If
        mLog.Add Text
        On Error Resume Next
        Debug.Print Text
        On Error GoTo 0

End Sub


Public Function LogText() _
    As String
'
'==============================================================================
'                                   LogText
'------------------------------------------------------------------------------
' PURPOSE
'   Every record kept since the last BeginRun or ResetTests, one per line,
'   separated by line feeds, without a final separator. The harness writes
'   no file: a host adapter saves this text, outside the checkout or in the
'   ignored test-results/ directory.
'
' RETURNS
'   The log text; an empty string before the first record.
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim i       As Long      'Position in the log
    Dim Text    As String    'Log text built so far

'------------------------------------------------------------------------------
' JOIN
'------------------------------------------------------------------------------
        If Not mLog Is Nothing Then
            For i = 1 To mLog.Count
                If i > 1 Then
                    Text = Text & vbLf
                End If
                Text = Text & CStr(mLog.Item(i))
            Next i
        End If
        LogText = Text

End Function


Public Function LastResult() _
    As String
'
'==============================================================================
'                                  LastResult
'------------------------------------------------------------------------------
' PURPOSE
'   The RESULT record of the last finished or refused run; empty before the
'   first.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        LastResult = mLastResult

End Function


'
'------------------------------------------------------------------------------
'
'                              INTERNAL PROCEDURES
'
'------------------------------------------------------------------------------
'

Private Sub LogAssertion( _
    ByVal AssertionName As String, _
    ByVal Passed As Boolean, _
    ByVal Detail As String)
'
'==============================================================================
'                                 LogAssertion
'------------------------------------------------------------------------------
' PURPOSE
'   Count one assertion, log its outcome and record it when it failed.
'
' ERROR POLICY
'   Raises ERR_TEST_USAGE outside a run. An assertion outside a case is
'   counted and recorded as a failure.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        RequireActiveRun "an assertion"
        mAssertionCount = mAssertionCount + 1
        If Len(mCurrentCase) = 0 Then
            RecordFailure "harness.no-case", "assertion '" & AssertionName & "' outside a case"
        End If
        If Passed Then
            Say "ASSERT=" & mCurrentCase & "/" & AssertionName & "; status=PASS"
        Else
            Say "ASSERT=" & mCurrentCase & "/" & AssertionName & "; status=FAIL; " & Detail
            RecordFailure mCurrentCase & "/" & AssertionName, Detail
        End If

End Sub


Private Sub RecordFailure( _
    ByVal FailureId As String, _
    ByVal Detail As String)
'
'==============================================================================
'                                RecordFailure
'------------------------------------------------------------------------------
' PURPOSE
'   Count and log one failure; the first one of a run is its primary failure.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        mFailureCount = mFailureCount + 1
        If Len(mPrimaryFailure) = 0 Then
            mPrimaryFailure = FailureId & "; " & Detail
        End If
        Say "FAILURE=" & FailureId & "; " & Detail

End Sub


Private Sub RequireActiveRun( _
    ByVal Caller As String)
'
'==============================================================================
'                               RequireActiveRun
'------------------------------------------------------------------------------
' PURPOSE
'   Refuse a lifecycle call or an assertion made outside BeginRun..EndRun.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        If Not mRunActive Then
            Err.Raise ERR_TEST_USAGE, "TEST_LCR_Harness", _
                "No test run is active for " & Caller & "; call BeginRun first."
        End If

End Sub


Private Function IsCaseId( _
    ByVal CaseId As String) _
    As Boolean
'
'==============================================================================
'                                   IsCaseId
'------------------------------------------------------------------------------
' PURPOSE
'   Whether CaseId is lower-case kebab-case: a-z and 0-9 in groups joined by
'   single hyphens, as the test-case files use (TEST_CASES.md, Files).
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim Character   As String    'Character under test
    Dim i           As Long      'Position in CaseId

'------------------------------------------------------------------------------
' CHECK
'------------------------------------------------------------------------------
        If Len(CaseId) = 0 Or Left$(CaseId, 1) = "-" Or Right$(CaseId, 1) = "-" Then
            IsCaseId = False
            Exit Function
        End If
        If InStr(CaseId, "--") > 0 Then
            IsCaseId = False
            Exit Function
        End If
        For i = 1 To Len(CaseId)
            Character = Mid$(CaseId, i, 1)
            If Not (Character Like "[a-z0-9-]") Then
                IsCaseId = False
                Exit Function
            End If
        Next i
        IsCaseId = True

End Function


Private Function IsKnownCase( _
    ByVal CaseId As String) _
    As Boolean
'
'==============================================================================
'                                 IsKnownCase
'------------------------------------------------------------------------------
' PURPOSE
'   Whether CaseId already started in this run.
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim Found   As Variant    'Item stored under CaseId, when present

'------------------------------------------------------------------------------
' LOOK UP
'------------------------------------------------------------------------------
    'A Collection raises error 5 for an unknown key; that error is the answer.
        On Error Resume Next
        Found = mCaseIds.Item(CaseId)
        IsKnownCase = (Err.Number = 0)
        On Error GoTo 0

End Function


Private Function NumberText( _
    ByVal Value As Double) _
    As String
'
'==============================================================================
'                                  NumberText
'------------------------------------------------------------------------------
' PURPOSE
'   A Double as text that does not depend on the regional settings: Str$
'   always uses a period as the decimal separator. Str$ drops the zero
'   before the point (" .75"), which is put back ("0.75", "-0.75").
'
' UPDATED
'   2026-11-13
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim Text   As String    'Str$ result without its sign space

'------------------------------------------------------------------------------
' FORMAT
'------------------------------------------------------------------------------
        Text = Trim$(Str$(Value))
        If Left$(Text, 1) = "." Then
            Text = "0" & Text
        ElseIf Left$(Text, 2) = "-." Then
            Text = "-0" & Mid$(Text, 2)
        End If
        NumberText = Text

End Function


Private Sub ResetRunState()
'
'==============================================================================
'                                ResetRunState
'------------------------------------------------------------------------------
' PURPOSE
'   Return the counters, case identifiers, failures and flags of a run to
'   their idle values; the recovery flag and the log are left to callers.
'
' UPDATED
'   2026-11-13
'==============================================================================
'
        mRunActive = False
        mSuite = vbNullString
        mExpectedCases = 0
        mExpectedAssertions = 0
        mCaseCount = 0
        mAssertionCount = 0
        mFailureCount = 0
        mErrorCount = 0
        mCurrentCase = vbNullString
        Set mCaseIds = New Collection
        mPrimaryFailure = vbNullString

End Sub
