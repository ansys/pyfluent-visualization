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

from ansys.fluent.visualization import set_config

set_config(blocking=False)

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

session.settings.file.read_case(file_name=import_case)
session.settings.file.read_data(file_name=import_data)

from ansys.fluent.visualization import (
    Contour,
    GraphicsWindow,
    Mesh,
    Monitor,
    Pathline,
    PlotterWindow,
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
p_xy = PlotterWindow()
p_xy.add_plots(p1)
p_xy.show()

session.monitors.get_monitor_set_names()
residual = Monitor(solver=session)
residual.monitor_set_name = "residual"
p_res = PlotterWindow()
p_res.add_plots(residual)
p_res.show()

mtr = Monitor(solver=session)
mtr.monitor_set_name = "mass-tot-rplot"
p_mtr = PlotterWindow()
p_mtr.add_plots(mtr)
p_mtr.show()

mbr = Monitor(solver=session)
mbr.monitor_set_name = "mass-bal-rplot"
p_mbr = PlotterWindow()
p_mbr.add_plots(mbr)
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

p_cont.plotter.view_isometric()

p_surf = GraphicsWindow()
p_surf.add_graphics(surface1)
p_surf.show()


def auto_refersh_call_back_iteration(session_id, event_info):
    if event_info.index % 1 == 0:
        p_cont.refresh_windows(session_id)
        p_res.refresh_windows(session_id)
        p_mtr.refresh_windows(session_id)
        p_mbr.refresh_windows(session_id)


def auto_refersh_call_back_time_step(session_id, event_info):
    p_res.refresh_windows(session_id)


def initialize_call_back(session_id, event_info):
    p_res.refresh_windows(session_id)
    p_mtr.refresh_windows(session_id)


cb_init_id = session.events.register_callback("InitializedEvent", initialize_call_back)
cb_data_read_id = session.events.register_callback(
    "DataReadEvent", initialize_call_back
)
cb_itr_id = session.events.register_callback(
    "IterationEndedEvent", auto_refersh_call_back_iteration
)

p_cont.animate_windows(session.id)
