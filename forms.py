import argparse
import csv
import io
import itertools
import json
import os
import sys
from subprocess import run, PIPE

def inspect_pdfs(args):
    field_defs = {}
    for filename in args.pdf_file:
        field_defs[filename] = get_fields(filename)
    with open(args.field_defs, 'w') as f:
        json.dump(field_defs, f, indent=4)
    test_data = generate_test_data(field_defs)
    fg = fill_forms(args.prefix, field_defs, test_data)
    for filepath in fg:
        print(filepath)


def main(filename):
    with open(filename) as f:
        form_data = read_data(f)
    for form_name, data in form_data.items():
        fields = list(get_fields(form_name))
        print(form_name, len(data), len(fields))
        fdf = generate_fdf(form_name, fields, data)
        fill_form(form_name, fdf)


def read_data(instream):
    form_data = {}
    for row in csv.reader(instream):
        if row and row[0].endswith('.pdf'):
            form_data[row[0]] = f = {}
        elif 2 < len(row) and row[0] and row[2]:
            f[field_name(row[0])] = row[2]
    return form_data


def field_name(s):
    return s if '[' in s else s + '['


def get_fields(form_name):
    cmd = ['pdftk', form_name, 'dump_data_fields', 'output', '-']
    p = run(cmd, stdout=PIPE, universal_newlines=True, check=True)
    num = itertools.count()
    fields = {}
    for line in p.stdout.splitlines():
        content = line.strip().split(' ')
        if ['---'] == content:
            fields[str(next(num))] = field_data = {}
        elif 2 == len(content):
            field_data[content[0][5:-1].lower()] = content[1]
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
    fdf.write('\n'.join(fdf_fields(fields, data)))
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
    template = '<< /T ({field_name}) /V ({data}) >>'
    for n, d in data.items():
        field_def = fields.get(n)
        if field_def:
            field_name = field_def.get('name')
            if field_name:
                yield template.format(field_name=field_name, data=d)


def fill_form(input_path, fdf, output_path):
    cmd = ['pdftk', input_path,
            'fill_form', '-',
            'output', output_path, 'flatten']
    run(cmd, input=fdf, check=True, encoding='utf-8')


def generate_test_data(field_defs):
    data = {}
    for filepath, fields in field_defs.items():
        data[filepath] = d = {}
        for field_id in fields.keys():
            d[field_id] = "f" + field_id
    return data


def make_path(prefix):
    return lambda path: prefix + os.path.basename(path)


def parse_cli(*args):
    parser = argparse.ArgumentParser(prog="forms")
    subparsers = parser.add_subparsers()
    inspect = subparsers.add_parser("inspect")
    inspect.set_defaults(func=inspect_pdfs)
    inspect.add_argument('pdf_file', nargs='+')
    inspect.add_argument('-f', '--field-defs', default='fields.json',
                            help='file in which to save field defs')
    inspect.add_argument('-p', '--prefix', default='test/', type=make_path,
                            help='location/prefix to which to save test files')
    return parser.parse_args(*args)


if __name__ == '__main__':
    args = parse_cli(sys.argv[1:])
    args.func(args)
