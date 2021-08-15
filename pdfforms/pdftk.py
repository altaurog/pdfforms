"pdftk wrapper functions"
import itertools
from subprocess import PIPE, run


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


def fill_form(input_path, fdf, output_path, flatten):
    "fill a form using fdf data"
    cmd = ["pdftk", input_path, "fill_form", "-", "output", output_path]
    if flatten:
        cmd.append("flatten")
    run(cmd, input=fdf.encode("utf-8"), check=True)
