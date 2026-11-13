Attribute VB_Name = "LCR_Formulas"
'==============================================================================
' MODULE: LCR_Formulas
'------------------------------------------------------------------------------
' PURPOSE
'   Worksheet functions exposing the regulatory aggregates of CORE_Engine, so
'   that a buffer or a net outflow can be recomputed in any cell.
'
' PUBLIC SURFACE
'   LCR_ExcessLiquidAssets(A1, A1CB, A2A, A2B, [Share30], [Share60], [Share15])
'   LCR_LiquidityBuffer(L1, L1CB, L2A, L2B, A1, A1CB, A2A, A2B, [...])
'   LCR_NetLiquidityOutflow(TO, FEI, IHC, IC, [Cap90], [Cap75])
'   LCR_Ratio(Buffer, NLO)
'
' DEPENDENCIES
'   CORE_Engine.
'
' STATE OWNERSHIP
'   None.
'
' ERROR POLICY
'   The functions never raise: an argument outside its domain returns
'   #VALUE!, a ratio with a zero denominator returns #DIV/0!.
'
' COMPATIBILITY
'   Excel VBA; no references beyond the defaults.
'
' REFERENCE
'   DR 2015/61 Article 4, Annex I paras 2 and 4 (as amended by DR 2018/1620),
'   Annex II.
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
'                           WORKSHEET FUNCTIONS
'------------------------------------------------------------------------------

Public Function LCR_ExcessLiquidAssets( _
    ByVal A1 As Double, _
    ByVal A1CB As Double, _
    ByVal A2A As Double, _
    ByVal A2B As Double, _
    Optional ByVal Share30 As Double = 0.3, _
    Optional ByVal Share60 As Double = 0.6, _
    Optional ByVal Share15 As Double = 0.15) _
    As Variant
'------------------------------------------------------------------------------
' PURPOSE
'   Excess liquid assets amount from the adjusted amounts (Annex I para 4).
'
' INPUTS
'   A1, A1CB, A2A, A2B  Adjusted level 1 excl. EHQCB, level 1 EHQCB, level
'                       2A, level 2B amounts, post-haircut; >= 0
'   Share30, Share60, Share15  Composition limits; defaults 0.30, 0.60, 0.15
'
' RETURNS
'   The amount, or #VALUE! for an argument out of domain.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        On Error GoTo Invalid
        LCR_ExcessLiquidAssets = CORE_Engine.ExcessLiquidAssets(A1, A1CB, A2A, A2B, Share30, Share60, Share15)
        Exit Function
Invalid:
        LCR_ExcessLiquidAssets = CVErr(xlErrValue)
End Function


Public Function LCR_LiquidityBuffer( _
    ByVal L1 As Double, _
    ByVal L1CB As Double, _
    ByVal L2A As Double, _
    ByVal L2B As Double, _
    ByVal A1 As Double, _
    ByVal A1CB As Double, _
    ByVal A2A As Double, _
    ByVal A2B As Double, _
    Optional ByVal Share30 As Double = 0.3, _
    Optional ByVal Share60 As Double = 0.6, _
    Optional ByVal Share15 As Double = 0.15) _
    As Variant
'------------------------------------------------------------------------------
' PURPOSE
'   Liquidity buffer (Annex I para 2): held post-haircut amounts less the
'   excess computed from the adjusted amounts.
'
' INPUTS
'   L1, L1CB, L2A, L2B  Held amounts per level, post-haircut; >= 0
'   A1, A1CB, A2A, A2B  Adjusted amounts per level, post-haircut; >= 0
'   Share30, Share60, Share15  Composition limits; defaults 0.30, 0.60, 0.15
'
' RETURNS
'   The buffer, or #VALUE! for an argument out of domain.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Excess             As Double    'Excess liquid assets amount

        On Error GoTo Invalid
        Excess = CORE_Engine.ExcessLiquidAssets(A1, A1CB, A2A, A2B, Share30, Share60, Share15)
        LCR_LiquidityBuffer = CORE_Engine.LiquidityBuffer(L1, L1CB, L2A, L2B, Excess)
        Exit Function
Invalid:
        LCR_LiquidityBuffer = CVErr(xlErrValue)
End Function


Public Function LCR_NetLiquidityOutflow( _
    ByVal TotalOutflows As Double, _
    ByVal ExemptInflows As Double, _
    ByVal HigherCapInflows As Double, _
    ByVal CappedInflows As Double, _
    Optional ByVal Cap90 As Double = 0.9, _
    Optional ByVal Cap75 As Double = 0.75) _
    As Variant
'------------------------------------------------------------------------------
' PURPOSE
'   Net liquidity outflow (Annex II).
'
' INPUTS
'   TotalOutflows     TO, weighted; >= 0
'   ExemptInflows     FEI, weighted; >= 0
'   HigherCapInflows  IHC, weighted; >= 0
'   CappedInflows     IC, weighted; >= 0
'   Cap90, Cap75      Caps as shares of outflows; defaults 0.90 and 0.75
'
' RETURNS
'   The net outflow, or #VALUE! for an argument out of domain.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
        On Error GoTo Invalid
        LCR_NetLiquidityOutflow = CORE_Engine.NetLiquidityOutflow(TotalOutflows, ExemptInflows, _
                                      HigherCapInflows, CappedInflows, Cap90, Cap75)
        Exit Function
Invalid:
        LCR_NetLiquidityOutflow = CVErr(xlErrValue)
End Function


Public Function LCR_Ratio( _
    ByVal Buffer As Double, _
    ByVal NetOutflow As Double) _
    As Variant
'------------------------------------------------------------------------------
' PURPOSE
'   Liquidity coverage ratio (Article 4): Buffer / NetOutflow.
'
' RETURNS
'   The ratio (1.25 = 125%), #DIV/0! when NetOutflow = 0, #VALUE! for a
'   negative argument.
'
' UPDATED
'   2026-11-13
'------------------------------------------------------------------------------
    Dim Ratio              As Variant   'Engine result, Empty when undefined

        On Error GoTo Invalid
        Ratio = CORE_Engine.CoverageRatio(Buffer, NetOutflow)
        If IsEmpty(Ratio) Then
            LCR_Ratio = CVErr(xlErrDiv0)
        Else
            LCR_Ratio = Ratio
        End If
        Exit Function
Invalid:
        LCR_Ratio = CVErr(xlErrValue)
End Function
