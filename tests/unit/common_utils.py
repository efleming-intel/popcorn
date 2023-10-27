from random import randint
from unittest.mock import MagicMock


from popcorn.structures import Case, Event, Reader


def generate_event_durs(event_names: list[str]) -> list[Event]:
    events: list[Event] = []
    for event_name in event_names:
        events.append(Event(name=event_name, dur=randint(0, 100000)))
    return events


class MockReader(Reader):
    def create_event_from_trace_item(self, _) -> Event:
        return None
    def read(self, _: str, __: bool, ___: str | None) -> list[Event]:
        return None # to be mocked
    

def prep_mock_case(
    name: str,
    events: list[Event],
    uniques: bool = True,
    category: str | None = None,
    reader_format: str | None = None
) -> Case:
    reader = MockReader(reader_format)
    reader.create_event_from_trace_item = None
    reader.read = MagicMock(return_value=events)
    return Case(file=name, reader=reader, uniques=uniques, cat=category)


def generate_cases_with_like_events(case_names: list[str], event_names: list[str]):
    cases: list[Case] = []
    for case_name in case_names:
        cases.append(prep_mock_case(
            case_name, generate_event_durs(event_names)
        ))
    return cases