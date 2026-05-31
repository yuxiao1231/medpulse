import unittest

from medpulse.core.scores import ScoreService
from medpulse.i18n import set_global_locale


class ScoreTests(unittest.TestCase):
    def setUp(self):
        set_global_locale("en")
        self.service = ScoreService()

    def test_qsofa_high_risk_band(self):
        result = self.service.calculate(
            "qsofa",
            {
                "respiratory_rate_high": True,
                "altered_mentation": True,
                "sbp_low": False,
            },
        )
        self.assertEqual(result.total_score, 2)
        self.assertEqual(result.risk_level, "High Risk")

    def test_gcs_mild_band(self):
        result = self.service.calculate(
            "gcs",
            {
                "eye": "spontaneous",
                "verbal": "oriented",
                "motor": "obeys",
            },
        )
        self.assertEqual(result.total_score, 15)
        self.assertEqual(result.risk_level, "Mild TBI / alert")


if __name__ == "__main__":
    unittest.main()
