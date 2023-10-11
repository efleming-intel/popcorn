from random import randint
from hypothesis import given, strategies as st
import math
from unittest.mock import MagicMock

from popcorn.analyzers import hotspots, kernel_differences
from popcorn.readers import Reader
from popcorn.structures import Case, Event


def _prep_mock_case(
    name: str, events: list[Event], uniques: bool = True, category: str | None = None
) -> Case:
    reader = Reader()
    reader.create_event_from_trace_item = None
    reader.read = MagicMock(return_value=events)
    return Case(file=name, reader=reader, uniques=uniques, cat=category)


@given(
    cases_dict=st.dictionaries(
        st.text(min_size=1), st.lists(st.integers(min_value=0), min_size=1), min_size=1
    )
)
def test_hotspots(cases_dict: dict[str, list[int]]):
    cases = [
        _prep_mock_case(name=item[0], events=(Event(dur=d) for d in item[1])) for item in cases_dict.items()
    ]
    analysis = list(hotspots(cases).items())

    assert len(analysis) > 0
    for _, events in analysis:
        for i in range(len(events) - 1):
            assert events[i].dur >= events[i + 1].dur


@given(
    event_names = st.sets(st.text(st.characters(exclude_characters=['_']), min_size=2), min_size=3),
    case_names = st.sets(st.text(st.characters(exclude_characters=['_']), min_size=2), min_size=2)
)
def test_kernel_differences(
    event_names, case_names
):
    event_names: list[str] = list(event_names)
    case_names: list[str] = list(case_names)

    cases: list[Case] = []
    for case_name in case_names:
        events: list[Event] = []
        for event_name in event_names:
            events.append(Event(name=event_name, dur=randint(0, 100000)))
        cases.append(_prep_mock_case(case_name, events))

    analysis = list(kernel_differences(cases).items())

    assert len(analysis) == math.comb(len(cases), 2)
    for diff_name, events in analysis:
        term_match = diff_name.split('_')
        case_pair: list[Case] = []
        for c in cases:
            if c.title in term_match:
                case_pair.append(c)
                
        assert len(case_pair) == 2

        for i in range(len(events) - 1):
            (event, diff) = events[i]
            e_c1 = case_pair[0][event.name]
            e_c2 = case_pair[1][event.name]
            assert isinstance(e_c1, Event) and isinstance(e_c2, Event)
            assert (diff == e_c1.dur - e_c2.dur) or (diff == e_c2.dur - e_c1.dur)
