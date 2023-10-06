from dataclasses import dataclass
import json
import os

def _add_quotes(s: str) -> str:
    return ('\"'+s+'\"')

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

    def __init__(self):
        self.ph = "N/A"
        self.tid = -1
        self.pid = -1
        self.name = "N/A"
        self.cat = "N/A"
        self.ts = -1
        self.id = -1
        self.dur = 0
        self.args_id = -1

    def __eq__(self, other):
        return self.name == other.name

    def row(self, trunc_name = False) -> list[str]:
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


class Case:
    def __init__(self, file, uniques=True, cat=None):
        self.filename : str = os.path.basename(file)

        trace_events: dict[str, Event] = {}

        with open(file, "r") as f:
            data = json.load(f)
            for item in data["traceEvents"]:
                same_category = (item["cat"] == cat) if "cat" in item else False
                if (cat and same_category) or (not cat):  # category specific search
                    if uniques and (
                        item["name"] in trace_events and "dur" in item
                    ):  # collapse uniques duration
                        trace_events[item["name"]].dur += item["dur"]
                    else:
                        event = Event()
                        event.ph = item["ph"] if "ph" in item else "N/A"
                        event.tid = item["tid"] if "tid" in item else -1
                        event.pid = item["pid"] if "pid" in item else -1
                        event.name = item["name"] if "name" in item else "N/A"
                        event.cat = item["cat"] if "cat" in item else "N/A"
                        event.ts = item["ts"] if "ts" in item else -1
                        event.id = item["id"] if "id" in item else -1
                        event.dur = item["dur"] if "dur" in item else 0
                        event.args_id = (
                            item["args"]["id"]
                            if ("args" in item) and ("id" in "args")
                            else -1
                        )
                        trace_events[item["name"]] = event

        self.events = list(trace_events.values())

    def __eq__(self, other):
        return self.filename == other.filename
    
    @property
    def title(self) -> str:
        return self.filename.removesuffix('.json')
