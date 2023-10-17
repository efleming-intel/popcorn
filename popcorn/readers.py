from json import load as load_json

from popcorn.structures import Event, Reader


def _getv(item: dict, prop: str, default: str | int | bool = -1) -> str | int | bool:
    return item[prop] if (prop in item.keys()) else default


class LevelZeroTracerJsonReader(Reader):
    def __init__(self):
        super().__init__(format="json")

    def create_event_from_trace_item(self, item) -> Event:
        event = Event()
        event.ph = _getv(item, "ph", default="N/A")
        event.tid = _getv(item, "tid")
        event.pid = _getv(item, "pid")
        event.name = _getv(item, "name", default="N/A")
        event.cat = _getv(item, "cat", default="N/A")
        event.ts = _getv(item, "ts")
        event.id = _getv(item, "id")
        event.dur = _getv(item, "dur", default=0)
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
                    item_category = _getv(item, "cat", default=False)
                    same_category = item_category and (item_category == cat)
                    if (
                        not cat
                    ) or same_category:  # no filter applied or category matches
                        if item["name"] in unique_events:  # collapse uniques duration
                            unique_events[item["name"]].dur += _getv(
                                item, "dur", default=0
                            )
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
                    item_category = _getv(item, "cat", default=False)
                    same_category = item_category and (item_category == cat)
                    if (
                        not cat
                    ) or same_category:  # no filter applied or category matches
                        trace_events.append(self.create_event_from_trace_item(item))

            return trace_events
