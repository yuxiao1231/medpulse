import json
import traceback

def wrap_call(module_name, func_name, kwargs_json):
    try:
        import importlib
        from medpulse.ui.adapter import ResultFormatter
        from medpulse.core.models import CalculationResult, ScoreResult, ABGAnalysis

        module = importlib.import_module("medpulse.core.calculators.%s" % module_name)
        func = getattr(module, func_name)
        
        # kwargs_json is always a JSON string from Kotlin side
        if isinstance(kwargs_json, str):
            py_kwargs = json.loads(kwargs_json)
        elif hasattr(kwargs_json, "entrySet"):
            py_kwargs = {str(e.getKey()): e.getValue() for e in kwargs_json.entrySet()}
        else:
            py_kwargs = dict(kwargs_json)
            
        result = func(**py_kwargs)
        
        if isinstance(result, ABGAnalysis):
            formatted = ResultFormatter.format_abg(result)
            return json.dumps({"success": True, "result": formatted})
        elif isinstance(result, ScoreResult):
            formatted = ResultFormatter.format_score(result)
            return json.dumps({"success": True, "result": formatted})
        elif isinstance(result, CalculationResult):
            formatted = ResultFormatter.format_calculation(result)
            return json.dumps({"success": True, "result": formatted})
        elif hasattr(result, "description") and getattr(result, "description"):
            return json.dumps({"success": True, "result": getattr(result, "description")})
        elif hasattr(result, "value"):
            return json.dumps({"success": True, "result": str(getattr(result, "value"))})
        else:
            return json.dumps({"success": True, "result": str(result)})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()})

def set_locale(locale):
    try:
        from medpulse.i18n import set_global_locale
        set_global_locale(locale)
        return json.dumps({"success": True})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()})


def get_implemented_scores():
    try:
        import pkgutil
        data_bytes = pkgutil.get_data("medpulse.data.scores", "index.json")
        data = json.loads(data_bytes.decode('utf-8'))
        
        # Only return implemented scores
        implemented = [s for s in data.get("scores", []) if s.get("status") == "implemented"]
        return json.dumps({"success": True, "result": json.dumps(implemented)})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()})

def get_score_schema(score_id):
    try:
        import pkgutil
        data_bytes = pkgutil.get_data("medpulse.data.scores", "%s.json" % score_id)
        data = json.loads(data_bytes.decode('utf-8'))
        return json.dumps({"success": True, "result": json.dumps(data)})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()})

def get_checklists():
    try:
        import pkgutil
        data_bytes = pkgutil.get_data("medpulse.data.checklists", "procedures.json")
        data = json.loads(data_bytes.decode('utf-8'))
        
        items = data.get("items", [])
        return json.dumps({"success": True, "result": json.dumps(items)})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()})

def calculate_score_wrap(score_id, answers_json):
    try:
        answers = json.loads(answers_json)
        from medpulse.core.scores.engine import calculate_score, load_definition
        from medpulse.ui.adapter import ResultFormatter
        definition = load_definition(score_id)
        result = calculate_score(definition, answers)
        formatted = ResultFormatter.format_score(result)
        return json.dumps({"success": True, "result": formatted})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()})

