from hypothesis import HealthCheck, given, settings, strategies as st

from popcorn.interfaces import (
    _str2dash,
    _generate_header_line,
    _tablify_row,
    Verbosity,
    Kettle,
)


@given(s=st.text())
def test_str2dash(s: str):
    dash = _str2dash(s)
    assert len(s) == len(dash)
    for char in dash:
        assert char == "-"


@given(row=st.lists(st.text(st.characters(exclude_characters=[" ", "|"]))))
def test_header_generator(row: list[str]):
    header_line = _generate_header_line(row)
    if header_line != None:
        tags = header_line.split(" | ")

        assert len(tags) == len(row)
        for i in range(len(tags)):
            assert len(tags[i]) == len(row[i])
    else:
        assert len(row) == 0


@given(row=st.lists(st.text(st.characters(exclude_characters=[" ", "|", "\n"]))))
def test_row_tablifier(row: list[str]):
    table_row = _tablify_row(row)
    assert table_row.startswith("| ")
    assert table_row.endswith(" |\n")
    assert (" | ".join(row)) in table_row


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
def test_kettle(verbosity: Verbosity, fields: list[str], data: list[list[str]]):
    title = "!!! - TITLE - !!!"
    kettle = Kettle(verbosity)
    table = kettle.print_table(title, fields, data)

    assert table.title == title
    for f in fields:
        assert f in table.field_names
    
    data_which_should_be_displayed: list[list[str]] = []
    match verbosity:
        case Verbosity.VERBOSE:
            data_which_should_be_displayed = data
        case _:
            limit = verbosity.item_limit
            if (limit <= 0) or (len(data) <= (2 * limit)):
                data_which_should_be_displayed = data
            else:
                data_which_should_be_displayed.extend(data[:limit] + data[-limit:])
    
    for d in data_which_should_be_displayed:
        assert d in table.rows