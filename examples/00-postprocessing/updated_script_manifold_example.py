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

""".. _ref_script_manifold:

Triggering callbacks and Animation
----------------------------------
This example uses PyVista and Matplotlib to demonstrate the use
of callback mechanisms. The 3D model in this example
is an exhaust manifold.
"""

###############################################################################
# Run the following in command prompt to execute this file:
# exec(open("updated_script_manifold_example.py").read())

from ansys.fluent.visualization import config

config.interactive = True

import ansys.fluent.core as pyfluent
from ansys.fluent.core import SolverEvent, examples

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

session.settings.file.read_case(file_name=import_case)
session.settings.file.read_data(file_name=import_data)

from ansys.fluent.visualization import (
    Contour,
    GraphicsWindow,
    Mesh,
    Monitor,
    Pathline,
    Surface,
    Vector,
    XYPlot,
)

# mesh
mesh1 = Mesh(solver=session, show_edges=True, surfaces=["solid_up:1:830"])

# pathlines
pathlines1 = Pathline(solver=session, field="velocity-magnitude", surfaces=["inlet"])

# contour
contour1 = Contour(
    solver=session, field="velocity-magnitude", surfaces=["solid_up:1:830"]
)

# vector
vector1 = Vector(
    solver=session, surfaces=["solid_up:1:830"], scale=4.0, skip=0, field="temperature"
)
p_vect = GraphicsWindow()
p_vect.add_graphics(vector1)
p_vect.show()

# iso surface
surface1 = Surface(solver=session)
surface1.definition.type = "iso-surface"
surface1.definition.iso_surface.field = "velocity-magnitude"
surface1.definition.iso_surface.rendering = "contour"
surface1.definition.iso_surface.iso_value = 0.0


p1 = XYPlot(solver=session, surfaces=["solid_up:1:830"])
p1.y_axis_function = "temperature"
p_xy = GraphicsWindow()
p_xy.add_plot(p1)
p_xy.show()

session.monitors.get_monitor_set_names()
residual = Monitor(solver=session)
residual.monitor_set_name = "residual"
p_res = GraphicsWindow()
p_res.add_plot(residual)
p_res.show()

mtr = Monitor(solver=session)
mtr.monitor_set_name = "mass-tot-rplot"
p_mtr = GraphicsWindow()
p_mtr.add_plot(mtr)
p_mtr.show()

mbr = Monitor(solver=session)
mbr.monitor_set_name = "mass-bal-rplot"
p_mbr = GraphicsWindow()
p_mbr.add_plot(mbr)
p_mbr.show()

p_mesh = GraphicsWindow()
p_mesh.add_graphics(mesh1)
p_mesh.show()
p_vect = GraphicsWindow()
p_vect.add_graphics(vector1)
p_vect.show()
p_cont = GraphicsWindow()
p_cont.add_graphics(contour1)
p_cont.show()
p_pathline = GraphicsWindow()
p_pathline.add_graphics(pathlines1)
p_pathline.show()

p_cont._visualizer.plotter.view_isometric()

p_surf = GraphicsWindow()
p_surf.add_graphics(surface1)
p_surf.show()


def auto_refersh_call_back_iteration(session, event_info):
    p_cont.refresh(session.id)
    p_res.refresh(session.id)
    p_mtr.refresh(session.id)
    p_mbr.refresh(session.id)


def auto_refersh_call_back_time_step(session, event_info):
    p_res.refresh(session.id)


def initialize_call_back(session, event_info):
    p_res.refresh(session.id)
    p_mtr.refresh(session.id)


session.events.register_callback(SolverEvent.SOLUTION_INITIALIZED, initialize_call_back)
session.events.register_callback(SolverEvent.DATA_LOADED, initialize_call_back)
session.events.register_callback(
    SolverEvent.ITERATION_ENDED, auto_refersh_call_back_iteration
)

p_cont.animate(session.id)

session.settings.solution.initialization.hybrid_initialize()
session.settings.solution.run_calculation.iterate(iter_count=50)
