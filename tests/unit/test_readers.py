from hypothesis import given, strategies as st

from popcorn.readers import _getv


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