"""Shared dataclasses for deterministic outputs."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CalculationResult:
    key: str
    label: str
    formula: str
    substitution: str
    value: float
    unit: str
    reference: str
    interpretation: str = ""
    latex_formula: str = ""
    conclusion: str = ""
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, object] = field(default_factory=dict)

    def format_value(self):
        return "%.2f" % self.value if isinstance(self.value, (int, float)) else str(self.value)

    @property
    def result(self):
        return self.value


@dataclass
class ScoreResult:
    score_id: str
    label: str
    total_score: int
    risk_level: str
    guidance: str
    breakdown: List[Dict[str, object]] = field(default_factory=list)


@dataclass
class ABGAnalysis:
    summary: str
    steps: List[str]
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, object] = field(default_factory=dict)
    formula: str = ""
    substitution: str = ""
    conclusion: str = ""
