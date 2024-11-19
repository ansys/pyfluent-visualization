""".. _ref_updated_exhaust_manifold_example:

Postprocessing using PyVista and Matplotlib
-------------------------------------------
This example uses PyVista and Matplotlib to demonstrate PyFluent
postprocessing capabilities. The 3D model in this example
is an exhaust manifold that has high temperature flows passing
through it. The flow through the manifold is turbulent and
involves conjugate heat transfer.

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
    PlotterWindow,
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
    ui_mode="gui",
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
mesh1 = Mesh(solver=solver_session, show_edges=True, surfaces=mesh_surfaces_list)

p1 = GraphicsWindow(grid=(1, 2))
p1.add_graphics(mesh1, position=(0, 0))

mesh2 = Mesh(solver=solver_session, surfaces=mesh_surfaces_list)
mesh2.show_edges = False

p1.add_graphics(mesh2, position=(0, 1))
p1.show()

###############################################################################
# Create plane-surface XY plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a plane-surface XY plane.

surf_xy_plane = Surface(solver=solver_session)
surf_xy_plane.definition.type = "plane-surface"
surf_xy_plane.definition.plane_surface.creation_method = "xy-plane"
plane_surface_xy = surf_xy_plane.definition.plane_surface.xy_plane
plane_surface_xy.z = -0.0441921
p2 = GraphicsWindow(grid=(1, 3))
p2.add_graphics(surf_xy_plane, position=(0, 0))

###############################################################################
# Create plane-surface YZ plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a plane-surface YZ plane.

surf_yz_plane = Surface(solver=solver_session)
surf_yz_plane.definition.type = "plane-surface"
surf_yz_plane.definition.plane_surface.creation_method = "yz-plane"
plane_surface_yz = surf_yz_plane.definition.plane_surface.yz_plane
plane_surface_yz.x = -0.174628
p2.add_graphics(surf_yz_plane, position=(0, 1))

###############################################################################
# Create plane-surface ZX plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a plane-surface ZX plane.

surf_zx_plane = Surface(solver=solver_session)
surf_zx_plane.definition.type = "plane-surface"
surf_zx_plane.definition.plane_surface.creation_method = "zx-plane"
plane_surface_zx = surf_zx_plane.definition.plane_surface.zx_plane
plane_surface_zx.y = -0.0627297
p2.add_graphics(surf_zx_plane, position=(0, 2))
p2.show()

###############################################################################
# Create iso-surface on outlet plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an iso-surface on the outlet plane.

surf_outlet_plane = Surface(solver=solver_session)
surf_outlet_plane.definition.type = "iso-surface"
iso_surf1 = surf_outlet_plane.definition.iso_surface
iso_surf1.field = "y-coordinate"
iso_surf1.iso_value = -0.125017
p3 = GraphicsWindow(grid=(2, 1))
p3.add_graphics(surf_outlet_plane, position=(0, 0))

###############################################################################
# Create iso-surface on mid-plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an iso-surface on the mid-plane.

surf_mid_plane_x = Surface(solver=solver_session)
surf_mid_plane_x.definition.type = "iso-surface"
iso_surf2 = surf_mid_plane_x.definition.iso_surface
iso_surf2.field = "x-coordinate"
iso_surf2.iso_value = -0.174
p3.add_graphics(surf_mid_plane_x, position=(1, 0))
p3.show()

###############################################################################
# Create iso-surface using velocity magnitude
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an iso-surface using the velocity magnitude.

surf_vel_contour = Surface(solver=solver_session)
surf_vel_contour.definition.type = "iso-surface"
iso_surf3 = surf_vel_contour.definition.iso_surface
iso_surf3.field = "velocity-magnitude"
iso_surf3.rendering = "contour"
iso_surf3.iso_value = 0.0
p4 = GraphicsWindow(grid=(2, 2))
p4.add_graphics(surf_vel_contour, position=(0, 0))

###############################################################################
# Create temperature contour on mid-plane and outlet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a temperature contour on the mid-plane and the outlet.

temperature_contour = Contour(solver=solver_session)
temperature_contour.field = "temperature"
temperature_contour.surfaces = [surf_mid_plane_x.name, surf_outlet_plane.name]
p4.add_graphics(temperature_contour, position=(0, 1))

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
p4.add_graphics(temperature_contour_manifold, position=(1, 0))

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
p4.add_graphics(velocity_vector, position=(1, 1))
p4.show()

###############################################################################
# Create Pathlines
# ~~~~~~~~~~~~~~~~
# Create a pathlines on a predefined surface.

pathlines = Pathline(solver=solver_session)
pathlines.field = "velocity-magnitude"
pathlines.surfaces = ["inlet", "inlet1", "inlet2"]

p5 = GraphicsWindow()
p5.add_graphics(pathlines)
p5.show()

p6 = GraphicsWindow()
p6.add_graphics(mesh2, opacity=0.05)
p6.add_graphics(velocity_vector)
p6.show()

###############################################################################
# Create XY plot
# ~~~~~~~~~~~~~~
# Create the default XY plot.

xy_plot = XYPlot(
    solver=solver_session,
    surfaces=["outlet"],
    y_axis_function="temperature",
)
p7 = PlotterWindow(grid=(2, 2))
p7.add_plots(xy_plot, position=(0, 0))

###############################################################################
# Create residual plot
# ~~~~~~~~~~~~~~~~~~~~~~
# Create and display the residual plot.

residual = Monitor(solver=solver_session)
residual.monitor_set_name = "residual"
p7.add_plots(residual, position=(0, 1))

###############################################################################
# Solve and plot solution monitors
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Solve and plot solution monitors.

solver_session.solution.initialization.hybrid_initialize()
solver_session.solution.run_calculation.iterate(iter_count=50)

mass_bal_rplot = Monitor(solver=solver_session)
mass_bal_rplot.monitor_set_name = "mass-bal-rplot"
p7.add_plots(mass_bal_rplot, position=(1, 0))

point_vel_rplot = Monitor(solver=solver_session, monitor_set_name="point-vel-rplot")
p7.add_plots(point_vel_rplot, position=(1, 1))
p7.show()

###############################################################################
# Close Fluent
# ~~~~~~~~~~~~
# Close Fluent.

solver_session.exit()
