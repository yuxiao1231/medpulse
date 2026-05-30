"""Service wrapper around score definitions."""

from medpulse.core.resources import load_json
from medpulse.core.scores.engine import calculate_score, load_definition


class ScoreService(object):
    """Loads score definitions and executes scoring."""

    def load_definition(self, score_id):
        return load_definition(score_id)

    def calculate(self, score_id, answers):
        definition = self.load_definition(score_id)
        return calculate_score(definition, answers)

    def catalog(self):
        return load_json("scores", "index.json")

