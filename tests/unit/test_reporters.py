import os
from pathlib import PosixPath
from hypothesis import HealthCheck, given, settings, strategies as st

from popcorn.interfaces import CSVArchive
from popcorn.reporters import report_hotspots, report_kdiff
from popcorn.structures import Event
from tests.unit.common_utils import generate_event_durs
from tests.unit.test_analyzers import generate_cases_with_like_events, prep_mock_case


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    trace_name=st.text("abcdefghijklmnop", min_size=1),
    event_names=st.sets(st.text("abcdefghijklmnop", min_size=1), min_size=1)
)
def test_hotspots_report(tmp_path: PosixPath, trace_name: str, event_names: list[str]):
    event_names: list[str] = list(event_names)
    events = generate_event_durs(event_names)
    trace = prep_mock_case(trace_name, events)
    testWb = CSVArchive()
    report_hotspots([trace], testWb)
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
    cases = generate_cases_with_like_events(list(trace_names), list(event_names))
    testWb = CSVArchive()

    report_kdiff(cases, testWb)
    result_path = os.path.abspath(str(tmp_path) + "/" + "result")
    testWb.save(result_path)

    mock_result_name = "_".join(trace_names)

    report_path = os.path.abspath(str(result_path) + "/kdiff__" + mock_result_name +".csv")
    assert os.path.exists(report_path)
    with open(report_path, "r") as output_file:
        output = output_file.readlines()
        assert len(output) == (len(event_names) + 1)
        assert output[0] == ("diff," + ",".join(Event.header()) + '\n')
