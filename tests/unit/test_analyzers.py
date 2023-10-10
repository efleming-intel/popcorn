from hypothesis import given, strategies as st
from unittest.mock import MagicMock

from popcorn.analyzers import hotspots, kernel_differences
from popcorn.readers import Reader
from popcorn.structures import Case, Event

def _prep_mock_case(name: str, events: list[Event], uniques: bool = True, category: str | None = None) -> Case:
    reader = Reader()
    reader.create_event_from_trace_item = None
    reader.read = MagicMock(return_value=events)
    return Case(file=name, reader=reader, uniques=uniques, cat=category)


@given(cases_dict=st.dictionaries(st.text(min_size=1), st.lists(st.from_type(Event)), min_size=1))
def test_hotspots(cases_dict: dict[str, list[Event]]):
    cases = [_prep_mock_case(name=item[0], events=item[1]) for item in cases_dict.items()]
    report = list(hotspots(cases).items())

    assert len(report) > 0
    for (_, events) in report:
        for i in range(len(events) - 1):
            assert events[i].dur >= events[i + 1].dur