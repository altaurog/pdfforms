import io
import itertools
import json
import os
from subprocess import PIPE, run

import pyexcel


def inspect(pdf_files, field_defs_file="fields.json", prefix="test/"):
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
        field_defs_file="fields.json",
        prefix="filled/",
        no_flatten=False,
    ):
    sheet = load_sheet(data_file, sheet_name)
    form_data = read_sheet(sheet)
    field_defs = load_field_defs(field_defs_file)
    flatten = not no_flatten
    fg = fill_forms(prefix, field_defs, form_data, flatten)
    for filepath in fg:
        print(filepath)


def load_sheet(file_name, sheet_name):
    kwargs = {
        "file_name": file_name,
        "column_limit": 3,
    }
    if sheet_name:
        kwargs["sheet_name"] = sheet_name
    return pyexcel.get_sheet(**kwargs)


def read_sheet(sheet):
    form_data = {}
    for row in sheet:
        if row[0] and row[0].endswith(".pdf"):
            form_data[row[0]] = f = {}
        elif 2 < len(row) and isinstance(row[0], int) and row[2]:
            f[str(row[0])] = row[2]
    return form_data


def load_field_defs(defs_file):
    with open(defs_file) as f:
        return json.load(f)


def inspect_pdf_fields(form_name):
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
    for filepath, formdata in data.items():
        if not formdata:
            continue
        yield filepath
        output_path = path_func(filepath)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fdf_str = generate_fdf(field_defs[filepath], formdata)
        fill_form(filepath, fdf_str, output_path, flatten)


def generate_fdf(fields, data):
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
    template = "<< /T ({field_name}) /V ({data}) >>"
    for n, d in data.items():
        field_def = fields.get(n)
        if field_def:
            field_name = field_def.get("name")
            if field_name:
                yield template.format(field_name=field_name, data=d)


def fill_form(input_path, fdf, output_path, flatten):
    cmd = ["pdftk", input_path,
            "fill_form", "-",
            "output", output_path]
    if flatten:
        cmd.append("flatten")
    run(cmd, input=fdf.encode("utf-8"), check=True)


def generate_test_data(pdf_files, field_defs):
    data = {}
    for filepath in pdf_files:
        fields = field_defs.get(filepath, {})
        data[filepath] = d = {}
        for field_id, field_def in fields.items():
            if "Text" == field_def.get("type"):
                d[field_id] = field_id
    return data
