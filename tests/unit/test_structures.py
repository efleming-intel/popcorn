from popcorn.structures import Event
from tests.unit.common_utils import prep_mock_case


# test Event
def test_initialized_event_defaults():
    event = Event()
    assert event.dur == 0
    assert event.num_calls == 1
    assert event.ph == ""
    assert event.pid == -1
    assert event.name == "N/A"
    assert event.cat == "N/A"
    assert event.ts == 0


def test_event_equivalence():
    event = Event(name="test", dur=1234)
    other = Event(name="test", dur=654)
    another = Event(name="other")

    assert event == other and event != event.row()
    assert event != another


def test_event_row():
    event_dict: dict[str, str | int] = {
        "dur": 3459876,
        "ph": "X",
        "pid": 1,
        "name": "gen_conv",
        "cat": "gpu_op",
        "ts": 87612348765
    }
    event = Event()
    for prop in event_dict.keys():
        setattr(event, prop, event_dict[prop])
    
    result_row = event.row()

    expected_vals = list(event_dict.values())

    for s in result_row:
        s = int(s) if s.isdigit() else str(s)
        assert s in expected_vals
    for s in expected_vals:
        assert str(s) in result_row


def test_event_header():
    expected_header = [
            "dur",
            "calls",
            "ph",
            "pid",
            "name",
            "category",
            "timestamp"
        ]
    expected_kdiff_header = [
            "diff",
            "name",
            "cat"
        ]
    actual_header = Event.header()
    actual_kdiff_header = Event.kdiff_header()

    for s in expected_header:
        assert s in actual_header
    for s in actual_header:
        assert s in expected_header

    for s in expected_kdiff_header:
        assert s in actual_kdiff_header
    for s in actual_kdiff_header:
        assert s in expected_kdiff_header


# test Case
def test_case_equivalence():
    case1 = prep_mock_case(
        "mnt/c/testing/filename.json",
        [Event(name="test1", dur=98), Event(name="test2", dur=27)]
    )
    case2 = prep_mock_case(
        "mnt/c/testing/filename.json",
        [Event(name="test3", dur=89), Event(name="test4", dur=72)]
    )
    case3 = prep_mock_case(
        "filename.json",
        [Event(name="test3", dur=27), Event(name="test4", dur=89)]
    )
    case4 = prep_mock_case(
        "other.json",
        [Event(name="test3", dur=27), Event(name="test4", dur=89)]
    )

    assert (case1 == case2) and (case2 == case3)
    assert case3 != case4


def test_case_string_indexing():
    case = prep_mock_case(
        "mnt/c/testing/filename.json",
        [Event(name="test1", dur=98), Event(name="test2", dur=27)]
    )

    assert case["test1"].dur == 98 and case["test2"].dur == 27
    assert case["test3"] == None


def test_case_title():
    case1 = prep_mock_case(
        "mnt/c/testing/filename.json",
        [Event(name="test1", dur=98), Event(name="test2", dur=27)]
    )
    case2 = prep_mock_case(
        "mnt/c/testing/filename.json",
        [Event(name="test1", dur=98), Event(name="test2", dur=27)],
        reader_format="json"
    )

    assert case1.title == "filename.json"
    assert case2.title == "filename"