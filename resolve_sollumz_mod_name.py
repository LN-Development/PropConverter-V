import importlib
import sys


def resolve_sollumz_mod_name():
    mod_name = None
    for name in ("sollumz", "Sollumz"):
        try:
            importlib.import_module(name)
            mod_name = name
            break
        except ImportError:
            continue

    if mod_name is None:
        for key in sys.modules.keys():
            if key.lower().endswith("sollumz"):
                mod_name = key
                break

    return mod_name
