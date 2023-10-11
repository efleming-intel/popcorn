from openpyxl import Workbook

from popcorn.interfaces import Kettle, MDTables, CSVArchive
from popcorn.structures import Event


def _hotspots_sheet_name(item_name: str) -> str:
    return str("pops__" + item_name)


def _kernel_differences_sheet_name(item_name: str) -> str:
    return str("kdiff__" + item_name)


def report_hotspots(
    result: dict[str, list[Event]], wb: Kettle | MDTables | Workbook | CSVArchive
):
    items = list(result.items())
    hotspot_header = ["ph", "tid", "pid", "name", "cat", "ts", "id", "dur", "args_id"]
    if isinstance(wb, Kettle):
        for item in items:
            wb.print_table(
                title=_hotspots_sheet_name(item[0]),
                fields=hotspot_header,
                data=[event.row(trunc_name=True) for event in item[1]],
            )
            print("\n")
    else:
        count = len(items)
        if isinstance(wb, Workbook) and wb.active.title == "Sheet":
            # excel workaround
            ws = wb.active
            ws.title = _hotspots_sheet_name(items[0][0])
        else:
            ws = wb.create_sheet(_hotspots_sheet_name(items[0][0]))

        for i in range(0, count):
            ws.append(hotspot_header)  # header
            for event in items[i][1]:
                ws.append(event.row())
            if i < count - 1:
                ws = wb.create_sheet(_hotspots_sheet_name(items[i + 1][0]))


def report_kdiff(
    result: dict[str, list[tuple[Event, int]]],
    wb: Kettle | MDTables | Workbook | CSVArchive,
):
    items = list(result.items())
    kdiff_header = [
        "diff",
        "ph",
        "tid",
        "pid",
        "name",
        "cat",
        "ts",
        "id",
        "dur",
        "args_id",
    ]
    if isinstance(wb, Kettle):
        for item in items:
            wb.print_table(
                title=_kernel_differences_sheet_name(item[0]),
                fields=kdiff_header,
                data=[
                    ([str(diff)] + event.row(trunc_name=True)) for (event, diff) in item[1]
                ],
            )
            print("\n")
    else:
        count = len(items)
        if isinstance(wb, Workbook) and wb.active.title == "Sheet":  # current sheet is unused
            ws = wb.active
            ws.title = _kernel_differences_sheet_name(items[0][0])
        else:
            ws = wb.create_sheet(_kernel_differences_sheet_name(items[0][0]))

        for i in range(0, count):
            ws.append(kdiff_header)  # header
            for event, diff in items[i][1]:
                ws.append(([str(diff)] + event.row()))
            if i < count - 1:
                ws = wb.create_sheet(_kernel_differences_sheet_name(items[i + 1][0]))
