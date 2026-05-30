"""Validation helpers."""

from decimal import Decimal, InvalidOperation

from medpulse.core.exceptions import ValidationError
from medpulse.i18n import t

def _get_field_name(field_name):
    return t("input_" + field_name, field_name)

import math

def coerce_float(value, field_name):
    if value is None or value == "":
        raise ValidationError(t("err_missing_value", "Please enter a valid number for {field}").format(field=_get_field_name(field_name)))
    try:
        val = float(value)
        if math.isnan(val) or math.isinf(val):
            raise ValueError("NaN or Inf not allowed")
        return val
    except (TypeError, ValueError):
        raise ValidationError(t("err_invalid_number", "Invalid number format for {field}").format(field=_get_field_name(field_name)))


def coerce_decimal(value, field_name):
    if value is None or value == "":
        raise ValidationError(t("err_missing_value", "Please enter a valid number for {field}").format(field=_get_field_name(field_name)))
    try:
        val = Decimal(str(value).strip())
        if val.is_nan() or val.is_infinite():
            raise ValueError("NaN or Inf not allowed")
        return val
    except (InvalidOperation, ValueError):
        raise ValidationError(t("err_invalid_number", "Invalid number format for {field}").format(field=_get_field_name(field_name)))


def ensure_between(value, field_name, minimum=None, maximum=None):
    field_translated = _get_field_name(field_name)
    if minimum is not None and maximum is not None:
        if value < minimum or value > maximum:
            raise ValidationError(t("err_range_between", "{field} must be between {min} and {max}.").format(field=field_translated, min=minimum, max=maximum))
    elif minimum is not None and value < minimum:
        raise ValidationError(t("err_range_min", "{field} must be >= {min}.").format(field=field_translated, min=minimum))
    elif maximum is not None and value > maximum:
        raise ValidationError(t("err_range_max", "{field} must be <= {max}.").format(field=field_translated, max=maximum))
    return value


def ensure_decimal_between(value, field_name, minimum=None, maximum=None):
    field_translated = _get_field_name(field_name)
    if minimum is not None and maximum is not None:
        if value < Decimal(str(minimum)) or value > Decimal(str(maximum)):
            raise ValidationError(t("err_range_between", "{field} must be between {min} and {max}.").format(field=field_translated, min=minimum, max=maximum))
    elif minimum is not None and value < Decimal(str(minimum)):
        raise ValidationError(t("err_range_min", "{field} must be >= {min}.").format(field=field_translated, min=minimum))
    elif maximum is not None and value > Decimal(str(maximum)):
        raise ValidationError(t("err_range_max", "{field} must be <= {max}.").format(field=field_translated, max=maximum))
    return value


def ensure_positive(value, field_name, allow_zero=False):
    field_translated = _get_field_name(field_name)
    threshold = 0.0 if allow_zero else 0.0
    if allow_zero and value < threshold:
        raise ValidationError(t("err_positive_zero", "{field} must be >= 0.").format(field=field_translated))
    if not allow_zero and value <= threshold:
        raise ValidationError(t("err_positive", "{field} must be > 0.").format(field=field_translated))
    return value


def ensure_decimal_positive(value, field_name, allow_zero=False):
    field_translated = _get_field_name(field_name)
    threshold = Decimal("0")
    if allow_zero and value < threshold:
        raise ValidationError(t("err_positive_zero", "{field} must be >= 0.").format(field=field_translated))
    if not allow_zero and value <= threshold:
        raise ValidationError(t("err_positive", "{field} must be > 0.").format(field=field_translated))
    return value

