from json import load as load_json

from popcorn.structures import Event, Reader


class UnitraceJsonReader(Reader):
    def __init__(self):
        super().__init__(format="json")

    def create_event_from_trace_item(self, item) -> Event:
        event = Event()
        event.ph = item["ph"] if ("ph" in item.keys()) else "N/A"
        event.tid = item["tid"] if ("tid" in item.keys()) else -1
        event.pid = item["pid"] if ("pid" in item.keys()) else -1
        event.name = item["name"] if ("name" in item.keys()) else "N/A"
        event.cat = item["cat"] if ("cat" in item.keys()) else "N/A"
        event.ts = item["ts"] if ("ts" in item.keys()) else -1
        event.id = item["id"] if ("id" in item.keys()) else -1
        event.dur = item["dur"] if ("dur" in item.keys()) else 0
        event.args_id = (
            item["args"]["id"]
            if (("args" in item.keys()) and ("id" in item["args"].keys()))
            else -1
        )
        return event

    def read(self, filename: str, uniques: bool, cat: str | None) -> list[Event]:
        if uniques:
            unique_events: dict[str, Event] = {}

            with open(filename, "r") as f:
                data = load_json(f)
                for item in data["traceEvents"]:
                    same_category = (item["cat"] == cat) if ("cat" in item.keys()) else False
                    if (cat and same_category) or (not cat):  # category specific search
                        if item["name"] in unique_events:  # collapse uniques duration
                            if ("dur" in item.keys()):
                                unique_events[item["name"]].dur += item["dur"]
                        else:
                            unique_events[
                                item["name"]
                            ] = self.create_event_from_trace_item(item)

            return list(unique_events.values())
        else:
            trace_events: list[Event] = []

            with open(filename, "r") as f:
                data = load_json(f)
                for item in data["traceEvents"]:
                    same_category = (item["cat"] == cat) if ("cat" in item.keys()) else False
                    if (cat and same_category) or (not cat):  # category specific search
                        trace_events.append(self.create_event_from_trace_item(item))

            return trace_events
