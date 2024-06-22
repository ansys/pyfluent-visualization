"""Module to display solution variables data."""

from enum import Enum
from typing import Callable, Optional, Union

from ansys.fluent.core.session_solver import Solver
import numpy as np
import pyvista as pv

from ansys.fluent.visualization.pyvista.pyvista_objects import (
    Graphics,
    pyvista_windows_manager,
)


class Format(Enum):
    DATA_ONLY = 1
    INDEX_AND_DATA = 2


def display_solution_variables_data(
    session: Solver,
    variables: list[str],
    zones: list[str],
    domain: Optional[str] = "mixture",
    format: Union[Format, Callable] = Format.INDEX_AND_DATA,
    precision: int = 2,
    font_size: int = 10,
    bold: bool = False,
) -> "Plotter":
    """Display solution variables data. The data is displayed as point labels
    on the centroid of mesh-elements of the specified zones.

    Parameters
    ----------
    session : Solver
        PyFluent solver session from which solution variables data will be fetched.
    variables : list[str]
        List of solution variable names. To see the list of available solution
        variable names, execute
        ``session.fields.solution_variable_info.get_variables_info(zones, domain).solution_variables``.  # noqa: E501
    zones : list[str]
        List of zone names.
    domain : str, optional
        Domain name, by default ``"mixture"``.
    format : Union[Format, Callable], optional
        How to format the data label, by default ``Format.INDEX_AND_DATA``.
        If a callable is provided, it should accept the index and the data as arguments.
    precision : int, optional
        Precision to show in the data label, by default 2.
    font_size : int, optional
        Font size of the data label, by default 10.
    bold : bool, optional
        Whether to show the data label in bold, by default False.

    Returns
    -------
    Plotter
        The PyVista plotter object.

    Examples
    --------
    Display pressure and temperature data of "inlet1".
    >>> display_solution_variables_data(session=session, variables=["SV_P", "SV_T"], zones=["inlet1"])  # noqa: E501
    Display pressure and temperature data of "inlet1" with custom format.
    >>> display_solution_variables_data(session=session, variables=["SV_P", "SV_T"], zones=["inlet1"], format=lambda i, x, y: f"{i}: {x:.2f}, {y:.2f}")  # noqa: E501
    """
    centroid_data = session.fields.solution_variable_data.get_data(
        solution_variable_name="SV_CENTROID", zone_names=zones, domain_name=domain
    )
    centroid_data = np.concatenate(list(centroid_data.data.values())).reshape(-1, 3)

    variables_data = []
    for variable in variables:
        variable_data = session.fields.solution_variable_data.get_data(
            solution_variable_name=variable, zone_names=zones, domain_name=domain
        )
        variable_data = np.concatenate(list(variable_data.data.values()))
        variables_data.append(variable_data.tolist())

    def format_fn(index, *data):
        if format == Format.DATA_ONLY:
            if len(data) == 1:
                return f"{data[0]:.{precision}f}"
            else:
                data_fmt = ", ".join(f"{d:.{precision}f}" for d in data)
                return f"({data_fmt})"
        elif format == Format.INDEX_AND_DATA:
            data_fmt = ", ".join(f"{d:.{precision}f}" for d in data)
            return f"({index}, {data_fmt})"
        elif callable(format):
            return format(index, *data)

    poly = pv.PolyData(centroid_data)
    poly["Pressure"] = [
        format_fn(index, *data) for index, data in enumerate(zip(*variables_data))
    ]
    graphics = Graphics(session=session)
    mesh_name = graphics.Meshes.Create()
    mesh = graphics.Meshes[mesh_name]
    mesh.show_edges = True
    mesh.surfaces_list = zones
    window_id = pyvista_windows_manager._get_unique_window_id()
    mesh.display(window_id)
    plotter = pyvista_windows_manager.get_plotter(window_id)
    plotter.add_point_labels(
        poly,
        "Pressure",
        point_color="black",
        font_size=font_size,
        bold=bold,
        shape=None,
    )
    return plotter
