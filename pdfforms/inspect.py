"inspect pdf forms"
from . import pdftk


def inspect(pdf_files, field_defs):
    "inspect pdf forms, extract field data and fill with field numbers"
    for filename in pdf_files:
        field_defs[filename] = pdftk.inspect_pdf_fields(filename)
    return field_defs
