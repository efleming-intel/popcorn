import os
import shutil
from hypothesis import HealthCheck, given, settings, strategies as st

from popcorn.interfaces import CSVArchive, CSVSheet, MDTable, MDTables, Verbosity, Kettle, _generate_markdown_header_line, _generate_markdown_row, _str2dash


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


# test markdown
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


def test_mdtables(tmp_path):
    mdtables = MDTables()
    test1_title = str(tmp_path) + "/first_test"
    test2_title = str(tmp_path) + "/second_test"

    sheet1 = mdtables.create_sheet(test1_title)
    sheet2 = mdtables.create_sheet(test2_title)

    test1_path = os.path.abspath(test1_title + ".md")
    test2_path = os.path.abspath(test1_title + ".md")
    assert os.path.exists(test1_path) and os.path.exists(test2_path)

    sheet1.append(["name", "date", "grade"])
    sheet1.append(["Lucy", "10/18/2023", 96])
    sheet2.append(["name", "salary", "class size"])
    sheet2.append(["Mary", "$10,000", 67])

    output_file = str(tmp_path) + "/result.md"
    mdtables.save(output_file)
    assert not(os.path.exists(test1_path) or os.path.exists(test2_path))
    assert os.path.exists(output_file)

    with open(output_file, "r") as file:
        lines = file.readlines()
        assert len(lines) == 21
        text = "".join(lines)
        assert output_file in text
        assert test1_title in text
        assert "| name | date | grade |\n" in text
        assert "| ---- | ---- | ----- |\n" in text
        assert "| Lucy | 10/18/2023 | 96 |\n" in text

        assert test2_title in text
        assert "| name | salary | class size |\n" in text
        assert "| ---- | ------ | ---------- |\n" in text
        assert "| Mary | $10,000 | 67 |\n" in text

    os.remove(output_file)


# test csv
def test_csvsheet(tmp_path):
    table = CSVSheet("test")
    assert table.filename == "test.csv"

    table.append(["name", "date", "grade"])
    table.append(["Lucy", "10/18/2023", 96])
    table.save(str(tmp_path))

    test_path = os.path.abspath(str(tmp_path) + "/" + table.filename)
    with open(test_path, "r") as file:
        lines = file.readlines()
        assert len(lines) == 2
        assert "name,date,grade\n" == lines[0]
        assert "Lucy,10/18/2023,96\n" == lines[1]
    
    os.remove(test_path)


def test_csvarchive(tmp_path):
    archive = CSVArchive()
    test1_title = "first_test"
    test2_title = "second_test"

    sheet1 = archive.create_sheet(test1_title)
    sheet1.append(["name", "date", "grade"])
    sheet1.append(["Lucy", "10/18/2023", 96])

    sheet2 = archive.create_sheet(test2_title)
    sheet2.append(["name", "salary", "class size"])
    sheet2.append(["Mary", "$10,000", 67])

    output_folder = str(tmp_path) + "/result"
    archive.save(output_folder)
    
    test1_path = os.path.abspath(output_folder + "/" + "first_test.csv")
    test2_path = os.path.abspath(output_folder + "/" + "second_test.csv")
    
    assert os.path.exists(output_folder)
    assert os.path.exists(test1_path) and os.path.exists(test2_path)

    shutil.rmtree(output_folder)