from typing import Callable
from openpyxl import Workbook

from popcorn.interfaces import Kettle, MDTables, CSVArchive
from popcorn.structures import Event


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
):
    items = list(result.items())
    if isinstance(wb, Kettle):
        for item in items:
            wb.print_table(
                title=sheetnamefn(item[0]),
                fields=header,
                data=[
                    _ensure_console_text_fits(keyrowfn(event_row))
                    for event_row in item[1]
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
    result: dict[str, list[Event]], wb: Kettle | MDTables | Workbook | CSVArchive
):
    hotspot_header = Event.header()
    _report(result, hotspot_header, lambda e: e.row(), _hotspots_sheet_name, wb)


def _kernel_differences_sheet_name(item_name: str) -> str:
    return str("kdiff__" + item_name)


def report_kdiff(
    result: dict[str, list[tuple[Event, int]]],
    wb: Kettle | MDTables | Workbook | CSVArchive,
):
    kdiff_header = ["diff"] + Event.header()
    _report(
        result,
        kdiff_header,
        lambda eventdiff: ([str(eventdiff[1])] + eventdiff[0].row()),
        _kernel_differences_sheet_name,
        wb,
    )
