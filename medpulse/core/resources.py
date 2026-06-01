"""Helpers for loading packaged JSON resources."""

import json
import pkgutil
import os
import importlib


def _package_for(path):
    if not path:
        return "medpulse.data"
    return "medpulse.data.%s" % path.replace("/", ".").replace("\\", ".")


def load_json(path, filename):
    package = _package_for(path)
    data = pkgutil.get_data(package, filename)
    if data is None:
        raise FileNotFoundError("%s not found in %s" % (filename, package))
    return json.loads(data.decode("utf-8"))


def list_json_files(path):
    package = _package_for(path)
    pkg = importlib.import_module(package)
    names = []
    if hasattr(pkg, '__file__') and pkg.__file__:
        pkg_dir = os.path.dirname(pkg.__file__)
        if os.path.isdir(pkg_dir):
            for name in os.listdir(pkg_dir):
                if name.endswith(".json"):
                    names.append(name)
    return sorted(names)


def load_app_metadata():
    return load_json("", "_meta.json")

