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

from ansys.fluent.visualization import Graphics, Plots, set_config
from ansys.fluent.visualization.graphics.graphics_windows import (
    GraphicsWrapper as GraphicsWindow,
)
from ansys.fluent.visualization.plotter.plotter_windows import (
    PlotterWrapper as PlotterWindow,
)

pyfluent.CONTAINER_MOUNT_PATH = pyfluent.EXAMPLES_PATH

set_config(blocking=False, set_view_on_display="isometric")

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
solver_session.file.read_case(file_name=import_case)
solver_session.file.read_data(file_name=import_data)

###############################################################################
# Get graphics object
# ~~~~~~~~~~~~~~~~~~~
# Get the graphics object.

graphics = Graphics(session=solver_session)

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
mesh1 = graphics.Meshes.create(show_edges=True, surfaces_list=mesh_surfaces_list)

p1 = GraphicsWindow()
p1.plot(mesh1)

###############################################################################
# Hide edges and display again
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Hide the edges and display again.

mesh1.show_edges = False
p2 = GraphicsWindow()
p2.plot(mesh1)

###############################################################################
# Create plane-surface XY plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a plane-surface XY plane.

surf_xy_plane = graphics.Surfaces.create()
surf_xy_plane.definition.type = "plane-surface"
surf_xy_plane.definition.plane_surface.creation_method = "xy-plane"
plane_surface_xy = surf_xy_plane.definition.plane_surface.xy_plane
plane_surface_xy.z = -0.0441921
p3 = GraphicsWindow()
p3.plot(surf_xy_plane)

###############################################################################
# Create plane-surface YZ plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a plane-surface YZ plane.

surf_yz_plane = graphics.Surfaces.create()
surf_yz_plane.definition.type = "plane-surface"
surf_yz_plane.definition.plane_surface.creation_method = "yz-plane"
plane_surface_yz = surf_yz_plane.definition.plane_surface.yz_plane
plane_surface_yz.x = -0.174628
p4 = GraphicsWindow()
p4.plot(surf_yz_plane)

###############################################################################
# Create plane-surface ZX plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a plane-surface ZX plane.

surf_zx_plane = graphics.Surfaces.create()
surf_zx_plane.definition.type = "plane-surface"
surf_zx_plane.definition.plane_surface.creation_method = "zx-plane"
plane_surface_zx = surf_zx_plane.definition.plane_surface.zx_plane
plane_surface_zx.y = -0.0627297
p5 = GraphicsWindow()
p5.plot(surf_zx_plane)

###############################################################################
# Create iso-surface on outlet plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an iso-surface on the outlet plane.

surf_outlet_plane = graphics.Surfaces.create()
surf_outlet_plane.definition.type = "iso-surface"
iso_surf1 = surf_outlet_plane.definition.iso_surface
iso_surf1.field = "y-coordinate"
iso_surf1.iso_value = -0.125017
p6 = GraphicsWindow()
p6.plot(surf_outlet_plane)

###############################################################################
# Create iso-surface on mid-plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an iso-surface on the mid-plane.

surf_mid_plane_x = graphics.Surfaces.create()
surf_mid_plane_x.definition.type = "iso-surface"
iso_surf2 = surf_mid_plane_x.definition.iso_surface
iso_surf2.field = "x-coordinate"
iso_surf2.iso_value = -0.174
p7 = GraphicsWindow()
p7.plot(surf_mid_plane_x)

###############################################################################
# Create iso-surface using velocity magnitude
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an iso-surface using the velocity magnitude.

surf_vel_contour = graphics.Surfaces.create()
surf_vel_contour.definition.type = "iso-surface"
iso_surf3 = surf_vel_contour.definition.iso_surface
iso_surf3.field = "velocity-magnitude"
iso_surf3.rendering = "contour"
iso_surf3.iso_value = 0.0
p8 = GraphicsWindow()
p8.plot(surf_vel_contour)

###############################################################################
# Create temperature contour on mid-plane and outlet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a temperature contour on the mid-plane and the outlet.

temperature_contour = graphics.Contours.create()
temperature_contour.field = "temperature"
temperature_contour.surfaces_list = [surf_mid_plane_x.name, surf_outlet_plane.name]
p9 = GraphicsWindow()
p9.plot(temperature_contour)

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
temperature_contour_manifold = graphics.Contours.create(
    field="temperature",
    surfaces_list=cont_surfaces_list,
)
p10 = GraphicsWindow()
p10.plot(temperature_contour_manifold)

###############################################################################
# Create vector
# ~~~~~~~~~~~~~
# Create a vector on a predefined surface.

velocity_vector = graphics.Vectors.create(
    field="pressure",
    surfaces_list=["solid_up:1:830"],
    scale=2,
)
p11 = GraphicsWindow()
p11.plot(velocity_vector)

###############################################################################
# Create Pathlines
# ~~~~~~~~~~~~~~~~
# Create a pathlines on a predefined surface.

pathlines = graphics.Pathlines.create()
pathlines.field = "velocity-magnitude"
pathlines.surfaces_list = ["inlet", "inlet1", "inlet2"]
p12 = GraphicsWindow()
p12.plot(pathlines)

###############################################################################
# Create plot object
# ~~~~~~~~~~~~~~~~~~
# Create the plot object for the session.

plots_session = Plots(solver_session)

###############################################################################
# Create XY plot
# ~~~~~~~~~~~~~~
# Create the default XY plot.

xy_plot = plots_session.XYPlots.create(
    surfaces_list=["outlet"],
    y_axis_function="temperature",
)
p13 = PlotterWindow()
p13.plot(xy_plot)

###############################################################################
# Create residual plot
# ~~~~~~~~~~~~~~~~~~~~~~
# Create and display the residual plot.

residual = plots_session.Monitors.create()
residual.monitor_set_name = "residual"
p14 = PlotterWindow()
p14.plot(residual)

###############################################################################
# Solve and plot solution monitors
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Solve and plot solution monitors.

solver_session.solution.initialization.hybrid_initialize()
solver_session.solution.run_calculation.iterate(iter_count=5)


mass_bal_rplot = plots_session.Monitors.create()
mass_bal_rplot.monitor_set_name = "mass-bal-rplot"
p15 = PlotterWindow()
p15.plot(mass_bal_rplot)

point_vel_rplot = plots_session.Monitors.create(monitor_set_name="point-vel-rplot")
p16 = PlotterWindow()
p16.plot(point_vel_rplot)

###############################################################################
# Close Fluent
# ~~~~~~~~~~~~
# Close Fluent.

solver_session.exit()
