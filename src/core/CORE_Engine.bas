Attribute VB_Name = "CORE_Engine"
'==============================================================================
' MODULE: CORE_Engine
'------------------------------------------------------------------------------
' PURPOSE
'   Compute the regulatory aggregates of the Liquidity Coverage Ratio from
'   already weighted amounts: the excess liquid assets amount and the
'   liquidity buffer (Annex I), the net liquidity outflow (Annex II), the
'   ratio and the surplus. Every procedure is a pure function of its
'   arguments: it reads and writes no worksheet.
'
' PUBLIC SURFACE
'   None outside this VBA project (Option Private Module). Called by M_Main,
'   LCR_Formulas and TEST_Engine.
'
' DEPENDENCIES
'   CORE_Config (error numbers).
'
' STATE OWNERSHIP
'   None.
'
' ERROR POLICY
'   Raises ERR_ENGINE_INPUT for an argument outside its valid domain; the
'   description names the argument and the offending value.
'
' COMPATIBILITY
'   Excel VBA; no references beyond the defaults.
'
' REFERENCE
'   Commission Delegated Regulation (EU) 2015/61 as amended by Commission
'   Delegated Regulation (EU) 2018/1620: Article 17, Annex I paras 2 to 4,
'   Article 33, Annex II.
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
    'Require explicit declarations; keep the engine inside this project.
    Option Explicit
    Option Private Module

'------------------------------------------------------------------------------
'                            LIQUIDITY BUFFER
'------------------------------------------------------------------------------

Public Function ExcessLiquidAssets( _
    ByVal AdjustedL1 As Double, _
    ByVal AdjustedL1CB As Double, _
    ByVal AdjustedL2A As Double, _
    ByVal AdjustedL2B As Double, _
    ByVal MinShareL1exCB As Double, _
    ByVal MinShareL1 As Double, _
    ByVal MaxShareL2B As Double) _
    As Double
'------------------------------------------------------------------------------
' PURPOSE
'   Return the excess liquid assets amount: the part of the adjusted liquid
'   assets that the composition caps of Article 17 do not admit.
'
' INPUTS
'   AdjustedL1      Level 1 assets excluding EHQCB, post-haircut, after the
'                   unwind of secured transactions maturing within 30 days;
'                   reporting currency; >= 0
'   AdjustedL1CB    Level 1 extremely high quality covered bonds, as above
'   AdjustedL2A     Level 2A assets, as above
'   AdjustedL2B     Level 2B assets, as above
'   MinShareL1exCB  Minimum share of level 1 excl. EHQCB (0.30); 0 < x <= 1
'   MinShareL1      Minimum share of level 1 (0.60); 0 < x <= 1
'   MaxShareL2B     Maximum share of level 2B (0.15); 0 <= x < 1
'
' RETURNS
'   Excess = S - MIN(S, A1/0.30, (A1 + A1CB)/0.60, (A1 + A1CB + A2A)/0.85),
'   S = A1 + A1CB + A2A + A2B; reporting currency; >= 0.
'
' ERROR POLICY
'   Raises ERR_ENGINE_INPUT for a negative amount or a share out of range.
'
' REFERENCE
'   DR 2015/61 Annex I para 4 (as amended by DR 2018/1620); Article 17(1).
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Total              As Double    'S: sum of the adjusted amounts
    Dim Admissible         As Double    'Largest total the caps admit

        RequireNonNegative AdjustedL1, "AdjustedL1", "ExcessLiquidAssets"
        RequireNonNegative AdjustedL1CB, "AdjustedL1CB", "ExcessLiquidAssets"
        RequireNonNegative AdjustedL2A, "AdjustedL2A", "ExcessLiquidAssets"
        RequireNonNegative AdjustedL2B, "AdjustedL2B", "ExcessLiquidAssets"
        RequireShare MinShareL1exCB, "MinShareL1exCB", "ExcessLiquidAssets", False
        RequireShare MinShareL1, "MinShareL1", "ExcessLiquidAssets", False
        RequireShare MaxShareL2B, "MaxShareL2B", "ExcessLiquidAssets", True

        Total = AdjustedL1 + AdjustedL1CB + AdjustedL2A + AdjustedL2B
        Admissible = MinOf(Total, AdjustedL1 / MinShareL1exCB)
        Admissible = MinOf(Admissible, (AdjustedL1 + AdjustedL1CB) / MinShareL1)
        Admissible = MinOf(Admissible, (AdjustedL1 + AdjustedL1CB + AdjustedL2A) / (1# - MaxShareL2B))
        ExcessLiquidAssets = Total - Admissible
End Function


Public Function LiquidityBuffer( _
    ByVal L1 As Double, _
    ByVal L1CB As Double, _
    ByVal L2A As Double, _
    ByVal L2B As Double, _
    ByVal ExcessAmount As Double) _
    As Double
'------------------------------------------------------------------------------
' PURPOSE
'   Return the liquidity buffer: the post-haircut liquid assets held at the
'   calculation date less the excess liquid assets amount, never below zero.
'
' INPUTS
'   L1, L1CB, L2A, L2B  Level 1 excl. EHQCB, level 1 EHQCB, level 2A and
'                       level 2B assets, post-haircut, before any unwind;
'                       reporting currency; >= 0
'   ExcessAmount        Result of ExcessLiquidAssets; >= 0
'
' RETURNS
'   Buffer = (L1 + L1CB + L2A + L2B) - MIN(L1 + L1CB + L2A + L2B, Excess).
'
' ERROR POLICY
'   Raises ERR_ENGINE_INPUT for a negative argument.
'
' REFERENCE
'   DR 2015/61 Annex I para 2: the level 1 asset amount includes level 1
'   covered bonds.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Gross              As Double    'Liquid assets held, post-haircut

        RequireNonNegative L1, "L1", "LiquidityBuffer"
        RequireNonNegative L1CB, "L1CB", "LiquidityBuffer"
        RequireNonNegative L2A, "L2A", "LiquidityBuffer"
        RequireNonNegative L2B, "L2B", "LiquidityBuffer"
        RequireNonNegative ExcessAmount, "ExcessAmount", "LiquidityBuffer"

        Gross = L1 + L1CB + L2A + L2B
        LiquidityBuffer = Gross - MinOf(Gross, ExcessAmount)
End Function


'------------------------------------------------------------------------------
'                           NET LIQUIDITY OUTFLOW
'------------------------------------------------------------------------------

Public Function NetLiquidityOutflow( _
    ByVal TotalOutflows As Double, _
    ByVal ExemptInflows As Double, _
    ByVal HigherCapInflows As Double, _
    ByVal CappedInflows As Double, _
    ByVal CapHigher As Double, _
    ByVal CapStandard As Double) _
    As Double
'------------------------------------------------------------------------------
' PURPOSE
'   Return the net liquidity outflow after the reductions for fully exempt
'   inflows, inflows subject to the higher cap and inflows subject to the
'   standard cap, applied in that order.
'
' INPUTS
'   TotalOutflows     TO: weighted outflows; reporting currency; >= 0
'   ExemptInflows     FEI: weighted inflows exempt from the cap; >= 0
'   HigherCapInflows  IHC: weighted inflows subject to the 90% cap; >= 0
'   CappedInflows     IC: weighted inflows subject to the 75% cap; >= 0
'   CapHigher         Higher cap as a share of outflows (0.90); 0 < x <= 1
'   CapStandard       Standard cap as a share of outflows (0.75); 0 < x <= 1
'
' RETURNS
'   NLO = TO - MIN(FEI, TO) - MIN(IHC, CapHigher x MAX(TO - FEI, 0))
'         - MIN(IC, CapStandard x MAX(TO - FEI - IHC / CapHigher, 0)); >= 0.
'
' ERROR POLICY
'   Raises ERR_ENGINE_INPUT for a negative amount or a cap out of range.
'
' REFERENCE
'   DR 2015/61 Annex II; Article 33.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Result             As Double    'Outflows left after each reduction

        RequireNonNegative TotalOutflows, "TotalOutflows", "NetLiquidityOutflow"
        RequireNonNegative ExemptInflows, "ExemptInflows", "NetLiquidityOutflow"
        RequireNonNegative HigherCapInflows, "HigherCapInflows", "NetLiquidityOutflow"
        RequireNonNegative CappedInflows, "CappedInflows", "NetLiquidityOutflow"
        RequireShare CapHigher, "CapHigher", "NetLiquidityOutflow", False
        RequireShare CapStandard, "CapStandard", "NetLiquidityOutflow", False

        Result = TotalOutflows - MinOf(ExemptInflows, TotalOutflows)
        Result = Result - MinOf(HigherCapInflows, CapHigher * MaxOf(TotalOutflows - ExemptInflows, 0#))
        Result = Result - MinOf(CappedInflows, CapStandard * _
                     MaxOf(TotalOutflows - ExemptInflows - HigherCapInflows / CapHigher, 0#))
        NetLiquidityOutflow = MaxOf(Result, 0#)
End Function


'------------------------------------------------------------------------------
'                                  RATIO
'------------------------------------------------------------------------------

Public Function CoverageRatio( _
    ByVal Buffer As Double, _
    ByVal NetOutflow As Double) _
    As Variant
'------------------------------------------------------------------------------
' PURPOSE
'   Return the liquidity coverage ratio, or Empty when it is not defined.
'
' INPUTS
'   Buffer      Liquidity buffer; reporting currency; >= 0
'   NetOutflow  Net liquidity outflow; reporting currency; >= 0
'
' RETURNS
'   Buffer / NetOutflow as a Double (1.25 for 125%); Empty when
'   NetOutflow = 0.
'
' ERROR POLICY
'   Raises ERR_ENGINE_INPUT for a negative argument.
'
' REFERENCE
'   DR 2015/61 Article 4(1).
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        RequireNonNegative Buffer, "Buffer", "CoverageRatio"
        RequireNonNegative NetOutflow, "NetOutflow", "CoverageRatio"
        If NetOutflow > 0# Then
            CoverageRatio = Buffer / NetOutflow
        Else
            CoverageRatio = Empty
        End If
End Function


'------------------------------------------------------------------------------
'                                 HELPERS
'------------------------------------------------------------------------------

Public Function MinOf( _
    ByVal FirstValue As Double, _
    ByVal SecondValue As Double) _
    As Double
'------------------------------------------------------------------------------
' PURPOSE
'   Return the smaller of two numbers (worksheet MIN without the Application).
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        If FirstValue < SecondValue Then MinOf = FirstValue Else MinOf = SecondValue
End Function


Public Function MaxOf( _
    ByVal FirstValue As Double, _
    ByVal SecondValue As Double) _
    As Double
'------------------------------------------------------------------------------
' PURPOSE
'   Return the larger of two numbers.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        If FirstValue > SecondValue Then MaxOf = FirstValue Else MaxOf = SecondValue
End Function


Private Sub RequireNonNegative( _
    ByVal Value As Double, _
    ByVal ArgumentName As String, _
    ByVal ProcedureName As String)
'------------------------------------------------------------------------------
' PURPOSE
'   Raise ERR_ENGINE_INPUT when an amount is negative.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        If Value < 0# Then
            Err.Raise ERR_ENGINE_INPUT, "CORE_Engine." & ProcedureName, _
                      ArgumentName & " must be >= 0; got " & CStr(Value) & "."
        End If
End Sub


Private Sub RequireShare( _
    ByVal Value As Double, _
    ByVal ArgumentName As String, _
    ByVal ProcedureName As String, _
    ByVal ZeroAllowed As Boolean)
'------------------------------------------------------------------------------
' PURPOSE
'   Raise ERR_ENGINE_INPUT when a share is outside (0, 1], or [0, 1) when
'   ZeroAllowed is True (a maximum share must leave room for the rest).
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Valid              As Boolean   'True when Value is in its domain

        If ZeroAllowed Then
            Valid = (Value >= 0# And Value < 1#)
        Else
            Valid = (Value > 0# And Value <= 1#)
        End If
        If Not Valid Then
            Err.Raise ERR_ENGINE_INPUT, "CORE_Engine." & ProcedureName, _
                      ArgumentName & " is out of range; got " & CStr(Value) & "."
        End If
End Sub
