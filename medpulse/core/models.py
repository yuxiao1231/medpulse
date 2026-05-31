"""Shared dataclasses for deterministic outputs."""

class CalculationResult:
    def __init__(self, key, label, formula, substitution, value, unit, reference, interpretation="", latex_formula="", conclusion="", warnings=None, metadata=None):
        self.key = key
        self.label = label
        self.formula = formula
        self.substitution = substitution
        self.value = value
        self.unit = unit
        self.reference = reference
        self.interpretation = interpretation
        self.latex_formula = latex_formula
        self.conclusion = conclusion
        self.warnings = warnings if warnings is not None else []
        self.metadata = metadata if metadata is not None else {}

    def format_value(self):
        return "%.2f" % self.value if isinstance(self.value, (int, float)) else str(self.value)

    @property
    def result(self):
        return self.value


class ScoreResult:
    def __init__(self, score_id, label, total_score, risk_level, guidance, breakdown=None):
        self.score_id = score_id
        self.label = label
        self.total_score = total_score
        self.risk_level = risk_level
        self.guidance = guidance
        self.breakdown = breakdown if breakdown is not None else []


class ABGAnalysis:
    def __init__(self, summary, steps, warnings=None, metadata=None, formula="", substitution="", conclusion=""):
        self.summary = summary
        self.steps = steps
        self.warnings = warnings if warnings is not None else []
        self.metadata = metadata if metadata is not None else {}
        self.formula = formula
        self.substitution = substitution
        self.conclusion = conclusion
