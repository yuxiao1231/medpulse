"""Infusion and pump-rate conversion helpers."""

from decimal import Decimal, ROUND_HALF_UP

from medpulse.core.models import CalculationResult
from medpulse.core.resources import load_json
from medpulse.core.units import concentration_from_amount, concentration_to_mcg_per_ml
from medpulse.core.validators import (
    coerce_decimal,
    ensure_decimal_between,
    ensure_decimal_positive,
)
from medpulse.i18n import t


TWO_DECIMALS = Decimal("0.01")


def _round_to_float(value):
    return float(value.quantize(TWO_DECIMALS, rounding=ROUND_HALF_UP))


def _decimal_text(value):
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _rate_inputs(
    dose_mcg_per_kg_min,
    weight_kg,
    concentration_mcg_per_ml,
    concentration_unit="mcg/mL",
):
    dose = ensure_decimal_between(
        coerce_decimal(dose_mcg_per_kg_min, "dose_mcg_per_kg_min"),
        "dose_mcg_per_kg_min",
        "0",
        "500",
    )
    weight = ensure_decimal_between(coerce_decimal(weight_kg, "weight_kg"), "weight_kg", "0.5", "400")
    concentration = concentration_to_mcg_per_ml(concentration_mcg_per_ml, concentration_unit)
    ensure_decimal_positive(weight, "weight_kg")
    ensure_decimal_positive(concentration, "concentration_mcg_per_ml")
    return dose, weight, concentration


def _dose_inputs(
    rate_ml_per_hour,
    weight_kg,
    concentration_mcg_per_ml,
    concentration_unit="mcg/mL",
):
    rate = ensure_decimal_between(coerce_decimal(rate_ml_per_hour, "rate_ml_per_hour"), "rate_ml_per_hour", "0", "1000")
    weight = ensure_decimal_between(coerce_decimal(weight_kg, "weight_kg"), "weight_kg", "0.5", "400")
    concentration = concentration_to_mcg_per_ml(concentration_mcg_per_ml, concentration_unit)
    ensure_decimal_positive(weight, "weight_kg")
    ensure_decimal_positive(concentration, "concentration_mcg_per_ml")
    return rate, weight, concentration


def mcg_per_kg_min_to_ml_per_hour(
    dose_mcg_per_kg_min,
    weight_kg,
    concentration_mcg_per_ml,
    concentration_unit="mcg/mL",
):
    dose, weight, concentration = _rate_inputs(
        dose_mcg_per_kg_min,
        weight_kg,
        concentration_mcg_per_ml,
        concentration_unit,
    )
    return _round_to_float((dose * weight * Decimal("60")) / concentration)


def ml_per_hour_to_mcg_per_kg_min(
    rate_ml_per_hour,
    weight_kg,
    concentration_mcg_per_ml,
    concentration_unit="mcg/mL",
):
    rate, weight, concentration = _dose_inputs(
        rate_ml_per_hour,
        weight_kg,
        concentration_mcg_per_ml,
        concentration_unit,
    )
    return _round_to_float((rate * concentration) / (weight * Decimal("60")))


def infusion_rate_result(
    dose_mcg_per_kg_min,
    weight_kg,
    concentration_mcg_per_ml,
    concentration_unit="mcg/mL",
):
    dose, weight, concentration = _rate_inputs(
        dose_mcg_per_kg_min,
        weight_kg,
        concentration_mcg_per_ml,
        concentration_unit,
    )
    value = (dose * weight * Decimal("60")) / concentration
    rate = _round_to_float(value)
    conclusion = "%.2f mL/h" % rate
    return CalculationResult(
        key="infusion_rate",
        label=t("pump_rate_calc", "Pump Rate Conversion"),
        formula=t("infusion_rate_formula", "mL/h = dose (mcg/kg/min) x weight (kg) x 60 / concentration (mcg/mL)"),
        substitution="%s x %s x 60 / %s = %.2f mL/h"
        % (_decimal_text(dose), _decimal_text(weight), _decimal_text(concentration), rate),
        value=rate,
        unit="mL/h",
        reference=t("checklist_note", "For reference only. Confirm concentration, units, pump settings, and local protocol."),
        interpretation=t("pump_rate_calc", "Calculated infusion pump rate."),
        conclusion=conclusion,
        metadata={"concentration_mcg_ml": _decimal_text(concentration)},
    )


def infusion_dose_result(
    rate_ml_per_hour,
    weight_kg,
    concentration_mcg_per_ml,
    concentration_unit="mcg/mL",
):
    rate, weight, concentration = _dose_inputs(
        rate_ml_per_hour,
        weight_kg,
        concentration_mcg_per_ml,
        concentration_unit,
    )
    value = (rate * concentration) / (weight * Decimal("60"))
    dose = _round_to_float(value)
    conclusion = "%.2f mcg/kg/min" % dose
    return CalculationResult(
        key="infusion_dose",
        label=t("dose_calc", "Dose Conversion"),
        formula=t("infusion_dose_formula", "Dose (mcg/kg/min) = rate (mL/h) x concentration (mcg/mL) / weight (kg) / 60"),
        substitution="%s x %s / %s / 60 = %.2f mcg/kg/min"
        % (_decimal_text(rate), _decimal_text(concentration), _decimal_text(weight), dose),
        value=dose,
        unit="mcg/kg/min",
        reference=t("checklist_note", "For reference only. Confirm concentration, units, pump settings, and local protocol."),
        interpretation=t("dose_calc", "Calculated delivered dose."),
        conclusion=conclusion,
        metadata={"concentration_mcg_ml": _decimal_text(concentration)},
    )


def infusion_rate_from_amount(dose_mcg_per_kg_min, weight_kg, drug_mg, volume_ml):
    concentration = concentration_from_amount(drug_mg, "mg", volume_ml)
    result = infusion_rate_result(dose_mcg_per_kg_min, weight_kg, concentration, "mcg/mL")
    drug = coerce_decimal(drug_mg, "drug_mg")
    volume = coerce_decimal(volume_ml, "volume_ml")
    result.formula = (
        "Concentration = total drug (mg) x 1000 / volume (mL); "
        "mL/h = dose (mcg/kg/min) x weight (kg) x 60 / concentration (mcg/mL)"
    )
    result.substitution = "C = %s x 1000 / %s = %s mcg/mL; %s" % (
        _decimal_text(drug),
        _decimal_text(volume),
        _decimal_text(concentration),
        result.substitution,
    )
    return result


def infusion_dose_from_amount(rate_ml_per_hour, weight_kg, drug_mg, volume_ml):
    concentration = concentration_from_amount(drug_mg, "mg", volume_ml)
    result = infusion_dose_result(rate_ml_per_hour, weight_kg, concentration, "mcg/mL")
    drug = coerce_decimal(drug_mg, "drug_mg")
    volume = coerce_decimal(volume_ml, "volume_ml")
    result.formula = (
        "Concentration = total drug (mg) x 1000 / volume (mL); "
        "Dose (mcg/kg/min) = rate (mL/h) x concentration (mcg/mL) / weight (kg) / 60"
    )
    result.substitution = "C = %s x 1000 / %s = %s mcg/mL; %s" % (
        _decimal_text(drug),
        _decimal_text(volume),
        _decimal_text(concentration),
        result.substitution,
    )
    return result


def load_infusion_templates():
    return load_json("drugs", "infusion_templates.json")


def get_supported_infusion_templates():
    data = load_infusion_templates()
    return [item for item in data.get("templates", []) if item.get("mode") == "mcg_per_kg_min"]
