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

""".. _ref_updated_exhaust_manifold_example:

Enhanced Postprocessing with PyVista and Matplotlib
---------------------------------------------------
This updated example demonstrates postprocessing capabilities in PyFluent
using an object-oriented approach, providing a more user-friendly interface
and improved flexibility.
The 3D model used in this example is an exhaust manifold, where high-temperature
turbulent flows are analyzed in a conjugate heat transfer scenario.

Key Improvements:

Object-Oriented Design: The code has been modularized into classes and methods,
enhancing maintainability and reusability.

Interactive User Interface: The user interface now allows seamless interaction,
enabling users to control and customize postprocessing parameters.

Enhanced Plot Interaction: Users have greater freedom to interact with the plots,
such as adding and super-imposing multiple plots, and toggling data views,
enhancing the visualization experience.

This example utilizes PyVista for 3D visualization and Matplotlib for 2D data plotting.
The new design provides a streamlined workflow for exploring and analyzing
the temperature and flow characteristics in the exhaust manifold.

"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports and set the configuration.

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

from ansys.fluent.visualization import (
    Contour,
    GraphicsWindow,
    Mesh,
    Monitor,
    Pathline,
    Surface,
    Vector,
    XYPlot,
    set_config,
)

pyfluent.CONTAINER_MOUNT_PATH = pyfluent.EXAMPLES_PATH

set_config(blocking=True, set_view_on_display="isometric")

###############################################################################
# Download files and launch Fluent
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download the case and data files and launch Fluent as a service in solver
# mode with double precision and two processors. Read in the case and data
# files.

import_case = examples.download_file(
    file_name="exhaust_system.cas.h5", directory="pyfluent/exhaust_system"
)

import_data = examples.download_file(
    file_name="exhaust_system.dat.h5", directory="pyfluent/exhaust_system"
)

solver_session = pyfluent.launch_fluent(
    precision="double",
    processor_count=2,
    start_transcript=False,
    mode="solver",
)

solver_session.settings.file.read_case(file_name=import_case)
solver_session.settings.file.read_data(file_name=import_data)

###############################################################################
# Create graphics object for mesh display
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a graphics object for the mesh display.

mesh_surfaces_list = [
    "in1",
    "in2",
    "in3",
    "out1",
    "solid_up:1",
    "solid_up:1:830",
    "solid_up:1:830-shadow",
]
mesh_object_1 = Mesh(
    solver=solver_session, show_edges=True, surfaces=mesh_surfaces_list
)

mesh_display_window = GraphicsWindow(grid=(1, 2))
mesh_display_window.add_graphics(mesh_object_1, position=(0, 0))

mesh_object_2 = Mesh(solver=solver_session, surfaces=mesh_surfaces_list)
mesh_object_2.show_edges = False

mesh_display_window.add_graphics(mesh_object_2, position=(0, 1))
mesh_display_window.show()

###############################################################################
# Create plane-surface XY plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a plane-surface XY plane.

surf_xy_plane_object = Surface(
    solver=solver_session,
    type="plane-surface",
    creation_method="xy-plane",
    z=-0.0441921,
)
surface_display_window = GraphicsWindow(grid=(1, 3))
surface_display_window.add_graphics(surf_xy_plane_object, position=(0, 0))

###############################################################################
# Create plane-surface YZ plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a plane-surface YZ plane.

surf_yz_plane_object = Surface(solver=solver_session)
surf_yz_plane_object.type = "plane-surface"
surf_yz_plane_object.creation_method = "yz-plane"
surf_yz_plane_object.x = -0.174628
surface_display_window.add_graphics(surf_yz_plane_object, position=(0, 1))

###############################################################################
# Create plane-surface ZX plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a plane-surface ZX plane.

surf_zx_plane_object = Surface(
    solver=solver_session,
    type="plane-surface",
    creation_method="zx-plane",
    y=-0.0627297,
)
surface_display_window.add_graphics(surf_zx_plane_object, position=(0, 2))
surface_display_window.show()

###############################################################################
# Create iso-surface on outlet plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an iso-surface on the outlet plane.

iso_surface_object = Surface(
    solver=solver_session, type="iso-surface", field="y-coordinate", iso_value=-0.125017
)
iso_surface_display_window = GraphicsWindow(grid=(2, 1))
iso_surface_display_window.add_graphics(iso_surface_object, position=(0, 0))

###############################################################################
# Create iso-surface on mid-plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an iso-surface on the mid-plane.

surf_mid_plane_x = Surface(solver=solver_session)
surf_mid_plane_x.type = "iso-surface"
surf_mid_plane_x.field = "x-coordinate"
surf_mid_plane_x.iso_value = -0.174
iso_surface_display_window.add_graphics(surf_mid_plane_x, position=(1, 0))
iso_surface_display_window.show()

###############################################################################
# Create iso-surface using velocity magnitude
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an iso-surface using the velocity magnitude.

surf_vel_contour = Surface(
    solver=solver_session,
    type="iso-surface",
    field="velocity-magnitude",
    iso_value=0.0,
    rendering="contour",
)
graphics_window = GraphicsWindow(grid=(2, 2))
graphics_window.add_graphics(surf_vel_contour, position=(0, 0))

###############################################################################
# Create temperature contour on mid-plane and outlet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a temperature contour on the mid-plane and the outlet.

temperature_contour = Contour(solver=solver_session)
temperature_contour.field = "temperature"
temperature_contour.surfaces = [surf_mid_plane_x.name, iso_surface_object.name]
graphics_window.add_graphics(temperature_contour, position=(0, 1))

###############################################################################
# Create contour plot of temperature on manifold
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a contour plot of the temperature on the manifold.

cont_surfaces_list = [
    "in1",
    "in2",
    "in3",
    "out1",
    "solid_up:1",
    "solid_up:1:830",
]
temperature_contour_manifold = Contour(
    solver=solver_session,
    field="temperature",
    surfaces=cont_surfaces_list,
)
graphics_window.add_graphics(temperature_contour_manifold, position=(1, 0))

###############################################################################
# Create vector
# ~~~~~~~~~~~~~
# Create a vector on a predefined surface.

velocity_vector = Vector(
    solver=solver_session,
    field="pressure",
    surfaces=["solid_up:1:830"],
    scale=2,
)
graphics_window.add_graphics(velocity_vector, position=(1, 1))
graphics_window.show()

###############################################################################
# Create Pathlines
# ~~~~~~~~~~~~~~~~
# Create a pathlines on a predefined surface.

pathlines = Pathline(solver=solver_session)
pathlines.field = "velocity-magnitude"
pathlines.surfaces = ["inlet", "inlet1", "inlet2"]

pathline_display_window = GraphicsWindow()
pathline_display_window.add_graphics(pathlines)
pathline_display_window.show()

mesh_velocity_display_window = GraphicsWindow()
mesh_velocity_display_window.add_graphics(mesh_object_2, opacity=0.05)
mesh_velocity_display_window.add_graphics(velocity_vector)
mesh_velocity_display_window.show()

###############################################################################
# Create XY plot
# ~~~~~~~~~~~~~~
# Create the default XY plot.

xy_plot_object = XYPlot(
    solver=solver_session,
    surfaces=["outlet"],
    y_axis_function="temperature",
)
plot_window = GraphicsWindow(grid=(2, 2))
plot_window.add_graphics(xy_plot_object, position=(0, 0))

###############################################################################
# Create residual plot
# ~~~~~~~~~~~~~~~~~~~~~~
# Create and display the residual plot.

residual = Monitor(solver=solver_session)
residual.monitor_set_name = "residual"
plot_window.add_graphics(residual, position=(0, 1))

###############################################################################
# Solve and plot solution monitors
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Solve and plot solution monitors.

solver_session.solution.initialization.hybrid_initialize()
solver_session.solution.run_calculation.iterate(iter_count=50)

mass_bal_rplot = Monitor(solver=solver_session)
mass_bal_rplot.monitor_set_name = "mass-bal-rplot"
plot_window.add_graphics(mass_bal_rplot, position=(1, 0))

point_vel_rplot = Monitor(solver=solver_session, monitor_set_name="point-vel-rplot")
plot_window.add_graphics(point_vel_rplot, position=(1, 1))
plot_window.show()

###############################################################################
# Close Fluent
# ~~~~~~~~~~~~
# Close Fluent.

solver_session.exit()
