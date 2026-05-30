import unittest

from medpulse.core.calculators.abg import analyze_abg
from medpulse.i18n import set_global_locale


class ABGTests(unittest.TestCase):
    def setUp(self):
        set_global_locale("en")

    def test_metabolic_acidosis_with_expected_compensation(self):
        analysis = analyze_abg(7.20, 30, 12)
        self.assertIn("Metabolic acidosis", analysis.summary)
        self.assertTrue(any("Step 3." in step for step in analysis.steps))
        self.assertIn("pH < 7.35", analysis.formula)
        self.assertIn("actual PCO2", analysis.substitution)
        self.assertIn("Metabolic acidosis", analysis.conclusion)

    def test_mixed_acidosis_warning(self):
        analysis = analyze_abg(7.10, 60, 12)
        self.assertTrue(analysis.warnings)

    def test_winter_boundary_warning_is_exposed(self):
        analysis = analyze_abg(7.20, 24.05, 12)
        self.assertTrue(any("close to the boundary" in warning for warning in analysis.warnings))

    def test_respiratory_compensation_boundary_warning_is_exposed(self):
        analysis = analyze_abg(7.30, 50, 25.05)
        self.assertTrue(any("Near formula boundary" in warning for warning in analysis.warnings))


if __name__ == "__main__":
    unittest.main()
