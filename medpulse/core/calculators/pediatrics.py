"""Pediatric deterministic formulas."""

import math

from medpulse.core.models import CalculationResult
from medpulse.core.validators import coerce_float, ensure_between, ensure_positive
from medpulse.i18n import t

def mosteller_bsa(weight_kg, height_cm):
    weight = ensure_between(coerce_float(weight_kg, "weight_kg"), "weight_kg", 0.5, 300.0)
    height = ensure_between(coerce_float(height_cm, "height_cm"), "height_cm", 20.0, 250.0)
    ensure_positive(weight, "weight_kg")
    ensure_positive(height, "height_cm")
    value = math.sqrt((weight * height) / 3600.0)
    return CalculationResult(
        key="mosteller_bsa",
        label=t('calculator_mosteller_bsa', "Mosteller BSA"),
        formula=t('bsa_formula', "BSA = sqrt(Height(cm) x Weight(kg) / 3600)"),
        substitution="sqrt(%.1f x %.1f / 3600) = %.2f" % (height, weight, value),
        value=round(value, 2),
        unit="m2",
        reference=t('bsa_ref', "Mosteller Body Surface Area formula."),
        interpretation=t('bsa_interp', "Estimate"),
    )

def maintenance_fluid_421(weight_kg):
    weight = ensure_between(coerce_float(weight_kg, "weight_kg"), "weight_kg", 0.5, 200.0)
    ensure_positive(weight, "weight_kg")
    remaining = weight
    total = 0.0
    segments = []
    first = min(remaining, 10.0)
    total += first * 4.0
    segments.append("4x%.1f" % first)
    remaining -= first
    if remaining > 0:
        second = min(remaining, 10.0)
        total += second * 2.0
        segments.append("2x%.1f" % second)
        remaining -= second
    if remaining > 0:
        total += remaining * 1.0
        segments.append("1x%.1f" % remaining)
    warnings = []
    if total > 100.0:
        warn_tmpl = t('fluid_warn_high', "Calculated rate %.0f mL/h exceeds usual maintenance limits (<=100-120). Not for routine adult use.")
        warnings.append(warn_tmpl % total)
    elif weight > 40.0:
        warn_tmpl = t('fluid_warn_weight', "Weight %.1f kg exceeds typical pediatric range (>40 kg). Use with caution.")
        warnings.append(warn_tmpl % weight)
    return CalculationResult(
        key="maintenance_fluid_421",
        label=t('calculator_fluid_421', "4-2-1 Maintenance Fluid"),
        formula=t('fluid_formula', "First 10kg x4 + Next 10kg x2 + Rest x1"),
        substitution=" + ".join(segments) + " = %.2f" % total,
        value=round(total, 2),
        unit="mL/h",
        reference=t('fluid_ref', "Pediatric 4-2-1 maintenance fluid rule."),
        interpretation=t('fluid_interp', "Maintenance fluid estimate"),
        warnings=warnings,
    )
