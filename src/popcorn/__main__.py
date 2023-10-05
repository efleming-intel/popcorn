#!/usr/bin/env python
"""
Popcorn, a kernel analyzer tool.

Args:
    files: A list of json trace file names.
"""

import argparse
from openpyxl import Workbook

from popcorn import __version__
from popcorn.analyzers import hotspots, kernel_differences
from popcorn.reporters import report_hotspots, report_kdiffs
from popcorn.structures import Case

def main_cli() -> str | None:
    # prepare console interface arguments
    parser = argparse.ArgumentParser(prog="popcorn", description='analyze kernel hotspots to solve problems like performance regression')

    parser.add_argument('files', nargs='+', type=str, help='input json trace files (provide at least one)')

    parser.add_argument('-o', '--output', type=str, help='output file name (default: "result")', dest='o')

    analyzer_args = parser.add_mutually_exclusive_group()
    analyzer_args.add_argument('-a', '--analyzer', type=str, choices=['pops', 'kdiff'], help='pops - hotspots; kdiff - kernel differences', dest='a')
    analyzer_args.add_argument('-A', '--full-analysis', action='store_true', dest='full_analysis', help='Use all possible analyzers on the files provided.')

    parser.add_argument('-cat', '--restrict-cat', type=str, help='e.g. -cat gpu_op', dest='category')
    parser.add_argument('--no-uniques', action='store_true', help='disallow collapsing items of the same name into one entry', dest='nu')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {version}'.format(version=__version__))

    args = parser.parse_args()

    input_file_count = len(args.files) # argparse will ensure at least one file is given
    args.full_analysis = (('full_analysis' in args) and args.full_analysis)
    # no analyzer (or all) specified -> find best analyzer given the input file count
    if (not args.a) or args.full_analysis:
        if input_file_count == 1:
            # only hotspots can be run on 1 file (for now?)
            args.a = 'pops'
        elif input_file_count == 2 and not args.full_analysis:
            # default to hotspots + kernel differences unless user specified all
            args.a = 'pops+kdiff'
        else:
            # default to all analyzers
            args.a = 'all'

    args.o = args.o if not args.o == None else 'result'
    args.nu = args.nu if 'nu' in args else False
    args.category = args.category if 'category' in args else None

    # extract cases from json files
    cases = []
    for file in args.files:
        cases.append(Case(file, not args.nu, args.category))

    # match analyzer and save its report
    args.o = args.o + ".xlsx" # output is an excel file
    report = Workbook()
    match args.a:
        case 'all':
            report_hotspots(hotspots(cases), report)
            report_kdiffs(kernel_differences(cases), report)
        case 'kdiff':
            report_kdiffs(kernel_differences(cases), report)
        case 'pops+kdiff':
            report_hotspots(hotspots(cases), report)
            report_kdiffs(kernel_differences(cases), report)
        case 'pops':
            report_hotspots(hotspots(cases), report)
        case _: # default is just hotspots
            report_hotspots(hotspots(cases), report)
    report.save(args.o)
    return None