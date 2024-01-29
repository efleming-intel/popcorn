from typing import Callable
from openpyxl import Workbook

from popcorn.analyzers import hotspots, kernel_differences
from popcorn.interfaces import Kettle, MDTables, CSVArchive, Verbosity
from popcorn.structures import Case



def _ensure_console_text_fits(row: list[str]) -> list[str]:
    trunc_limit = 25
    for i in range(len(row)):
        if (not str(row[i]).isdigit()) and (len(str(row[i])) > trunc_limit):
            row[i] = row[i][:trunc_limit]
    return row


def _report(
    result: dict[str, list],
    header: list[str],
    keyrowfn: Callable[..., list[str]],
    sheetnamefn: Callable[[str], str],
    wb: Kettle | MDTables | Workbook | CSVArchive,
    case_count: list[int]
):
    items = list(result.items())
    if isinstance(wb, Kettle):
        for i in range(len(items)):
            if wb.verbosity == Verbosity.VERBOSE:
                print(f"Displaying all {case_count[i]} items:")
            else:
                print(f"Displaying the most interesting {2 * wb.verbosity.limit} items out of {case_count[i]}:")

            wb.print_table(
                title=sheetnamefn(items[i][0]),
                fields=header,
                data=[
                    _ensure_console_text_fits(keyrowfn(event_row))
                    for event_row in items[i][1]
                ],
            )
            print("\n")
    else:
        count = len(items)
        if (
            isinstance(wb, Workbook) and wb.active.title == "Sheet"
        ):  # current sheet is unused
            ws = wb.active
            ws.title = sheetnamefn(items[0][0])
        else:
            ws = wb.create_sheet(sheetnamefn(items[0][0]))

        for i in range(0, count):
            ws.append(header)  # header
            for eventrow in items[i][1]:
                ws.append(keyrowfn(eventrow))
            if i < count - 1:
                ws = wb.create_sheet(sheetnamefn(items[i + 1][0]))


def _hotspots_sheet_name(item_name: str) -> str:
    return str("pops__" + item_name)


def report_hotspots(
    cases: list[Case], wb: Kettle | MDTables | Workbook | CSVArchive
):
    result = hotspots(cases)
    hotspot_first_event = cases[0].getfirstitem()

    if(hotspot_first_event is None):
        print("Warning: Hotspots empty, no events found")
        return
    hotspot_header = hotspot_first_event.header()

    _report(result, hotspot_header, lambda e: e.row(), _hotspots_sheet_name, wb, [len(case.events) for case in cases])


def _kernel_differences_sheet_name(item_name: str) -> str:
    return str("kdiff__" + item_name)


def report_kdiff(
    cases: list[Case],
    wb: Kettle | MDTables | Workbook | CSVArchive,
):
    result = kernel_differences(cases)

    hotspot_first_event = cases[0].getfirstitem()

    if(hotspot_first_event is None):
        print("Warning: Hotspots empty, no events found")
        return
    kdiff_header = ["diff"] + hotspot_first_event.header()

    _report(
        result,
        kdiff_header,
        lambda eventdiff: ([str(eventdiff[1])] + eventdiff[0].row()),
        _kernel_differences_sheet_name,
        wb,
        [len(case.events) for case in cases]
    )
