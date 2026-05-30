"""JSON-driven score calculation engine."""

from medpulse.core.exceptions import FeatureNotReadyError, ValidationError
from medpulse.core.models import ScoreResult
from medpulse.core.resources import load_json


def _normalize_boolean(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        return normalized in ("1", "true", "yes", "y", "on")
    return False


def load_definition(score_id):
    return load_json("scores", "%s.json" % score_id)


def calculate_score(definition, answers):
    if definition.get("status") != "implemented":
        raise FeatureNotReadyError("Score '%s' is not implemented yet." % definition.get("id"))

    total = 0
    breakdown = []

    for item in definition.get("items", []):
        item_id = item["id"]
        if item_id not in answers:
            raise ValidationError("Missing score item: %s" % item_id)
        raw_value = answers[item_id]
        item_type = item.get("type")
        from medpulse.i18n import t
        if item_type == "boolean":
            selected = _normalize_boolean(raw_value)
            score = item.get("score_when_true", 1) if selected else item.get("score_when_false", 0)
            display_value = t("yes", "yes") if selected else t("no", "no")
        elif item_type == "choice":
            option = None
            for candidate in item.get("options", []):
                if candidate["id"] == raw_value:
                    option = candidate
                    break
            if option is None:
                raise ValidationError(t("err_invalid_option", "Invalid option for %s") % item_id)
            score = int(option.get("score", 0))
            display_value = t("%s_opt_%s" % (definition["id"], option["id"]), option.get("label", option["id"]))
        else:
            raise ValidationError(t("err_unsupported_item", "Unsupported score item type: %s") % item_type)

        total += int(score)
        breakdown.append(
            {
                "id": item_id,
                "label": t("%s_%s" % (definition["id"], item_id), item.get("label", item_id)),
                "value": display_value,
                "score": int(score),
            }
        )

    from medpulse.i18n import t

    risk_level = t("risk_unstratified", "Unstratified")
    for idx, band in enumerate(definition.get("risk_bands", [])):
        minimum = int(band.get("min_score", -99999))
        maximum = int(band.get("max_score", 99999))
        if minimum <= total <= maximum:
            raw_label = band.get("label", "Unstratified")
            risk_level = t("%s_risk_band_%d" % (definition["id"], idx), raw_label)
            break

    return ScoreResult(
        score_id=definition["id"],
        label=t("%s_name" % definition["id"], definition.get("name", definition["id"])),
        total_score=total,
        risk_level=risk_level,
        guidance=t("%s_guidance" % definition["id"], definition.get("guidance", "")),
        breakdown=breakdown,
    )

