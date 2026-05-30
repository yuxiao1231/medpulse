import unittest

from medpulse.core.calculators.electrolytes import (
    anion_gap,
    delta_gap,
    plasma_osmolarity,
    sodium_correction_rate,
    winter_expected_pco2,
)
from medpulse.i18n import set_global_locale


class ElectrolyteCalculatorTests(unittest.TestCase):
    def setUp(self):
        set_global_locale("en")

    def test_anion_gap(self):
        result = anion_gap(140, 104, 24)
        self.assertEqual(result.value, 12.0)

    def test_anion_gap_albumin_correction_metadata(self):
        result = anion_gap(140, 104, 24, albumin=2.0)
        self.assertEqual(result.metadata["corrected_for_albumin"], 17.0)

    def test_delta_gap(self):
        result = delta_gap(24, 12)
        self.assertEqual(result.value, 1.0)

    def test_delta_gap_zero_denominator(self):
        result = delta_gap(20, 24)
        self.assertEqual(result.value, 0.0)
        self.assertTrue(result.warnings)

    def test_winter_formula(self):
        result = winter_expected_pco2(12, 26)
        self.assertEqual(result.metadata["expected_low"], 24.0)
        self.assertEqual(result.metadata["expected_high"], 28.0)

    def test_winter_formula_boundary_warning(self):
        result = winter_expected_pco2(12, 24.05)
        self.assertTrue(result.warnings)
        self.assertIn("close to the boundary", result.warnings[0])

    def test_sodium_correction_warning(self):
        result = sodium_correction_rate(120, 132, 12)
        self.assertTrue(result.warnings)

    def test_plasma_osmolarity(self):
        result = plasma_osmolarity(140, 90, 14)
        self.assertAlmostEqual(result.value, 290.0, places=1)

    def test_plasma_osmolarity_hyperosmolar_warning(self):
        result = plasma_osmolarity(160, 360, 56)
        self.assertGreater(result.value, 320.0)
        self.assertTrue(result.warnings)

    def test_delta_gap_interpretation_pure_ag(self):
        result = delta_gap(24, 12)
        self.assertIn("1-2", result.interpretation)

    def test_delta_gap_interpretation_mixed(self):
        result = delta_gap(16, 12)
        self.assertIn("0.4", result.interpretation)


if __name__ == "__main__":
    unittest.main()
