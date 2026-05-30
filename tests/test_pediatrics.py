import unittest

from medpulse.core.calculators.pediatrics import maintenance_fluid_421, mosteller_bsa


class PediatricsTests(unittest.TestCase):
    def test_mosteller_bsa(self):
        result = mosteller_bsa(70, 170)
        self.assertAlmostEqual(result.value, 1.82, places=2)

    def test_maintenance_fluid(self):
        result = maintenance_fluid_421(25)
        self.assertEqual(result.value, 65.0)
        self.assertFalse(result.warnings)

    def test_maintenance_fluid_overload_warning(self):
        # 70 kg -> 4*10 + 2*10 + 1*50 = 110 mL/h, should trigger a warning
        result = maintenance_fluid_421(70)
        self.assertEqual(result.value, 110.0)
        self.assertTrue(result.warnings)

    def test_mosteller_bsa_edge_low(self):
        # Extremely low birth weight infant scale
        result = mosteller_bsa(3.5, 50)
        self.assertGreater(result.value, 0.0)
        self.assertLess(result.value, 0.5)


if __name__ == "__main__":
    unittest.main()

