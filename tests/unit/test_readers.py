import os
from hypothesis import given, strategies as st

from popcorn.readers import _getv, LevelZeroTracerJsonReader


@given(
    item=st.dictionaries(
        st.text("abcdefghijklmnopqrstuvwxyz", min_size=1), st.integers(), min_size=1
    ),
    prop=st.text("abcdefghijklmnopqrstuvwxyz", min_size=1),
    default=st.integers(),
)
def test_getv(item: dict, prop: str, default: int):
    default_def_value = _getv({"test": 25}, "not_present")
    assert default_def_value == -1

    value = _getv(item, prop, default=default)
    if prop in item.keys():
        assert value == item[prop]
    else:
        assert value == default


# test LevelZeroTracerJsonReader
def test_event_creation_from_zetrace_json():
    item: dict = {
        "dur": 3459876,
        "ph": "X",
        "pid": 1,
        "name": "gen_conv",
        "cat": "gpu_op",
        "ts": 87612348765
    }
    null = {"nulltest": '\0'}
    reader = LevelZeroTracerJsonReader()
    event = reader.create_event_from_trace_item(item)
    null_event = reader.create_event_from_trace_item(null)

    assert event.dur == item["dur"] and null_event.dur == 0
    assert event.num_calls == 1 and null_event.num_calls == 1
    assert event.ph == item["ph"] and null_event.ph == "N/A"
    assert event.pid == item["pid"] and null_event.pid == -1
    assert event.name == item["name"] and null_event.name == "N/A"
    assert event.cat == item["cat"] and null_event.cat == "N/A"
    assert event.ts == item["ts"] and null_event.ts == -1


def test_event_retrieval_from_zetrace_json(tmp_path):
    input_json = '''
{
    "traceEvents": [
        { "ph": "r", "cat": "host_op", "name": "sys::open" },
        { "ph": "X", "cat": "gpu_op", "name": "gen_conv", "dur": 543234 },
        { "ph": "X", "cat": "gpu_op", "name": "eigen::sub", "dur": 732 },
        { "ph": "X", "cat": "gpu_op", "name": "eigen::sub", "dur": 321 },
        { "id": 1, "pid": 1 }
    ]
}
'''
    input_file_path = os.path.abspath(str(tmp_path) + "/test.tmp.json")
    with open(input_file_path, "w") as input_file:
        input_file.write(input_json)
    
    reader = LevelZeroTracerJsonReader()
    events = reader.read(input_file_path)
    events_gpu = reader.read(input_file_path, cat="gpu_op")
    events_nu = reader.read(input_file_path, uniques=False)

    assert len(events) == 4
    assert len(events_gpu) == 2
    assert len(events_nu) == 5

    eigen_name = "eigen::sub"
    assert events[2].name == eigen_name and (events[3].name == "N/A" and events[3].dur == 0)
    assert events_nu[2].name == eigen_name and events_nu[3].name == eigen_name
    assert events[2].dur == 1053 and events_nu[2].dur == 732
    assert events_gpu[1].name == eigen_name

    os.remove(input_file_path)