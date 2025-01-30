# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

""".. _ref_script_manifold:

Triggering callbacks and Animation
----------------------------------
This example uses PyVista and Matplotlib to demonstrate the use
of callback mechanisms. The 3D model in this example
is an exhaust manifold.
"""

###############################################################################
# Run the following in command prompt to execute this file:
# exec(open("script_manifold.py").read())

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

import_case = examples.download_file(
    file_name="exhaust_system.cas.h5", directory="pyfluent/exhaust_system"
)

import_data = examples.download_file(
    file_name="exhaust_system.dat.h5", directory="pyfluent/exhaust_system"
)

session = pyfluent.launch_fluent(
    precision="double",
    processor_count=2,
    start_transcript=False,
    mode="solver",
    ui_mode="gui",
)

from ansys.fluent.visualization import set_config

set_config(blocking=False)


from ansys.fluent.visualization import Graphics, Plots
from ansys.fluent.visualization.graphics import graphics_windows_manager
from ansys.fluent.visualization.plotter import plotter_windows_manager

# get the graphics objects for the session
graphics_session1 = Graphics(session)
graphics_session1_1 = Graphics(session)

# mesh
mesh1 = graphics_session1.Meshes["mesh-1"]
mesh1.show_edges = True
mesh1.surfaces = ["solid_up:1:830"]

# pathlines
pathlines1 = graphics_session1.Pathlines["pathlines-1"]
pathlines1.field = "velocity-magnitude"
pathlines1.surfaces = ["inlet"]

# contour
contour1 = graphics_session1.Contours["contour-1"]
contour1.field = "velocity-magnitude"
contour1.surfaces = ["solid_up:1:830"]


graphics_session1.Contours["contour-2"]
graphics_session1_1.Contours["contour-3"]

# vector
vector1 = graphics_session1_1.Vectors["vector-1"]
vector1.surfaces = ["solid_up:1:830"]
vector1.scale = 4.0
vector1.skip = 0
vector1.field = "temperature"
vector1.display()

# iso surface
surface1 = graphics_session1_1.Surfaces["surface-1"]
surface1.definition.type = "iso-surface"
surface1.definition.iso_surface.field = "velocity-magnitude"
surface1.definition.iso_surface.rendering = "contour"
surface1.definition.iso_surface.iso_value = 0.0


local_surfaces_provider = Graphics(session).Surfaces
matplotlib_plots1 = Plots(session, local_surfaces_provider=local_surfaces_provider)


p1 = matplotlib_plots1.XYPlots["p1"]
p1.surfaces = ["solid_up:1:830", "surface-1"]
p1.surfaces = ["solid_up:1:830"]
p1.y_axis_function = "temperature"
p1.plot("p1")

session.monitors.get_monitor_set_names()
residual = matplotlib_plots1.Monitors["residual"]
residual.monitor_set_name = "residual"
residual.plot("residual")

mtr = matplotlib_plots1.Monitors["mass-tot-rplot"]
mtr.monitor_set_name = "mass-tot-rplot"
mtr.plot("mass-tot-rplot")

mbr = matplotlib_plots1.Monitors["mass-bal-rplot"]
mbr.monitor_set_name = "mass-bal-rplot"
mbr.plot("mass-bal-rplot")

mesh1.display("mesh-1")
vector1.display("vector-1")
contour1.display("contour-1")
pathlines1.display("pthlines-1")
plotter = graphics_windows_manager.get_plotter("contour-1")
plotter.view_isometric()
surface1.display("surface-1")


def auto_refersh_call_back_iteration(session_id, event_info):
    if event_info.index % 1 == 0:
        graphics_windows_manager.refresh_windows(session_id, ["contour-1"])
        plotter_windows_manager.refresh_windows(
            session_id, ["residual", "mass-tot-rplot", "mass-bal-rplot"]
        )


def auto_refersh_call_back_time_step(session_id, event_info):
    graphics_windows_manager.refresh_windows(session_id)
    plotter_windows_manager.refresh_windows("", ["residual"])


def initialize_call_back(session_id, event_info):
    graphics_windows_manager.refresh_windows(session_id)
    plotter_windows_manager.refresh_windows("", ["residual", "mass-tot-rplot"])


cb_init_id = session.events.register_callback("InitializedEvent", initialize_call_back)
cb_data_read_id = session.events.register_callback(
    "DataReadEvent", initialize_call_back
)
cb_itr_id = session.events.register_callback(
    "IterationEndedEvent", auto_refersh_call_back_iteration
)

graphics_windows_manager.animate_windows(session.id, ["contour-1"])
