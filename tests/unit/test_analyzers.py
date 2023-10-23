from hypothesis import given, strategies as st
from math import comb as possible_combinations

from popcorn.analyzers import hotspots, kernel_differences
from popcorn.structures import Case, Event
from tests.unit.common_utils import generate_event_durs, prep_mock_case


def generate_cases_with_like_events(case_names: list[str], event_names: list[str]):
    cases: list[Case] = []
    for case_name in case_names:
        cases.append(prep_mock_case(
            case_name, generate_event_durs(event_names)
        ))
    return cases


@given(
    cases_dict=st.dictionaries(
        st.text(min_size=1), st.lists(st.integers(min_value=0), min_size=1), min_size=1
    )
)
def test_hotspots(cases_dict: dict[str, list[int]]):
    cases = [
        prep_mock_case(name=item[0], events=(Event(dur=d) for d in item[1])) for item in cases_dict.items()
    ]
    analysis = list(hotspots(cases).items())

    assert len(analysis) > 0
    for _, events in analysis:
        for i in range(len(events) - 1):
            assert events[i].dur >= events[i + 1].dur


@given(
    event_names = st.sets(st.text("abcdefghijklmnop", min_size=3), min_size=3),
    case_names = st.sets(st.text("qrstuvwxyz", min_size=3), min_size=2)
)
def test_kernel_differences(
    event_names, case_names
):
    event_names: list[str] = event_names
    case_names: list[str] = list(case_names)
    cases = generate_cases_with_like_events(case_names, event_names)

    analysis = list(kernel_differences(cases).items())

    assert len(analysis) == possible_combinations(len(cases), 2)
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
