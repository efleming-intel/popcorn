from abc import ABC, abstractmethod
import os


class Event:
    def __init__(
        self,
        dur=0,
        num_calls=1,
        ph="",
        pid=-1,
        name="N/A",
        cat="N/A",
        ts=0,
    ):
        self.dur = dur
        self.num_calls = num_calls
        self.ph = ph
        self.pid = pid
        self.name = name
        self.cat = cat
        self.ts = ts

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.name == other.name
        return False

    def row(self) -> list[str]:
        return [
            str(self.dur),
            str(self.num_calls),
            self.ph,
            str(self.pid),
            self.name,
            self.cat,
            str(self.ts)
        ]
    
    def kdiff_row(self) -> list[str]:
        return [
            self.name,
            self.cat
        ]
    
    @staticmethod
    def header() -> list[str]:
        return [
            "dur",
            "# calls",
            "ph",
            "pid",
            "name",
            "category",
            "timestamp"
        ]
    
    @staticmethod
    def kdiff_header() -> list[str]:
        return [
            "diff",
            "name",
            "cat"
        ]


class Reader(ABC):
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
        if isinstance(other, Case):
            return self.filename == other.filename
        return False

    def __getitem__(self, event_name: str) -> Event | None:
        for e in self.events:
            if e.name == event_name:
                return e

        return None

    @property
    def title(self) -> str:
        return (
            self.filename.removesuffix(("." + self.reader.format))
            if self.reader.format
            else self.filename
        )
