"""Electrolyte and acid-base formulas."""

from medpulse.core.models import CalculationResult
from medpulse.core.validators import coerce_float, ensure_between, ensure_positive
from medpulse.i18n import t

def _round(value):
    return round(float(value), 2)

def anion_gap(na, cl, hco3, albumin=None):
    sodium = ensure_between(coerce_float(na, "na"), "na", 80.0, 200.0)
    chloride = ensure_between(coerce_float(cl, "cl"), "cl", 40.0, 160.0)
    bicarbonate = ensure_between(coerce_float(hco3, "hco3"), "hco3", 1.0, 60.0)
    value = sodium - (chloride + bicarbonate)
    warnings = []
    metadata = {}
    
    if value > 16:
        interpretation = t('ag_high', "Elevated")
    elif value < 8:
        interpretation = t('ag_low', "Low")
    else:
        interpretation = t('ag_normal', "Within reference range")
        
    substitution = "%.1f - (%.1f + %.1f) = %.2f" % (sodium, chloride, bicarbonate, value)
    if albumin not in (None, ""):
        albumin_value = ensure_between(coerce_float(albumin, "albumin"), "albumin", 0.5, 6.0)
        corrected = value + 2.5 * (4.0 - albumin_value)
        metadata["albumin_g_dl"] = albumin_value
        metadata["corrected_for_albumin"] = _round(corrected)
        warnings.append(t('ag_warn_albumin', "Albumin-corrected AG provided for reference. Clinical correlation required."))
    return CalculationResult(
        key="anion_gap",
        label=t('calculator_anion_gap', "Anion Gap"),
        formula=t("ag_formula", "AG = Na - (Cl + HCO\u2083)"),
        substitution=substitution,
        value=_round(value),
        unit="mmol/L",
        reference=t('ag_ref', "Reference range approx 8-16 mmol/L; Delta Gap uses normal AG of 12 mmol/L."),
        interpretation=interpretation,
        latex_formula=r"AG = Na^+ - (Cl^- + HCO_3^-)",
        warnings=warnings,
        metadata=metadata,
    )

def delta_gap(ag_value, hco3):
    ag = ensure_between(coerce_float(ag_value, "ag_value"), "ag_value", -20.0, 60.0)
    bicarbonate = ensure_between(coerce_float(hco3, "hco3"), "hco3", 1.0, 60.0)
    denominator = 24.0 - bicarbonate
    warnings = []
    if denominator == 0:
        value = 0.0
        warnings.append(t('dg_warn_zero', "HCO3 is exactly 24 mmol/L. Delta Gap denominator is 0. Returning 0."))
        interpretation = t('dg_interp_zero', "Denominator is 0, cannot calculate ratio.")
    else:
        value = (ag - 12.0) / denominator
        if value > 2.0:
            interpretation = t('dg_interp_gt2', "Delta Ratio > 2: High AG metabolic acidosis + concurrent metabolic alkalosis.")
        elif value >= 1.0:
            interpretation = t('dg_interp_1_2', "Delta Ratio 1-2: Pure high AG metabolic acidosis.")
        elif value >= 0.4:
            interpretation = t('dg_interp_04_1', "Delta Ratio 0.4-1: Mixed high AG and hyperchloremic metabolic acidosis.")
        else:
            interpretation = t('dg_interp_lt04', "Delta Ratio < 0.4: Predominantly hyperchloremic (non-AG) metabolic acidosis.")
    return CalculationResult(
        key="delta_gap",
        label=t('calculator_delta_gap', "Delta Gap"),
        formula=t("delta_ratio_formula", "(AG - 12) / (24 - HCO\u2083)"),
        substitution="(%.1f - 12) / (24 - %.1f) = %.2f" % (ag, bicarbonate, value),
        value=_round(value),
        unit="ratio",
        reference=t('dg_ref', "Structured assessment for mixed acid-base disorders. Interpret with clinical context."),
        interpretation=interpretation,
        latex_formula=r"\Delta Ratio = \frac{AG - 12}{24 - HCO_3^-}",
        warnings=warnings,
    )

def winter_expected_pco2(hco3, actual_pco2=None, boundary_tolerance=0.1):
    bicarbonate = ensure_between(coerce_float(hco3, "hco3"), "hco3", 1.0, 60.0)
    expected = 1.5 * bicarbonate + 8.0
    low = expected - 2.0
    high = expected + 2.0
    warnings = []
    interpretation = t('winter_interp_base', "Correlate with actual PCO2 to assess compensation.")
    metadata = {"expected_low": _round(low), "expected_high": _round(high)}
    substitution = t('winter_subst_format', "1.5 x %.1f + 8 = %.2f, %s %.2f-%.2f") % (
        bicarbonate,
        expected,
        t('winter_allow_range', 'Allowed range'),
        low,
        high,
    )
    if actual_pco2 not in (None, ""):
        pco2 = ensure_between(coerce_float(actual_pco2, "pco2"), "pco2", 10.0, 120.0)
        metadata["actual_pco2"] = _round(pco2)
        boundary_distance = min(abs(pco2 - low), abs(pco2 - high))
        metadata["boundary_distance"] = _round(boundary_distance)
        if boundary_distance <= boundary_tolerance:
            warn_tmpl = t('winter_warn_boundary', "Compensation judgment is close to the boundary (<= %.1f mmHg). Interpret with caution.")
            warnings.append(warn_tmpl % boundary_tolerance)
        if pco2 < low:
            interpretation = t('winter_interp_low', "Actual PCO2 is lower than expected. Possible concurrent respiratory alkalosis.")
        elif pco2 > high:
            interpretation = t('winter_interp_high', "Actual PCO2 is higher than expected. Possible concurrent respiratory acidosis.")
        else:
            interpretation = t('winter_interp_match', "Compensation matches Winter's formula.")
    return CalculationResult(
        key="winter_formula",
        label=t('calculator_winter_formula', "Winter's Formula"),
        formula="PCO\u2082 = 1.5 x HCO\u2083 + 8 +/- 2",
        substitution=substitution,
        value=_round(expected),
        unit="mmHg",
        reference=t('winter_ref', "Respiratory compensation check for metabolic acidosis."),
        interpretation=interpretation,
        latex_formula=r"PCO_2 = 1.5 \times HCO_3^- + 8 \pm 2",
        warnings=warnings,
        metadata=metadata,
    )

def sodium_correction_rate(start_na, end_na, hours_elapsed, max_rate_per_hour=0.5, max_delta_24h=8.0):
    initial = ensure_between(coerce_float(start_na, "start_na"), "start_na", 80.0, 200.0)
    final = ensure_between(coerce_float(end_na, "end_na"), "end_na", 80.0, 200.0)
    hours = ensure_between(coerce_float(hours_elapsed, "hours_elapsed"), "hours_elapsed", 0.1, 240.0)
    ensure_positive(hours, "hours_elapsed")
    delta = final - initial
    rate = delta / hours
    warnings = []
    if abs(rate) > max_rate_per_hour:
        warn_tmpl = t('na_warn_rate', "Correction rate exceeds %.2f mmol/L/h. Risk of rapid correction.")
        warnings.append(warn_tmpl % max_rate_per_hour)
    if hours <= 24.0 and abs(delta) > max_delta_24h:
        warn_tmpl2 = t('na_warn_total', "Total 24h change exceeds %.1f mmol/L.")
        warnings.append(warn_tmpl2 % max_delta_24h)
        
    if rate > 0:
        interpretation = t('na_up', "Increase")
    elif rate < 0:
        interpretation = t('na_down', "Decrease")
    else:
        interpretation = t('na_none', "No change")
        
    ref_tmpl = t('na_ref', "Alert limit: <= %.2f mmol/L/h; 24h change <= %.1f mmol/L.")
    
    return CalculationResult(
        key="sodium_correction_rate",
        label=t('calculator_sodium_correction', "Sodium Correction Rate"),
        formula=t("delta_na_formula", "Delta-Na / h"),
        substitution="(%.1f - %.1f) / %.1f = %.2f" % (final, initial, hours, rate),
        value=_round(rate),
        unit="mmol/L/h",
        reference=ref_tmpl % (max_rate_per_hour, max_delta_24h),
        interpretation=interpretation,
        latex_formula=r"\Delta Na^+ / h",
        warnings=warnings,
        metadata={"delta_na": _round(delta)},
    )

def plasma_osmolarity(na, glucose_mg_dl, bun_mg_dl):
    sodium = ensure_between(coerce_float(na, "na"), "na", 80.0, 200.0)
    glucose = ensure_between(coerce_float(glucose_mg_dl, "glucose_mg_dl"), "glucose_mg_dl", 0.0, 2000.0)
    bun = ensure_between(coerce_float(bun_mg_dl, "bun_mg_dl"), "bun_mg_dl", 0.0, 300.0)
    value = 2.0 * sodium + glucose / 18.0 + bun / 2.8
    warnings = []
    if value > 320.0:
        warn_tmpl = t('osm_warn_high', "Estimated osmolarity %.1f mOsm/L exceeds threshold (>320). Compare with measured osmolarity and gap.")
        warnings.append(warn_tmpl % value)
    return CalculationResult(
        key="plasma_osmolarity",
        label=t('calculator_plasma_osmolarity', "Plasma Osmolarity"),
        formula=t("osmol_formula", "2 x Na + Glu/18 + BUN/2.8"),
        substitution="2 x %.1f + %.1f/18 + %.1f/2.8 = %.2f" % (sodium, glucose, bun, value),
        value=_round(value),
        unit="mOsm/L",
        reference=t('osm_ref', "Estimate only. Correlate with measured osmolarity."),
        interpretation=t('osm_interp', "Estimated value"),
        latex_formula=r"2 \times Na^+ + \frac{Glu}{18} + \frac{BUN}{2.8}",
        warnings=warnings,
    )
