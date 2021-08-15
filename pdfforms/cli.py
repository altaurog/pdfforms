#!/usr/bin/env python3
"cli to inspect and fill pdf fillable forms"
import argparse
import sys

from . import pdfforms


def inspect_pdfs(args):
    "entry point for inspect command"
    for filepath in pdfforms.inspect_pdfs(
        pdf_files=args.pdf_file,
        field_defs_file=args.field_defs_file,
        prefix=args.prefix,
    ):
        print(filepath)


def fill_pdfs(args):
    "entry point for fill command"
    value_transforms = []
    if args.round:
        value_transforms.append(pdfforms.round_float)
    if args.add_commas:
        value_transforms.append(pdfforms.comma_format)
    for filepath in pdfforms.fill_pdfs(
        data_file=args.data_file,
        sheet_name=args.sheet_name,
        pyexcel_library=args.pyexcel_library,
        field_defs_file=args.field_defs_file,
        prefix=args.prefix,
        no_flatten=args.no_flatten,
        value_transforms=value_transforms,
    ):
        print(filepath)


def cli_parser():
    "parse command line arguments"
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    # TODO: Make this a parameter of add_subparsers() in Python 3.7+
    subparsers.required = True

    inspect = subparsers.add_parser(
        "inspect",
        description="""
        Inspect one or more pdf files for forms and number the form fields.
        For each pdf containing form fields, a test file is generated showing
        the number of each field.
    """,
    )
    inspect.set_defaults(func=inspect_pdfs)
    inspect.add_argument("pdf_file", nargs="+")
    inspect.add_argument(
        "-p",
        "--prefix",
        default="test/",
        help="location/prefix to which to save test files (test/)",
    )
    inspect.add_argument(
        "-f",
        "--field-defs",
        default="fields.json",
        help="""file in which to save field defs (fields.json).
        In general it should not be necessary to change this.
        """,
        dest="field_defs_file",
    )

    fill = subparsers.add_parser(
        "fill",
        description="""
        Fill one or more pdf forms with data from specified datafile.
    """,
    )
    fill.set_defaults(func=fill_pdfs)
    fill.add_argument("data_file", help="spreadsheet data file")
    fill.add_argument("-s", "--sheet-name", help="input sheet name (first sheet)")
    fill.add_argument(
        "-p",
        "--prefix",
        default="filled/",
        help="location/prefix to which to save filled forms (filled/)",
    )
    fill.add_argument(
        "--round",
        action="store_true",
        help="round floating-point numbers",
    )
    fill.add_argument(
        "--add-commas",
        action="store_true",
        help="format numbers with comma as thousands-separator",
    )
    fill.add_argument(
        "--no-flatten",
        action="store_true",
        help="do not flatten pdf output, leaving form fillable (False).",
    )
    fill.add_argument(
        "--pyexcel-library",
        help="""pyexcel library to use for loading data file
            (only necessary if more than one library is available for specified data file)
        """,
    )
    fill.add_argument(
        "-f",
        "--field-defs",
        default="fields.json",
        help="""file from which to load field defs (fields.json).
            In general it should not be necessary to change this.
        """,
        dest="field_defs_file",
    )
    return parser


def parse_cli(*args):
    parser = cli_parser()
    return parser.parse_args(*args)


def main(argv=None):
    "cli entry point"
    args = parse_cli(argv or sys.argv[1:])
    args.func(args)


if __name__ == "__main__":
    main()
