import unittest

from medpulse.core.calculators.drugs import antibiotic_dose, dilute_powder, insulin_tdd
from medpulse.core.exceptions import ValidationError


class DrugCalculatorTests(unittest.TestCase):
    def test_dilute_powder(self):
        res = dilute_powder(1000, 50)
        self.assertEqual(res.result, 20.0)
        self.assertEqual(res.unit, "mg/mL")
        self.assertIn("Concentration", res.formula)
        self.assertIn("1000.00 mg / 50.00 mL", res.substitution)

    def test_dilute_powder_invalid(self):
        with self.assertRaises(ValidationError):
            dilute_powder(100, 0)
        with self.assertRaises(ValidationError):
            dilute_powder("a", 10)

    def test_antibiotic_dose(self):
        res = antibiotic_dose(50, 15)
        self.assertEqual(res.result, 750.0)
        self.assertEqual(res.unit, "mg")
        self.assertIn("Single dose", res.formula)
        self.assertIn("50.00 kg x 15.00 mg/kg", res.substitution)

    def test_antibiotic_dose_invalid(self):
        with self.assertRaises(ValidationError):
            antibiotic_dose(0, 15)
        with self.assertRaises(ValidationError):
            antibiotic_dose(50, -5)

    def test_insulin_tdd(self):
        res = insulin_tdd(60)
        self.assertEqual(res.result, 30.0)
        self.assertEqual(res.unit, "U/day")
        self.assertIn("TDD", res.formula)
        self.assertIn("60.00 kg x 0.5 U/kg", res.substitution)

    def test_insulin_tdd_invalid(self):
        with self.assertRaises(ValidationError):
            insulin_tdd(-1)


if __name__ == "__main__":
    unittest.main()
