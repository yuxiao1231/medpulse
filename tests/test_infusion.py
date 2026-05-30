import unittest

from medpulse.core.calculators.infusion import (
    concentration_from_amount,
    get_supported_infusion_templates,
    mcg_per_kg_min_to_ml_per_hour,
    ml_per_hour_to_mcg_per_kg_min,
)


class InfusionTests(unittest.TestCase):
    def test_round_trip_conversion(self):
        rate = mcg_per_kg_min_to_ml_per_hour(0.1, 70, 80)
        self.assertEqual(rate, 5.25)
        dose = ml_per_hour_to_mcg_per_kg_min(rate, 70, 80)
        self.assertEqual(dose, 0.1)

    def test_mg_per_ml_concentration_is_converted(self):
        rate = mcg_per_kg_min_to_ml_per_hour(0.1, 70, 0.08, "mg/mL")
        self.assertEqual(rate, 5.25)

    def test_total_amount_concentration_is_converted(self):
        concentration = concentration_from_amount(4, "mg", 50)
        self.assertEqual(str(concentration), "80")
        rate = mcg_per_kg_min_to_ml_per_hour(0.1, 70, concentration)
        self.assertEqual(rate, 5.25)

    def test_direct_mcg_per_ml_concentration(self):
            # Direct mcg/mL numerical value, bypassing unit conversion path
            rate = mcg_per_kg_min_to_ml_per_hour(0.1, 70, 80, "mcg/mL")
            self.assertEqual(rate, 5.25)
            dose = ml_per_hour_to_mcg_per_kg_min(5.25, 70, 80, "mcg/mL")
            self.assertEqual(dose, 0.1)

    def test_supported_templates_only_include_mcg_weight_mode(self):
        templates = get_supported_infusion_templates()
        self.assertTrue(templates)
        self.assertTrue(all(item["mode"] == "mcg_per_kg_min" for item in templates))


if __name__ == "__main__":
    unittest.main()
