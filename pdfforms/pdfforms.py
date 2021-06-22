"library functions to inspect and fill pdf fillable forms"
from . import fill, inspect, spreadsheet
from .field_def import load_field_defs, save_field_defs


def fill_pdfs(
        data_file,
        sheet_name=None,
        pyexcel_library=None,
        field_defs_file="fields.json",
        prefix="filled/",
        no_flatten=False,
        value_transforms=None,
    ):
    "fill pdf forms with data from a spreadsheet"
    sheet = spreadsheet.load_sheet(data_file, sheet_name, pyexcel_library)
    form_data = spreadsheet.read_sheet(sheet, value_transforms)
    field_defs = load_field_defs(field_defs_file)
    flatten = not no_flatten
    yield from fill.fill_forms(prefix, field_defs, form_data, flatten)


def inspect_pdfs(pdf_files, field_defs_file="fields.json", prefix="test/"):
    "inspect pdf for fillable form fields"
    field_defs = load_field_defs(field_defs_file, fail_silently=True)
    field_defs = inspect.inspect(pdf_files, field_defs)
    save_field_defs(field_defs_file, field_defs)
    test_data = generate_test_data(pdf_files, field_defs)
    yield from fill.fill_forms(prefix, field_defs, test_data, flatten=True)


def generate_test_data(pdf_files, field_defs):
    "generate test data with field ids"
    data = {}
    for filepath in pdf_files:
        fields = field_defs.get(filepath, {})
        data[filepath] = d = {}
        for field_id, field_def in fields.items():
            if "Text" == field_def.get("type"):
                d[field_id] = field_id
    return data


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
