.. _ref_user_guide:

==========
User guide
==========
You can use PyFluent-Visualization for postprocessing of Fluent results
to display graphics objects and plot data.

Graphics operations
-------------------
Examples of graphics operations that PyFluent-Visualization supports:

Launching Fluent and setting up data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You launch Fluent, read a case and hybrid initialize to get the data:

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples
    from ansys.fluent.visualization import set_config

    set_config(blocking=True, set_view_on_display="isometric")

    import_case = examples.download_file(
        file_name="exhaust_system.cas.h5", directory="pyfluent/exhaust_system"
    )

    import_data = examples.download_file(
        file_name="exhaust_system.dat.h5", directory="pyfluent/exhaust_system"
    )

    solver_session = pyfluent.launch_fluent(precision="double", processor_count=2, mode="solver")

    solver_session.tui.file.read_case(import_case)
    solver_session.tui.file.read_data(import_data)

Display mesh
~~~~~~~~~~~~
This example shows how you can display a mesh:

.. code:: python

    from ansys.fluent.visualization import GraphicsWindow, Mesh

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

Display plane-surface
~~~~~~~~~~~~~~~~~~~~~
This example shows how you can display an plane-surface:

.. code:: python

    from ansys.fluent.visualization import Surface

    surf_xy_plane = Surface(solver=solver_session)
    surf_xy_plane.definition.type = "plane-surface"
    surf_xy_plane.definition.plane_surface.creation_method = "xy-plane"
    plane_surface_xy = surf_xy_plane.definition.plane_surface.xy_plane
    plane_surface_xy.z = -0.0441921
    p2 = GraphicsWindow()
    p2.add_graphics(surf_xy_plane)
    p2.show()

Display iso-surface
~~~~~~~~~~~~~~~~~~~
This example shows how you can display an iso-surface:

.. code:: python

    surf_outlet_plane = Surface(solver=solver_session)
    surf_outlet_plane.definition.type = "iso-surface"
    iso_surf1 = surf_outlet_plane.definition.iso_surface
    iso_surf1.field = "y-coordinate"
    iso_surf1.iso_value = -0.125017
    p3 = GraphicsWindow()
    p3.add_graphics(surf_outlet_plane)
    p3.show()

Display contour
~~~~~~~~~~~~~~~
This example shows how you can display a contour:

.. code:: python

    from ansys.fluent.visualization import Contour

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
    p4 = GraphicsWindow()
    p4.add_graphics(temperature_contour_manifold)
    p4.show()

Display vector
~~~~~~~~~~~~~~
This example shows how you can display a vector:

.. code:: python

    from ansys.fluent.visualization import Vector

    velocity_vector = Vector(
        solver=solver_session,
        field="pressure",
        surfaces=["solid_up:1:830"],
        scale=2,
    )
    p5 = GraphicsWindow()
    p5.add_graphics(velocity_vector)
    p5.show()

Display pathlines
~~~~~~~~~~~~~~~~~
This example shows how you can display a pathlines:

.. code:: python

    from ansys.fluent.visualization import Pathline

    pathlines = Pathline(solver=solver_session)
    pathlines.field = "velocity-magnitude"
    pathlines.surfaces = ["inlet", "inlet1", "inlet2"]

    p6 = GraphicsWindow()
    p6.add_graphics(pathlines)
    p6.show()

Plot operations
---------------
Examples follow for plot operations that PyFluent-Visualization
supports.

Display plot
~~~~~~~~~~~~
This example shows how you can display the XY plot:

.. code:: python

    from ansys.fluent.visualization import XYPlot

    xy_plot = XYPlot(
        solver=solver_session,
        surfaces=["outlet"],
        y_axis_function="temperature",
    )
    p7 = GraphicsWindow()
    p7.add_graphics(xy_plot)
    p7.show()

Display solution residual plot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This example shows how you can display the solution residual plot:

.. code:: python

    from ansys.fluent.visualization import Monitor

    residual = Monitor(solver=solver_session)
    residual.monitor_set_name = "residual"
    p8 = GraphicsWindow()
    p8.add_graphics(residual)
    p8.show()

Display solution monitors plot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This example shows how you can display the solution monitors plot:

.. code:: python

    solver_session.settings.solution.initialization.hybrid_initialize()
    solver_session.settings.solution.run_calculation.iterate(iter_count=50)

    mass_bal_rplot = Monitor(solver=solver_session)
    mass_bal_rplot.monitor_set_name = "mass-bal-rplot"
    p9 = GraphicsWindow(grid=(1, 2))
    p9.add_graphics(mass_bal_rplot, position=(0, 0))

    point_vel_rplot = Monitor(solver=solver_session, monitor_set_name="point-vel-rplot")
    p9.add_graphics(point_vel_rplot, position=(0, 1))
    p9.show()
