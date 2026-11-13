"""Single source of truth for the K-LCR prototype: parameters, category
catalogue, illustrative inputs, and a reference implementation of the
EU LCR aggregation (Delegated Regulation (EU) 2015/61, as amended by
Delegated Regulation (EU) 2018/1620, Annex I and Annex II).

The template builder writes these values into the workbook; the test
script compares the VBA engine's output with `compute()`. Neither script is
tracked yet; tools/test_lcr_spec.py pins the figures that `compute()` returns
for the demonstration data below.

This is a model written for the prototype, not an independent oracle in the
sense of docs/methodology/VALIDATION_PLAN.md, and its regulatory factors have
not been checked against the stored sources.
"""
from __future__ import annotations

import datetime as dt
from collections.abc import Sequence

# A parameter: (code, description, value, number format, editable, reference).
Param = tuple[str, str, dt.datetime | str | float, str, bool, str]
# A catalogue entry: (code, type, class, description, factor, editable, reference).
Category = tuple[str, str, str, str, float, bool, str]
# A holding: (id, description, category, currency, market value, unwind adjustment).
Holding = tuple[str, str, str, str, int, int]
# An outflow or inflow line: (id, description, category, currency, amount).
Line = tuple[str, str, str, str, int]

# --------------------------------------------------------------- params ----
# (code, description, value, number format, editable, reference)
PARAMS: list[Param] = [
    ("AsOfDate", "Reporting (calculation) date", dt.datetime(2026, 9, 30), "yyyy\\-mm\\-dd", True, ""),
    ("ReportingCcy", "Reporting currency (all amounts converted into it)", "EUR", "@", True, ""),
    ("LCRRequirement", "Minimum LCR", 1.0, "0%", False, "CRR Art. 412(1); DR 2015/61 Art. 4(2)"),
    ("MinShareL1exCB", "Minimum share of level 1 excl. EHQCB in the buffer", 0.30, "0%", False, "DR 2015/61 Art. 17(1)(b); Annex I"),
    ("MinShareL1", "Minimum share of level 1 in the buffer", 0.60, "0%", False, "DR 2015/61 Art. 17(1)(a); Annex I"),
    ("MaxShareL2B", "Maximum share of level 2B in the buffer", 0.15, "0%", False, "DR 2015/61 Art. 17(1)(c); Annex I"),
    ("InflowCapStandard", "Cap on inflows: share of outflows (standard)", 0.75, "0%", False, "DR 2015/61 Art. 33(1); Annex II"),
    ("InflowCapHigher", "Cap on inflows: share of outflows (higher cap)", 0.90, "0%", False, "DR 2015/61 Art. 33(4); Annex II"),
    ("WithholdIncomplete", "TRUE = withhold the LCR of a scope with rejected lines", True, "General", True, "K-LCR policy"),
]

# ------------------------------------------------------------ catalogue ----
# (code, type, class, description, factor, editable, reference)
# HQLA: factor = haircut, class = level (L1, L1CB, L2A, L2B)
# OUTFLOW: factor = outflow rate, class = "-"
# INFLOW: factor = inflow rate, class = cap class (75, 90, EXEMPT)
CATALOGUE: list[Category] = [
    ("L1_CASH", "HQLA", "L1", "Coins and banknotes", 0.00, False, "Art. 10(1)(a)"),
    ("L1_CB_RESERVES", "HQLA", "L1", "Withdrawable central bank reserves", 0.00, False, "Art. 10(1)(b)"),
    ("L1_SOV", "HQLA", "L1", "Central government, central bank, PSE and MDB assets (level 1)", 0.00, False, "Art. 10(1)(c)-(e), (g)"),
    ("L1_EHQCB", "HQLA", "L1CB", "Extremely high quality covered bonds", 0.07, False, "Art. 10(1)(f), 10(2)"),
    ("L2A_SOV", "HQLA", "L2A", "Government, central bank and PSE assets, 20% risk weight", 0.15, False, "Art. 11(1)(a)-(b)"),
    ("L2A_CB", "HQLA", "L2A", "High quality covered bonds (level 2A)", 0.15, False, "Art. 11(1)(c)-(d)"),
    ("L2A_CORP", "HQLA", "L2A", "Corporate debt securities, CQS 1", 0.15, False, "Art. 11(1)(e)"),
    ("L2B_ABS_25", "HQLA", "L2B", "Securitisations: residential, guaranteed residential, auto", 0.25, False, "Art. 13(2)(g)(i), (ii), (iv); 13(14)"),
    ("L2B_ABS_35", "HQLA", "L2B", "Securitisations: SME and consumer loans", 0.35, False, "Art. 13(2)(g)(iii), (v); 13(14)"),
    ("L2B_CB", "HQLA", "L2B", "High quality covered bonds (level 2B)", 0.30, False, "Art. 12(1)(e)"),
    ("L2B_CORP", "HQLA", "L2B", "Corporate debt securities, CQS 1-3", 0.50, False, "Art. 12(1)(b)"),
    ("L2B_EQUITY", "HQLA", "L2B", "Shares in a major stock index", 0.50, False, "Art. 12(1)(c)"),
    ("L2B_RCLF", "HQLA", "L2B", "Restricted-use committed liquidity facilities", 0.00, False, "Art. 12(1)(d), 14"),

    ("OUT_RET_STABLE", "OUTFLOW", "-", "Stable retail deposits", 0.05, False, "Art. 24(1)"),
    ("OUT_RET_STABLE_3", "OUTFLOW", "-", "Stable retail deposits, 3% treatment (with permission)", 0.03, False, "Art. 24(4)"),
    ("OUT_RET_OTHER", "OUTFLOW", "-", "Other retail deposits", 0.10, False, "Art. 25(1)"),
    ("OUT_RET_HIGH1", "OUTFLOW", "-", "Retail deposits, higher outflow category 1 (10-15%)", 0.15, True, "Art. 25(3)(a)"),
    ("OUT_RET_HIGH2", "OUTFLOW", "-", "Retail deposits, higher outflow category 2 (15-20%)", 0.20, True, "Art. 25(3)(b)"),
    ("OUT_OPER_DGS", "OUTFLOW", "-", "Operational deposits, portion covered by a DGS", 0.05, False, "Art. 27(2)"),
    ("OUT_OPER", "OUTFLOW", "-", "Operational deposits, not covered by a DGS", 0.25, False, "Art. 27(1)"),
    ("OUT_NONOP_DGS", "OUTFLOW", "-", "Non-operational deposits of non-financial customers, covered by a DGS", 0.20, False, "Art. 28(1)"),
    ("OUT_NONOP", "OUTFLOW", "-", "Non-operational deposits of non-financial customers", 0.40, False, "Art. 28(1)"),
    ("OUT_FIN", "OUTFLOW", "-", "Deposits and other liabilities of financial customers", 1.00, False, "Art. 31a(1)"),
    ("OUT_OWN_DEBT", "OUTFLOW", "-", "Own debt securities maturing within 30 days", 1.00, False, "Art. 28(6)"),
    ("OUT_SEC_L1", "OUTFLOW", "-", "Secured funding against level 1 excl. EHQCB", 0.00, False, "Art. 28(3)(a)"),
    ("OUT_SEC_EHQCB", "OUTFLOW", "-", "Secured funding against EHQCB", 0.07, False, "Art. 28(3)(b)"),
    ("OUT_SEC_L2A", "OUTFLOW", "-", "Secured funding against level 2A", 0.15, False, "Art. 28(3)(c)"),
    ("OUT_SEC_L2B_25", "OUTFLOW", "-", "Secured funding against level 2B securitisations (25%)", 0.25, False, "Art. 28(3)(d)"),
    ("OUT_SEC_L2B_30", "OUTFLOW", "-", "Secured funding against level 2B covered bonds", 0.30, False, "Art. 28(3)(e)"),
    ("OUT_SEC_L2B_35", "OUTFLOW", "-", "Secured funding against level 2B securitisations (35%)", 0.35, False, "Art. 28(3)(f)"),
    ("OUT_SEC_L2B_50", "OUTFLOW", "-", "Secured funding against other level 2B", 0.50, False, "Art. 28(3)(g)"),
    ("OUT_SEC_OTHER", "OUTFLOW", "-", "Secured funding against non-liquid collateral", 1.00, False, "Art. 28(3)(i)"),
    ("OUT_COLL_NONL1", "OUTFLOW", "-", "Non-cash collateral posted for derivatives, other than level 1", 0.20, False, "Art. 30(1)"),
    ("OUT_DOWNGRADE", "OUTFLOW", "-", "Additional collateral on a 3-notch downgrade", 1.00, False, "Art. 30(2)"),
    ("OUT_HLBA", "OUTFLOW", "-", "Market valuation changes (historical look-back approach)", 1.00, False, "Art. 30(3)"),
    ("OUT_DER_NET", "OUTFLOW", "-", "Net derivative outflows", 1.00, False, "Art. 30(4)"),
    ("OUT_SHORT", "OUTFLOW", "-", "Uncovered short positions", 1.00, False, "Art. 30(5)"),
    ("OUT_EXCESS_COLL", "OUTFLOW", "-", "Excess, due or substitutable collateral", 1.00, False, "Art. 30(6)"),
    ("OUT_FAC_RET", "OUTFLOW", "-", "Undrawn committed credit and liquidity facilities, retail", 0.05, False, "Art. 31(3)"),
    ("OUT_FAC_NFC_CR", "OUTFLOW", "-", "Undrawn committed credit facilities, non-financial customers", 0.10, False, "Art. 31(4)"),
    ("OUT_FAC_NFC_LIQ", "OUTFLOW", "-", "Undrawn committed liquidity facilities, non-financial customers", 0.30, False, "Art. 31(5)"),
    ("OUT_FAC_CI", "OUTFLOW", "-", "Undrawn committed facilities to credit institutions", 0.40, False, "Art. 31(8)(a)"),
    ("OUT_FAC_OFI_CR", "OUTFLOW", "-", "Undrawn committed credit facilities, other regulated financials", 0.40, False, "Art. 31(8)(a)"),
    ("OUT_FAC_OTHER", "OUTFLOW", "-", "Other undrawn committed facilities to financial customers", 1.00, False, "Art. 31(8)(b)-(c)"),
    ("OUT_TRADE_FIN", "OUTFLOW", "-", "Trade finance off-balance sheet products", 0.05, True, "Art. 23"),
    ("OUT_OTHER", "OUTFLOW", "-", "Other liabilities due within 30 days", 1.00, False, "Art. 31a(1)"),

    ("IN_NFC", "INFLOW", "75", "Monies due from non-financial customers (incl. retail)", 0.50, False, "Art. 32(3)(a)"),
    ("IN_FIN", "INFLOW", "75", "Monies due from financial customers and central banks", 1.00, False, "Art. 32(2)(a)"),
    ("IN_SEC_L1", "INFLOW", "75", "Secured lending against level 1 excl. EHQCB", 0.00, False, "Art. 32(3)(b)(i)"),
    ("IN_SEC_EHQCB", "INFLOW", "75", "Secured lending against EHQCB", 0.07, False, "Art. 32(3)(b)(ii)"),
    ("IN_SEC_L2A", "INFLOW", "75", "Secured lending against level 2A", 0.15, False, "Art. 32(3)(b)(iii)"),
    ("IN_SEC_L2B_25", "INFLOW", "75", "Secured lending against level 2B securitisations (25%)", 0.25, False, "Art. 32(3)(b)(iv)"),
    ("IN_SEC_L2B_30", "INFLOW", "75", "Secured lending against level 2B covered bonds", 0.30, False, "Art. 32(3)(b)(v)"),
    ("IN_SEC_L2B_35", "INFLOW", "75", "Secured lending against level 2B securitisations (35%)", 0.35, False, "Art. 32(3)(b)(vi)"),
    ("IN_SEC_L2B_50", "INFLOW", "75", "Secured lending against other level 2B", 0.50, False, "Art. 32(3)(b)(vii)"),
    ("IN_SEC_OTHER", "INFLOW", "75", "Secured lending against non-liquid collateral", 1.00, False, "Art. 32(3)(b)(ix)"),
    ("IN_MARGIN", "INFLOW", "75", "Margin loans against non-liquid collateral", 0.50, False, "Art. 32(3)(c)"),
    ("IN_OPER", "INFLOW", "75", "Operational deposits held at other institutions", 0.05, False, "Art. 32(3)(d)"),
    ("IN_DER_NET", "INFLOW", "75", "Net derivative inflows", 1.00, False, "Art. 32(5)"),
    ("IN_HIGHER_CAP", "INFLOW", "90", "Inflows subject to the 90% cap (with permission)", 1.00, True, "Art. 33(4)"),
    ("IN_EXEMPT", "INFLOW", "EXEMPT", "Inflows exempt from the cap (with permission)", 1.00, True, "Art. 33(2)-(3)"),
]

FX: list[tuple[str, str, float]] = [("EUR", "Euro", 1.0), ("USD", "US dollar", 0.86), ("GBP", "Pound sterling", 1.16),
      ("CHF", "Swiss franc", 1.07), ("JPY", "Japanese yen", 0.0058)]

# --------------------------------------------------------------- inputs ----
# HQLA: (id, description, category, ccy, market value, unwind adjustment)
HQLA: list[Holding] = [
    ("H001", "Banknotes and coins", "L1_CASH", "EUR", 25_000_000, 0),
    ("H002", "Eurosystem reserves above minimum", "L1_CB_RESERVES", "EUR", 500_000_000, 0),
    ("H003", "BTP 2.80% 2029", "L1_SOV", "EUR", 700_000_000, 0),
    ("H004", "Bund 0% 2031, received in reverse repo (10 days)", "L1_SOV", "EUR", 150_000_000, -150_000_000),
    ("H005", "Covered bonds ECAI CQS1, EHQCB", "L1_EHQCB", "EUR", 500_000_000, 0),
    ("H006", "Regional government bonds, 20% RW", "L2A_SOV", "EUR", 300_000_000, 0),
    ("H007", "Covered bonds CQS1 (level 2A)", "L2A_CB", "EUR", 250_000_000, 0),
    ("H008", "Corporate bonds CQS1", "L2A_CORP", "EUR", 150_000_000, 0),
    ("H009", "RMBS senior tranche", "L2B_ABS_25", "EUR", 200_000_000, 0),
    ("H010", "Corporate bonds CQS2-3", "L2B_CORP", "EUR", 900_000_000, 0),
    ("H011", "Shares, EURO STOXX 50 constituents", "L2B_EQUITY", "EUR", 400_000_000, 0),
    ("H012", "Federal Reserve balances", "L1_CB_RESERVES", "USD", 120_000_000, 0),
    ("H013", "US Treasury notes", "L1_SOV", "USD", 150_000_000, 0),
    ("H014", "Agency debentures, 20% RW", "L2A_SOV", "USD", 100_000_000, 0),
    ("H015", "Corporate bonds CQS2", "L2B_CORP", "USD", 120_000_000, 0),
    ("H016", "US Treasury posted in repo (returned on unwind)", "L1_SOV", "USD", 0, 80_000_000),
]

# Outflows: (id, description, category, ccy, amount)
OUTFLOWS: list[Line] = [
    ("O001", "Retail deposits, stable", "OUT_RET_STABLE", "EUR", 6_000_000_000),
    ("O002", "Retail deposits, other", "OUT_RET_OTHER", "EUR", 2_500_000_000),
    ("O003", "Retail deposits, higher outflow category 1", "OUT_RET_HIGH1", "EUR", 400_000_000),
    ("O004", "Operational deposits, cash management", "OUT_OPER", "EUR", 1_200_000_000),
    ("O005", "Corporate deposits, non-operational", "OUT_NONOP", "EUR", 1_500_000_000),
    ("O006", "SME deposits, non-operational, DGS covered", "OUT_NONOP_DGS", "EUR", 300_000_000),
    ("O007", "Deposits of financial customers", "OUT_FIN", "EUR", 250_000_000),
    ("O008", "Senior bond maturing 2026-10-15", "OUT_OWN_DEBT", "EUR", 150_000_000),
    ("O009", "Repo against level 1 collateral", "OUT_SEC_L1", "EUR", 400_000_000),
    ("O010", "Repo against corporate bonds (level 2B)", "OUT_SEC_L2B_50", "EUR", 100_000_000),
    ("O011", "Undrawn committed credit lines, corporates", "OUT_FAC_NFC_CR", "EUR", 2_000_000_000),
    ("O012", "Undrawn committed liquidity lines, corporates", "OUT_FAC_NFC_LIQ", "EUR", 300_000_000),
    ("O013", "Undrawn retail credit lines", "OUT_FAC_RET", "EUR", 800_000_000),
    ("O014", "Undrawn lines to credit institutions", "OUT_FAC_CI", "EUR", 150_000_000),
    ("O015", "Net derivative outflows", "OUT_DER_NET", "EUR", 40_000_000),
    ("O016", "Historical look-back approach", "OUT_HLBA", "EUR", 60_000_000),
    ("O017", "Trade finance guarantees", "OUT_TRADE_FIN", "EUR", 200_000_000),
    ("O018", "Corporate deposits, non-operational", "OUT_NONOP", "USD", 1_200_000_000),
    ("O019", "Deposits of financial customers", "OUT_FIN", "USD", 200_000_000),
    ("O020", "Undrawn committed credit lines, corporates", "OUT_FAC_NFC_CR", "USD", 500_000_000),
    ("O021", "Net derivative outflows", "OUT_DER_NET", "USD", 30_000_000),
]

# Inflows: (id, description, category, ccy, amount)
INFLOWS: list[Line] = [
    ("I001", "Corporate loans, contractual repayments", "IN_NFC", "EUR", 500_000_000),
    ("I002", "Interbank placements", "IN_FIN", "EUR", 300_000_000),
    ("I003", "Reverse repo against level 1 collateral", "IN_SEC_L1", "EUR", 150_000_000),
    ("I004", "Reverse repo against non-liquid collateral", "IN_SEC_OTHER", "EUR", 50_000_000),
    ("I005", "Retail loans, contractual repayments", "IN_NFC", "EUR", 200_000_000),
    ("I006", "Net derivative inflows", "IN_DER_NET", "EUR", 25_000_000),
    ("I007", "Intragroup inflow (exempt, with permission)", "IN_EXEMPT", "EUR", 100_000_000),
    ("I008", "Interbank placements", "IN_FIN", "USD", 800_000_000),
    ("I009", "Reverse repo against level 2A collateral", "IN_SEC_L2A", "USD", 100_000_000),
]


# ------------------------------------------------------------- reference ----
def liquidity_buffer(l1: float, l1cb: float, l2a: float, l2b: float,
                     a1: float, a1cb: float, a2a: float, a2b: float,
                     s30: float = 0.30, s60: float = 0.60, s15: float = 0.15) -> tuple[float, float]:
    """Annex I, paras 2 and 4 (as amended by DR 2018/1620). Returns (excess, buffer)."""
    s = a1 + a1cb + a2a + a2b
    excess = s - min(s, a1 / s30, (a1 + a1cb) / s60, (a1 + a1cb + a2a) / (1 - s15))
    gross = l1 + l1cb + l2a + l2b
    return excess, gross - min(gross, excess)


def net_outflow(to: float, fei: float, ihc: float, ic: float,
                cap75: float = 0.75, cap90: float = 0.90) -> float:
    """Annex II."""
    return (to - min(fei, to) - min(ihc, cap90 * max(to - fei, 0))
            - min(ic, cap75 * max(to - fei - ihc / cap90, 0)))


def compute(hqla: Sequence[Holding] = HQLA, outflows: Sequence[Line] = OUTFLOWS,
            inflows: Sequence[Line] = INFLOWS) -> dict[str, dict[str, float | None]]:
    cat = {c[0]: c for c in CATALOGUE}
    fx = {c: r for c, _, r in FX}
    scopes: dict[str, dict[str, float]] = {}

    def acc(scope: str, key: str, value: float) -> None:
        scopes.setdefault(scope, {}).setdefault(key, 0.0)
        scopes[scope][key] += value

    for _, _, code, ccy, mv, unwind in hqla:
        _, _, level, _, haircut, _, _ = cat[code]
        for scope in (ccy, "TOTAL"):
            acc(scope, "H_" + level, mv * fx[ccy] * (1 - haircut))
            acc(scope, "A_" + level, (mv + unwind) * fx[ccy] * (1 - haircut))
    for _, _, code, ccy, amount in outflows:
        for scope in (ccy, "TOTAL"):
            acc(scope, "TO", amount * fx[ccy] * cat[code][4])
    for _, _, code, ccy, amount in inflows:
        cls = cat[code][2]
        key = {"75": "IC", "90": "IHC", "EXEMPT": "FEI"}[cls]
        for scope in (ccy, "TOTAL"):
            acc(scope, key, amount * fx[ccy] * cat[code][4])
    out: dict[str, dict[str, float | None]] = {}
    for scope, v in scopes.items():
        def g(key: str, v: dict[str, float] = v) -> float:
            return v.get(key, 0.0)

        a = {k: max(g("A_" + k), 0.0) for k in ("L1", "L1CB", "L2A", "L2B")}
        excess, buffer = liquidity_buffer(g("H_L1"), g("H_L1CB"), g("H_L2A"), g("H_L2B"),
                                          a["L1"], a["L1CB"], a["L2A"], a["L2B"])
        nlo = net_outflow(g("TO"), g("FEI"), g("IHC"), g("IC"))
        out[scope] = dict(L1=g("H_L1"), L1CB=g("H_L1CB"), L2A=g("H_L2A"), L2B=g("H_L2B"),
                          A1=a["L1"], A1CB=a["L1CB"], A2A=a["L2A"], A2B=a["L2B"],
                          Excess=excess, Buffer=buffer, TO=g("TO"), FEI=g("FEI"), IHC=g("IHC"),
                          IC=g("IC"), NLO=nlo, LCR=buffer / nlo if nlo > 0 else None)
    return out


if __name__ == "__main__":
    for scope, r in compute().items():
        print(scope, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
