"""Provides a module for generating PyFluent API RST files."""

from pathlib import Path
import shutil


def _get_folder_path(folder_name: str):
    """Get folder path.

    Parameters
    ----------
    folder_name: str
        Name of the folder.

    Returns
    -------
        Path of the folder.
    """
    return (Path(__file__) / ".." / "source" / "api" / folder_name).resolve()


def _get_file_path(folder_name: str, file_name: str):
    """Get file path.

    Parameters
    ----------
    folder_name: str
        Name of the folder.

    file_name: str
        Name of the file.

    Returns
    -------
        Path of the file.
    """
    return (
        Path(__file__) / ".." / "source" / "api" / folder_name / f"{file_name}.rst"
    ).resolve()


hierarchy = {
    "visualization": [
        "Mesh",
        "Murface",
        "Montour",
        "Mector",
        "Mathline",
        "XYPlot",
        "Monitor",
        "GraphicsWindow",
    ],
}


def _write_common_rst_members(rst_file):
    rst_file.write("    :members:\n")
    rst_file.write("    :show-inheritance:\n")
    rst_file.write("    :undoc-members:\n")
    rst_file.write("    :exclude-members: __weakref__, __dict__\n")
    rst_file.write("    :special-members: __init__\n")
    rst_file.write("    :autosummary:\n")


def _generate_api_source_rst_files(folder: str, files: list):
    for file in files:
        if file.endswith("_contents"):
            pass
        else:
            if folder:
                rst_file = _get_file_path(folder, file)
            else:
                rst_file = _get_file_path("", file)
            with open(rst_file, "w", encoding="utf8") as rst:
                rst.write(f".. _ref_{file}:\n\n")
                if folder:
                    rst.write(f"{file}\n")
                    rst.write(f'{"="*(len(f"{file}"))}\n\n')
                    rst.write(f".. automodule:: ansys.fluent.visualization.{folder}.{file}\n")
                else:
                    rst.write(f"{file}\n")
                    rst.write(f'{"="*(len(f"{file}"))}\n\n')
                    rst.write(f".. automodule:: ansys.fluent.visualization.{file}\n")
                _write_common_rst_members(rst_file=rst)


def _generate_api_index_rst_files():
    for folder, files in hierarchy.items():
        if Path(_get_folder_path(folder)).is_dir():
            shutil.rmtree(_get_folder_path(folder))
        if folder == "other":
            _generate_api_source_rst_files(None, files)
        else:
            Path(_get_folder_path(folder)).mkdir(parents=True, exist_ok=True)
            folder_index = _get_file_path(folder, f"{folder}_contents")
            with open(folder_index, "w", encoding="utf8") as index:
                index.write(f".. _ref_{folder}:\n\n")
                index.write(f"{folder}\n")
                index.write(f'{"="*(len(f"{folder}"))}\n\n')
                index.write(f".. automodule:: ansys.fluent.visualization.{folder}\n")
                _write_common_rst_members(rst_file=index)
                index.write(".. toctree::\n")
                index.write("    :maxdepth: 2\n")
                index.write("    :hidden:\n\n")
                for file in files:
                    index.write(f"    {file}\n")
                index.write("\n")
            _generate_api_source_rst_files(folder, files)


if __name__ == "__main__":
    _generate_api_index_rst_files()
