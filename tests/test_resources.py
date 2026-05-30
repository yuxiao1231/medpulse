import unittest

from medpulse.core.resources import load_app_metadata, load_json


class ResourceTests(unittest.TestCase):
    def test_load_metadata(self):
        metadata = load_app_metadata()
        self.assertEqual(metadata["project"]["id"], "medpulse")

    def test_load_score_definition(self):
        definition = load_json("scores", "qsofa.json")
        self.assertEqual(definition["id"], "qsofa")


if __name__ == "__main__":
    unittest.main()

