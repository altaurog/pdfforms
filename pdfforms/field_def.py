"save/load field defs"
import json


def save_field_defs(field_defs_file, field_defs):
    "save field definitions"
    with open(field_defs_file, "w") as f:
        json.dump(field_defs, f, indent=4)


def load_field_defs(field_defs_file, fail_silently=False):
    "load field definitions"
    try:
        with open(field_defs_file) as f:
            return json.load(f)
    except OSError:
        if fail_silently:
            return {}
        raise
