import os
import shutil
from unittest.mock import patch
import pytest

from popcorn.__main__ import main_cli
from popcorn.reporters import _hotspots_sheet_name, _kernel_differences_sheet_name

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


def test_error_when_arg_not_passed(tmp_path):
    testargs = ["popcorn", str(tmp_path)]
    with pytest.raises(IsADirectoryError):
        with patch("sys.argv", testargs):
            main_cli()
    

def test_error_when_no_files_found(tmp_path):
    testargs = ["popcorn", "-f", str(tmp_path)]
    with patch("sys.argv", testargs):
        error = main_cli()
        assert error.startswith("Error!") and str(tmp_path) in error


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_folder_input(request, tmp_path):
    # for unknown reasons, this test stopped working in Github Actions
    inputdir = str(os.path.dirname(request.fspath)) + "/data/"
    input_files = [str(inputdir + "trace1.json"), str(inputdir + "trace0.json")]
    output = tmp_path / "result"

    testargs = ["popcorn", "-f", inputdir, "-ot", "csv", "-o", str(output)]

    with patch("sys.argv", testargs):
        errors = main_cli()
        assert errors == None

    assert os.path.exists(output)
    
    expected_result_names = [
        _hotspots_sheet_name(os.path.basename(input_files[0]).removesuffix(".json")),
        _hotspots_sheet_name(os.path.basename(input_files[1]).removesuffix(".json")),
        _kernel_differences_sheet_name(
            f"{os.path.basename(input_files[0]).removesuffix('.json')}_{os.path.basename(input_files[1]).removesuffix('.json')}"
        )
    ]
    expected_result_files = [
        (output / f"{name}.csv") for name in expected_result_names
    ]

    for expected_file in expected_result_files:
        assert os.path.exists(expected_file)

    shutil.rmtree(output)