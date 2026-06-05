"""Calculators for burn fluid resuscitation."""
from medpulse.core.exceptions import ValidationError
from medpulse.core.models import CalculationResult
from medpulse.i18n import t

class ParklandResult(CalculationResult):
    def __init__(self, key, label, formula, substitution, value, unit, reference, interpretation="", latex_formula="", conclusion="", warnings=None, metadata=None, total_24h_ml=0.0, first_8h_rate_ml_h=0.0, next_16h_rate_ml_h=0.0):
        super().__init__(key, label, formula, substitution, value, unit, reference, interpretation, latex_formula, conclusion, warnings, metadata)
        self.total_24h_ml = total_24h_ml
        self.first_8h_rate_ml_h = first_8h_rate_ml_h
        self.next_16h_rate_ml_h = next_16h_rate_ml_h


def _coerce_float(value, error_key, default_message):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValidationError(t(error_key, default_message))


def parkland_formula(weight_kg, tbsa_percent):
    """Calculate the Parkland burn resuscitation formula."""
    weight = _coerce_float(weight_kg, "err_weight_tbsa_num", "Weight and TBSA must be valid numbers.")
    tbsa = _coerce_float(tbsa_percent, "err_weight_tbsa_num", "Weight and TBSA must be valid numbers.")

    if weight <= 0:
        raise ValidationError(t("err_weight_gt_zero", "Weight must be greater than zero."))
    if tbsa <= 0 or tbsa > 100:
        raise ValidationError(t("err_tbsa_range", "TBSA must be between 1 and 100."))

    total_fluid = 4.0 * weight * tbsa
    first_8h_volume = total_fluid / 2.0
    next_16h_volume = total_fluid / 2.0
    first_8h_rate = first_8h_volume / 8.0
    next_16h_rate = next_16h_volume / 16.0

    conclusion_tmpl = t(
        "parkland_desc",
        "24h Total: %.0f mL\nFirst 8h Rate: %.0f mL/h\nNext 16h Rate: %.0f mL/h",
    )
    conclusion = conclusion_tmpl % (total_fluid, first_8h_rate, next_16h_rate)

    return ParklandResult(
        key="parkland_formula",
        label=t("burn_calc", "Burn (Parkland)"),
        formula=(
            "24h fluid = 4 mL x weight (kg) x TBSA (%); first 8h rate = 50% total / 8; "
            "next 16h rate = 50% total / 16"
        ),
        substitution=(
            "4 x %.2f x %.2f = %.2f mL; %.2f / 2 / 8 = %.2f mL/h; "
            "%.2f / 2 / 16 = %.2f mL/h"
        )
        % (weight, tbsa, total_fluid, total_fluid, first_8h_rate, total_fluid, next_16h_rate),
        value=round(total_fluid, 2),
        unit="mL/24h",
        reference=t("checklist_note", "For reference only. Does not replace clinical training and supervision."),
        interpretation=t("desc_burn", "Parkland Burn Formula"),
        latex_formula=r"\text{Total} = 4 \times W \times TBSA",
        conclusion=conclusion,
        metadata={
            "first_8h_volume_ml": round(first_8h_volume, 2),
            "first_8h_rate_ml_h": round(first_8h_rate, 2),
            "next_16h_volume_ml": round(next_16h_volume, 2),
            "next_16h_rate_ml_h": round(next_16h_rate, 2),
        },
        total_24h_ml=total_fluid,
        first_8h_rate_ml_h=first_8h_rate,
        next_16h_rate_ml_h=next_16h_rate,
    )
