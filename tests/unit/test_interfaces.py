import os
from hypothesis import HealthCheck, given, settings, strategies as st

from popcorn.interfaces import MDTable, Verbosity, Kettle, _generate_markdown_header_line, _generate_markdown_row, _str2dash


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


# test markdown output
@given(s=st.text())
def test_str2dash(s: str):
    dash = _str2dash(s)
    assert len(s) == len(dash)
    for char in dash:
        assert char == '-'


@given(row=st.lists(st.text(st.characters(exclude_characters=[' ', '|']), min_size=1), min_size=1))
def test_header_generator(row: list[str]):
    header_line = _generate_markdown_header_line(row)
    if header_line != None:
        tags = header_line.split(" | ")

        assert len(tags) == len(row)
        for i in range(len(tags)):
            assert len(tags[i]) == len(row[i])
    else:
        assert len(row) == 0


@given(row=st.lists(st.text(st.characters(exclude_characters=[' ', '|', '\n']))))
def test_row_tablifier(row: list[str]):
    table_row = _generate_markdown_row(row)
    assert table_row.startswith('| ')
    assert table_row.endswith(' |\n')
    assert (" | ".join(row)) in table_row


def test_mdtable(tmp_path):
    test_path = str(tmp_path) + "/test"
    table = MDTable(test_path)
    assert table.filename == (str(tmp_path) + "/test.md")

    assert table.headerWritten == False
    table.append(["name", "date", "grade"])
    assert table.headerWritten == True
    with open(table.filename, "r") as file:
        lines = file.readlines()
        assert len(lines) == 2
        assert "| name | date | grade |\n" == lines[0]
        assert "| ---- | ---- | ----- |\n" == lines[1]

    table.append(["Lucy", "10/18/2023", 96])
    with open(table.filename, "r") as file:
        lines = file.readlines()
        assert len(lines) == 3
        assert "| name | date | grade |\n" == lines[0]
        assert "| ---- | ---- | ----- |\n" == lines[1]
        assert "| Lucy | 10/18/2023 | 96 |\n" == lines[2]
    
    os.remove(table.filename)