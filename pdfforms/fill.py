"fill pdf forms"
import os

from . import fdf, pdftk


def fill_forms(prefix, field_defs, data, flatten=True):
    "fill pdf forms"
    path_func = _make_path(prefix)
    for filepath, formdata in data.items():
        yield filepath
        output_path = path_func(filepath)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fdf_str = fdf.generate_fdf(field_defs[filepath], formdata)
        pdftk.fill_form(filepath, fdf_str, output_path, flatten)


def _make_path(prefix):
    return lambda path: prefix + os.path.basename(path)
