"library functions to inspect and fill pdf fillable forms"
import functools
import io
import itertools
import json
import os
from subprocess import PIPE, run

import pyexcel


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


def inspect(pdf_files, field_defs_file="fields.json", prefix="test/"):
    "inspect pdf forms, extract field data and fill with field numbers"
    try:
        with open(field_defs_file, "r") as f:
            field_defs = json.load(f)
    except OSError:
        field_defs = {}
    for filename in pdf_files:
        field_defs[filename] = inspect_pdf_fields(filename)
    with open(field_defs_file, "w") as f:
        json.dump(field_defs, f, indent=4)
    test_data = generate_test_data(pdf_files, field_defs)
    fg = fill_forms(prefix, field_defs, test_data, True)
    for filepath in fg:
        print(filepath)


def fill(
        data_file,
        sheet_name=None,
        pyexcel_library=None,
        field_defs_file="fields.json",
        prefix="filled/",
        no_flatten=False,
        value_transforms=None,
    ):
    "fill pdf forms with data from a spreadsheet"
    sheet = load_sheet(data_file, sheet_name, pyexcel_library)
    form_data = read_sheet(sheet, value_transforms)
    field_defs = load_field_defs(field_defs_file)
    flatten = not no_flatten
    fg = fill_forms(prefix, field_defs, form_data, flatten)
    for filepath in fg:
        print(filepath)


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
        if isinstance(row[0], str) and row[0].endswith(".pdf"):
            form_name = row[0]
            form_data[form_name] = {}
        elif form_name and  2 < len(row) and isinstance(row[0], int) and row[2]:
            field = str(row[0])
            form_data[form_name][field] = transform(row[2])
    return form_data


def load_field_defs(defs_file):
    "load field definitions"
    with open(defs_file) as f:
        return json.load(f)


def inspect_pdf_fields(form_name):
    "inspect a pdf for fillable fields"
    cmd = ["pdftk", form_name, "dump_data_fields", "output", "-"]
    p = run(cmd, stdout=PIPE, universal_newlines=True, check=True)
    num = itertools.count()
    fields = {}
    for line in p.stdout.splitlines():
        content = line.split(": ", 1)
        if ["---"] == content:
            fields[str(next(num))] = field_data = {}
        elif 2 == len(content):
            key = content[0][5:].lower()
            if "stateoption" == key:
                field_data.setdefault(key, []).append(content[1])
            else:
                field_data[key] = content[1]
    return fields


def fill_forms(path_func, field_defs, data, flatten=True):
    "fill pdf forms"
    for filepath, formdata in data.items():
        if not formdata:
            continue
        yield filepath
        output_path = path_func(filepath)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fdf_str = generate_fdf(field_defs[filepath], formdata)
        fill_form(filepath, fdf_str, output_path, flatten)


def generate_fdf(fields, data):
    "generate an fdf with to fill out form fields"
    fdf = io.StringIO()
    fdf.write(fdf_head)
    fdf.write("\n".join(fdf_fields(fields, data)))
    fdf.write(fdf_tail)
    return fdf.getvalue()


fdf_head = """%FDF-1.2
%âãÏÓ
1 0 obj 
<< /FDF 
<< /Fields [
"""

fdf_tail = """
] >> >>
endobj 
trailer
<< /Root 1 0 R >>
%%EOF
"""


def fdf_fields(fields, data):
    "format fdf fields"
    template = "<< /T ({field_name}) /V ({data}) >>"
    for n, d in data.items():
        field_def = fields.get(n)
        if field_def:
            field_name = field_def.get("name")
            if field_name:
                yield template.format(field_name=field_name, data=d)


def fill_form(input_path, fdf, output_path, flatten):
    "fill a form using fdf data"
    cmd = ["pdftk", input_path,
            "fill_form", "-",
            "output", output_path]
    if flatten:
        cmd.append("flatten")
    run(cmd, input=fdf.encode("utf-8"), check=True)


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


def make_transform(value_transforms):
    "compose a transform"
    apply = lambda v, f: f(v)
    return lambda v: functools.reduce(apply, value_transforms, v)
