from hypothesis import given, strategies as st

from popcorn.interfaces import _str2dash, _generate_header_line, _tablify_row


# test helper functions
@given(s=st.text())
def test_str2dash(s: str):
    dash = _str2dash(s)
    assert len(s) == len(dash)
    for char in dash:
        assert char == '-'


@given(row=st.lists(st.text(st.characters(exclude_characters=[' ', '|']))))
def test_header_generator(row: list[str]):
    header_line = _generate_header_line(row)
    if header_line != None:
        tags = header_line.split(" | ")

        assert len(tags) == len(row)
        for i in range(len(tags)):
            assert len(tags[i]) == len(row[i])
    else:
        assert len(row) == 0


@given(row=st.lists(st.text(st.characters(exclude_characters=[' ', '|', '\n']))))
def test_row_tablifier(row: list[str]):
    table_row = _tablify_row(row)
    assert table_row.startswith('| ')
    assert table_row.endswith(' |\n')
    assert (" | ".join(row)) in table_row