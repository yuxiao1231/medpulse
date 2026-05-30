"""Helpers for loading packaged JSON resources."""

import json
from importlib import resources


def _package_for(path):
    if not path:
        return "medpulse.data"
    return "medpulse.data.%s" % path.replace("/", ".").replace("\\", ".")


def load_json(path, filename):
    package = _package_for(path)
    with resources.open_text(package, filename, encoding="utf-8") as handle:
        return json.load(handle)


def list_json_files(path):
    package = _package_for(path)
    names = []
    for name in resources.contents(package):
        if name.endswith(".json"):
            names.append(name)
    return sorted(names)


def load_app_metadata():
    return load_json("", "_meta.json")

