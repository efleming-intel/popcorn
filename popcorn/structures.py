from abc import ABC, abstractmethod
import os


class Event:
    def __init__(
        self,
        ph="",
        tid=-1,
        pid=-1,
        name="N/A",
        cat="N/A",
        ts=0,
        id=-1,
        dur=0,
        args_id=-1,
    ):
        self.ph = ph
        self.tid = tid
        self.pid = pid
        self.name = name
        self.cat = cat
        self.ts = ts
        self.id = id
        self.dur = dur
        self.args_id = args_id

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.name == other.name
        return False

    def row(self) -> list[str]:
        return [
            self.ph,
            str(self.tid),
            str(self.pid),
            self.name,
            self.cat,
            str(self.ts),
            str(self.id),
            str(self.dur),
            str(self.args_id),
        ]
    
    @staticmethod
    def header() -> list[str]:
        return ["ph", "tid", "pid", "name", "cat", "ts", "id", "dur", "args_id"]


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
