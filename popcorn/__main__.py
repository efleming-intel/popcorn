#!/usr/bin/env python
"""
Popcorn, a kernel analyzer tool.

Args:
    files: A list of trace file names.
"""

import argparse
import os
from openpyxl import Workbook
import sys

from popcorn.interfaces import Verbosity, Kettle, MDTables, CSVArchive
from popcorn.reporters import report_hotspots, report_kdiff
from popcorn.readers import LevelZeroTracerJsonReader, OnednnTracerCsvReader
from popcorn.structures import Case

__version__ = "0.0.2"


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

    parser.add_argument("-f", "--folder", "--dir", "--directory",
        action="store_true",
        help="input name(s) reference(s) folder(s) and not file(s)",
        dest="folder_input",
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

    parser.add_argument(
        "-dnnl",
        action="store_true",
        help="parse onednn csv logs",
    )
    args = parser.parse_args()
    
    reader = (OnednnTracerCsvReader()) if (args.dnnl) else (LevelZeroTracerJsonReader())
    
    # TODO: add more input file formats? and add 'input_type' option to control manually? and autodetect?

    if args.folder_input:
        args.folders: list[str] = args.files
        args.files: list[str] = []
        for folder in args.folders:
            print(folder)
            if os.path.exists(os.path.abspath(folder)):
                supported_files: list[str] = []
                for (dirpath, _, filenames) in os.walk(folder):
                    supported_files.extend([
                        os.path.join(dirpath, filename) for filename in 
                        filter(lambda f: f.endswith(reader.format), filenames)
                    ])
                if len(supported_files) < 1 and len(args.folders) > 1:
                    print(f"Could not find any supported files within {folder}!\n")
                else:
                    args.files.extend(supported_files)
            else:
                print(f"{folder} does not exist!\n")
    
    input_file_count = len(args.files)
    # argparse will ensure args.files > 0 when input type isn't a folder
    if input_file_count < 1:
        # input was a foldername which had no supported files in it
        return f"Error! No supported file(s) found in {' or '.join(args.folders)}!\n"

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

    if not (args.o or args.ot):  # file specified -> don't print to console
        args.o = ""
        args.ot = "console"
    else:
        if not args.o:
            args.o = "result"
        if not args.ot:
            args.ot = "xlsx"

    if args.nu:
        print(
            "!!! - WARNING - !!!\nIf using large input files in conjunction with --no-uniques,\npopcorn may degrade in performance and even crash!"
        )

    # extract cases from json files
    cases: list[Case] = []
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
            report_hotspots(cases, report)
            report_kdiff(cases, report)
        case "kdiff":
            report_kdiff(cases, report)
        case "pops+kdiff":
            report_hotspots(cases, report)
            report_kdiff(cases, report)
        case "pops":
            report_hotspots(cases, report)
        case _:  # default is just hotspots
            report_hotspots(cases, report)

    report.save(args.o)
    return None


if __name__ == "__main__":
    sys.exit(main_cli())
