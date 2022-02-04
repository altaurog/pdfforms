"fdf functions"
from encodings import utf_8
import io

fdf_head = """<?xml version="1.0" encoding="UTF-8"?>
<xfdf xmlns="http://ns.adobe.com/xfdf/" xml:space="preserve">
   <fields>
"""

fdf_tail = """
   </fields>
</xfdf>
"""


def generate_fdf(fields, data):
    "generate an xfdf with to fill out form fields"
    fdf = io.StringIO()
    fdf.write(fdf_head)
    fdf.write("\n".join(fdf_fields(fields, data)))
    fdf.write(fdf_tail)
    return fdf.getvalue()


def fdf_fields(fields, data):
    "format xfdf fields"
    template = "      <field name=\"{field_name}\">\n      <value>{data}</value>\n      </field>"
    for n, d in data.items():
        field_def = fields.get(n)
        if field_def:
            field_name = field_def.get("name")
            if field_name:
                yield template.format(field_name=field_name, data=d)
