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

from unittest.mock import patch

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
import pytest
import pyvista as pv

from ansys.fluent.visualization import (
    GraphicsWindow,
    Mesh,
    Surface,
    config,
)
from ansys.fluent.visualization.graphics.graphics_windows_manager import (
    GraphicsWindow as TGraphicsWindow,
)
from ansys.fluent.visualization.graphics.pyvista.graphics_defns import Renderer


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
        config.interactive = False
        solver = new_solver_session_with_exhaust_case_and_data
        mesh_surfaces_list = [
            "in1",
            "in2",
            "in3",
        ]
        TGraphicsWindow.show_graphics = lambda win_id: None
        mesh = Mesh(solver=solver, show_edges=True, surfaces=mesh_surfaces_list)
        graphics_window = GraphicsWindow()
        graphics_window.add_graphics(mesh)
        graphics_window.show()

        # Check that render was called 3 times for 3 surfaces
        assert mock_render.call_count == 3

        # Get the actual arguments
        args, kwargs = mock_render.call_args
        called_mesh = args[0]

        # Assertions on arguments
        assert isinstance(called_mesh, pv.PolyData)
        assert kwargs.get("color") == [128, 0, 0]
        assert kwargs.get("show_edges") is True
        assert kwargs.get("position") == (0, 0)
        assert kwargs.get("opacity") == 1


def test_visualization_calls_render_correctly_with_dual_mesh(
    new_solver_session_with_exhaust_case_and_data,
):
    with patch.object(Renderer, "render") as mock_render:
        config.interactive = False
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

        # Check that render was called 3 times for 3 surfaces
        assert mock_render.call_count == 6

        # Get the actual arguments
        args, kwargs = mock_render.call_args
        called_mesh = args[0]

        # Assertions on arguments
        assert isinstance(called_mesh, pv.PolyData)
        assert kwargs.get("color") == [128, 0, 0]
        assert kwargs.get("show_edges") is False
        assert kwargs.get("position") == (0, 1)
        assert kwargs.get("opacity") == 1


def test_visualization_calls_render_correctly_with_plane_and_iso_surface(
    new_solver_session_with_exhaust_case_and_data,
):
    with patch.object(Renderer, "render") as mock_render:
        config.interactive = False
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
        called_mesh = args[0]

        # Assertions on arguments
        assert isinstance(called_mesh, pv.PolyData)
        assert kwargs.get("color") == [128, 0, 128]
        assert kwargs.get("position") == (0, 0)

        # Iso-surface
        surf_outlet_plane = Surface(solver=solver)
        surf_outlet_plane.definition.type = "iso-surface"
        iso_surf1 = surf_outlet_plane.definition.iso_surface
        iso_surf1.field = "y-coordinate"
        iso_surf1.iso_value = -0.125017
        graphics_window = GraphicsWindow()
        graphics_window.add_graphics(surf_outlet_plane)
        graphics_window.show()

        # Check that render was called 2 times for 1 iso-surface (contains 2 surfaces)
        assert mock_render.call_count == 2

        # Get the actual arguments
        args, kwargs = mock_render.call_args
        called_mesh = args[0]

        # Assertions on arguments
        assert isinstance(called_mesh, pv.PolyData)
        assert kwargs.get("color") == [128, 0, 128]
        assert kwargs.get("position") == (0, 0)
