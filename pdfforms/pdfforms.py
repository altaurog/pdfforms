import argparse
import csv
import io
import itertools
import json
import os
import sys
from subprocess import run, PIPE

def inspect_pdfs(args):
    try:
        with open(args.field_defs, "r") as f:
            field_defs = json.load(f)
    except OSError:
        field_defs = {}
    for filename in args.pdf_file:
        field_defs[filename] = inspect_pdf_fields(filename)
    with open(args.field_defs, "w") as f:
        json.dump(field_defs, f, indent=4)
    test_data = generate_test_data(args.pdf_file, field_defs)
    fg = fill_forms(args.prefix, field_defs, test_data)
    for filepath in fg:
        print(filepath)


def fill_pdfs(args):
    form_data = read_data(args.data_file)
    field_defs = load_field_defs(args.field_defs)
    fg = fill_forms(args.prefix, field_defs, form_data)
    for filepath in fg:
        print(filepath)


def read_data(instream):
    form_data = {}
    for row in csv.reader(instream):
        if row and row[0].endswith(".pdf"):
            form_data[row[0]] = f = {}
        elif 2 < len(row) and row[0] and row[2]:
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
        content = line.strip().split(" ")
        if ["---"] == content:
            fields[str(next(num))] = field_data = {}
        elif 2 == len(content):
            key = content[0][5:-1].lower()
            if "stateoption" == key:
                field_data.setdefault(key, []).append(content[1])
            else:
                field_data[key] = content[1]
    return fields


def fill_forms(path_func, field_defs, data):
    for filepath, formdata in data.items():
        yield filepath
        output_path = path_func(filepath)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fdf_str = generate_fdf(field_defs[filepath], formdata)
        fill_form(filepath, fdf_str, output_path)


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


def fill_form(input_path, fdf, output_path):
    cmd = ["pdftk", input_path,
            "fill_form", "-",
            "output", output_path, "flatten"]
    run(cmd, input=fdf, check=True, encoding="utf-8")


def generate_test_data(pdf_files, field_defs):
    data = {}
    for filepath in pdf_files:
        fields = field_defs.get(filepath, {})
        data[filepath] = d = {}
        for field_id, field_def in fields.items():
            if "Text" == field_def.get("type"):
                d[field_id] = field_id
    return data


def make_path(prefix):
    return lambda path: prefix + os.path.basename(path)


def parse_cli(*args):
    parser = argparse.ArgumentParser(prog="forms")
    subparsers = parser.add_subparsers()

    inspect = subparsers.add_parser("inspect")
    inspect.set_defaults(func=inspect_pdfs)
    inspect.add_argument("pdf_file", nargs="+")
    inspect.add_argument("-f", "--field-defs", default="fields.json",
                            help="file in which to save field defs")
    inspect.add_argument("-p", "--prefix", default="test/", type=make_path,
                            help="location/prefix to which to save test files")

    fill = subparsers.add_parser("fill")
    fill.set_defaults(func=fill_pdfs)
    fill.add_argument("data_file", default='-',
                            type=argparse.FileType('r', encoding='utf-8'),
                            help="csv input data file")
    fill.add_argument("-f", "--field-defs", default="fields.json",
                            help="file from which to load field defs")
    fill.add_argument("-p", "--prefix", default="filled/", type=make_path,
                            help="location/prefix to which to save filled forms")
    return parser.parse_args(*args)


def main():
    args = parse_cli(sys.argv[1:])
    args.func(args)


if __name__ == "__main__":
    main()
