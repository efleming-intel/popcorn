from hypothesis import HealthCheck, given, settings, strategies as st

from popcorn.interfaces import (
    Verbosity,
    Kettle,
)


# test kettle
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    verbosity=st.from_type(Verbosity),
    fields=st.lists(
        st.text("abcdefghi", min_size=1, max_size=4),
        min_size=10,
        max_size=10,
        unique=True,
    ),
    data=st.lists(
        st.lists(
            st.text("1234567890", min_size=1, max_size=10),
            min_size=10,
            max_size=10,
            unique=True,
        ),
        min_size=1
    ),
)
def test_kettle(capfd, verbosity: Verbosity, fields: list[str], data: list[list[str]]):
    title = "!!! - TITLE - !!!"
    Kettle(verbosity).print_table(title, fields, data)
    table, err = capfd.readouterr()

    assert table and (not err)

    assert title in table
    for f in fields:
        assert f in table
    
    data_which_should_be_displayed: list[list[str]] = []
    limit = verbosity.limit
    if (limit > 0) and (len(data) > (2 * limit)):
        data_which_should_be_displayed.extend(data[:limit] + data[-limit:])
    else:
        data_which_should_be_displayed = data
    
    for row in data_which_should_be_displayed:
        for s in row:
            assert s in table
