#!/usr/bin/env python
"""
Popcorn, a kernel analyzer tool.

Args:
    files: A list of trace file names.
"""

import argparse
import importlib.metadata
from openpyxl import Workbook
import sys

from popcorn.analyzers import hotspots, kernel_differences
from popcorn.interfaces import Verbosity, Kettle, MDTables, CSVArchive
from popcorn.reporters import report_hotspots, report_kdiff
from popcorn.readers import LevelZeroTracerJsonReader
from popcorn.structures import Case

__version__ = importlib.metadata.version("popcorn")


def main_cli() -> str | None:
    # prepare console interface arguments
    parser = argparse.ArgumentParser(
        prog="popcorn",
        description="analyze kernel hotspots to solve problems like performance regression",
    )

    parser.add_argument(
        "files",
        nargs="+",
        type=str,
        help="input trace files (provide at least one)",
    )

    parser.add_argument(
        "-o", "--output", type=str, help="output file name (default: result)", dest="o"
    )
    parser.add_argument(
        "-ot",
        "--output-type",
        dest="ot",
        type=str,
        choices=["xlsx", "csv", "md"],
        help="specify output type (default: xlsx)",
    )

    analyzer_args = parser.add_mutually_exclusive_group()
    analyzer_args.add_argument(
        "-a",
        "--analyzer",
        type=str,
        choices=["pops", "kdiff"],
        help="pops - hotspots; kdiff - kernel differences",
        dest="a",
    )
    analyzer_args.add_argument(
        "-A",
        "--full-analysis",
        action="store_true",
        dest="full_analysis",
        help="Use all possible analyzers on the files provided.",
    )

    verbosity_args = parser.add_mutually_exclusive_group()
    verbosity_args.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="give a detailed report (console output only)",
        dest="verbose",
    )
    verbosity_args.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="give a minimal report (console output only)",
        dest="quiet",
    )

    parser.add_argument(
        "-cat", "--restrict-cat", type=str, help="e.g. -cat gpu_op", dest="category"
    )
    parser.add_argument(
        "--no-uniques",
        action="store_true",
        help="disallow collapsing items of the same name into one entry",
        dest="nu",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    args = parser.parse_args()

    input_file_count = len(
        args.files
    )  # argparse will ensure at least one file is given

    output_verbosity = Verbosity.STANDARD
    if args.verbose:
        output_verbosity = Verbosity.VERBOSE
    elif args.quiet:
        output_verbosity = Verbosity.QUIET

    # no analyzer (or all) specified -> find best analyzer given the input file count
    if (not args.a) or args.full_analysis:
        if input_file_count == 1:
            # only hotspots can be run on 1 file (for now?)
            args.a = "pops"
        elif input_file_count == 2 and not args.full_analysis:
            # default to hotspots + kernel differences unless user specified all
            args.a = "pops+kdiff"
        else:
            # default to all analyzers
            args.a = "all"

    if args.o or args.ot:  # file specified -> don't print to console
        if not args.o:
            args.o = "result"
        else:
            args.ot = "xlsx"
    else:
        args.o = ""
        args.ot = "console"

    if args.nu:
        print(
            "!!! - WARNING - !!!\nIf using large input files in conjunction with --no-uniques,\npopcorn may degrade in performance and even crash!"
        )

    # extract cases from json files
    cases = []
    reader = (
        LevelZeroTracerJsonReader()
    )  # TODO: add more input file formats? and add 'input_type' option to control manually? and autodetect?
    for input_filename in args.files:
        cases.append(
            Case(
                file=input_filename,
                reader=reader,
                uniques=(not args.nu),
                cat=args.category,
            )
        )

    # match analyzer and save its report
    match args.ot:
        case "xlsx":
            args.o = args.o + "." + args.ot
            report = Workbook()
        case "console":
            report = Kettle(output_verbosity)
        case "csv":
            report = CSVArchive()
        case "md":
            args.o = args.o + "." + args.ot
            report = MDTables()
        case _:
            # default to console output
            report = Kettle()

    match args.a:
        case "all":
            report_hotspots(hotspots(cases), report)
            report_kdiff(kernel_differences(cases), report)
        case "kdiff":
            report_kdiff(kernel_differences(cases), report)
        case "pops+kdiff":
            report_hotspots(hotspots(cases), report)
            report_kdiff(kernel_differences(cases), report)
        case "pops":
            report_hotspots(hotspots(cases), report)
        case _:  # default is just hotspots
            report_hotspots(hotspots(cases), report)

    report.save(args.o)
    return None


if __name__ == "__main__":
    sys.exit(main_cli())
