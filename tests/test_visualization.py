# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys

from ansys.units import VariableCatalog
import pytest

from ansys.fluent.interface.post_objects.post_object_definitions import ContourDefn

# Windows CI runners don't have the capacity to hold fluent image.
# Adding this makes sure that these tests only run in ubuntu CI.
if sys.platform == "win32":
    pytest.skip("Skipping this module on Windows", allow_module_level=True)
else:
    # These tests are failing in python 3.13. Investigate it along with
    # "test_vector_object" and "test_surface_object" in "test_post.py".
    if sys.version_info[:2] == (3, 13):
        pytest.skip("Skipped on Python 3.13", allow_module_level=True)

from unittest.mock import patch

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
import numpy as np
import pytest
import pyvista as pv

from ansys.fluent.visualization import (
    Contour,
    GraphicsWindow,
    Mesh,
    Monitor,
    Pathline,
    Surface,
    Vector,
    XYPlot,
    config,
)

config.interactive = False
from ansys.fluent.visualization.graphics.graphics_windows_manager import (
    GraphicsWindow as TGraphicsWindow,
)
from ansys.fluent.visualization.graphics.pyvista.renderer import Renderer
from ansys.fluent.visualization.plotter.matplotlib.renderer import Plotter as MatPlotter
from ansys.fluent.visualization.plotter.plotter_windows_manager import (
    PlotterWindow as TPlotterWindow,
)
from ansys.fluent.visualization.plotter.pyvista.renderer import Plotter


@pytest.fixture(scope="module")
def new_solver_session():
    solver = pyfluent.launch_fluent()
    yield solver
    solver.exit()


@pytest.fixture(scope="module")
def new_solver_session_with_exhaust_case_and_data(new_solver_session):
    import_case = examples.download_file(
        file_name="exhaust_system.cas.h5", directory="pyfluent/exhaust_system"
    )

    import_data = examples.download_file(
        file_name="exhaust_system.dat.h5", directory="pyfluent/exhaust_system"
    )
    solver = new_solver_session
    solver.settings.file.read_case(file_name=import_case)
    solver.settings.file.read_data(file_name=import_data)
    return solver


def test_visualization_calls_render_correctly_with_single_mesh(
    new_solver_session_with_exhaust_case_and_data,
):
    with patch.object(Renderer, "render") as mock_render:
        solver = new_solver_session_with_exhaust_case_and_data
        mesh_surfaces_list = [
            "in1",
            "in2",
            "in3",
        ]
        TGraphicsWindow.show_graphics = lambda win_id: None
        mesh = Mesh(solver=solver, show_edges=True, surfaces=mesh_surfaces_list)
        graphics_window = GraphicsWindow()
        # One can pass any args to the plotter using 'add_graphics'
        graphics_window.add_graphics(
            mesh, opacity=0.05, random_str_arg="any_val", random_int_arg=5
        )
        graphics_window.show()

        # Check that render was called only 1 times
        mock_render.assert_called_once()

        # Get the actual arguments
        args, kwargs = mock_render.call_args
        assert kwargs == {}

        # For single mesh object
        assert len(args[0]) == 1
        # For 3 surfaces
        assert len(args[0][0]) == 3

        # For first surface
        mesh_dict = args[0][0][0]
        assert list(mesh_dict.keys()) == [
            "data",
            "show_edges",
            "color",
            "kwargs",
            "position",
            "opacity",
        ]

        # Assertions on arguments
        assert isinstance(mesh_dict["data"], pv.PolyData)
        assert mesh_dict.get("color") == [255, 255, 0]
        assert mesh_dict.get("show_edges") is True
        assert mesh_dict.get("position") == (0, 0)
        assert mesh_dict.get("opacity") == 0.05

        # For third surface
        mesh_dict = args[0][0][2]
        assert mesh_dict.get("color") == [255, 255, 0]
        assert mesh_dict.get("kwargs") == {
            "random_str_arg": "any_val",
            "random_int_arg": 5,
        }


def test_visualization_calls_render_correctly_with_dual_mesh(
    new_solver_session_with_exhaust_case_and_data,
):
    with patch.object(Renderer, "render") as mock_render:
        solver = new_solver_session_with_exhaust_case_and_data
        mesh_surfaces_list = [
            "in1",
            "in2",
            "in3",
        ]
        TGraphicsWindow.show_graphics = lambda win_id: None
        mesh = Mesh(solver=solver, show_edges=True, surfaces=mesh_surfaces_list)
        graphics_window = GraphicsWindow()
        graphics_window.add_graphics(mesh, position=(0, 0))

        mesh = Mesh(solver=solver, show_edges=False, surfaces=mesh_surfaces_list)
        graphics_window.add_graphics(mesh, position=(0, 1))
        graphics_window.show()

        # Check that render was called only 1 times
        mock_render.assert_called_once()

        # Get the actual arguments
        args, kwargs = mock_render.call_args
        assert kwargs == {}

        # For two mesh objects
        assert len(args[0]) == 2
        # For 3 surfaces
        assert len(args[0][0]) == 3
        assert len(args[0][1]) == 3

        # For first surface in second mesh
        mesh_dict = args[0][1][0]
        assert list(mesh_dict.keys()) == [
            "data",
            "show_edges",
            "color",
            "kwargs",
            "position",
            "opacity",
        ]

        # Assertions on arguments
        assert isinstance(mesh_dict["data"], pv.PolyData)
        assert mesh_dict.get("color") == [255, 255, 0]
        assert mesh_dict.get("show_edges") is False
        assert mesh_dict.get("position") == (0, 1)

        # For third surface in first mesh
        mesh_dict = args[0][0][2]
        assert mesh_dict.get("color") == [255, 255, 0]
        assert mesh_dict.get("show_edges") is True
        assert mesh_dict.get("position") == (0, 0)


def test_visualization_calls_render_correctly_with_plane_and_iso_surface(
    new_solver_session_with_exhaust_case_and_data,
):
    with patch.object(Renderer, "render") as mock_render:
        solver = new_solver_session_with_exhaust_case_and_data
        TGraphicsWindow.show_graphics = lambda win_id: None

        # Plane surface
        surf_xy_plane = Surface(solver=solver)
        surf_xy_plane.definition.type = "plane-surface"
        surf_xy_plane.definition.plane_surface.creation_method = "xy-plane"
        plane_surface_xy = surf_xy_plane.definition.plane_surface.xy_plane
        plane_surface_xy.z = -0.0441921
        graphics_window = GraphicsWindow()
        graphics_window.add_graphics(surf_xy_plane)
        graphics_window.show()

        # Check that render was called 1 time for 1 surface
        mock_render.assert_called_once()

        # Get the actual arguments
        args, kwargs = mock_render.call_args
        mesh_dict = args[0][0][0]
        assert kwargs == {}

        # Assertions on arguments
        assert isinstance(mesh_dict["data"], pv.PolyData)
        assert mesh_dict.get("color") == [128, 128, 0]
        assert mesh_dict.get("position") == (0, 0)

        # Iso-surface
        surf_outlet_plane = Surface(solver=solver)
        surf_outlet_plane.definition.type = "iso-surface"
        iso_surf1 = surf_outlet_plane.definition.iso_surface
        iso_surf1.field = "y-coordinate"
        iso_surf1.iso_value = -0.125017
        graphics_window = GraphicsWindow()
        graphics_window.add_graphics(surf_outlet_plane)
        graphics_window.show()

        # Check that render was called 2 times 2nd time in the same module
        assert mock_render.call_count == 2

        # Get the actual arguments
        args, kwargs = mock_render.call_args
        assert kwargs == {}
        mesh_dict = args[0][0][0]

        # Assertions on arguments
        assert isinstance(mesh_dict["data"], pv.PolyData)
        assert mesh_dict.get("color") == [128, 128, 0]
        assert mesh_dict.get("position") == (0, 0)


def test_visualization_calls_render_correctly_with_contour(
    new_solver_session_with_exhaust_case_and_data,
):
    with patch.object(Renderer, "render") as mock_render:
        solver = new_solver_session_with_exhaust_case_and_data
        TGraphicsWindow.show_graphics = lambda win_id: None
        contour = Contour(
            solver=solver,
            field=VariableCatalog.TEMPERATURE,
            surfaces=["in1", "in2", "in3"],
        )
        # All attributes are exposed at this level.
        assert "field" in dir(contour)
        assert contour.field is not None
        graphics_window = GraphicsWindow()
        graphics_window.add_graphics(contour)
        graphics_window.show()

        # Check that render was called 1 time
        mock_render.assert_called_once()

        # Get the actual arguments
        args, kwargs = mock_render.call_args
        assert kwargs == {}
        # For 3 surfaces
        assert len(args[0][0]) == 3
        mesh_dict = args[0][0][0]

        # Assertions on arguments
        assert isinstance(mesh_dict["data"], pv.PolyData)
        assert mesh_dict["scalar_bar_args"]
        assert mesh_dict.get("show_edges") is False
        assert mesh_dict.get("position") == (0, 0)
        assert mesh_dict.get("opacity") == 1


def test_visualization_calls_render_correctly_with_vector(
    new_solver_session_with_exhaust_case_and_data,
):
    with patch.object(Renderer, "render") as mock_render:
        solver = new_solver_session_with_exhaust_case_and_data
        TGraphicsWindow.show_graphics = lambda win_id: None
        velocity_vector = Vector(
            solver=solver,
            field="x-velocity",
            surfaces=["solid_up:1:830"],
            scale=2,
        )
        graphics_window = GraphicsWindow()
        graphics_window.add_graphics(velocity_vector)
        graphics_window.show()

        # Check that render was called 1 time
        mock_render.assert_called_once()

        # Get the actual arguments
        args, kwargs = mock_render.call_args
        assert kwargs == {}
        mesh_dict = args[0][0][0]

        # Assertions on arguments
        assert isinstance(mesh_dict["data"], pv.PolyData)
        assert mesh_dict["scalar_bar_args"]
        assert mesh_dict.get("scalars") == "x-velocity\n[m s^-1]"
        assert mesh_dict.get("position") == (0, 0)
        assert mesh_dict.get("opacity") == 1


def test_visualization_calls_render_correctly_with_pathlines(
    new_solver_session_with_exhaust_case_and_data,
):
    with patch.object(Renderer, "render") as mock_render:
        solver = new_solver_session_with_exhaust_case_and_data
        TGraphicsWindow.show_graphics = lambda win_id: None
        pathlines = Pathline(solver=solver)
        pathlines.field = "velocity-magnitude"
        pathlines.surfaces = ["inlet", "inlet1", "inlet2"]
        graphics_window = GraphicsWindow()
        graphics_window.add_graphics(pathlines)
        graphics_window.show()

        # Check that render was called 1 time
        mock_render.assert_called_once()

        # Get the actual arguments
        args, kwargs = mock_render.call_args
        assert kwargs == {}
        # For 3 surfaces
        assert len(args[0][0]) == 3
        mesh_dict = args[0][0][0]

        # Assertions on arguments
        assert isinstance(mesh_dict["data"], pv.PolyData)
        assert mesh_dict["scalar_bar_args"]
        assert mesh_dict.get("scalars") == "velocity-magnitude\n[m s^-1]"
        assert mesh_dict.get("position") == (0, 0)
        assert mesh_dict.get("opacity") == 1


def test_visualization_calls_render_correctly_with_xy_plot_pyvista(
    new_solver_session_with_exhaust_case_and_data,
):
    with patch.object(Plotter, "render") as mock_render:
        solver = new_solver_session_with_exhaust_case_and_data
        TPlotterWindow._show_plot = lambda win_id: None
        xy_plot_object = XYPlot(
            solver=solver,
            surfaces=["outlet"],
            y_axis_function="temperature",
        )
        plot_window = GraphicsWindow()
        plot_window.add_plot(xy_plot_object)
        plot_window.show()

        # Check that render was called 1 time
        mock_render.assert_called_once()

        # Get the actual arguments
        args, kwargs = mock_render.call_args
        assert kwargs == {}
        data_dict = args[0][0][0]

        # Assertions on arguments
        assert isinstance(data_dict["data"]["outlet"], np.ndarray)
        assert data_dict["properties"]["title"] == "XY Plot"
        assert data_dict.get("position") == (0, 0)


def test_visualization_calls_render_correctly_with_xy_plot_matplotlib(
    new_solver_session_with_exhaust_case_and_data,
):
    with patch.object(MatPlotter, "render") as mock_render:
        solver = new_solver_session_with_exhaust_case_and_data
        TPlotterWindow._show_plot = lambda win_id: None
        xy_plot_object = XYPlot(
            solver=solver,
            surfaces=["outlet"],
            y_axis_function="temperature",
        )
        plot_window = GraphicsWindow(renderer="matplotlib")
        plot_window.add_plot(xy_plot_object)
        plot_window.show()

        # Check that render was called 1 time for 1 surface
        mock_render.assert_called_once()

        # Get the actual arguments
        args, kwargs = mock_render.call_args
        assert kwargs == {}
        data_dict = args[0][0][0]

        # Assertions on arguments
        assert isinstance(data_dict["data"]["outlet"], np.ndarray)
        assert data_dict["properties"]["title"] == "XY Plot"
        assert data_dict.get("position") == (0, 0)


def test_visualization_calls_render_correctly_with_monitor_plot(
    new_solver_session_with_exhaust_case_and_data,
):
    with patch.object(Plotter, "render") as mock_render:
        solver = new_solver_session_with_exhaust_case_and_data
        TPlotterWindow._show_plot = lambda win_id: None
        residual = Monitor(solver=solver)
        residual.monitor_set_name = "residual"
        plot_window = GraphicsWindow()
        plot_window.add_plot(residual)
        plot_window.show()

        # Check that render was called 1 time for 1 surface
        mock_render.assert_called_once()

        # Get the actual arguments
        args, kwargs = mock_render.call_args
        assert kwargs == {}
        data_dict = args[0][0][0]

        # Assertions on arguments
        assert list(data_dict["data"].keys()) == [
            "continuity",
            "x-velocity",
            "y-velocity",
            "z-velocity",
            "energy",
            "k",
            "omega",
        ]
        assert data_dict["properties"]["title"] == "residual"
        assert data_dict.get("position") == (0, 0)


def test_exception_for_unsupported_argument_combination(
    new_solver_session_with_exhaust_case_and_data,
):
    solver = new_solver_session_with_exhaust_case_and_data

    with pytest.raises(ValueError):
        # if filled is False then node_values cannot be False
        contour = Contour(
            solver=solver, filled=False, node_values=False, surfaces=["in1"]
        )

    contour = Contour(solver=solver, surfaces=["in1"])
    assert contour.filled() is True
    assert contour.node_values() is True
    assert contour.range.auto_range_off.clip_to_range() is False

    contour.filled = False
    with pytest.raises(ValueError):
        contour.node_values = False

    contour.filled = True
    assert contour.node_values.is_active
    contour.node_values = False
    contour.filled = False
    assert not contour.node_values.is_active
    assert contour.node_values() == True

    contour.filled = True
    contour.node_values = False
    contour.range.auto_range_off.clip_to_range = True
    assert not contour.node_values.is_active
    assert contour.node_values() == True


def test_attribute_access_behaviour(
    new_solver_session_with_exhaust_case_and_data,
):
    solver = new_solver_session_with_exhaust_case_and_data
    contour = Contour(solver=solver, filled=False, surfaces=["in1"])

    assert isinstance(contour.node_values, ContourDefn.node_values)
    # Accessing attribute value like this is not allowed,
    # it will return the object only, not it's value
    assert not contour.node_values is True
    # Attribute can be accessed via method call
    assert contour.node_values() is True

    assert isinstance(contour.filled, ContourDefn.filled)
    assert not contour.filled is False
    assert contour.filled() is False
