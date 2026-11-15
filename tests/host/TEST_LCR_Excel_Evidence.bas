Attribute VB_Name = "TEST_LCR_Excel_Evidence"
'==============================================================================
' MODULE: TEST_LCR_Excel_Evidence
'------------------------------------------------------------------------------
' PURPOSE
'   Record a run of the neutral harness in Excel as evidence: run the
'   example suite in its four modes, save each complete log, run the
'   verification of the modes, and record the host and whether its state
'   was the same after the runs as before. tools/check_excel_run.py checks
'   the folder against the candidate commit, without Excel.
'
' PUBLIC SURFACE
'   SaveHarnessEvidence. Option Private Module keeps it out of the
'   workbook's external surface.
'
' DEPENDENCIES
'   TEST_LCR_Harness and TEST_LCR_Examples; the VBA file statements and the
'   Excel Application object, which the harness itself never touches.
'
' STATE OWNERSHIP
'   Owns nothing between calls. It reads the host state and changes none;
'   it writes only the files named below, in the folder it is given.
'
' ERROR POLICY
'   The error that ends each run of the suite is its reported outcome: it
'   is printed after the log is saved, not raised, so that every file is
'   written. Whether the runs ended as documented is judged by
'   tools/check_excel_run.py, never here. A folder that was not prepared by
'   a workbook build raises ERR_EVIDENCE_FOLDER; a file error propagates
'   after its file is closed.
'
' USAGE
'   In a development workbook built from the candidate commit, type
'   TEST_LCR_Excel_Evidence.SaveHarnessEvidence "<folder>" in the Immediate
'   window (INSTALLATION.md, Recording host evidence).
'
' STATUS
'   Source only. It has not been compiled or run in Excel: that run is #15.
'
' UPDATED
'   2026-11-15
'
' AUTHOR
'   Daniele Penza
'==============================================================================

'------------------------------------------------------------------------------
' MODULE SETTINGS
'------------------------------------------------------------------------------
    'Require explicit declarations; keep the recorder inside the project.
    Option Explicit
    Option Private Module

'------------------------------------------------------------------------------
' MODULE CONSTANTS
'------------------------------------------------------------------------------
    'Raised when the folder holds no record of the workbook build. Kept apart
    'from the harness range (&H80040FE0 to &H80040FE2) and from the example
    'suite (&H80040FE8). Written as a literal equal to vbObjectError + 4080.
        Public Const ERR_EVIDENCE_FOLDER    As Long = &H80040FF0   'vbObjectError + 4080: Folder not prepared
    'The record of the workbook build, written by tools/Sync-KLCR-VBA.ps1
    'or by hand before the run.
        Private Const CANDIDATE_FILE        As String = "candidate.txt"
    'The files this recorder writes; host.txt is written after the run, by
    'hand. An earlier run's files are removed first.
        Private Const OUTPUT_FILES          As String = _
            "normal.log|injected.log|skipped.log|cleanup.log|verification.txt|" & _
            "environment.txt|host-state.txt|host.txt"


'
'------------------------------------------------------------------------------
'
'                                 ENTRY POINT
'
'------------------------------------------------------------------------------
'

Public Sub SaveHarnessEvidence( _
    ByVal Folder As String)
'
'==============================================================================
'                             SaveHarnessEvidence
'------------------------------------------------------------------------------
' PURPOSE
'   Run the example suite in each of its four modes and save each complete
'   log in Folder: normal.log, injected.log, skipped.log and cleanup.log.
'   Then save the report of TEST_LCR_Examples.VerifyExampleModes as
'   verification.txt, the host as environment.txt and the host state
'   before and after the runs as host-state.txt.
'
' INPUTS
'   Folder: the evidence folder of the workbook build, holding
'   candidate.txt; in the ignored test-results/ directory or outside the
'   checkout; without a trailing separator.
'
' ERROR POLICY
'   Raises ERR_EVIDENCE_FOLDER when Folder holds no candidate.txt. The
'   cleanup problem of CLEANUP_PROBLEM is simulated: it is acknowledged
'   with ResetTests after its log is saved, but only when that run
'   completed and only its cleanup failed. A refused start is left as it
'   was found, for the manual check that ResetTests stands for.
'
' UPDATED
'   2026-11-15
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim Separator   As String     'Path separator of the host
    Dim Leftover    As Variant    'File name an earlier run left in Folder
    Dim Before      As String     'Host state before the runs
    Dim After       As String     'Host state after the runs

'------------------------------------------------------------------------------
' REQUIRE A PREPARED FOLDER
'------------------------------------------------------------------------------
    'candidate.txt binds the folder to the build of one commit; without it,
    'the logs could not be tied to the source they ran.
        Separator = Application.PathSeparator
        If Len(Dir$(Folder & Separator & CANDIDATE_FILE)) = 0 Then
            Err.Raise ERR_EVIDENCE_FOLDER, "TEST_LCR_Excel_Evidence.SaveHarnessEvidence", _
                "No " & CANDIDATE_FILE & " in the folder: build the workbook into it first."
        End If
        For Each Leftover In Split(OUTPUT_FILES, "|")
            If Len(Dir$(Folder & Separator & CStr(Leftover))) > 0 Then
                Kill Folder & Separator & CStr(Leftover)
            End If
        Next Leftover

'------------------------------------------------------------------------------
' RUN, SAVE AND VERIFY
'------------------------------------------------------------------------------
        Before = HostState()
        SaveRun "NORMAL", Folder & Separator & "normal.log"
        SaveRun "INJECTED_FAILURE", Folder & Separator & "injected.log"
        SaveRun "SKIPPED_CASE", Folder & Separator & "skipped.log"
        SaveRun "CLEANUP_PROBLEM", Folder & Separator & "cleanup.log"
        WriteText Folder & Separator & "verification.txt", TEST_LCR_Examples.VerifyExampleModes()
        After = HostState()

'------------------------------------------------------------------------------
' RECORD THE HOST
'------------------------------------------------------------------------------
        WriteText Folder & Separator & "environment.txt", EnvironmentRecord()
        WriteText Folder & Separator & "host-state.txt", _
            "before=" & Before & vbLf & "after=" & After & vbLf & _
            "cleanup=" & IIf(Before = After, "PASS", "FAIL")
        Report "EVIDENCE=saved; files=7; cleanup=" & IIf(Before = After, "PASS", "FAIL")

End Sub


'
'------------------------------------------------------------------------------
'
'                              INTERNAL PROCEDURES
'
'------------------------------------------------------------------------------
'

Private Sub SaveRun( _
    ByVal Mode As String, _
    ByVal Path As String)
'
'==============================================================================
'                                   SaveRun
'------------------------------------------------------------------------------
' PURPOSE
'   Run the example suite in Mode, save its log to Path and print how the
'   run ended.
'
' ERROR POLICY
'   The run's own error is captured and printed after the log is saved; an
'   error of WriteText propagates.
'
' UPDATED
'   2026-11-15
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim RunError     As Long      'Error that ended the run; 0 for none
    Dim Outcome      As String    'RESULT record of the run

'------------------------------------------------------------------------------
' RUN AND SAVE
'------------------------------------------------------------------------------
        On Error Resume Next
        Select Case Mode
            Case "NORMAL"
                TEST_LCR_Examples.RunExampleTests
            Case "INJECTED_FAILURE"
                TEST_LCR_Examples.RunExampleTestsWithInjectedFailure
            Case "SKIPPED_CASE"
                TEST_LCR_Examples.RunExampleTestsWithSkippedCase
            Case "CLEANUP_PROBLEM"
                TEST_LCR_Examples.RunExampleTestsWithCleanupProblem
        End Select
        RunError = Err.Number
        On Error GoTo 0
        WriteText Path, TEST_LCR_Harness.LogText()
        Outcome = TEST_LCR_Harness.LastResult()
        Report "SAVED=" & Mode & "; error=" & CStr(RunError)

    'The simulated cleanup problem changed no host state: acknowledge it, but
    'only when the run itself completed and its cleanup alone failed.
        If Mode = "CLEANUP_PROBLEM" And InStr(Outcome, "; operation=PASS;") > 0 _
            And InStr(Outcome, "; cleanup=FAIL;") > 0 Then
            TEST_LCR_Harness.ResetTests
        End If

End Sub


Private Function HostState() _
    As String
'
'==============================================================================
'                                  HostState
'------------------------------------------------------------------------------
' PURPOSE
'   The Excel settings a suite could leave changed, and the number of open
'   workbooks, as one line; two equal lines mean the state was kept.
'
' UPDATED
'   2026-11-15
'==============================================================================
'
        HostState = "calculation=" & CStr(Application.Calculation) & _
            "; alerts=" & CStr(Application.DisplayAlerts) & _
            "; events=" & CStr(Application.EnableEvents) & _
            "; screen=" & CStr(Application.ScreenUpdating) & _
            "; workbooks=" & CStr(Application.Workbooks.Count)

End Function


Private Function EnvironmentRecord() _
    As String
'
'==============================================================================
'                              EnvironmentRecord
'------------------------------------------------------------------------------
' PURPOSE
'   Describe the Excel host and the compiled VBA environment, one field per
'   line: host, version, build, os, office (bitness), runtime (VBA
'   generation) and the decimal separator and country of the locale. It
'   holds no machine name, user or path.
'
' UPDATED
'   2026-11-15
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim Bitness   As String    'Office bitness, from conditional compilation
    Dim Runtime   As String    'VBA generation, from conditional compilation

'------------------------------------------------------------------------------
' DESCRIBE
'------------------------------------------------------------------------------
#If Win64 Then
        Bitness = "64-bit"
#Else
        Bitness = "32-bit"
#End If
#If VBA7 Then
        Runtime = "VBA7"
#Else
        Runtime = "VBA6"
#End If
        EnvironmentRecord = "host=" & Application.Name & vbLf & _
            "version=" & Application.Version & vbLf & _
            "build=" & CStr(Application.Build) & vbLf & _
            "os=" & Application.OperatingSystem & vbLf & _
            "office=" & Bitness & vbLf & _
            "runtime=" & Runtime & vbLf & _
            "decimal=" & CStr(Application.International(xlDecimalSeparator)) & vbLf & _
            "country=" & CStr(Application.International(xlCountrySetting))

End Function


Private Sub Report( _
    ByVal Text As String)
'
'==============================================================================
'                                    Report
'------------------------------------------------------------------------------
' PURPOSE
'   Print one progress line to the Immediate window.
'
' ERROR POLICY
'   A host without an Immediate window raises on Debug.Print; that failure
'   is ignored, because the files, not the window, are the evidence.
'
' UPDATED
'   2026-11-15
'==============================================================================
'
        On Error Resume Next
        Debug.Print Text
        On Error GoTo 0

End Sub


Private Sub WriteText( _
    ByVal Path As String, _
    ByVal Text As String)
'
'==============================================================================
'                                  WriteText
'------------------------------------------------------------------------------
' PURPOSE
'   Write Text to a file, created or overwritten, ending with one line end.
'
' ERROR POLICY
'   A file error is re-raised after the file is closed.
'
' UPDATED
'   2026-11-15
'==============================================================================
'

'------------------------------------------------------------------------------
' DECLARE
'------------------------------------------------------------------------------
    Dim FileNumber         As Integer    'Handle of the open file
    Dim ErrorNumber        As Long       'File error number
    Dim ErrorSource        As String     'File error source
    Dim ErrorDescription   As String     'File error description

'------------------------------------------------------------------------------
' WRITE
'------------------------------------------------------------------------------
        FileNumber = FreeFile
        Open Path For Output As #FileNumber
        On Error GoTo WriteFailed
        Print #FileNumber, Text
        Close #FileNumber
        Exit Sub

'------------------------------------------------------------------------------
' HANDLE A WRITE ERROR
'------------------------------------------------------------------------------
WriteFailed:
        ErrorNumber = Err.Number
        ErrorSource = Err.Source
        ErrorDescription = Err.Description
        On Error GoTo 0
        Close #FileNumber
        Err.Raise ErrorNumber, ErrorSource, ErrorDescription

End Sub
