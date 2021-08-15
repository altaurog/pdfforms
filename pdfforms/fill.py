"""
Low-level library function to fill pdf forms.

.. note:: This function returns a generator.

    If you don’t iterate the results, it won’t do anything.
"""
import os

from typing import Iterator, Mapping

from . import fdf, pdftk


def fill_forms(
    prefix: str,
    field_defs,
    data: Mapping[str, Mapping[str, str]],
    flatten: bool = True,
) -> Iterator[str]:
    """
    Fill pdf forms.

    :param prefix: prefix for saving filled pdf files
    :param field_defs: field definitions dictionary loaded from `fields.json` file
    :param data: a mapping of <pdfpath> -> (mapping of <field num> -> <data value>)
    :param flatten: flatten output pdf files
    :return: a generator of filled form file names.
        Be sure to iterate it or nothing will happen.
    """
    path_func = _make_path(prefix)
    for filepath, formdata in data.items():
        yield filepath
        output_path = path_func(filepath)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fdf_str = fdf.generate_fdf(field_defs[filepath], formdata)
        pdftk.fill_form(filepath, fdf_str, output_path, flatten)


def _make_path(prefix):
    return lambda path: prefix + os.path.basename(path)
