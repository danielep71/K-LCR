Attribute VB_Name = "CORE_Config"
'==============================================================================
' MODULE: CORE_Config
'------------------------------------------------------------------------------
' PURPOSE
'   Hold every layout constant the LCR engine depends on: sheet names, header
'   and first data rows, the column of each input and output field, the
'   header labels that locate the tables on Params, the parameter codes, the
'   category types and classes, the severity labels and diagnostic codes of
'   the Checks sheet, and the error numbers raised by the workbook macros.
'   When a sheet layout changes, it changes here and nowhere else.
'
' PUBLIC SURFACE
'   None outside this VBA project. The constants are Public for in-project use
'   by CORE_Engine, M_Main and TEST_Engine; Option Private
'   Module keeps them off the supported external surface.
'
' DEPENDENCIES
'   None. Every value is a literal.
'
' STATE OWNERSHIP
'   Constants only; no state.
'
' ERROR POLICY
'   Not applicable.
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
    'Require explicit declarations; keep the constants inside this project.
    Option Explicit
    Option Private Module

'------------------------------------------------------------------------------
' SHEET NAMES
'------------------------------------------------------------------------------
    'Worksheet tab names, as the engine looks them up in ThisWorkbook.
        Public Const SH_PARAMS      As String = "Params"      'Parameters, catalogue, FX
        Public Const SH_HQLA        As String = "HQLA"        'Liquid asset holdings
        Public Const SH_OUTFLOWS    As String = "Outflows"    'Outflow lines
        Public Const SH_INFLOWS     As String = "Inflows"     'Inflow lines
        Public Const SH_RESULTS     As String = "Results"     'One row per scope
        Public Const SH_LINECALC    As String = "LineCalc"    'One row per input line
        Public Const SH_CHECKS      As String = "Checks"      'Errors, warnings, information

'------------------------------------------------------------------------------
' PARAMS LAYOUT
'------------------------------------------------------------------------------
    'Scalar parameters: code in column C, value in column E, from row 6
    'down to the first blank code.
        Public Const PARAM_FIRST_ROW    As Long = 6
        Public Const PARAM_CODE_COL     As Long = 3
        Public Const PARAM_VALUE_COL    As Long = 5
    'Tables below the parameters are located by the label of their header
    'cell in column C; their rows run down to the first blank code.
        Public Const CAT_HEADER_LABEL   As String = "Category"   'Category catalogue
        Public Const FX_HEADER_LABEL    As String = "FX_Ccy"     'FX table
        Public Const TABLE_SCAN_ROWS    As Long = 2000           'Rows searched for a header
    'Catalogue columns: code, description, factor, type, class, reference.
        Public Const CAT_COL_CODE       As Long = 3
        Public Const CAT_COL_FACTOR     As Long = 5
        Public Const CAT_COL_TYPE       As Long = 6
        Public Const CAT_COL_CLASS      As Long = 7
        Public Const CAT_COL_REF        As Long = 8
    'FX columns: currency, name, units of reporting currency per unit.
        Public Const FX_COL_CCY         As Long = 3
        Public Const FX_COL_RATE        As Long = 5

'------------------------------------------------------------------------------
' PARAMETER CODES
'------------------------------------------------------------------------------
        Public Const P_ASOFDATE         As String = "AsOfDate"
        Public Const P_REPORTING_CCY    As String = "ReportingCcy"
        Public Const P_REQUIREMENT      As String = "LCRRequirement"
        Public Const P_SHARE_L1EXCB     As String = "MinShareL1exCB"
        Public Const P_SHARE_L1         As String = "MinShareL1"
        Public Const P_SHARE_L2B        As String = "MaxShareL2B"
        Public Const P_CAP_STANDARD     As String = "InflowCapStandard"
        Public Const P_CAP_HIGHER       As String = "InflowCapHigher"
        Public Const P_WITHHOLD         As String = "WithholdIncomplete"

'------------------------------------------------------------------------------
' CATEGORY TYPES AND CLASSES
'------------------------------------------------------------------------------
        Public Const TYPE_HQLA          As String = "HQLA"
        Public Const TYPE_OUTFLOW       As String = "OUTFLOW"
        Public Const TYPE_INFLOW        As String = "INFLOW"
    'HQLA levels (Delegated Regulation (EU) 2015/61, Articles 10 to 12).
        Public Const LVL_L1             As String = "L1"     'Level 1 excluding EHQCB
        Public Const LVL_L1CB           As String = "L1CB"   'Level 1 extremely high quality covered bonds
        Public Const LVL_L2A            As String = "L2A"
        Public Const LVL_L2B            As String = "L2B"
    'Inflow cap classes (Article 33, Annex II).
        Public Const CAP_75             As String = "75"
        Public Const CAP_90             As String = "90"
        Public Const CAP_EXEMPT         As String = "EXEMPT"
    'Scope label of the all-currency aggregate.
        Public Const SCOPE_TOTAL        As String = "TOTAL"

'------------------------------------------------------------------------------
' INPUT SHEETS LAYOUT
'------------------------------------------------------------------------------
    'HQLA, Outflows and Inflows: header in row 4, data from row 5.
        Public Const IN_HEADER_ROW      As Long = 4
        Public Const IN_FIRST_ROW       As Long = 5
        Public Const IN_COL_ID          As Long = 3     'C: AssetID / LineID
        Public Const IN_COL_CATEGORY    As Long = 5     'E: category code
        Public Const IN_COL_CCY         As Long = 6     'F: currency
        Public Const IN_COL_AMOUNT      As Long = 7     'G: market value / amount
        Public Const IN_COL_UNWIND      As Long = 8     'H: unwind adjustment (HQLA)
        Public Const IN_LAST_COL_HQLA   As Long = 8     'H: last input column of HQLA
        Public Const IN_LAST_COL_FLOW   As Long = 7     'G: last input column of flows

'------------------------------------------------------------------------------
' OUTPUT SHEETS LAYOUT
'------------------------------------------------------------------------------
    'Results: status lines in C4 and C5, header in row 6, data from row 7,
    'columns C (scope) to Z (formula check).
        Public Const RES_STATUS_ROW     As Long = 4
        Public Const RES_SUMMARY_ROW    As Long = 5
        Public Const RES_FIRST_ROW      As Long = 7
        Public Const RES_FIRST_COL      As Long = 3
        Public Const RES_WIDTH          As Long = 21    'C..W written as values
        Public Const RES_CHECK_COL      As Long = 24    'X: first formula-check column
        Public Const RES_LAST_COL       As Long = 26    'Z: Check
    'LineCalc and Checks: header in row 5, data from row 6.
        Public Const LC_FIRST_ROW       As Long = 6
        Public Const LC_FIRST_COL       As Long = 3
        Public Const LC_WIDTH           As Long = 15
        Public Const CHK_FIRST_ROW      As Long = 6
        Public Const CHK_FIRST_COL      As Long = 3
        Public Const CHK_WIDTH          As Long = 6

'------------------------------------------------------------------------------
' SCOPE ACCUMULATORS
'------------------------------------------------------------------------------
    'Second index of the per-scope accumulator array in M_Main.
        Public Const ACC_H_L1           As Long = 1     'Level 1 excl. EHQCB, post-haircut
        Public Const ACC_H_L1CB         As Long = 2     'Level 1 EHQCB, post-haircut
        Public Const ACC_H_L2A          As Long = 3
        Public Const ACC_H_L2B          As Long = 4
        Public Const ACC_A_L1           As Long = 5     'Adjusted amounts (after unwind)
        Public Const ACC_A_L1CB         As Long = 6
        Public Const ACC_A_L2A          As Long = 7
        Public Const ACC_A_L2B          As Long = 8
        Public Const ACC_TO             As Long = 9     'Total weighted outflows
        Public Const ACC_FEI            As Long = 10    'Weighted inflows exempt from the cap
        Public Const ACC_IHC            As Long = 11    'Weighted inflows, 90% cap
        Public Const ACC_IC             As Long = 12    'Weighted inflows, 75% cap
        Public Const ACC_LINES          As Long = 13    'Lines assigned to the scope
        Public Const ACC_REJECTED       As Long = 14    'Lines rejected in the scope
        Public Const ACC_WIDTH          As Long = 14

'------------------------------------------------------------------------------
' CHECKS
'------------------------------------------------------------------------------
        Public Const SEV_ERROR          As String = "ERROR"
        Public Const SEV_WARNING        As String = "WARNING"
        Public Const SEV_INFO           As String = "INFO"
    'Stable diagnostic codes.
        Public Const D_PARAM_INVALID    As String = "LCR-P001"   'Parameter missing or invalid
        Public Const D_PARAM_CCY        As String = "LCR-P002"   'Reporting currency and FX table
        Public Const D_CAT_INVALID      As String = "LCR-P003"   'Catalogue row invalid
        Public Const D_FX_INVALID       As String = "LCR-P004"   'FX row invalid
        Public Const D_DUPLICATE_KEY    As String = "LCR-P005"   'Duplicate catalogue or FX code
        Public Const D_ID_MISSING       As String = "LCR-L001"
        Public Const D_ID_DUPLICATE     As String = "LCR-L002"
        Public Const D_CAT_UNKNOWN      As String = "LCR-L003"
        Public Const D_CAT_TYPE         As String = "LCR-L004"
        Public Const D_CCY_UNKNOWN      As String = "LCR-L005"
        Public Const D_AMOUNT_INVALID   As String = "LCR-L006"
        Public Const D_AMOUNT_NEGATIVE  As String = "LCR-L007"
        Public Const D_UNWIND_INVALID   As String = "LCR-L008"
        Public Const D_UNWIND_NEGATIVE  As String = "LCR-L009"
        Public Const D_ADJ_FLOORED      As String = "LCR-S001"
        Public Const D_NO_OUTFLOW       As String = "LCR-S002"
        Public Const D_WITHHELD         As String = "LCR-S003"
        Public Const D_BELOW_MINIMUM    As String = "LCR-S004"
        Public Const D_RUN_SUMMARY      As String = "LCR-R001"

'------------------------------------------------------------------------------
' ERROR NUMBERS
'------------------------------------------------------------------------------
    'Range vbObjectError + 2048 to vbObjectError + 4095 (house style),
    'written as literals (vbObjectError = &H80040000) so that the module
    'also compiles in LibreOffice, where the smoke test runs.
        Public Const ERR_SHEET_MISSING  As Long = &H80040801     'vbObjectError + 2049
        Public Const ERR_TABLE_MISSING  As Long = &H80040802     'vbObjectError + 2050
        Public Const ERR_ENGINE_INPUT   As Long = &H80040803     'vbObjectError + 2051
        Public Const ERR_CLEANUP_FAILED As Long = &H80040804     'vbObjectError + 2052

'------------------------------------------------------------------------------
' TOLERANCES
'------------------------------------------------------------------------------
        Public Const CHECK_TOLERANCE    As Double = 0.01    'Formula check, reporting ccy units
