"""Minimal JSON-based i18n support."""

import json
import pkgutil


DEFAULT_LOCALE = "en"


def _load_locale(locale):
    normalized = locale.replace("-", "_")
    package = "medpulse.locales"
    
    # Try exact match first
    data = pkgutil.get_data(package, "%s.json" % normalized)
    if data is not None:
        return json.loads(data.decode("utf-8"))
        
    # Try base language (e.g. 'en' from 'en_US')
    base_lang = normalized.split("_")[0]
    if base_lang != normalized:
        data = pkgutil.get_data(package, "%s.json" % base_lang)
        if data is not None:
            return json.loads(data.decode("utf-8"))

    # Fallback to default
    if normalized == DEFAULT_LOCALE or base_lang == DEFAULT_LOCALE:
        raise FileNotFoundError("Default locale %s.json not found" % DEFAULT_LOCALE)
        
    data = pkgutil.get_data(package, "%s.json" % DEFAULT_LOCALE)
    if data is not None:
        return json.loads(data.decode("utf-8"))
    
    return {}


class Translator(object):
    """Simple locale dictionary wrapper with dot-path lookup."""

    def __init__(self, locale=DEFAULT_LOCALE):
        self.locale = locale.replace("-", "_")
        self._active = _load_locale(self.locale)
        self._default = self._active if self.locale == DEFAULT_LOCALE else _load_locale(DEFAULT_LOCALE)

    def t(self, key, default=None):
        value = self._lookup(self._active, key)
        if value is not None:
            return value
        value = self._lookup(self._default, key)
        if value is not None:
            return value
        return default if default is not None else key

    @staticmethod
    def _lookup(mapping, key):
        current = mapping
        for part in key.split("."):
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return current

_global_translator = None

def set_global_locale(locale):
    global _global_translator
    _global_translator = Translator(locale)

def t(key, default=None):
    if _global_translator is None:
        return default if default is not None else key
    return _global_translator.t(key, default)

