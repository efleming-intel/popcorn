from abc import ABC, abstractmethod

class Event(ABC):
    def __init__(
        self,
        name="N/A",
        cat="N/A",
        ts=0,
        dur=0,
    ):

        self.name = name
        self.cat = cat
        self.ts = ts
        self.dur = dur


    def __eq__(self, other):
        if isinstance(other, BaseEvent):
            return self.name == other.name
        return False

    def row(self) -> list[str]:
        return [
            self.name,
            self.cat,
            str(self.ts),
            str(self.dur),]
            
    @abstractmethod
    def header() -> list[str]:
        raise NotImplementedError("Error header")
      


class OneDnnEvent(Event):
    def __init__(
        self,
        ph="",
        tid=-1,
        pid=-1,
        name="N/A",
        cat="N/A",
        kernel="N/A",
        shape="N/A",
        ts=0,
        dur=0,
        args=[],
    ):
        Event.__init__(self, name, cat, ts, dur) 
        self.ph = ph
        self.tid = tid
        self.pid = pid
        self.args = args
        self.shape = shape
        self.kernel = kernel


    def __eq__(self, other):
        if isinstance(other, OneDnnEvent):
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
            str(self.dur),
            self.args,
            str(self.shape),
            str(self.kernel),
        ]
    
    @staticmethod
    def header() -> list[str]:
        return ["ph", "tid", "pid", "name", "cat", "ts", "dur", "kernel", "shape", "args"]

class LevelZeroEvent(Event):
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
        Event.__init__(self, name, cat, ts, dur) 
        self.ph = ph
        self.tid = tid
        self.pid = pid
        self.cat = cat
        self.id = id
        self.args_id = args_id

    def __eq__(self, other):
        if isinstance(other, LevelZeroEvent):
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
