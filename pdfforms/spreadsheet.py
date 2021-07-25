"spreadsheet data functions"
import functools

import pyexcel


def load_sheet(file_name, sheet_name, pyexcel_library):
    "load a spreadsheet"
    kwargs = {
        "file_name": file_name,
        "column_limit": 3,
    }
    if sheet_name:
        kwargs["sheet_name"] = sheet_name
    if pyexcel_library:
        kwargs["library"] = pyexcel_library
    return pyexcel.get_sheet(**kwargs)


def read_sheet(sheet, value_transforms=None):
    "extract data from the spreadsheet"
    form_data = {}
    form_name = None
    transform = make_transform(value_transforms or [])
    for row in sheet:
        if isinstance(row[0], str) and row[0].lower().endswith(".pdf"):
            form_name = row[0]
            form_data[form_name] = {}
        elif form_name and 2 < len(row) and isinstance(row[0], int) and row[2]:
            field = str(row[0])
            form_data[form_name][field] = transform(row[2])
    return {name: data for name, data in form_data.items() if data}


def make_transform(value_transforms):
    "compose a transform"
    apply = lambda v, f: f(v)
    return lambda v: functools.reduce(apply, value_transforms, v)
