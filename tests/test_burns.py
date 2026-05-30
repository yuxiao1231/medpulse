import unittest

from medpulse.core.calculators.burns import parkland_formula
from medpulse.core.exceptions import ValidationError


class BurnCalculatorTests(unittest.TestCase):
    def test_parkland_formula(self):
        res = parkland_formula(70, 50)
        self.assertEqual(res.total_24h_ml, 14000)
        self.assertEqual(res.first_8h_rate_ml_h, 7000 / 8.0)
        self.assertEqual(res.next_16h_rate_ml_h, 7000 / 16.0)
        self.assertIn("24h fluid", res.formula)
        self.assertIn("4 x 70.00 x 50.00", res.substitution)

    def test_parkland_invalid(self):
        with self.assertRaises(ValidationError):
            parkland_formula(70, 150)
        with self.assertRaises(ValidationError):
            parkland_formula(0, 50)
        with self.assertRaises(ValidationError):
            parkland_formula("a", 50)


if __name__ == "__main__":
    unittest.main()
