"""Tests of the prototype's Python model (tools/lcr_spec.py).

They pin what `compute()` returns for the demonstration data and check the
formulas of Annex I and Annex II on small hand-made cases. The model is written
for the prototype: these tests make it stable, they do not validate it against
the regulation (docs/methodology/VALIDATION_PLAN.md).
"""

from __future__ import annotations

import unittest

import lcr_spec

AMOUNTS = ("L1", "L1CB", "L2A", "L2B", "TO", "FEI", "IHC", "IC")


def demonstration() -> dict[str, dict[str, float | None]]:
    return lcr_spec.compute()


class DemonstrationFigureTests(unittest.TestCase):
    """The figures that compute() returns for the demonstration data."""

    def test_the_scopes_are_each_currency_and_the_total(self) -> None:
        self.assertEqual(set(demonstration()), {"EUR", "USD", "TOTAL"})

    def test_the_ratio_of_each_scope(self) -> None:
        ratios = {scope: round(figures["LCR"] or 0.0, 2) for scope, figures in demonstration().items()}
        self.assertEqual(ratios, {"EUR": 1.67, "TOTAL": 1.95, "USD": 2.18})

    def test_the_buffer_and_the_net_outflow_of_each_scope(self) -> None:
        expected = {"EUR": (2838235294.12, 1695000000.0),
                    "TOTAL": (3209552941.18, 1647700000.0),
                    "USD": (356900000.0, 163400000.0)}
        for scope, (buffer, net) in expected.items():
            with self.subTest(scope=scope):
                self.assertAlmostEqual(demonstration()[scope]["Buffer"] or 0.0, buffer, places=2)
                self.assertAlmostEqual(demonstration()[scope]["NLO"] or 0.0, net, places=2)

    def test_the_total_adds_the_amounts_of_the_currencies(self) -> None:
        figures = demonstration()
        for key in AMOUNTS:
            with self.subTest(key=key):
                self.assertAlmostEqual(figures["TOTAL"][key] or 0.0,
                                       (figures["EUR"][key] or 0.0) + (figures["USD"][key] or 0.0), places=2)

    def test_the_buffer_never_exceeds_its_gross_amount(self) -> None:
        for scope, figures in demonstration().items():
            gross = sum(figures[key] or 0.0 for key in ("L1", "L1CB", "L2A", "L2B"))
            with self.subTest(scope=scope):
                self.assertLessEqual(figures["Buffer"] or 0.0, gross)


class DataTests(unittest.TestCase):
    def test_catalogue_codes_are_unique_and_typed(self) -> None:
        codes = [entry[0] for entry in lcr_spec.CATALOGUE]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual({entry[1] for entry in lcr_spec.CATALOGUE}, {"HQLA", "OUTFLOW", "INFLOW"})

    def test_factors_are_proportions(self) -> None:
        for code, _, _, _, factor, _, _ in lcr_spec.CATALOGUE:
            with self.subTest(code=code):
                self.assertGreaterEqual(factor, 0.0)
                self.assertLessEqual(factor, 1.0)

    def test_classes_follow_the_type(self) -> None:
        classes = {"HQLA": {"L1", "L1CB", "L2A", "L2B"}, "OUTFLOW": {"-"}, "INFLOW": {"75", "90", "EXEMPT"}}
        for code, kind, cls, _, _, _, _ in lcr_spec.CATALOGUE:
            with self.subTest(code=code):
                self.assertIn(cls, classes[kind])

    def test_every_line_names_a_category_of_its_type_and_a_known_currency(self) -> None:
        kind = {entry[0]: entry[1] for entry in lcr_spec.CATALOGUE}
        currencies = {entry[0] for entry in lcr_spec.FX}
        lines = ([("HQLA", row[0], row[2], row[3]) for row in lcr_spec.HQLA]
                 + [("OUTFLOW", row[0], row[2], row[3]) for row in lcr_spec.OUTFLOWS]
                 + [("INFLOW", row[0], row[2], row[3]) for row in lcr_spec.INFLOWS])
        for expected_kind, line_id, category, currency in lines:
            with self.subTest(line=line_id):
                self.assertEqual(kind[category], expected_kind)
                self.assertIn(currency, currencies)

    def test_line_identifiers_are_unique(self) -> None:
        ids = ([row[0] for row in lcr_spec.HQLA] + [row[0] for row in lcr_spec.OUTFLOWS]
               + [row[0] for row in lcr_spec.INFLOWS])
        self.assertEqual(len(ids), len(set(ids)))

    def test_the_reporting_currency_has_a_rate_of_one(self) -> None:
        self.assertEqual({code: rate for code, _, rate in lcr_spec.FX}["EUR"], 1.0)


class FormulaTests(unittest.TestCase):
    def test_no_excess_when_the_composition_limits_hold(self) -> None:
        excess, buffer = lcr_spec.liquidity_buffer(100, 0, 0, 0, 100, 0, 0, 0)
        self.assertEqual((excess, buffer), (0.0, 100.0))

    def test_level_2b_above_its_share_is_cut(self) -> None:
        # 60 of level 1 and 40 of level 2B: level 2B may be at most 15 % of the buffer.
        excess, buffer = lcr_spec.liquidity_buffer(60, 0, 0, 40, 60, 0, 0, 40)
        self.assertAlmostEqual(excess, 100 - 60 / 0.85)
        self.assertAlmostEqual(buffer, 60 / 0.85)

    def test_the_buffer_is_never_negative(self) -> None:
        self.assertGreaterEqual(lcr_spec.liquidity_buffer(0, 0, 0, 0, 0, 0, 0, 0)[1], 0.0)

    def test_inflows_below_their_cap_reduce_outflows_in_full(self) -> None:
        self.assertEqual(lcr_spec.net_outflow(100, 0, 0, 50), 50)

    def test_inflows_above_the_cap_reduce_outflows_by_the_cap(self) -> None:
        self.assertEqual(lcr_spec.net_outflow(100, 0, 0, 100), 25)

    def test_exempt_inflows_come_off_before_the_cap(self) -> None:
        self.assertEqual(lcr_spec.net_outflow(100, 20, 0, 100), 100 - 20 - 0.75 * 80)

    def test_no_ratio_without_a_net_outflow(self) -> None:
        figures = lcr_spec.compute(hqla=[("H", "x", "L1_CASH", "EUR", 10, 0)], outflows=[], inflows=[])
        self.assertIsNone(figures["EUR"]["LCR"])


if __name__ == "__main__":
    unittest.main()
