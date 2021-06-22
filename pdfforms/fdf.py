"fdf functions"
import io

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


def generate_fdf(fields, data):
    "generate an fdf with to fill out form fields"
    fdf = io.StringIO()
    fdf.write(fdf_head)
    fdf.write("\n".join(fdf_fields(fields, data)))
    fdf.write(fdf_tail)
    return fdf.getvalue()


def fdf_fields(fields, data):
    "format fdf fields"
    template = "<< /T ({field_name}) /V ({data}) >>"
    for n, d in data.items():
        field_def = fields.get(n)
        if field_def:
            field_name = field_def.get("name")
            if field_name:
                yield template.format(field_name=field_name, data=d)
