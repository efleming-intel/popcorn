from itertools import repeat
import os

from prettytable import PrettyTable


# useful functions
def _str2dash(s: str) -> str:
    # returns a string of dashes the same length as s
    return "".join(list(repeat("-", len(s))))


def _generate_header_line(row: list[str]):
    tags = []
    for item in row:
        tags.append(_str2dash(item))
    return " | ".join(tags)


def _tablify_row(row: list[str]):
    return "| " + (" | ".join(str(i) for i in row)) + " |\n"


# default console interface
class Kettle:
    def print_table(self, title: str, fields: list[str], data: list[list[str]]):
        table = PrettyTable(title=title, field_names=fields)
        table._max_table_width = os.get_terminal_size().columns
        table.add_rows(data)
        print(table)
    
    def save(self, _):
        pass


# markdown interface
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
            file.write(_tablify_row(row))
            if not self.headerWritten:
                file.write("| " + _generate_header_line(row) + " |\n")
                self.headerWritten = True


class MDTables:
    def __init__(self):
        self._tables: list[MDTable] = []
        self._active_sheet_index = -1

    @property
    def active(self):
        try:
            return self._sheets[self._active_sheet_index]
        except IndexError:
            pass

    def create_sheet(self, title: str) -> MDTable:
        sheet = MDTable(title)
        self._tables.append(sheet)
        self._active_sheet_index += 1
        return sheet

    def save(self, filename: str):
        # combine temp sheets into one markdown file
        if len(self._sheets) > 0:
            with open(filename, "w") as file:
                for table in self._tables:
                    with open(table.filename, "r") as temp:
                        file.write("## " + table.title + "\n")
                        file.writelines(temp.readlines())
                        file.write("\n\n")
                    os.remove(table.filename)  # delete temp file


# csv interfaces
class CSVSheet:
    def __init__(self, title: str):
        self.title = title
        open(self.filename, "w").close()  # prep file

    @property
    def filename(self):
        return self.title + ".csv"

    def append(self, row: list[str]):
        with open(self.filename, "a") as file:
            file.write(",".join(row) + "\n")


class CSVArchive:
    def __init__(self):
        self._sheets = []
        self._active_sheet_index = -1

    @property
    def active(self):
        try:
            return self._sheets[self._active_sheet_index]
        except IndexError:
            pass

    def create_sheet(self, title: str) -> CSVSheet:
        sheet = CSVSheet(title)
        self._sheets.append(sheet)
        self._active_sheet_index += 1
        return sheet

    def save(self, foldername: str):
        if len(self._sheets) > 0:
            # make a folder then move the sheets into it
            folder_path = os.path.abspath(foldername)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            for sheet in self._sheets:
                os.replace(
                    os.path.abspath(sheet.filename), folder_path + "/" + sheet.filename
                )
