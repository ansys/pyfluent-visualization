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

""".. _ref_enhanced_postprocessing:

Enhanced Postprocessing
-----------------------
This example demonstrates access to the actual renderer from the pyfluent
renderer layer so that users can perform operations on it.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports and set the configuration.

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
from ansys.fluent.core.solver import (
    PressureOutlets,
    WallBoundaries,
    using,
)
from ansys.units import VariableCatalog

from ansys.fluent.visualization import (
    GraphicsWindow,
    Mesh,
    Monitor,
    XYPlot,
    config,
)

pyfluent.CONTAINER_MOUNT_PATH = pyfluent.EXAMPLES_PATH

config.interactive = False
config.view = "isometric"

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
    precision=pyfluent.Precision.DOUBLE,
    processor_count=2,
    start_transcript=False,
    mode=pyfluent.FluentMode.SOLVER,
)

solver_session.settings.file.read_case(file_name=import_case)
solver_session.settings.file.read_data(file_name=import_data)

with using(solver_session):

    # Create a graphics object for the mesh display.
    graphics_window = GraphicsWindow()

    mesh = Mesh(show_edges=True, surfaces=WallBoundaries())
    graphics_window.add_graphics(mesh, position=(0, 0))
    mesh = Mesh(surfaces=WallBoundaries())
    graphics_window.add_graphics(mesh, position=(0, 1))

    graphics_window.renderer.set_background("black", top="white")
    graphics_window.save_graphics("sample_mesh_image.pdf")
    graphics_window.renderer.set_background("white")
    graphics_window.show()

    # Create and display XY plot, residual plot and solve and plot solution monitors.
    plot_window = GraphicsWindow()

    xy_plot_object = XYPlot(
        surfaces=PressureOutlets(), y_axis_function=VariableCatalog.TEMPERATURE
    )
    plot_window.add_plot(xy_plot_object, position=(0, 0), title="Temperature")

    residual = Monitor(monitor_set_name="residual")
    plot_window.add_plot(residual, position=(0, 1))
    plot_window.save_graphics("sample_plot.pdf")
    plot_window.show()

    plot_window.renderer = "matplotlib"
    plot_window.save_graphics("sample_plot.png")
    plot_window.show()
