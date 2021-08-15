"""
High-level library functions to inspect and fill pdf fillable forms.
These functions provide an programmatic interface similar to the command-line
interface.

.. note:: These functions return a generator.

    If you don’t iterate the results, they won’t do anything.
"""
from typing import Callable, Iterable, Iterator, Optional
from . import fill, inspect, spreadsheet
from .field_def import load_field_defs, save_field_defs


def inspect_pdfs(
    pdf_files: Iterable[str],
    field_defs_file: str = "fields.json",
    prefix: str = "test/",
) -> Iterator[str]:
    """
    inspect pdf for fillable form fields

    This is essentially the same as `pdfforms inspect` command.

    :param pdf_files: file paths to inspect
    :param field_defs_file: path to which to save json field definitions
    :param prefix: prefix for saving test files
    :return: a generator of inspected file names.
        Be sure to iterate it or nothing will happen.
    """
    field_defs = load_field_defs(field_defs_file, fail_silently=True)
    field_defs = inspect.inspect(pdf_files, field_defs)
    save_field_defs(field_defs_file, field_defs)
    test_data = _generate_test_data(pdf_files, field_defs)
    yield from fill.fill_forms(prefix, field_defs, test_data, flatten=True)


def fill_pdfs(
    data_file: str,
    sheet_name: Optional[str] = None,
    pyexcel_library: Optional[str] = None,
    field_defs_file: str = "fields.json",
    prefix: str = "filled/",
    no_flatten: bool = False,
    value_transforms: Optional[Iterable[Callable]] = None,
) -> Iterator[str]:
    """
    fill pdf forms with data from a spreadsheet

    This is essentially the same as `pdfforms fill` command.

    :param data_file: path of spreadsheet datafile
    :param sheet_name: sheet name, defaults to first sheet
    :param field_defs_file: path from which to load json field definitions
    :param prefix: prefix for saving filled pdf files
    :param no_flatten: do not flatten output pdf files
    :param value_transforms: value transformation/format functions
        to be called in order on each data value before inserting
        it into the pdf form.  See api example for more information.
    :return: a generator of filled form file names.
        Be sure to iterate it or nothing will happen.
    """
    sheet = spreadsheet.load_sheet(data_file, sheet_name, pyexcel_library)
    form_data = spreadsheet.read_sheet(sheet, list(value_transforms))
    field_defs = load_field_defs(field_defs_file)
    flatten = not no_flatten
    yield from fill.fill_forms(prefix, field_defs, form_data, flatten)


def _generate_test_data(pdf_files, field_defs):
    "generate test data with field ids"
    data = {}
    for filepath in pdf_files:
        fields = field_defs.get(filepath, {})
        data[filepath] = d = {}
        for field_id, field_def in fields.items():
            if "Text" == field_def.get("type"):
                d[field_id] = field_id
    return data
