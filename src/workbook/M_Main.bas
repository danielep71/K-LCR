Attribute VB_Name = "M_Main"
'==============================================================================
' MODULE: M_Main
'------------------------------------------------------------------------------
' PURPOSE
'   Command macros of the K-LCR workbook and their automation entry points:
'   read Params and the input sheets, validate every line, aggregate the
'   weighted amounts per scope (each currency and TOTAL), call CORE_Engine
'   for the buffer, the net liquidity outflow and the ratio, and write
'   Results, LineCalc and Checks.
'
' PUBLIC SURFACE
'   RunLCR, ValidateInputs, ClearOutputs     Buttons on the sheets
'   AutomationRun, AutomationValidate        Silent runs; return the summary
'
' DEPENDENCIES
'   CORE_Config (layout, codes), CORE_Engine (regulatory aggregates).
'
' STATE OWNERSHIP
'   Reads Params, HQLA, Outflows, Inflows; writes the data rows of Results,
'   LineCalc and Checks and the status cells of Results. Changes
'   ScreenUpdating, Calculation and EnableEvents for the duration of an
'   operation and restores them. Module state holds the parameters and lines
'   of the operation in progress only; every operation resets it.
'
' ERROR POLICY
'   Input problems are findings on Checks, not errors. Unexpected errors are
'   shown in a message box by the button macros and re-raised by the
'   automation entry points, after the Excel state has been restored.
'
' COMPATIBILITY
'   Excel VBA, Windows 64-bit primary target; no references beyond the
'   defaults; no Scripting.Dictionary (Collection keys only).
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
    'Require explicit declarations.
    Option Explicit

'------------------------------------------------------------------------------
' MODULE STATE
'------------------------------------------------------------------------------
    'Checks lines of the operation in progress.
        Private mCheckData()       As Variant       '(1 To CHK_WIDTH, 1 To capacity)
        Private mCheckCount        As Long          'Lines written so far
        Private mErrorCount        As Long          'ERROR lines
        Private mWarningCount      As Long          'WARNING lines
    'Parameters.
        Private mParamValue        As Collection    'Code -> cell value
        Private mParamRow          As Collection    'Code -> row on Params
        Private mParamsValid       As Boolean       'False stops the calculation
        Private mAsOfDate          As Date
        Private mReportingCcy      As String
        Private mRequirement       As Double        'Minimum LCR, 1 = 100%
        Private mShareL1exCB       As Double
        Private mShareL1           As Double
        Private mShareL2B          As Double
        Private mCapStandard       As Double
        Private mCapHigher         As Double
        Private mWithhold          As Boolean
    'Category catalogue.
        Private mCatIndex          As Collection    'Code -> index
        Private mCatCode()         As String
        Private mCatType()         As String
        Private mCatClass()        As String
        Private mCatFactor()       As Double
        Private mCatCount          As Long
    'FX table.
        Private mFxIndex           As Collection    'Currency -> index
        Private mFxCcy()           As String
        Private mFxRate()          As Double        'Units of reporting ccy per unit
        Private mFxCount           As Long
    'Input lines of every input sheet, in sheet and row order.
        Private mLineCount         As Long
        Private mLineSheet()       As String
        Private mLineRow()         As Long
        Private mLineID()          As String
        Private mLineCategory()    As String
        Private mLineType()        As String        'HQLA, OUTFLOW, INFLOW
        Private mLineClass()       As String        'Level or cap class
        Private mLineCcy()         As String
        Private mLineAmount()      As Variant       'Double, or Empty when invalid
        Private mLineUnwind()      As Variant       'Double (HQLA), or Empty
        Private mLineFactor()      As Variant       'Double, or Empty when unknown
        Private mLineCcyValid()    As Boolean
        Private mLineValid()       As Boolean
        Private mLineStatus()      As String
    'Scopes: each currency used by a line, then TOTAL.
        Private mScopeCount        As Long
        Private mScopeName()       As String
        Private mScopeIndex        As Collection    'Scope -> index
        Private mAcc()             As Double        '(1 To scopes, 1 To ACC_WIDTH)

'------------------------------------------------------------------------------
'                              COMMAND MACROS
'------------------------------------------------------------------------------

Public Sub RunLCR()
'------------------------------------------------------------------------------
' PURPOSE
'   Button "Run LCR": validate, calculate and write every output sheet.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Summary            As String    'Outcome shown to the user

        Summary = ExecuteOperation(True, False)
End Sub


Public Sub ValidateInputs()
'------------------------------------------------------------------------------
' PURPOSE
'   Button "Validate inputs": write every finding on Checks without
'   calculating; Results and LineCalc are left unchanged.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Summary            As String    'Outcome shown to the user

        Summary = ExecuteOperation(False, False)
End Sub


Public Sub ClearOutputs()
'------------------------------------------------------------------------------
' PURPOSE
'   Button "Clear outputs": empty the data rows of Results, LineCalc and
'   Checks and reset the Results status cells. Formats are kept.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim SavedScreen        As Boolean   'ScreenUpdating before the operation

        SavedScreen = Application.ScreenUpdating
        Application.ScreenUpdating = False
        On Error GoTo Failed
        ClearOutputArea
        Application.ScreenUpdating = SavedScreen
        Exit Sub
Failed:
        Application.ScreenUpdating = SavedScreen
        MsgBox "Clear outputs failed: " & Err.Description, vbExclamation, "K-LCR"
End Sub


Public Function AutomationRun() As String
'------------------------------------------------------------------------------
' PURPOSE
'   Silent "Run LCR" for scripts and tests: no message box.
'
' RETURNS
'   The summary written to Results!C5.
'
' ERROR POLICY
'   Re-raises any unexpected error after the Excel state is restored.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        AutomationRun = ExecuteOperation(True, True)
End Function


Public Function AutomationValidate() As String
'------------------------------------------------------------------------------
' PURPOSE
'   Silent "Validate inputs" for scripts and tests.
'
' RETURNS
'   The validation summary.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        AutomationValidate = ExecuteOperation(False, True)
End Function


'------------------------------------------------------------------------------
'                                OPERATION
'------------------------------------------------------------------------------

Private Function ExecuteOperation( _
    ByVal Calculate As Boolean, _
    ByVal Silent As Boolean) _
    As String
'------------------------------------------------------------------------------
' PURPOSE
'   Run one validation or calculation from start to end with the Excel state
'   captured and restored.
'
' INPUTS
'   Calculate  True to calculate and write the outputs; False to validate
'   Silent     True to suppress message boxes and re-raise errors
'
' RETURNS
'   A one-line summary of the outcome.
'
' ERROR POLICY
'   Preserves the primary error across cleanup (house style); shows it when
'   not Silent, re-raises it when Silent.
'
' STATE OWNERSHIP
'   ScreenUpdating, Calculation and EnableEvents, restored on every path.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim SavedCalculation   As Long      'Calculation mode before the operation
    Dim SavedScreen        As Boolean   'ScreenUpdating before the operation
    Dim SavedEvents        As Boolean   'EnableEvents before the operation
    Dim StateCaptured      As Boolean   'True once the three were read
    Dim Summary            As String    'Outcome
    Dim ErrNumber          As Long      'Primary error number; 0 for none
    Dim ErrSource          As String    'Primary error source
    Dim ErrDescription     As String    'Primary error description

        On Error GoTo Failed
        SavedCalculation = Application.Calculation
        SavedScreen = Application.ScreenUpdating
        SavedEvents = Application.EnableEvents
        StateCaptured = True
        Application.ScreenUpdating = False
        Application.EnableEvents = False
        Application.Calculation = xlCalculationManual

        ResetState
        LoadParams
        If mParamsValid Then
            LoadLines SH_HQLA, TYPE_HQLA, IN_LAST_COL_HQLA
            LoadLines SH_OUTFLOWS, TYPE_OUTFLOW, IN_LAST_COL_FLOW
            LoadLines SH_INFLOWS, TYPE_INFLOW, IN_LAST_COL_FLOW
        End If

        If Calculate Then
            ClearOutputArea
            If mParamsValid Then
                BuildScopes
                Aggregate
                Summary = WriteResults()
                WriteLineCalc
            Else
                Summary = "Run stopped: " & mErrorCount & " parameter error(s); see Checks."
                GetSheet(SH_RESULTS).Cells(RES_STATUS_ROW, RES_FIRST_COL).Value = _
                    "Last run " & Format$(Now, "yyyy-mm-dd hh:mm:ss") & " stopped."
                GetSheet(SH_RESULTS).Cells(RES_SUMMARY_ROW, RES_FIRST_COL).Value = Summary
            End If
        Else
            Summary = "Validation: " & mLineCount & " line(s); " & mErrorCount & " error(s), " & _
                      mWarningCount & " warning(s)."
            AddCheck SEV_INFO, vbNullString, 0, vbNullString, Summary, D_RUN_SUMMARY
        End If
        WriteChecks
        GetSheet(SH_RESULTS).Calculate

CleanUp:
        On Error GoTo 0
        If StateCaptured Then
            On Error Resume Next
            Application.Calculation = SavedCalculation
            Application.EnableEvents = SavedEvents
            Application.ScreenUpdating = SavedScreen
            On Error GoTo 0
        End If
        If ErrNumber <> 0 Then
            If Silent Then Err.Raise ErrNumber, ErrSource, ErrDescription
            MsgBox "K-LCR stopped on an unexpected error." & vbCrLf & vbCrLf & ErrDescription & _
                   vbCrLf & "(" & ErrSource & ", " & ErrNumber & ")", vbCritical, "K-LCR"
            ExecuteOperation = "ERROR: " & ErrDescription
            Exit Function
        End If
        If Not Silent Then
            If mErrorCount > 0 Then
                GetSheet(SH_CHECKS).Activate
            ElseIf Calculate Then
                GetSheet(SH_RESULTS).Activate
            End If
            MsgBox Summary, IIf(mErrorCount > 0, vbExclamation, vbInformation), "K-LCR"
        End If
        ExecuteOperation = Summary
        Exit Function

Failed:
        ErrNumber = Err.Number
        ErrSource = Err.Source
        ErrDescription = Err.Description
        Resume CleanUp
End Function


Private Sub ResetState()
'------------------------------------------------------------------------------
' PURPOSE
'   Empty the module state before an operation.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        ReDim mCheckData(1 To CHK_WIDTH, 1 To 64)
        mCheckCount = 0
        mErrorCount = 0
        mWarningCount = 0
        Set mParamValue = New Collection
        Set mParamRow = New Collection
        Set mCatIndex = New Collection
        Set mFxIndex = New Collection
        Set mScopeIndex = New Collection
        mParamsValid = True
        mCatCount = 0
        mFxCount = 0
        mLineCount = 0
        mScopeCount = 0
End Sub


'------------------------------------------------------------------------------
'                                PARAMETERS
'------------------------------------------------------------------------------

Private Sub LoadParams()
'------------------------------------------------------------------------------
' PURPOSE
'   Read and validate the scalar parameters, the category catalogue and the
'   FX table of Params. Clears mParamsValid when the run cannot proceed.
'
' STATE OWNERSHIP
'   Reads Params; fills the parameter, catalogue and FX module state.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim ws                 As Worksheet 'Params
    Dim r                  As Long      'Row on Params
    Dim Code               As String    'Parameter code in column C
    Dim Value              As Variant   'Parameter value in column E

        Set ws = GetSheet(SH_PARAMS)
        r = PARAM_FIRST_ROW
        Do While Len(Trim$(CStr(ws.Cells(r, PARAM_CODE_COL).Value))) > 0
            Code = Trim$(CStr(ws.Cells(r, PARAM_CODE_COL).Value))
            If Not HasKey(mParamValue, Code) Then
                'Read into a Variant first: the item must be the value, not the cell.
                Value = ws.Cells(r, PARAM_VALUE_COL).Value
                mParamValue.Add Value, Code
                mParamRow.Add r, Code
            End If
            r = r + 1
            If r > PARAM_FIRST_ROW + TABLE_SCAN_ROWS Then Exit Do
        Loop

        'Reporting date.
        Value = ParamValue(P_ASOFDATE)
        If IsDate(Value) Then
            mAsOfDate = CDate(Value)
        ElseIf IsNumber(Value) Then
            mAsOfDate = CDate(CDbl(Value))
        Else
            ParamProblem P_ASOFDATE, "must be a date"
        End If
        'Reporting currency.
        mReportingCcy = UCase$(Trim$(CStr(ParamValue(P_REPORTING_CCY))))
        If Len(mReportingCcy) = 0 Then ParamProblem P_REPORTING_CCY, "must be a currency code"
        'Ratios and caps.
        mRequirement = ReadShare(P_REQUIREMENT, 0#, 10#, False)
        mShareL1exCB = ReadShare(P_SHARE_L1EXCB, 0#, 1#, False)
        mShareL1 = ReadShare(P_SHARE_L1, 0#, 1#, False)
        mShareL2B = ReadShare(P_SHARE_L2B, 0#, 1#, True)
        mCapStandard = ReadShare(P_CAP_STANDARD, 0#, 1#, False)
        mCapHigher = ReadShare(P_CAP_HIGHER, 0#, 1#, False)
        'Withholding policy.
        Value = ParamValue(P_WITHHOLD)
        Select Case UCase$(Trim$(CStr(Value)))
            Case "TRUE", "VERO", "1", "-1": mWithhold = True
            Case "FALSE", "FALSO", "0": mWithhold = False
            Case Else
                ParamProblem P_WITHHOLD, "must be TRUE or FALSE"
        End Select

        LoadCatalogue ws
        LoadFx ws
        If mParamsValid Or Len(mReportingCcy) > 0 Then
            If Not HasKey(mFxIndex, mReportingCcy) Then
                AddCheck SEV_ERROR, SH_PARAMS, RowOfParam(P_REPORTING_CCY), P_REPORTING_CCY, _
                         "Reporting currency " & mReportingCcy & " is not in the FX table.", D_PARAM_CCY
                mParamsValid = False
            ElseIf Abs(mFxRate(mFxIndex.Item(mReportingCcy)) - 1#) > 0.0000001 Then
                AddCheck SEV_WARNING, SH_PARAMS, RowOfParam(P_REPORTING_CCY), P_REPORTING_CCY, _
                         "FX rate of the reporting currency " & mReportingCcy & " is " & _
                         CStr(mFxRate(mFxIndex.Item(mReportingCcy))) & ", not 1; amounts are converted with it.", _
                         D_PARAM_CCY
            End If
        End If
End Sub


Private Function ReadShare( _
    ByVal Code As String, _
    ByVal LowerBound As Double, _
    ByVal UpperBound As Double, _
    ByVal LowerIncluded As Boolean) _
    As Double
'------------------------------------------------------------------------------
' PURPOSE
'   Read a numeric parameter that must lie in (LowerBound, UpperBound], or
'   [LowerBound, UpperBound) when LowerIncluded; report it otherwise.
'
' RETURNS
'   The value, or 0 when invalid (mParamsValid is then False).
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Value              As Variant   'Cell value
    Dim Valid              As Boolean   'True when in its domain

        Value = ParamValue(Code)
        If IsNumber(Value) Then
            If LowerIncluded Then
                Valid = (CDbl(Value) >= LowerBound And CDbl(Value) < UpperBound)
            Else
                Valid = (CDbl(Value) > LowerBound And CDbl(Value) <= UpperBound)
            End If
        End If
        If Valid Then
            ReadShare = CDbl(Value)
        Else
            ParamProblem Code, "must be a number in " & IIf(LowerIncluded, "[", "(") & LowerBound & ", " & _
                         UpperBound & IIf(LowerIncluded, ")", "]")
        End If
End Function


Private Sub LoadCatalogue(ByVal ws As Worksheet)
'------------------------------------------------------------------------------
' PURPOSE
'   Read the category catalogue below its header label in column C.
'
' INPUTS
'   ws  The Params sheet
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim HeaderRow          As Long      'Row of the "Category" header
    Dim r                  As Long      'Row on Params
    Dim Code               As String    'Category code
    Dim TypeCode           As String    'HQLA, OUTFLOW, INFLOW
    Dim ClassCode          As String    'Level or cap class
    Dim Factor             As Variant   'Haircut or rate
    Dim Problem            As String    'Why the row is rejected

        HeaderRow = FindHeader(ws, CAT_HEADER_LABEL)
        If HeaderRow = 0 Then
            AddCheck SEV_ERROR, SH_PARAMS, 0, CAT_HEADER_LABEL, "Category catalogue not found: no cell '" & _
                     CAT_HEADER_LABEL & "' in column C.", D_CAT_INVALID
            mParamsValid = False
            Exit Sub
        End If
        ReDim mCatCode(1 To 16)
        ReDim mCatType(1 To 16)
        ReDim mCatClass(1 To 16)
        ReDim mCatFactor(1 To 16)
        r = HeaderRow + 1
        Do While Len(Trim$(CStr(ws.Cells(r, CAT_COL_CODE).Value))) > 0
            Code = UCase$(Trim$(CStr(ws.Cells(r, CAT_COL_CODE).Value)))
            TypeCode = UCase$(Trim$(CStr(ws.Cells(r, CAT_COL_TYPE).Value)))
            ClassCode = UCase$(Trim$(CStr(ws.Cells(r, CAT_COL_CLASS).Value)))
            Factor = ws.Cells(r, CAT_COL_FACTOR).Value
            Problem = vbNullString
            If HasKey(mCatIndex, Code) Then
                Problem = "duplicate category code"
            ElseIf Not IsNumber(Factor) Then
                Problem = "factor is not a number"
            ElseIf CDbl(Factor) < 0# Or CDbl(Factor) > 1# Then
                Problem = "factor must be between 0% and 100%"
            Else
                Select Case TypeCode
                    Case TYPE_HQLA
                        If ClassCode <> LVL_L1 And ClassCode <> LVL_L1CB And ClassCode <> LVL_L2A And _
                           ClassCode <> LVL_L2B Then Problem = "HQLA class must be L1, L1CB, L2A or L2B"
                    Case TYPE_INFLOW
                        If ClassCode <> CAP_75 And ClassCode <> CAP_90 And ClassCode <> CAP_EXEMPT Then _
                            Problem = "INFLOW class must be 75, 90 or EXEMPT"
                    Case TYPE_OUTFLOW
                    Case Else
                        Problem = "type must be HQLA, OUTFLOW or INFLOW"
                End Select
            End If
            If Len(Problem) > 0 Then
                AddCheck SEV_ERROR, SH_PARAMS, r, Code, "Catalogue row ignored: " & Problem & ".", _
                         IIf(Problem = "duplicate category code", D_DUPLICATE_KEY, D_CAT_INVALID)
            Else
                mCatCount = mCatCount + 1
                If mCatCount > UBound(mCatCode) Then
                    ReDim Preserve mCatCode(1 To 2 * mCatCount)
                    ReDim Preserve mCatType(1 To 2 * mCatCount)
                    ReDim Preserve mCatClass(1 To 2 * mCatCount)
                    ReDim Preserve mCatFactor(1 To 2 * mCatCount)
                End If
                mCatCode(mCatCount) = Code
                mCatType(mCatCount) = TypeCode
                mCatClass(mCatCount) = ClassCode
                mCatFactor(mCatCount) = CDbl(Factor)
                mCatIndex.Add mCatCount, Code
            End If
            r = r + 1
        Loop
End Sub


Private Sub LoadFx(ByVal ws As Worksheet)
'------------------------------------------------------------------------------
' PURPOSE
'   Read the FX table below its header label in column C.
'
' INPUTS
'   ws  The Params sheet
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim HeaderRow          As Long      'Row of the "FX_Ccy" header
    Dim r                  As Long      'Row on Params
    Dim Ccy                As String    'Currency code
    Dim Rate               As Variant   'Units of reporting ccy per unit

        HeaderRow = FindHeader(ws, FX_HEADER_LABEL)
        If HeaderRow = 0 Then
            AddCheck SEV_ERROR, SH_PARAMS, 0, FX_HEADER_LABEL, "FX table not found: no cell '" & _
                     FX_HEADER_LABEL & "' in column C.", D_FX_INVALID
            mParamsValid = False
            Exit Sub
        End If
        ReDim mFxCcy(1 To 8)
        ReDim mFxRate(1 To 8)
        r = HeaderRow + 1
        Do While Len(Trim$(CStr(ws.Cells(r, FX_COL_CCY).Value))) > 0
            Ccy = UCase$(Trim$(CStr(ws.Cells(r, FX_COL_CCY).Value)))
            Rate = ws.Cells(r, FX_COL_RATE).Value
            If HasKey(mFxIndex, Ccy) Then
                AddCheck SEV_ERROR, SH_PARAMS, r, Ccy, "FX row ignored: duplicate currency.", D_DUPLICATE_KEY
            ElseIf Not IsNumber(Rate) Then
                AddCheck SEV_ERROR, SH_PARAMS, r, Ccy, "FX row ignored: rate is not a number.", D_FX_INVALID
            ElseIf CDbl(Rate) <= 0# Then
                AddCheck SEV_ERROR, SH_PARAMS, r, Ccy, "FX row ignored: rate must be > 0.", D_FX_INVALID
            Else
                mFxCount = mFxCount + 1
                If mFxCount > UBound(mFxCcy) Then
                    ReDim Preserve mFxCcy(1 To 2 * mFxCount)
                    ReDim Preserve mFxRate(1 To 2 * mFxCount)
                End If
                mFxCcy(mFxCount) = Ccy
                mFxRate(mFxCount) = CDbl(Rate)
                mFxIndex.Add mFxCount, Ccy
            End If
            r = r + 1
        Loop
End Sub


Private Function ParamValue(ByVal Code As String) As Variant
'------------------------------------------------------------------------------
' PURPOSE
'   Return the value of a parameter, or Empty (with an ERROR) when its code
'   is missing from Params.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        If HasKey(mParamValue, Code) Then
            ParamValue = mParamValue.Item(Code)
        Else
            AddCheck SEV_ERROR, SH_PARAMS, 0, Code, "Parameter " & Code & " not found in column C.", _
                     D_PARAM_INVALID
            mParamsValid = False
            ParamValue = Empty
        End If
End Function


Private Function RowOfParam(ByVal Code As String) As Long
'------------------------------------------------------------------------------
' PURPOSE
'   Return the Params row of a parameter code, or 0 when absent.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        If HasKey(mParamRow, Code) Then RowOfParam = mParamRow.Item(Code)
End Function


Private Sub ParamProblem(ByVal Code As String, ByVal Problem As String)
'------------------------------------------------------------------------------
' PURPOSE
'   Report an invalid parameter (once it exists on Params) and stop the run.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        If HasKey(mParamValue, Code) Then
            AddCheck SEV_ERROR, SH_PARAMS, RowOfParam(Code), Code, "Parameter " & Code & " " & Problem & _
                     "; got '" & CStr(mParamValue.Item(Code)) & "'.", D_PARAM_INVALID
        End If
        mParamsValid = False
End Sub


'------------------------------------------------------------------------------
'                                  LINES
'------------------------------------------------------------------------------

Private Sub LoadLines( _
    ByVal SheetName As String, _
    ByVal TypeCode As String, _
    ByVal LastInputCol As Long)
'------------------------------------------------------------------------------
' PURPOSE
'   Read and validate every non-blank line of an input sheet and append it
'   to the line state, valid or not.
'
' INPUTS
'   SheetName     HQLA, Outflows or Inflows
'   TypeCode      Category type the sheet accepts (TYPE_ constant)
'   LastInputCol  Last input column of the sheet
'
' STATE OWNERSHIP
'   Reads the sheet; appends to the line state and to Checks.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim ws                 As Worksheet 'Input sheet
    Dim LastRow            As Long      'Last row with an input value
    Dim FirstLine          As Long      'Line count before this sheet
    Dim i                  As Long      'Row of Data
    Dim Data               As Variant   'Input block, 1-based
    Dim Seen               As Collection 'IDs of the sheet -> row
    Dim RowNumber          As Long      'Worksheet row of the line
    Dim n                  As Long      'Index of the new line
    Dim Reference          As String    'ID shown on Checks
    Dim Problems           As String    'Reasons the line is excluded
    Dim CatIdx             As Long      'Catalogue index, 0 when unknown
    Dim Amount             As Variant   'Amount cell
    Dim Unwind             As Variant   'Unwind adjustment cell

        Set ws = GetSheet(SheetName)
        'The used range covers the pre-formatted input rows; blank rows in it
        'are skipped below, so no End(xlUp) search is needed.
        LastRow = ws.UsedRange.Row + ws.UsedRange.Rows.Count - 1
        If LastRow < IN_FIRST_ROW Then
            AddCheck SEV_INFO, SheetName, 0, vbNullString, "No lines on " & SheetName & ".", D_RUN_SUMMARY
            Exit Sub
        End If
        Data = ws.Range(ws.Cells(IN_FIRST_ROW, IN_COL_ID), ws.Cells(LastRow, LastInputCol)).Value
        Set Seen = New Collection
        FirstLine = mLineCount

        For i = 1 To UBound(Data, 1)
            If Not RowIsBlank(Data, i) Then
                RowNumber = IN_FIRST_ROW + i - 1
                n = NewLine()
                mLineSheet(n) = SheetName
                mLineRow(n) = RowNumber
                mLineType(n) = TypeCode
                mLineID(n) = Trim$(CStr(Data(i, IN_COL_ID - IN_COL_ID + 1)))
                mLineCategory(n) = UCase$(Trim$(CStr(Data(i, IN_COL_CATEGORY - IN_COL_ID + 1))))
                mLineCcy(n) = UCase$(Trim$(CStr(Data(i, IN_COL_CCY - IN_COL_ID + 1))))
                Amount = Data(i, IN_COL_AMOUNT - IN_COL_ID + 1)
                Problems = vbNullString
                Reference = IIf(Len(mLineID(n)) > 0, mLineID(n), SheetName & "!C" & RowNumber)

                'Identifier.
                If Len(mLineID(n)) = 0 Then
                    Problems = Problems & "; missing ID"
                    AddCheck SEV_ERROR, SheetName, RowNumber, Reference, "Missing ID in column C.", D_ID_MISSING
                ElseIf HasKey(Seen, UCase$(mLineID(n))) Then
                    Problems = Problems & "; duplicate ID"
                    AddCheck SEV_ERROR, SheetName, RowNumber, Reference, "ID " & mLineID(n) & _
                             " already used in row " & Seen.Item(UCase$(mLineID(n))) & ".", D_ID_DUPLICATE
                Else
                    Seen.Add RowNumber, UCase$(mLineID(n))
                End If

                'Category.
                CatIdx = 0
                If HasKey(mCatIndex, mLineCategory(n)) Then CatIdx = mCatIndex.Item(mLineCategory(n))
                If CatIdx = 0 Then
                    Problems = Problems & "; unknown category"
                    AddCheck SEV_ERROR, SheetName, RowNumber, Reference, "Category '" & mLineCategory(n) & _
                             "' is not in the catalogue on Params.", D_CAT_UNKNOWN
                ElseIf mCatType(CatIdx) <> TypeCode Then
                    Problems = Problems & "; category of type " & mCatType(CatIdx)
                    AddCheck SEV_ERROR, SheetName, RowNumber, Reference, "Category " & mLineCategory(n) & _
                             " is of type " & mCatType(CatIdx) & "; " & SheetName & " accepts " & TypeCode & _
                             " categories only.", D_CAT_TYPE
                    mLineClass(n) = mCatClass(CatIdx)
                Else
                    mLineClass(n) = mCatClass(CatIdx)
                    mLineFactor(n) = mCatFactor(CatIdx)
                End If

                'Currency.
                mLineCcyValid(n) = HasKey(mFxIndex, mLineCcy(n))
                If Not mLineCcyValid(n) Then
                    Problems = Problems & "; unknown currency"
                    AddCheck SEV_ERROR, SheetName, RowNumber, Reference, "Currency '" & mLineCcy(n) & _
                             "' is not in the FX table on Params.", D_CCY_UNKNOWN
                End If

                'Amount.
                If IsEmpty(Amount) Then
                    Problems = Problems & "; missing amount"
                    AddCheck SEV_ERROR, SheetName, RowNumber, Reference, "Missing amount in column G.", _
                             D_AMOUNT_INVALID
                ElseIf Not IsNumber(Amount) Then
                    Problems = Problems & "; amount not a number"
                    AddCheck SEV_ERROR, SheetName, RowNumber, Reference, "Amount '" & CStr(Amount) & _
                             "' is not a number.", D_AMOUNT_INVALID
                ElseIf CDbl(Amount) < 0# Then
                    Problems = Problems & "; negative amount"
                    AddCheck SEV_ERROR, SheetName, RowNumber, Reference, "Amount " & CStr(Amount) & _
                             " is negative; enter amounts as positive values.", D_AMOUNT_NEGATIVE
                Else
                    mLineAmount(n) = CDbl(Amount)
                End If

                'Unwind adjustment (HQLA only).
                If TypeCode = TYPE_HQLA Then
                    Unwind = Data(i, IN_COL_UNWIND - IN_COL_ID + 1)
                    If IsEmpty(Unwind) Then
                        mLineUnwind(n) = 0#
                    ElseIf Not IsNumber(Unwind) Then
                        Problems = Problems & "; unwind adjustment not a number"
                        AddCheck SEV_ERROR, SheetName, RowNumber, Reference, "Unwind adjustment '" & _
                                 CStr(Unwind) & "' is not a number.", D_UNWIND_INVALID
                    Else
                        mLineUnwind(n) = CDbl(Unwind)
                        If Not IsEmpty(mLineAmount(n)) Then
                            If CDbl(mLineAmount(n)) + CDbl(Unwind) < 0# Then
                                AddCheck SEV_WARNING, SheetName, RowNumber, Reference, "Market value plus " & _
                                         "unwind adjustment is negative; kept as entered.", D_UNWIND_NEGATIVE
                            End If
                        End If
                    End If
                End If

                mLineValid(n) = (Len(Problems) = 0)
                If mLineValid(n) Then
                    mLineStatus(n) = "INCLUDED"
                Else
                    mLineStatus(n) = "EXCLUDED: " & Mid$(Problems, 3)
                End If
            End If
        Next i
        If mLineCount = FirstLine Then
            AddCheck SEV_INFO, SheetName, 0, vbNullString, "No lines on " & SheetName & ".", D_RUN_SUMMARY
        End If
End Sub


Private Function NewLine() As Long
'------------------------------------------------------------------------------
' PURPOSE
'   Append an empty line to the line state, growing the arrays by doubling.
'
' RETURNS
'   Index of the new line.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Capacity           As Long      'Current array size

        If mLineCount = 0 Then
            Capacity = 0
        Else
            Capacity = UBound(mLineID)
        End If
        mLineCount = mLineCount + 1
        If mLineCount > Capacity Then
            Capacity = IIf(Capacity < 64, 64, 2 * Capacity)
            If mLineCount = 1 Then
                ReDim mLineSheet(1 To Capacity)
                ReDim mLineRow(1 To Capacity)
                ReDim mLineID(1 To Capacity)
                ReDim mLineCategory(1 To Capacity)
                ReDim mLineType(1 To Capacity)
                ReDim mLineClass(1 To Capacity)
                ReDim mLineCcy(1 To Capacity)
                ReDim mLineAmount(1 To Capacity)
                ReDim mLineUnwind(1 To Capacity)
                ReDim mLineFactor(1 To Capacity)
                ReDim mLineCcyValid(1 To Capacity)
                ReDim mLineValid(1 To Capacity)
                ReDim mLineStatus(1 To Capacity)
            Else
                ReDim Preserve mLineSheet(1 To Capacity)
                ReDim Preserve mLineRow(1 To Capacity)
                ReDim Preserve mLineID(1 To Capacity)
                ReDim Preserve mLineCategory(1 To Capacity)
                ReDim Preserve mLineType(1 To Capacity)
                ReDim Preserve mLineClass(1 To Capacity)
                ReDim Preserve mLineCcy(1 To Capacity)
                ReDim Preserve mLineAmount(1 To Capacity)
                ReDim Preserve mLineUnwind(1 To Capacity)
                ReDim Preserve mLineFactor(1 To Capacity)
                ReDim Preserve mLineCcyValid(1 To Capacity)
                ReDim Preserve mLineValid(1 To Capacity)
                ReDim Preserve mLineStatus(1 To Capacity)
            End If
        End If
        mLineAmount(mLineCount) = Empty
        mLineUnwind(mLineCount) = Empty
        mLineFactor(mLineCount) = Empty
        mLineClass(mLineCount) = vbNullString
        NewLine = mLineCount
End Function


Private Function RowIsBlank(ByRef Data As Variant, ByVal i As Long) As Boolean
'------------------------------------------------------------------------------
' PURPOSE
'   Return True when every cell of row i of an input block is empty.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim c                  As Long      'Column of Data

        RowIsBlank = True
        For c = LBound(Data, 2) To UBound(Data, 2)
            If Not IsEmpty(Data(i, c)) Then
                If Len(Trim$(CStr(Data(i, c)))) > 0 Then
                    RowIsBlank = False
                    Exit Function
                End If
            End If
        Next c
End Function


'------------------------------------------------------------------------------
'                               AGGREGATION
'------------------------------------------------------------------------------

Private Sub BuildScopes()
'------------------------------------------------------------------------------
' PURPOSE
'   List the scopes: the reporting currency first when a line uses it, the
'   other currencies used by a line in FX-table order, then TOTAL.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim f                  As Long      'FX table index
    Dim n                  As Long      'Line index
    Dim Ccy                As String    'Candidate currency
    Dim Used               As Boolean   'True when a line uses Ccy

        ReDim mScopeName(1 To mFxCount + 1)
        For f = 0 To mFxCount
            If f = 0 Then
                Ccy = mReportingCcy
            Else
                Ccy = mFxCcy(f)
            End If
            If Not HasKey(mScopeIndex, Ccy) Then
                Used = False
                For n = 1 To mLineCount
                    If mLineCcyValid(n) And mLineCcy(n) = Ccy Then
                        Used = True
                        Exit For
                    End If
                Next n
                If Used Then
                    mScopeCount = mScopeCount + 1
                    mScopeName(mScopeCount) = Ccy
                    mScopeIndex.Add mScopeCount, Ccy
                End If
            End If
        Next f
        mScopeCount = mScopeCount + 1
        mScopeName(mScopeCount) = SCOPE_TOTAL
        mScopeIndex.Add mScopeCount, SCOPE_TOTAL
        ReDim mAcc(1 To mScopeCount, 1 To ACC_WIDTH)
End Sub


Private Sub Aggregate()
'------------------------------------------------------------------------------
' PURPOSE
'   Add every valid line's weighted amount to its currency scope and to
'   TOTAL, and count the lines and the rejected lines of each scope.
'
' REFERENCE
'   DR 2015/61 Articles 9 (market value), 10-12 (haircuts), 22-31 (outflow
'   rates), 32-33 (inflow rates and cap classes); Annex I para 3 (adjusted
'   amounts after the unwind).
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim n                  As Long      'Line index
    Dim k                  As Long      'Scope pass: 1 currency, 2 TOTAL
    Dim s                  As Long      'Scope index
    Dim Fx                 As Double    'Units of reporting ccy per unit
    Dim Weighted           As Double    'Weighted amount, reporting ccy
    Dim Adjusted           As Double    'Adjusted weighted amount (HQLA)

        For n = 1 To mLineCount
            For k = 1 To 2
                s = 0
                If k = 1 Then
                    If mLineCcyValid(n) Then s = mScopeIndex.Item(mLineCcy(n))
                Else
                    s = mScopeIndex.Item(SCOPE_TOTAL)
                End If
                If s > 0 Then
                    mAcc(s, ACC_LINES) = mAcc(s, ACC_LINES) + 1
                    If Not mLineValid(n) Then mAcc(s, ACC_REJECTED) = mAcc(s, ACC_REJECTED) + 1
                End If
                If s > 0 And mLineValid(n) Then
                    Fx = mFxRate(mFxIndex.Item(mLineCcy(n)))
                    Select Case mLineType(n)
                        Case TYPE_HQLA
                            Weighted = CDbl(mLineAmount(n)) * Fx * (1# - CDbl(mLineFactor(n)))
                            Adjusted = (CDbl(mLineAmount(n)) + CDbl(mLineUnwind(n))) * Fx * (1# - CDbl(mLineFactor(n)))
                            Select Case mLineClass(n)
                                Case LVL_L1
                                    mAcc(s, ACC_H_L1) = mAcc(s, ACC_H_L1) + Weighted
                                    mAcc(s, ACC_A_L1) = mAcc(s, ACC_A_L1) + Adjusted
                                Case LVL_L1CB
                                    mAcc(s, ACC_H_L1CB) = mAcc(s, ACC_H_L1CB) + Weighted
                                    mAcc(s, ACC_A_L1CB) = mAcc(s, ACC_A_L1CB) + Adjusted
                                Case LVL_L2A
                                    mAcc(s, ACC_H_L2A) = mAcc(s, ACC_H_L2A) + Weighted
                                    mAcc(s, ACC_A_L2A) = mAcc(s, ACC_A_L2A) + Adjusted
                                Case LVL_L2B
                                    mAcc(s, ACC_H_L2B) = mAcc(s, ACC_H_L2B) + Weighted
                                    mAcc(s, ACC_A_L2B) = mAcc(s, ACC_A_L2B) + Adjusted
                            End Select
                        Case TYPE_OUTFLOW
                            mAcc(s, ACC_TO) = mAcc(s, ACC_TO) + CDbl(mLineAmount(n)) * Fx * CDbl(mLineFactor(n))
                        Case TYPE_INFLOW
                            Weighted = CDbl(mLineAmount(n)) * Fx * CDbl(mLineFactor(n))
                            Select Case mLineClass(n)
                                Case CAP_EXEMPT
                                    mAcc(s, ACC_FEI) = mAcc(s, ACC_FEI) + Weighted
                                Case CAP_90
                                    mAcc(s, ACC_IHC) = mAcc(s, ACC_IHC) + Weighted
                                Case Else
                                    mAcc(s, ACC_IC) = mAcc(s, ACC_IC) + Weighted
                            End Select
                    End Select
                End If
            Next k
        Next n
End Sub


'------------------------------------------------------------------------------
'                                 OUTPUTS
'------------------------------------------------------------------------------

Private Function WriteResults() As String
'------------------------------------------------------------------------------
' PURPOSE
'   Compute the buffer, net liquidity outflow and LCR of every scope and
'   write one Results row per scope, with the formula-check columns.
'
' RETURNS
'   The run summary, also written to Results!C5.
'
' REFERENCE
'   DR 2015/61 Article 4, Annex I, Annex II.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim ws                 As Worksheet 'Results
    Dim Out()              As Variant   'Values C..W per scope
    Dim s                  As Long      'Scope index
    Dim r                  As Long      'Worksheet row
    Dim Level              As Long      'Adjusted-amount accumulator index
    Dim Adjusted(1 To 4)   As Double    'A1, A1CB, A2A, A2B floored at zero
    Dim Excess             As Double    'Excess liquid assets amount
    Dim Buffer             As Double    'Liquidity buffer
    Dim Nlo                As Double    'Net liquidity outflow
    Dim Ratio              As Variant   'LCR as a decimal, Empty when undefined
    Dim Lines              As Long      'Lines assigned to the scope
    Dim Rejected           As Long      'Rejected lines of the scope
    Dim Status             As String    'Status column text
    Dim Withheld           As Boolean   'True when the aggregates are withheld
    Dim TotalRatio         As Variant   'LCR of TOTAL, for the summary
    Dim TotalStatus        As String    'Status of TOTAL, for the summary
    Dim Summary            As String    'Run summary
    Dim Rejections         As Long      'Rejected lines overall

        Set ws = GetSheet(SH_RESULTS)
        ReDim Out(1 To mScopeCount, 1 To RES_WIDTH)
        For s = 1 To mScopeCount
            For Level = 0 To 3
                Adjusted(Level + 1) = mAcc(s, ACC_A_L1 + Level)
                If Adjusted(Level + 1) < 0# Then
                    AddCheck SEV_WARNING, SH_RESULTS, RES_FIRST_ROW + s - 1, mScopeName(s), _
                             "Adjusted " & Choose(Level + 1, "level 1 excl. EHQCB", "level 1 EHQCB", "level 2A", _
                             "level 2B") & " amount is negative (" & Format$(Adjusted(Level + 1), "#,##0") & _
                             "); floored at zero.", D_ADJ_FLOORED
                    Adjusted(Level + 1) = 0#
                End If
            Next Level
            Excess = CORE_Engine.ExcessLiquidAssets(Adjusted(1), Adjusted(2), Adjusted(3), Adjusted(4), _
                                                    mShareL1exCB, mShareL1, mShareL2B)
            Buffer = CORE_Engine.LiquidityBuffer(mAcc(s, ACC_H_L1), mAcc(s, ACC_H_L1CB), mAcc(s, ACC_H_L2A), _
                                                 mAcc(s, ACC_H_L2B), Excess)
            Nlo = CORE_Engine.NetLiquidityOutflow(mAcc(s, ACC_TO), mAcc(s, ACC_FEI), mAcc(s, ACC_IHC), _
                                                  mAcc(s, ACC_IC), mCapHigher, mCapStandard)
            Ratio = CORE_Engine.CoverageRatio(Buffer, Nlo)
            Lines = CLng(mAcc(s, ACC_LINES))
            Rejected = CLng(mAcc(s, ACC_REJECTED))
            Withheld = (Rejected > 0 And mWithhold)
            If Withheld Then
                Status = "INCOMPLETE: " & Rejected & " of " & Lines & " line(s) rejected"
                AddCheck SEV_WARNING, SH_RESULTS, RES_FIRST_ROW + s - 1, mScopeName(s), "LCR of " & _
                         mScopeName(s) & " withheld: " & Rejected & " line(s) rejected.", D_WITHHELD
            ElseIf Rejected > 0 Then
                Status = "PARTIAL: " & Rejected & " of " & Lines & " line(s) excluded"
            ElseIf IsEmpty(Ratio) Then
                Status = "NO NET OUTFLOW: ratio not defined"
                AddCheck SEV_WARNING, SH_RESULTS, RES_FIRST_ROW + s - 1, mScopeName(s), "Net liquidity " & _
                         "outflow of " & mScopeName(s) & " is zero; no ratio.", D_NO_OUTFLOW
            Else
                Status = "VALID"
            End If
            If Not Withheld And Not IsEmpty(Ratio) Then
                If CDbl(Ratio) < mRequirement Then
                    AddCheck SEV_WARNING, SH_RESULTS, RES_FIRST_ROW + s - 1, mScopeName(s), "LCR of " & _
                             mScopeName(s) & " is " & Format$(CDbl(Ratio), "0.0%") & ", below the " & _
                             Format$(mRequirement, "0%") & " requirement.", D_BELOW_MINIMUM
                End If
            End If

            'Columns C..L: scope, lines, held and adjusted amounts per level.
            Out(s, 1) = mScopeName(s)
            Out(s, 2) = (Lines - Rejected) & " / " & Lines
            Out(s, 3) = mAcc(s, ACC_H_L1)
            Out(s, 4) = mAcc(s, ACC_H_L1CB)
            Out(s, 5) = mAcc(s, ACC_H_L2A)
            Out(s, 6) = mAcc(s, ACC_H_L2B)
            Out(s, 7) = Adjusted(1)
            Out(s, 8) = Adjusted(2)
            Out(s, 9) = Adjusted(3)
            Out(s, 10) = Adjusted(4)
            'Columns M..W: excess, buffer, TO, FEI, IHC, IC, reduction, NLO, LCR,
            'surplus, status; the aggregates are left blank when withheld.
            Out(s, 11) = IIf(Withheld, Empty, Excess)
            Out(s, 12) = IIf(Withheld, Empty, Buffer)
            Out(s, 13) = mAcc(s, ACC_TO)
            Out(s, 14) = mAcc(s, ACC_FEI)
            Out(s, 15) = mAcc(s, ACC_IHC)
            Out(s, 16) = mAcc(s, ACC_IC)
            Out(s, 17) = IIf(Withheld, Empty, mAcc(s, ACC_TO) - Nlo)
            Out(s, 18) = IIf(Withheld, Empty, Nlo)
            If Withheld Or IsEmpty(Ratio) Then
                Out(s, 19) = Empty
            Else
                Out(s, 19) = CDbl(Ratio)
            End If
            Out(s, 20) = IIf(Withheld, Empty, Buffer - mRequirement * Nlo)
            Out(s, 21) = Status
            If mScopeName(s) = SCOPE_TOTAL Then
                TotalRatio = Out(s, 19)
                TotalStatus = Status
                Rejections = Rejected
            End If
        Next s

        r = RES_FIRST_ROW
        ws.Range(ws.Cells(r, RES_FIRST_COL), ws.Cells(r + mScopeCount - 1, RES_FIRST_COL + RES_WIDTH - 1)).Value = Out
        For s = 1 To mScopeCount
            r = RES_FIRST_ROW + s - 1
            ws.Cells(r, RES_CHECK_COL).Formula = "=E" & r & "+F" & r & "+G" & r & "+H" & r & "-MIN(E" & r & _
                "+F" & r & "+G" & r & "+H" & r & ",(I" & r & "+J" & r & "+K" & r & "+L" & r & ")-MIN(I" & r & _
                "+J" & r & "+K" & r & "+L" & r & ",I" & r & "/MinShareL1exCB,(I" & r & "+J" & r & _
                ")/MinShareL1,(I" & r & "+J" & r & "+K" & r & ")/(1-MaxShareL2B)))"
            ws.Cells(r, RES_CHECK_COL + 1).Formula = "=O" & r & "-MIN(P" & r & ",O" & r & ")-MIN(Q" & r & _
                ",InflowCapHigher*MAX(O" & r & "-P" & r & ",0))-MIN(R" & r & ",InflowCapStandard*MAX(O" & r & _
                "-P" & r & "-Q" & r & "/InflowCapHigher,0))"
            ws.Cells(r, RES_LAST_COL).Formula = "=IF(N" & r & "="""",""n/a"",IF(AND(ABS(X" & r & "-N" & r & _
                ")<=" & Trim$(Str$(CHECK_TOLERANCE)) & ",ABS(Y" & r & "-T" & r & ")<=" & _
                Trim$(Str$(CHECK_TOLERANCE)) & "),""OK"",""DIFF""))"
        Next s
        ws.Range(ws.Cells(RES_FIRST_ROW + mScopeCount - 1, RES_FIRST_COL), _
                 ws.Cells(RES_FIRST_ROW + mScopeCount - 1, RES_LAST_COL)).Font.Bold = True

        If IsEmpty(TotalRatio) Then
            Summary = "LCR TOTAL: " & TotalStatus & "."
        Else
            Summary = "LCR TOTAL " & Format$(CDbl(TotalRatio), "0.0%") & " (" & TotalStatus & ")."
        End If
        Summary = Summary & " " & (mScopeCount - 1) & " currency scope(s); " & mLineCount & " line(s), " & _
                  Rejections & " rejected; " & mErrorCount & " error(s), " & mWarningCount & " warning(s)."
        ws.Cells(RES_STATUS_ROW, RES_FIRST_COL).Value = "Last run " & Format$(Now, "yyyy-mm-dd hh:mm:ss") & _
            "; reporting date " & Format$(mAsOfDate, "yyyy-mm-dd") & "; amounts in " & mReportingCcy & "."
        ws.Cells(RES_SUMMARY_ROW, RES_FIRST_COL).Value = Summary
        AddCheck SEV_INFO, SH_RESULTS, 0, vbNullString, Summary, D_RUN_SUMMARY
        WriteResults = Summary
End Function


Private Sub WriteLineCalc()
'------------------------------------------------------------------------------
' PURPOSE
'   Write one LineCalc row per input line with its factor, weighted amount
'   in the reporting currency and status.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim ws                 As Worksheet 'LineCalc
    Dim Out()              As Variant   '(1 To lines, 1 To LC_WIDTH)
    Dim n                  As Long      'Line index
    Dim Fx                 As Variant   'Rate, or Empty when the ccy is unknown
    Dim AmountRep          As Variant   'Amount in reporting ccy

        If mLineCount = 0 Then Exit Sub
        Set ws = GetSheet(SH_LINECALC)
        ReDim Out(1 To mLineCount, 1 To LC_WIDTH)
        For n = 1 To mLineCount
            Fx = Empty
            AmountRep = Empty
            If mLineCcyValid(n) Then Fx = mFxRate(mFxIndex.Item(mLineCcy(n)))
            If Not IsEmpty(Fx) And Not IsEmpty(mLineAmount(n)) Then AmountRep = CDbl(mLineAmount(n)) * CDbl(Fx)
            Out(n, 1) = mLineSheet(n)
            Out(n, 2) = mLineRow(n)
            Out(n, 3) = mLineID(n)
            Out(n, 4) = mLineCategory(n)
            Out(n, 5) = mLineClass(n)
            Out(n, 6) = mLineCcy(n)
            Out(n, 7) = mLineAmount(n)
            Out(n, 8) = mLineUnwind(n)
            Out(n, 9) = Fx
            Out(n, 10) = AmountRep
            Out(n, 11) = mLineFactor(n)
            Select Case mLineType(n)
                Case TYPE_HQLA: Out(n, 12) = "Haircut"
                Case TYPE_OUTFLOW: Out(n, 12) = "Outflow rate"
                Case Else: Out(n, 12) = "Inflow rate"
            End Select
            If mLineValid(n) Then
                If mLineType(n) = TYPE_HQLA Then
                    Out(n, 13) = CDbl(AmountRep) * (1# - CDbl(mLineFactor(n)))
                    Out(n, 14) = (CDbl(mLineAmount(n)) + CDbl(mLineUnwind(n))) * CDbl(Fx) * _
                                 (1# - CDbl(mLineFactor(n)))
                Else
                    Out(n, 13) = CDbl(AmountRep) * CDbl(mLineFactor(n))
                End If
            End If
            Out(n, 15) = mLineStatus(n)
        Next n
        ws.Range(ws.Cells(LC_FIRST_ROW, LC_FIRST_COL), _
                 ws.Cells(LC_FIRST_ROW + mLineCount - 1, LC_FIRST_COL + LC_WIDTH - 1)).Value = Out
End Sub


Private Sub WriteChecks()
'------------------------------------------------------------------------------
' PURPOSE
'   Replace the Checks lines with those of the operation in progress.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim ws                 As Worksheet 'Checks
    Dim Out()              As Variant   '(1 To lines, 1 To CHK_WIDTH)
    Dim i                  As Long      'Check line
    Dim c                  As Long      'Field

        Set ws = GetSheet(SH_CHECKS)
        ClearBelow ws, CHK_FIRST_ROW, CHK_FIRST_COL, CHK_FIRST_COL + CHK_WIDTH - 1
        If mCheckCount = 0 Then
            AddCheck SEV_INFO, vbNullString, 0, vbNullString, "No findings.", D_RUN_SUMMARY
        End If
        ReDim Out(1 To mCheckCount, 1 To CHK_WIDTH)
        For i = 1 To mCheckCount
            For c = 1 To CHK_WIDTH
                Out(i, c) = mCheckData(c, i)
            Next c
        Next i
        ws.Range(ws.Cells(CHK_FIRST_ROW, CHK_FIRST_COL), _
                 ws.Cells(CHK_FIRST_ROW + mCheckCount - 1, CHK_FIRST_COL + CHK_WIDTH - 1)).Value = Out
End Sub


Private Sub ClearOutputArea()
'------------------------------------------------------------------------------
' PURPOSE
'   Empty the data rows of Results, LineCalc and Checks; reset the Results
'   status cells and the bold total row.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim ws                 As Worksheet 'Results

        Set ws = GetSheet(SH_RESULTS)
        ClearBelow ws, RES_FIRST_ROW, RES_FIRST_COL, RES_LAST_COL
        ws.Range(ws.Cells(RES_FIRST_ROW, RES_FIRST_COL), ws.Cells(RES_FIRST_ROW + 50, RES_LAST_COL)).Font.Bold = False
        ws.Cells(RES_STATUS_ROW, RES_FIRST_COL).Value = "No results yet: press Run LCR."
        ws.Cells(RES_SUMMARY_ROW, RES_FIRST_COL).Value = _
            "Amounts in the reporting currency. Scope = currency of the lines, or TOTAL."
        ClearBelow GetSheet(SH_LINECALC), LC_FIRST_ROW, LC_FIRST_COL, LC_FIRST_COL + LC_WIDTH - 1
        ClearBelow GetSheet(SH_CHECKS), CHK_FIRST_ROW, CHK_FIRST_COL, CHK_FIRST_COL + CHK_WIDTH - 1
End Sub


Private Sub ClearBelow( _
    ByVal ws As Worksheet, _
    ByVal FirstRow As Long, _
    ByVal FirstCol As Long, _
    ByVal LastCol As Long)
'------------------------------------------------------------------------------
' PURPOSE
'   Clear the contents, not the formats, of FirstCol..LastCol from FirstRow
'   down to the last used row of the sheet.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim LastRow            As Long      'Last used row

        LastRow = ws.UsedRange.Row + ws.UsedRange.Rows.Count - 1
        If LastRow < FirstRow Then LastRow = FirstRow
        ws.Range(ws.Cells(FirstRow, FirstCol), ws.Cells(LastRow, LastCol)).ClearContents
End Sub


'------------------------------------------------------------------------------
'                                 HELPERS
'------------------------------------------------------------------------------

Private Sub AddCheck( _
    ByVal Severity As String, _
    ByVal SheetName As String, _
    ByVal RowNumber As Long, _
    ByVal Reference As String, _
    ByVal Message As String, _
    ByVal Code As String)
'------------------------------------------------------------------------------
' PURPOSE
'   Append one line to the Checks buffer and count errors and warnings.
'
' INPUTS
'   Severity   SEV_ERROR, SEV_WARNING or SEV_INFO
'   SheetName  Sheet the finding concerns, or empty
'   RowNumber  Worksheet row, or 0 when none
'   Reference  ID, code or cell the finding concerns
'   Message    Plain-language description
'   Code       Stable diagnostic code (D_ constant)
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        mCheckCount = mCheckCount + 1
        If mCheckCount > UBound(mCheckData, 2) Then
            ReDim Preserve mCheckData(1 To CHK_WIDTH, 1 To 2 * mCheckCount)
        End If
        mCheckData(1, mCheckCount) = Severity
        mCheckData(2, mCheckCount) = SheetName
        If RowNumber > 0 Then
            mCheckData(3, mCheckCount) = RowNumber
        Else
            mCheckData(3, mCheckCount) = Empty
        End If
        mCheckData(4, mCheckCount) = Reference
        mCheckData(5, mCheckCount) = Message
        mCheckData(6, mCheckCount) = Code
        If Severity = SEV_ERROR Then mErrorCount = mErrorCount + 1
        If Severity = SEV_WARNING Then mWarningCount = mWarningCount + 1
End Sub


Private Function FindHeader(ByVal ws As Worksheet, ByVal Label As String) As Long
'------------------------------------------------------------------------------
' PURPOSE
'   Return the row of the first cell of column C equal to Label, or 0.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim r                  As Long      'Row on the sheet

        For r = 1 To TABLE_SCAN_ROWS
            If Trim$(CStr(ws.Cells(r, PARAM_CODE_COL).Value)) = Label Then
                FindHeader = r
                Exit Function
            End If
        Next r
End Function


Private Function GetSheet(ByVal SheetName As String) As Worksheet
'------------------------------------------------------------------------------
' PURPOSE
'   Return a worksheet of this workbook by tab name.
'
' ERROR POLICY
'   Raises ERR_SHEET_MISSING when the sheet does not exist.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        On Error Resume Next
        Set GetSheet = ThisWorkbook.Worksheets(SheetName)
        On Error GoTo 0
        If GetSheet Is Nothing Then
            Err.Raise ERR_SHEET_MISSING, "M_Main.GetSheet", "Sheet '" & SheetName & "' not found."
        End If
End Function


Private Function HasKey(ByVal Items As Collection, ByVal Key As String) As Boolean
'------------------------------------------------------------------------------
' PURPOSE
'   Return True when a Collection holds Key (keys are case-insensitive).
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Probe              As Variant   'Item read only to test the key

        If Len(Key) = 0 Then Exit Function
        On Error Resume Next
        Probe = Items.Item(Key)
        HasKey = (Err.Number = 0)
        Err.Clear
        On Error GoTo 0
End Function


Private Function IsNumber(ByVal Value As Variant) As Boolean
'------------------------------------------------------------------------------
' PURPOSE
'   Return True for a numeric cell value; text that looks like a number is
'   not accepted, so that a number stored as text is reported.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        Select Case VarType(Value)
            Case vbInteger, vbLong, vbSingle, vbDouble, vbCurrency, vbDecimal, vbByte, 20
                IsNumber = True
        End Select
End Function
