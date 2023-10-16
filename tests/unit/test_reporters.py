import os
from pathlib import PosixPath
from random import randint
from hypothesis import HealthCheck, given, settings, strategies as st

from popcorn.interfaces import CSVArchive
from popcorn.reporters import report_hotspots, report_kdiff
from popcorn.structures import Event
from tests.unit.common_utils import generate_event_durs


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    trace_name=st.text("abcdefghijklmnop", min_size=1),
    event_names=st.sets(st.text("abcdefghijklmnop", min_size=1), min_size=1)
)
def test_hotspots_report(tmp_path: PosixPath, trace_name, event_names):
    event_names: list[str] = list(event_names)
    events = generate_event_durs(event_names)
    testWb = CSVArchive()
    report_hotspots({trace_name: events}, testWb)
    result_path = os.path.abspath(str(tmp_path) + "/" + "result")
    testWb.save(result_path)

    report_path = os.path.abspath(str(result_path) + "/pops__" + trace_name +".csv")
    assert os.path.exists(report_path)
    with open(report_path, "r") as output_file:
        output = output_file.readlines()
        assert output[0] == (",".join(Event.header()) + '\n')
        for event in events:
            assert (",".join(event.row()) + '\n') in output


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    trace_names=st.sets(st.text("abcdefghijklmnop", min_size=1), min_size=2, max_size=2),
    event_names=st.sets(st.text("abcdefghijklmnop", min_size=1), min_size=1)
)
def test_kernel_differences_report(tmp_path: PosixPath, trace_names, event_names):
    event_names: list[str] = list(event_names)
    events = generate_event_durs(event_names)
    events_dict: list[tuple[Event, int]] = []
    for event in events:
        events_dict.append((event, randint(-100000, 100000)))
    testWb = CSVArchive()

    mock_result_name = "_".join(trace_names)
    mock_result: dict[str, list[tuple[Event, int]]] = {mock_result_name: events_dict}

    report_kdiff(mock_result, testWb)
    result_path = os.path.abspath(str(tmp_path) + "/" + "result")
    testWb.save(result_path)

    report_path = os.path.abspath(str(result_path) + "/kdiff__" + mock_result_name +".csv")
    assert os.path.exists(report_path)
    with open(report_path, "r") as output_file:
        output = output_file.readlines()
        assert output[0] == ("diff," + ",".join(Event.header()) + '\n')
        for (event, diff) in events_dict:
            assert (str(diff) + "," + ",".join(event.row()) + '\n') in output