"""Structured arterial blood gas interpretation helpers."""

from medpulse.core.calculators.electrolytes import winter_expected_pco2
from medpulse.core.models import ABGAnalysis
from medpulse.core.validators import coerce_float, ensure_between
from medpulse.i18n import t

ABG_BOUNDARY_TOLERANCE = 0.1

def _boundary_warnings(measured_label, measured_value, unit, ranges, tolerance=ABG_BOUNDARY_TOLERANCE):
    warnings = []
    seen = set()
    for _, low, high in ranges:
        for boundary in (low, high):
            marker = round(boundary, 4)
            if marker in seen:
                continue
            if abs(measured_value - boundary) <= tolerance:
                warning_tmpl = t('abg_boundary_warning', "Near formula boundary (%s = %.2f, boundary = %.2f %s). Rounding or sampling error may alter classification; correlate with clinical history.")
                warnings.append(warning_tmpl % (measured_label, measured_value, boundary, unit))
                seen.add(marker)
    return warnings


def _classification_formula():
    return t('abg_class_formula', "pH < 7.35 -> acidosis; pH > 7.45 -> alkalosis; HCO\u2083 < 22 -> metabolic acidosis; HCO\u2083 > 26 -> metabolic alkalosis; PCO\u2082 > 45 -> respiratory acidosis; PCO\u2082 < 35 -> respiratory alkalosis")


def _classification_substitution(ph, pco2, hco3, status, primary):
    return t('abg_class_subst', "pH %.2f -> %s; PCO\u2082 %.1f mmHg and HCO\u2083 %.1f mmol/L -> %s") % (
        ph,
        status,
        pco2,
        hco3,
        primary,
    )


def _respiratory_acidosis_details(pco2):
    delta = (pco2 - 40.0) / 10.0
    acute_low = 24.0 + delta * 1.0
    acute_high = 24.0 + delta * 2.0
    chronic_low = 24.0 + delta * 3.0
    chronic_high = 24.0 + delta * 4.0
    formula = t('abg_resp_acid_formula', "Respiratory acidosis compensation: acute HCO\u2083 = 24 + ((PCO\u2082 - 40) / 10) x 1 to 2; chronic HCO\u2083 = 24 + ((PCO\u2082 - 40) / 10) x 3 to 4")
    substitution = t('abg_resp_acid_subst', "(%.1f - 40) / 10 = %.2f; acute range %.2f-%.2f mmol/L; chronic range %.2f-%.2f mmol/L") % (pco2, delta, acute_low, acute_high, chronic_low, chronic_high)
    return formula, substitution


def _respiratory_alkalosis_details(pco2):
    delta = (40.0 - pco2) / 10.0
    acute_low = 24.0 - delta * 2.0
    acute_high = 24.0 - delta * 1.0
    chronic_low = 24.0 - delta * 5.0
    chronic_high = 24.0 - delta * 4.0
    formula = t('abg_resp_alk_formula', "Respiratory alkalosis compensation: acute HCO\u2083 = 24 - ((40 - PCO\u2082) / 10) x 1 to 2; chronic HCO\u2083 = 24 - ((40 - PCO\u2082) / 10) x 4 to 5")
    substitution = t('abg_resp_alk_subst', "(40 - %.1f) / 10 = %.2f; acute range %.2f-%.2f mmol/L; chronic range %.2f-%.2f mmol/L") % (pco2, delta, acute_low, acute_high, chronic_low, chronic_high)
    return formula, substitution


def _metabolic_alkalosis_details(pco2, hco3):
    expected = 40.0 + 0.7 * (hco3 - 24.0)
    low = expected - 5.0
    high = expected + 5.0
    formula = t('abg_met_alk_formula', "Metabolic alkalosis compensation: expected PCO\u2082 = 40 + 0.7 x (HCO\u2083 - 24) +/- 5")
    substitution = t('abg_met_alk_subst', "40 + 0.7 x (%.1f - 24) = %.2f; expected range %.2f-%.2f mmHg; actual PCO\u2082 %.1f") % (
        hco3,
        expected,
        low,
        high,
        pco2,
    )
    return formula, substitution


def _winter_substitution(winter):
    substitution = winter.substitution
    actual = winter.metadata.get("actual_pco2")
    if actual is not None:
        substitution = t('abg_winter_actual_pco2', "%s; actual PCO\u2082 = %.2f mmHg") % (substitution, actual)
    return substitution


def _respiratory_acidosis_assessment(pco2, hco3):
    delta = pco2 - 40.0
    acute_low = 24.0 + (delta / 10.0) * 1.0
    acute_high = 24.0 + (delta / 10.0) * 2.0
    chronic_low = 24.0 + (delta / 10.0) * 3.0
    chronic_high = 24.0 + (delta / 10.0) * 4.0
    ranges = [
        ("acute", acute_low, acute_high),
        ("chronic", chronic_low, chronic_high),
    ]
    warnings = _boundary_warnings("HCO\u2083", hco3, "mmol/L", ranges)
    if acute_low <= hco3 <= acute_high:
        return t('abg_resp_acidosis_acute', "HCO3 consistent with acute respiratory acidosis compensation."), warnings
    if chronic_low <= hco3 <= chronic_high:
        return t('abg_resp_acidosis_chronic', "HCO3 consistent with chronic respiratory acidosis compensation."), warnings
    return t('abg_resp_acidosis_mismatch', "HCO3 does not fully match simple respiratory acidosis compensation. Consider mixed disorder."), warnings

def _respiratory_alkalosis_assessment(pco2, hco3):
    delta = 40.0 - pco2
    acute_low = 24.0 - (delta / 10.0) * 2.0
    acute_high = 24.0 - (delta / 10.0) * 1.0
    chronic_low = 24.0 - (delta / 10.0) * 5.0
    chronic_high = 24.0 - (delta / 10.0) * 4.0
    ranges = [
        ("acute", acute_low, acute_high),
        ("chronic", chronic_low, chronic_high),
    ]
    warnings = _boundary_warnings("HCO\u2083", hco3, "mmol/L", ranges)
    if acute_low <= hco3 <= acute_high:
        return t('abg_resp_alkalosis_acute', "HCO3 consistent with acute respiratory alkalosis compensation."), warnings
    if chronic_low <= hco3 <= chronic_high:
        return t('abg_resp_alkalosis_chronic', "HCO3 consistent with chronic respiratory alkalosis compensation."), warnings
    return t('abg_resp_alkalosis_mismatch', "HCO3 does not fully match simple respiratory alkalosis compensation. Consider mixed disorder."), warnings

def _metabolic_alkalosis_assessment(pco2, hco3):
    expected = 40.0 + 0.7 * (hco3 - 24.0)
    low = expected - 5.0
    high = expected + 5.0
    warnings = _boundary_warnings("PCO\u2082", pco2, "mmHg", [("expected", low, high)])
    if low <= pco2 <= high:
        return t('abg_met_alkalosis_match', "Respiratory compensation consistent with metabolic alkalosis."), warnings
    return t('abg_met_alkalosis_mismatch', "PCO2 does not fully match simple metabolic alkalosis compensation. Consider mixed disorder."), warnings

def analyze_abg(ph, pco2, hco3):
    measured_ph = ensure_between(coerce_float(ph, "ph"), "ph", 6.8, 7.8)
    measured_pco2 = ensure_between(coerce_float(pco2, "pco2"), "pco2", 10.0, 120.0)
    measured_hco3 = ensure_between(coerce_float(hco3, "hco3"), "hco3", 1.0, 60.0)

    steps = []
    warnings = []
    metadata = {}
    formula_parts = [_classification_formula()]
    substitution_parts = []

    if measured_ph < 7.35:
        acid_base_status = t('abg_status_acidosis', "Acidosis")
    elif measured_ph > 7.45:
        acid_base_status = t('abg_status_alkalosis', "Alkalosis")
    else:
        acid_base_status = t('abg_status_normal', "pH near normal")
    steps.append(t('abg_step1', "Step 1. pH = %.2f, suggests %s.") % (measured_ph, acid_base_status))

    metabolic_acid = measured_hco3 < 22.0
    metabolic_alkalosis = measured_hco3 > 26.0
    respiratory_acid = measured_pco2 > 45.0
    respiratory_alkalosis = measured_pco2 < 35.0

    primary = t('abg_primary_undetermined', "Undetermined")
    compensation = t('abg_comp_more_info', "More information needed to assess compensation.")

    if acid_base_status == t('abg_status_acidosis', "Acidosis"):
        if metabolic_acid and respiratory_acid:
            primary = t('abg_primary_mixed_acidosis', "Mixed acidosis (metabolic + respiratory)")
            compensation = t('abg_comp_mixed_acidosis', "Both PCO2 and HCO3 support acidosis. Consider mixed disorder.")
        elif metabolic_acid:
            primary = t('abg_primary_met_acidosis', "Metabolic acidosis")
            winter = winter_expected_pco2(measured_hco3, measured_pco2)
            compensation = winter.interpretation
            warnings.extend(winter.warnings)
            metadata["winter"] = winter.metadata
            formula_parts.append(winter.formula)
            substitution_parts.append(_winter_substitution(winter))
        elif respiratory_acid:
            primary = t('abg_primary_resp_acidosis', "Respiratory acidosis")
            compensation, compensation_warnings = _respiratory_acidosis_assessment(measured_pco2, measured_hco3)
            warnings.extend(compensation_warnings)
            formula, substitution = _respiratory_acidosis_details(measured_pco2)
            formula_parts.append(formula)
            substitution_parts.append(substitution)
    elif acid_base_status == t('abg_status_alkalosis', "Alkalosis"):
        if metabolic_alkalosis and respiratory_alkalosis:
            primary = t('abg_primary_mixed_alkalosis', "Mixed alkalosis (metabolic + respiratory)")
            compensation = t('abg_comp_mixed_alkalosis', "Both PCO2 and HCO3 support alkalosis. Consider mixed disorder.")
        elif metabolic_alkalosis:
            primary = t('abg_primary_met_alkalosis', "Metabolic alkalosis")
            compensation, compensation_warnings = _metabolic_alkalosis_assessment(measured_pco2, measured_hco3)
            warnings.extend(compensation_warnings)
            formula, substitution = _metabolic_alkalosis_details(measured_pco2, measured_hco3)
            formula_parts.append(formula)
            substitution_parts.append(substitution)
        elif respiratory_alkalosis:
            primary = t('abg_primary_resp_alkalosis', "Respiratory alkalosis")
            compensation, compensation_warnings = _respiratory_alkalosis_assessment(measured_pco2, measured_hco3)
            warnings.extend(compensation_warnings)
            formula, substitution = _respiratory_alkalosis_details(measured_pco2)
            formula_parts.append(formula)
            substitution_parts.append(substitution)
    else:
        if metabolic_acid and respiratory_alkalosis:
            primary = t('abg_primary_normal_mixed1', "pH near normal, but metabolic acidosis / respiratory alkalosis pattern present")
            compensation = t('abg_comp_normal_mixed', "May be compensated to near-normal, or may be a mixed disorder.")
        elif metabolic_alkalosis and respiratory_acid:
            primary = t('abg_primary_normal_mixed2', "pH near normal, but metabolic alkalosis / respiratory acidosis pattern present")
            compensation = t('abg_comp_normal_mixed', "May be compensated to near-normal, or may be a mixed disorder.")
        elif metabolic_acid:
            primary = t('abg_primary_trend_met_acidosis', "Metabolic acidosis tendency")
            winter = winter_expected_pco2(measured_hco3, measured_pco2)
            compensation = winter.interpretation
            warnings.extend(winter.warnings)
            metadata["winter"] = winter.metadata
            formula_parts.append(winter.formula)
            substitution_parts.append(_winter_substitution(winter))
        elif metabolic_alkalosis:
            primary = t('abg_primary_trend_met_alkalosis', "Metabolic alkalosis tendency")
            compensation, compensation_warnings = _metabolic_alkalosis_assessment(measured_pco2, measured_hco3)
            warnings.extend(compensation_warnings)
            formula, substitution = _metabolic_alkalosis_details(measured_pco2, measured_hco3)
            formula_parts.append(formula)
            substitution_parts.append(substitution)
        elif respiratory_acid:
            primary = t('abg_primary_trend_resp_acidosis', "Respiratory acidosis tendency")
            compensation, compensation_warnings = _respiratory_acidosis_assessment(measured_pco2, measured_hco3)
            warnings.extend(compensation_warnings)
            formula, substitution = _respiratory_acidosis_details(measured_pco2)
            formula_parts.append(formula)
            substitution_parts.append(substitution)
        elif respiratory_alkalosis:
            primary = t('abg_primary_trend_resp_alkalosis', "Respiratory alkalosis tendency")
            compensation, compensation_warnings = _respiratory_alkalosis_assessment(measured_pco2, measured_hco3)
            warnings.extend(compensation_warnings)
            formula, substitution = _respiratory_alkalosis_details(measured_pco2)
            formula_parts.append(formula)
            substitution_parts.append(substitution)
        else:
            primary = t('abg_primary_none', "No obvious simple acid-base abnormality")
            compensation = t('abg_comp_none', "PCO2 and HCO3 do not show significant deviation.")

    steps.append(t('abg_step2', "Step 2. Primary disorder: %s.") % primary)
    steps.append(t('abg_step3', "Step 3. Compensation assessment: %s") % compensation)
    steps.append(t('abg_step4', "Step 4. Mixed disorders: If compensation does not match expected, review AG, Delta Gap, and clinical context."))

    mismatch_str = t('abg_mismatch_keyword', "does not fully match")
    mixed_str = t('abg_mixed_keyword', "Mixed")
    if mismatch_str in compensation or mixed_str in primary:
        warnings.append(t('abg_warning_mixed', "Possible mixed acid-base disorder."))

    substitution_parts.insert(
        0,
        _classification_substitution(
            measured_ph,
            measured_pco2,
            measured_hco3,
            acid_base_status,
            primary,
        ),
    )

    return ABGAnalysis(
        summary="%s; %s" % (acid_base_status, primary),
        steps=steps,
        warnings=warnings,
        metadata=metadata,
        formula=" | ".join(formula_parts),
        substitution=" | ".join(substitution_parts),
        conclusion="%s; %s" % (primary, compensation),
    )
