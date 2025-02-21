import os
import streamlit as st
from openpyxl import Workbook

from popcorn.interfaces import Verbosity, Kettle, MDTables, CSVArchive
from popcorn.reporters import report_hotspots, report_kdiff
from popcorn.readers import UnitraceJsonReader
from popcorn.structures import Case

__version__ = "0.0.1"

def analyze_logs(
    files: list[str],
    folder_input: bool = False,
    output_type: str = "console",
    analyzer: str = None,
    full_analysis: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    category: str = None,
    no_uniques: bool = False,
):
    
    reader = UnitraceJsonReader()
    input_file_count = len(files)

    if input_file_count < 1:
        st.error("Error! No supported file(s) found in the provided input!")
        return

    output_verbosity = Verbosity.STANDARD
    if verbose:
        output_verbosity = Verbosity.VERBOSE
    elif quiet:
        output_verbosity = Verbosity.QUIET

    if not analyzer or full_analysis:
        if input_file_count == 1:
            analyzer = "pops"
        elif input_file_count == 2 and not full_analysis:
            analyzer = "pops+kdiff"
        else:
            analyzer = "all"

    output = ""

    if output_type == "console":
        output = ""
    else:
        output = "result" if not output else output
        if output_type in ["xlsx", "md"]:
            if not output.endswith("." + output_type):
                output = output + "." + output_type

    match output_type:
        case "xlsx":
            report = Workbook()
        case "console":
            report = Kettle(output_verbosity)
        case "csv":
            report = CSVArchive()
        case "md":
            report = MDTables()
        case _:
            report = Kettle(output_verbosity)

    cases: list[Case] = []
    for input_filename in files:
        cases.append(
            Case(
                file=input_filename,
                reader=reader,
                uniques=(not no_uniques),
                cat=category,
            )
        )

    match analyzer:
        case "all":
            report_hotspots(cases, report)
            report_kdiff(cases, report)
        case "kdiff":
            report_kdiff(cases, report)
        case "pops+kdiff":
            report_hotspots(cases, report)
            report_kdiff(cases, report)
        case "pops":
            report_hotspots(cases, report)
        case _:
            report_hotspots(cases, report)

    report.save(output)

    if output_type == "console":
        note = (
            "\nNote: When popcorn outputs to console, it truncates the names to display the table neatly."
            "\nFor the most verbose results, please output to a file.\n"
        )
        st.info(note)
    else:
        st.success(f"Results saved to file: {output}")
    
    return output

def main():
    st.title("Web Popcorn Analysis")
    st.write("Analyze kernel hotspots to solve performance regressions")

    # Checkbox to decide whether to use one file or two files
    use_two_files = st.checkbox("Use two files for analysis")

    uploaded_files = st.file_uploader("Upload trace files", accept_multiple_files=True)
    temp_files = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            temp_file_path = os.path.join("/tmp", uploaded_file.name)
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_file.getbuffer())
            temp_files.append(temp_file_path)

    if use_two_files and len(uploaded_files) != 2:
        st.error("Please upload exactly two files for analysis.")
        return
    elif not use_two_files and len(uploaded_files) != 1:
        st.error("Please upload exactly one file for analysis.")
        return

    if st.button("Analyze"):
        output = analyze_logs(
            files=temp_files,
            folder_input=False,
            output_type="md",
            analyzer="kdiff" if use_two_files else "pops",
            full_analysis=False,
            verbose=False,
            quiet=False,
            category=None,
            no_uniques=False,
        )

        with open(output, 'r') as md_file:
            markdown_content = md_file.readlines()
        
        top_30_lines = ''.join(markdown_content[6:26])
        st.markdown(top_30_lines)

        with open(output, 'rb') as file:
            btn = st.download_button(
                label="Download Markdown File",
                data=file,
                file_name=output,
                mime="text/markdown"
            )


if __name__ == "__main__":
    main()        
