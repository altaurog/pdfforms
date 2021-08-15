"""
Value transform functions

`pdfforms` provides a mechanism for transforming and formatting values before
using them to populate fields in a pdf form.  The motivation behind this is
to make data read directly from an Excel or LibreOffice spreadsheet presentable
before using it.  The transforms are applied while reading data from the data file.

The library currently ships with two such functions, which implement the functionality
provided by the `--round` and `--add-commas` command-line arguments.

To use these (or other formatting functions) with the api, pass them to
:py:func:`.fill_pdfs` in the `value_transforms` parameter.
"""


def round_float(value):
    "round float to int"
    try:
        return round(value)
    except TypeError:
        return value


def comma_format(value):
    "add thousands separators to numbers"
    try:
        return f"{value:,}"
    except ValueError:
        return value
