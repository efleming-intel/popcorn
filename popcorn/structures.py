from abc import abstractmethod
from dataclasses import dataclass
import os


def _add_quotes(s: str) -> str:
    return '"' + s + '"'


@dataclass
class Event:
    ph: str
    tid: int
    pid: int
    name: str
    cat: str
    ts: int
    id: int
    dur: int
    args_id: int

    def __eq__(self, other):
        return self.name == other.name

    def row(self, trunc_name=False) -> list[str]:
        return [
            self.ph,
            self.tid,
            self.pid,
            _add_quotes(self.name if not trunc_name else self.name[0:25]),
            self.cat,
            self.ts,
            self.id,
            self.dur,
            self.args_id,
        ]


class Reader:
    def __init__(self, format: str | None = None):
        self._file_format = format

    @property
    def format(self) -> str:
        return self._file_format

    @abstractmethod
    def create_event_from_trace_item(self, item) -> Event:
        ...

    @abstractmethod
    def read(self, filename: str, uniques: bool, cat: str | None) -> list[Event]:
        ...


class Case:
    def __init__(self, file, reader: Reader, uniques=True, cat=None):
        self.filename: str = os.path.basename(file)
        self.reader = reader
        self.events: list[Event] = self.reader.read(file, uniques, cat)

    def __eq__(self, other):
        return self.filename == other.filename

    @property
    def title(self) -> str:
        return (
            self.filename.removesuffix(("." + self.reader.format))
            if self.reader.format
            else self.filename
        )
