API Example
============

`pdfforms` v2.0 introduces a python API for filling pdf forms similar to
the command-line interface.  This can be useful for preprocessing and
formatting data values used to populate the forms.

For example, when loading a LibreOffice Calc spreadsheet with pyexcel-ods_,
values formatted as currency are read as a string with a floating point
number followed by a space and a currency designation, so:
``'18746.3048283886 USD'``.  Since a more friendly representation may be
desired, the api provides for successive application of a chain of
formatting functions.  :doc:`Two such functions <pdfforms/transforms>`
are provided with the library.

Here is a concrete example which I use to fill my tax forms from a
LibreOffice Calc spreadsheet.  It parses US and Israel currency
designations, rounds floating-point numbers, and represents negative
numbers with parentheses rather than a minus sign.

.. code-block:: python

    "fill pdf tax forms"
    import sys

    from pdfforms import pdfforms


    def main(data_file):
        "do it"
        for filepath in pdfforms.fill_pdfs(
            data_file,
            sheet_name="f1040",
            value_transforms=[parse_currency, format_number],
        ):
            print(filepath)


    def parse_currency(value):
        "try to read a number with a currency mark"
        try:
            if value.endswith((" USD", " ILS")):
                return float(value.split()[0])
        except (AttributeError, ValueError):
            pass
        return value


    def format_number(value):
        try:
            format_str = "({:,})" if value < 0 else "{:,}"
            return format_str.format(round(abs(value)))
        except (TypeError, ValueError):
            return value


    if __name__ == "__main__":
        main(sys.argv[1])

.. _pyexcel-ods: https://github.com/pyexcel/pyexcel-ods
