from enum import Enum
from itertools import repeat
import os

from prettytable import PrettyTable, MARKDOWN


# default console interface
class Verbosity(Enum):
    STANDARD = 0
    VERBOSE = 1
    QUIET = 2

    @property
    def limit(self):
        match self:
            case Verbosity.STANDARD:
                return 25
            case Verbosity.QUIET:
                return 10
            case _:  # no limit
                return -1


class Kettle:
    def __init__(self, verbosity=Verbosity.STANDARD) -> None:
        self.verbosity = verbosity

    def print_table(self, title: str, fields: list[str], data: list[list[str]]):
        table = PrettyTable(title=title, field_names=fields)
        limit = self.verbosity.limit
        if (limit > 0) and (len(data) > (2 * limit)):
            table.add_rows(data[:limit] + data[-limit:])
        else:  # either verbose chosen or data is small
            table.add_rows(data)

        print(table)

    def save(self, _):
        pass


# TODO: add html output interface?
# markdown interface
def _str2dash(s: str) -> str:
    # returns a string of dashes the same length as s
    return "".join(list(repeat("-", len(s))))


def _generate_markdown_header_line(row: list[str]) -> str:
    tags = []
    for item in row:
        tags.append(_str2dash(item))
    return " | ".join(tags)


def _generate_markdown_row(row: list[str]) -> str:
    return "| " + (" | ".join(str(i) for i in row)) + " |\n"


class MDTable:
    def __init__(self, title: str):
        self.title = title
        self.headerWritten = False
        open(self.filename, "w").close()  # prep temp file

    @property
    def filename(self):
        return self.title + ".md"

    def append(self, row: list[str]):
        with open(self.filename, "a") as file:
            file.write(_generate_markdown_row(row))
            if not self.headerWritten:
                file.write("| " + _generate_markdown_header_line(row) + " |\n")
                self.headerWritten = True


class MDTables:
    def __init__(self):
        self._tables: list[MDTable] = []

    def create_sheet(self, title: str) -> MDTable:
        sheet = MDTable(title)
        self._tables.append(sheet)
        return sheet

    def save(self, filename: str):
        # combine temp sheets into one markdown file
        if len(self._tables) > 0:
            with open(filename, "w") as out:
                # generate table of contents
                out.write("# " + filename + "\n\nContents:\n\n")
                for table in self._tables:
                    out.write('* [' + table.title + ']( #' + table.title + ' )\n')
                out.write('\n')
                # write data
                for table in self._tables:
                    with open(table.filename, "r") as temp:
                        out.write("## " + table.title + "\n")
                        out.writelines(temp.readlines())
                        out.write("\n\n")
                    os.remove(table.filename)  # delete temp file
                    out.write('\n')


# csv interfaces
class CSVSheet:
    def __init__(self, title: str):
        self.title = title
        self._table = PrettyTable(title=title)

    @property
    def filename(self):
        return self.title + ".csv"

    def append(self, row: list[str]):
        self._table.add_row(row)

    def save(self, folder_path: str):
        file_path = folder_path + "/" + self.filename
        with open(file_path, "w") as file:
            file.write(self._table.get_csv_string(header=False))


class CSVArchive:
    def __init__(self):
        self._sheets: list[CSVSheet] = []

    def create_sheet(self, title: str) -> CSVSheet:
        sheet = CSVSheet(title)
        self._sheets.append(sheet)
        return sheet

    def save(self, foldername: str):
        if len(self._sheets) > 0:
            # make a folder then save the sheets into it
            folder_path = os.path.abspath(foldername)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            for sheet in self._sheets:
                sheet.save(folder_path=folder_path)
