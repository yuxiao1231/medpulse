"""Formatting helpers shared by platform UIs."""

from medpulse.i18n import t

class ResultFormatter(object):
    """Turn deterministic outputs into plain display text."""

    @staticmethod
    def format_calculation(result):
        value_text = "%s %s" % (result.format_value(), result.unit)
        conclusion = result.conclusion or value_text
        lines = [
            result.label,
            "%s %s" % (t('fmt_formula', 'Formula:'), result.formula),
            "%s %s" % (t('fmt_substitution', 'Substitution:'), result.substitution),
            "%s %s" % (t('fmt_conclusion', 'Conclusion:'), conclusion),
            "%s %s" % (t('fmt_reference', 'Reference:'), result.reference),
        ]
        if result.interpretation:
            lines.append("%s %s" % (t('fmt_interpretation', 'Interpretation:'), result.interpretation))
        if result.warnings:
            lines.append("")
            lines.append(t('fmt_warnings', 'Warnings:'))
            for warning in result.warnings:
                lines.append("- %s" % warning)
        return "\n".join(lines)

    @staticmethod
    def format_score(result):
        lines = [
            result.label,
            "",
            t('fmt_score_rule', 'Scoring Rule:'),
            result.guidance,
            "",
            t('fmt_score_process', 'Scoring Process:'),
        ]
        for item in result.breakdown:
            lines.append("- %s: %s (%s)" % (item['label'], item['value'], item['score']))
        
        lines.append("")
        lines.append(t('fmt_score_conclusion', 'Conclusion:'))
        lines.append("- %s %s" % (t('fmt_total_score', 'Total Score:'), result.total_score))
        lines.append("- %s %s" % (t('fmt_risk_level', 'Risk Level:'), result.risk_level))
        return "\n".join(lines)

    @staticmethod
    def format_abg(analysis):
        lines = [analysis.summary, ""]
        if getattr(analysis, "formula", ""):
            lines.append("%s %s" % (t('fmt_formula', 'Formula:'), analysis.formula))
        if getattr(analysis, "substitution", ""):
            lines.append("%s %s" % (t('fmt_substitution', 'Substitution:'), analysis.substitution))
        if getattr(analysis, "conclusion", ""):
            lines.append("%s %s" % (t('fmt_conclusion', 'Conclusion:'), analysis.conclusion))
        if len(lines) > 2:
            lines.append("")
        lines.extend(analysis.steps)
        if analysis.warnings:
            lines.append("")
            lines.append(t('fmt_warnings', 'Warnings:'))
            for warning in analysis.warnings:
                lines.append("- %s" % warning)
        return "\n".join(lines)
