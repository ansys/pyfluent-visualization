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

session = pyfluent.connect_to_fluent(ip="10.18.44.105", port=62599, password="hzk1dhbc")

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
mesh1.surfaces_list = ["solid_up:1:830"]

# pathlines
pathlines1 = graphics_session1.Pathlines["pathlines-1"]
pathlines1.field = "velocity-magnitude"
pathlines1.surfaces_list = ["inlet"]

# contour
contour1 = graphics_session1.Contours["contour-1"]
contour1.field = "velocity-magnitude"
contour1.surfaces_list = ["solid_up:1:830"]


graphics_session1.Contours["contour-2"]
graphics_session1_1.Contours["contour-3"]

# vector
vector1 = graphics_session1_1.Vectors["vector-1"]
vector1.surfaces_list = ["solid_up:1:830"]
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
p1.surfaces_list = ["solid_up:1:830", "surface-1"]
p1.surfaces_list = ["solid_up:1:830"]
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
