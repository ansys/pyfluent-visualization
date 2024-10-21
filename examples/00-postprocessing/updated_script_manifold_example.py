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

import ansys.fluent.core as pyfluent

session = pyfluent.connect_to_fluent(ip="10.18.44.105", port=61042, password="gcr7ienc")

from ansys.fluent.visualization import set_config

set_config(blocking=False)


from ansys.fluent.visualization import Graphics, Plots
from ansys.fluent.visualization.graphics.graphics_windows import (
    GraphicsWrapper as GraphicsWindow,
)
from ansys.fluent.visualization.plotter.plotter_windows import (
    PlotterWrapper as PlotterWindow,
)

# get the graphics objects for the session
graphics_session = Graphics(session)

# mesh
mesh1 = graphics_session.Meshes.create(
    show_edges=True, surfaces_list=["solid_up:1:830"]
)

# pathlines
pathlines1 = graphics_session.Pathlines.create(
    field="velocity-magnitude", surfaces_list=["inlet"]
)

# contour
contour1 = graphics_session.Contours.create(
    field="velocity-magnitude", surfaces_list=["solid_up:1:830"]
)

# vector
vector1 = graphics_session.Vectors.create(
    surfaces_list=["solid_up:1:830"], scale=4.0, skip=0, field="temperature"
)
p_vect = GraphicsWindow()
p_vect.plot(vector1)

# iso surface
surface1 = graphics_session.Surfaces.create()
surface1.definition.type = "iso-surface"
surface1.definition.iso_surface.field = "velocity-magnitude"
surface1.definition.iso_surface.rendering = "contour"
surface1.definition.iso_surface.iso_value = 0.0


local_surfaces_provider = Graphics(session).Surfaces
matplotlib_plots = Plots(session, local_surfaces_provider=local_surfaces_provider)


p1 = matplotlib_plots.XYPlots.create()
p1.surfaces_list = ["solid_up:1:830", "surface-0"]
p1.surfaces_list = ["solid_up:1:830"]
p1.y_axis_function = "temperature"
p1.plot("p1")

session.monitors.get_monitor_set_names()
residual = matplotlib_plots.Monitors.create()
residual.monitor_set_name = "residual"
p_res = PlotterWindow()
p_res.plot(residual)

mtr = matplotlib_plots.Monitors.create()
mtr.monitor_set_name = "mass-tot-rplot"
p_mtr = PlotterWindow()
p_mtr.plot(mtr)

mbr = matplotlib_plots.Monitors.create()
mbr.monitor_set_name = "mass-bal-rplot"
p_mbr = PlotterWindow()
p_mbr.plot(mbr)

p_mesh = GraphicsWindow()
p_mesh.plot(mesh1)
p_vect = GraphicsWindow()
p_vect.plot(vector1)
p_cont = GraphicsWindow()
p_cont.plot(contour1)
p_pathline = GraphicsWindow()
p_pathline.plot(pathlines1)

p_cont.plotter.view_isometric()

p_surf = GraphicsWindow()
p_surf.plot(surface1)


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
