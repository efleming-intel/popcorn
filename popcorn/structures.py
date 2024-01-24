from popcorn.events import Event
from abc import ABC, abstractmethod
import os



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


    def getfirstitem(self) -> Event | None:
        if(len(self.events) > 0):
            return self.events[0] if (self.events[0] != None) else None
        
        return None


    @property
    def title(self) -> str:
        return (
            self.filename.removesuffix(("." + self.reader.format))
            if self.reader.format
            else self.filename
        )
