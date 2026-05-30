"""Unit conversion helpers used by deterministic calculators."""

from decimal import Decimal

from medpulse.core.exceptions import ValidationError
from medpulse.i18n import t
from medpulse.core.validators import (
    coerce_decimal,
    ensure_decimal_between,
    ensure_decimal_positive,
)


MASS_TO_MCG = {
    "mcg": Decimal("1"),
    "ug": Decimal("1"),
    "μg": Decimal("1"),
    "mg": Decimal("1000"),
}

CONCENTRATION_TO_MCG_PER_ML = {
    "mcg/ml": Decimal("1"),
    "mcg/mL": Decimal("1"),
    "mcg_per_ml": Decimal("1"),
    "ug/ml": Decimal("1"),
    "ug/mL": Decimal("1"),
    "μg/ml": Decimal("1"),
    "μg/mL": Decimal("1"),
    "mg/ml": Decimal("1000"),
    "mg/mL": Decimal("1000"),
    "mg_per_ml": Decimal("1000"),
}


def normalize_unit(unit):
    if unit is None:
        return ""
    return str(unit).strip()


def amount_to_mcg(amount, amount_unit):
    value = ensure_decimal_between(coerce_decimal(amount, "amount"), "amount", "0", "1000000000")
    ensure_decimal_positive(value, "amount")
    normalized = normalize_unit(amount_unit)
    multiplier = MASS_TO_MCG.get(normalized)
    if multiplier is None:
        raise ValidationError(t("err_unsupported_mass_unit", "Unsupported mass unit. Use mcg/μg/ug or mg."))
    return value * multiplier


def concentration_to_mcg_per_ml(value, unit="mcg/mL"):
    concentration = ensure_decimal_between(
        coerce_decimal(value, "concentration"),
        "concentration",
        "0.000001",
        "1000000000",
    )
    ensure_decimal_positive(concentration, "concentration")
    normalized = normalize_unit(unit)
    multiplier = CONCENTRATION_TO_MCG_PER_ML.get(normalized)
    if multiplier is None:
        raise ValidationError(t("err_unsupported_conc_unit", "Unsupported concentration unit. Use mcg/mL or mg/mL."))
    return concentration * multiplier


def concentration_from_amount(amount, amount_unit, volume_ml):
    volume = ensure_decimal_between(coerce_decimal(volume_ml, "volume_ml"), "volume_ml", "0.01", "100000")
    ensure_decimal_positive(volume, "volume_ml")
    return amount_to_mcg(amount, amount_unit) / volume
