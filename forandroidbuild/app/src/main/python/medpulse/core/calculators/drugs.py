"""Calculators for common drug preparations and dosings."""

from medpulse.core.exceptions import ValidationError
from medpulse.core.models import CalculationResult
from medpulse.i18n import t


def _coerce_float(value, error_key, default_message):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValidationError(t(error_key, default_message))


def _reference_note():
    return t("checklist_note", "For reference only. Does not replace clinical training and supervision.")


def dilute_powder(amount_mg, volume_ml):
    """Calculate final concentration after powder dilution."""
    amount = _coerce_float(amount_mg, "err_amount_volume_num", "Amount and volume must be valid numbers.")
    volume = _coerce_float(volume_ml, "err_amount_volume_num", "Amount and volume must be valid numbers.")

    if volume <= 0:
        raise ValidationError(t("err_volume_gt_zero", "Volume must be greater than zero."))

    concentration = amount / volume
    conclusion_tmpl = t("dilute_desc", "%.0f mg in %s mL gives %.2f mg/mL")
    conclusion = conclusion_tmpl % (amount, volume, concentration)

    return CalculationResult(
        key="dilute_powder",
        label=t("dilution_calc", "Dilution"),
        formula=t("dilute_formula", "Concentration = drug amount (mg) / diluent volume (mL)"),
        substitution=t("dilute_subst", "%.2f mg / %.2f mL = %.2f mg/mL") % (amount, volume, concentration),
        value=round(concentration, 2),
        unit="mg/mL",
        reference=_reference_note(),
        interpretation=t("dilution_calc", "Dilution"),
        latex_formula=r"C = \frac{m}{V}",
        conclusion=conclusion,
    )


def antibiotic_dose(weight_kg, dose_mg_per_kg):
    """Calculate a weight-based single antibiotic dose."""
    weight = _coerce_float(weight_kg, "err_weight_dose_num", "Weight and dose must be valid numbers.")
    dose = _coerce_float(dose_mg_per_kg, "err_weight_dose_num", "Weight and dose must be valid numbers.")

    if weight <= 0 or dose <= 0:
        raise ValidationError(t("err_weight_dose_gt_zero", "Weight and dose must be greater than zero."))

    total_dose = weight * dose
    conclusion_tmpl = t("antibiotic_desc", "Weight %s kg @ %s mg/kg = %.2f mg per dose")
    conclusion = conclusion_tmpl % (weight, dose, total_dose)

    return CalculationResult(
        key="antibiotic_dose",
        label=t("antibiotic_calc", "Antibiotic Dose"),
        formula=t("anti_dose_formula", "Single dose = weight (kg) x prescribed dose (mg/kg)"),
        substitution=t("anti_dose_subst", "%.2f kg x %.2f mg/kg = %.2f mg") % (weight, dose, total_dose),
        value=round(total_dose, 2),
        unit="mg",
        reference=_reference_note(),
        interpretation=t("desc_antibiotic", "Weight-based Antibiotic Dose"),
        latex_formula=r"\text{Dose} = W \times D",
        conclusion=conclusion,
    )


def insulin_tdd(weight_kg):
    """Estimate insulin total daily dose from weight using the existing 0.5 U/kg rule."""
    weight = _coerce_float(weight_kg, "err_weight_num", "Weight must be a valid number.")

    if weight <= 0:
        raise ValidationError(t("err_weight_gt_zero", "Weight must be greater than zero."))

    tdd = weight * 0.5
    basal = tdd * 0.5
    bolus = tdd * 0.5
    conclusion_tmpl = t(
        "insulin_desc",
        "Weight %s kg -> Estimated TDD %.1f U (Basal %.1f U, Bolus %.1f U)",
    )
    conclusion = conclusion_tmpl % (weight, tdd, basal, bolus)

    return CalculationResult(
        key="insulin_tdd",
        label=t("insulin_calc", "Insulin TDD"),
        formula=t("insulin_tdd_formula", "TDD = weight (kg) x 0.5 U/kg; basal = TDD x 50%; bolus = TDD x 50%"),
        substitution=t("insulin_tdd_subst", "%.2f kg x 0.5 U/kg = %.2f U; %.2f U x 50%% = %.2f U basal; %.2f U x 50%% = %.2f U bolus") % (weight, tdd, tdd, basal, tdd, bolus),
        value=round(tdd, 2),
        unit="U/day",
        reference=_reference_note(),
        interpretation=t("desc_insulin", "Insulin Total Daily Dose (TDD)"),
        latex_formula=r"\text{TDD} = W \times 0.5",
        conclusion=conclusion,
        metadata={"basal_units": round(basal, 2), "bolus_units": round(bolus, 2)},
    )


def calculate_dilution(drug_mg=None, volume_ml=None, amount_mg=None):
    """Backward-compatible Android wrapper for older Kotlin callers."""
    amount = amount_mg if amount_mg is not None else drug_mg
    return dilute_powder(amount, volume_ml)


def calculate_antibiotic_dose(weight_kg, dose_mg_per_kg):
    """Backward-compatible Android wrapper for older Kotlin callers."""
    return antibiotic_dose(weight_kg, dose_mg_per_kg)


def calculate_insulin_tdd(weight_kg):
    """Backward-compatible Android wrapper for older Kotlin callers."""
    return insulin_tdd(weight_kg)

def glucose_insulin(concentration_pct, volume_ml, ratio_g_per_u=4.0):
    """
    Calculate insulin dose for glucose neutralization.
    Returns: CalculationResult
    """
    c = _coerce_float(concentration_pct, "err_conc_invalid", "Concentration must be a valid non-negative number.")
    v = _coerce_float(volume_ml, "err_vol_invalid", "Volume must be a valid non-negative number.")
    r = _coerce_float(ratio_g_per_u, "err_ratio_invalid", "Ratio must be a valid positive number.")

    if c < 0:
        raise ValidationError(t("err_conc_invalid", "Concentration must be a valid non-negative number."))
    if v < 0:
        raise ValidationError(t("err_vol_invalid", "Volume must be a valid non-negative number."))
    if r <= 0:
        raise ValidationError(t("err_ratio_invalid", "Ratio must be a valid positive number."))

    glucose_g = v * c / 100.0
    insulin_u = glucose_g / r

    conclusion = t("fmt_glucose_insulin_conclusion", "Glucose: %.2f g -> Insulin: %.2f U") % (glucose_g, insulin_u)

    return CalculationResult(
        key="glucose_insulin",
        label=t("glucose_insulin_calc", "Glucose-Insulin Neutralization"),
        formula=t("glucose_insulin_formula", "Glucose (g) = Vol \u00d7 Conc%; Insulin (U) = Glucose / Ratio"),
        substitution=t("glucose_insulin_subst", "%.2f mL \u00d7 %.2f%% = %.2f g; %.2f g / %.2f g/U = %.2f U") % (v, c, glucose_g, glucose_g, r, insulin_u),
        value=round(insulin_u, 2),
        unit="U",
        reference=_reference_note(),
        interpretation=t("desc_glucose_insulin", "Insulin dose to neutralize IV glucose"),
        latex_formula=r"\text{Insulin (U)} = \frac{\text{Vol} \times \text{Conc\%}}{100 \times \text{Ratio}}",
        conclusion=conclusion,
        metadata={"glucose_g": round(glucose_g, 2), "ratio": r},
    )

def calculate_glucose_insulin(concentration_pct, volume_ml, ratio_g_per_u=4.0):
    """Android wrapper."""
    return glucose_insulin(concentration_pct, volume_ml, ratio_g_per_u)
