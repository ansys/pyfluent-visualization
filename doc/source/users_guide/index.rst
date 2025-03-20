.. _ref_user_guide:

==========
User guide
==========
You can use PyFluent-Visualization for postprocessing of Fluent results
to display graphics objects and plot data.

Launch Fluent and read data
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

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

Graphics operations
-------------------
Graphics operations that PyFluent-Visualization supports:

Display mesh
~~~~~~~~~~~~

.. code-block:: python

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

    mesh_object_1 = Mesh(solver=solver_session, show_edges=True, surfaces=mesh_surfaces_list)
    mesh_window = GraphicsWindow(grid=(1, 2))
    mesh_window.add_graphics(mesh1, position=(0, 0))

    mesh_object_2 = Mesh(solver=solver_session, surfaces=mesh_surfaces_list)
    mesh_object_2.show_edges = False

    mesh_window.add_graphics(mesh2, position=(0, 1))
    mesh_window.show()

Display plane-surface
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ansys.fluent.visualization import Surface

    surf_xy_plane = Surface(solver=solver_session)
    surf_xy_plane.definition.type = "plane-surface"
    surf_xy_plane.definition.plane_surface.creation_method = "xy-plane"
    plane_surface_xy = surf_xy_plane.definition.plane_surface.xy_plane
    plane_surface_xy.z = -0.0441921
    surface_window = GraphicsWindow()
    surface_window.add_graphics(surf_xy_plane)
    surface_window.show()

Display iso-surface
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    surf_outlet_plane = Surface(solver=solver_session)
    surf_outlet_plane.definition.type = "iso-surface"
    iso_surf1 = surf_outlet_plane.definition.iso_surface
    iso_surf1.field = "y-coordinate"
    iso_surf1.iso_value = -0.125017
    surface_window = GraphicsWindow()
    surface_window.add_graphics(surf_outlet_plane)
    surface_window.show()

Display contour
~~~~~~~~~~~~~~~

.. code-block:: python

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
    contour_window = GraphicsWindow()
    contour_window.add_graphics(temperature_contour_manifold)
    contour_window.show()

Display vector
~~~~~~~~~~~~~~

.. code-block:: python

    from ansys.fluent.visualization import Vector

    velocity_vector = Vector(
        solver=solver_session,
        field="pressure",
        surfaces=["solid_up:1:830"],
        scale=2,
    )
    vector_window = GraphicsWindow()
    vector_window.add_graphics(velocity_vector)
    vector_window.show()

Display pathlines
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ansys.fluent.visualization import Pathline

    pathlines = Pathline(solver=solver_session)
    pathlines.field = "velocity-magnitude"
    pathlines.surfaces = ["inlet", "inlet1", "inlet2"]

    pathlines_window = GraphicsWindow()
    pathlines_window.add_graphics(pathlines)
    pathlines_window.show()

Plot operations
---------------
Plot operations that PyFluent-Visualization supports:

Display plot
~~~~~~~~~~~~

.. code-block:: python

    from ansys.fluent.visualization import XYPlot

    xy_plot = XYPlot(
        solver=solver_session,
        surfaces=["outlet"],
        y_axis_function="temperature",
    )
    xy_plot_window = GraphicsWindow()
    xy_plot_window.add_graphics(xy_plot)
    xy_plot_window.show()

Display solution residual plot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ansys.fluent.visualization import Monitor

    residual = Monitor(solver=solver_session)
    residual.monitor_set_name = "residual"
    monitor_window = GraphicsWindow()
    monitor_window.add_graphics(residual)
    monitor_window.show()

Display solution monitors plot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    solver_session.settings.solution.initialization.hybrid_initialize()
    solver_session.settings.solution.run_calculation.iterate(iter_count=50)

    mass_bal_rplot = Monitor(solver=solver_session)
    mass_bal_rplot.monitor_set_name = "mass-bal-rplot"
    monitor_window = GraphicsWindow(grid=(1, 2))
    monitor_window.add_graphics(mass_bal_rplot, position=(0, 0))

    point_vel_rplot = Monitor(solver=solver_session, monitor_set_name="point-vel-rplot")
    monitor_window.add_graphics(point_vel_rplot, position=(0, 1))
    monitor_window.show()

Interactive Graphics
--------------------
The ``GraphicsWindow`` class provides for managing and directly interacting
with the graphics window. By registering the window with ``EventsManager``, you
can update graphics during run time and create animations.

The following example updates the graphics window (contour_window, xy_plot_window and
monitor_window) during solution initialization and whenever data is read.
During the calculation, it also updates the graphics window at
the end of every time step. These are done via. explicit callback registrations.
You can create an animation as well from a graphics window.

.. code-block:: python

    from ansys.fluent.visualization import Contour, XYPlot, Monitor, GraphicsWindow

    contour_object = Contour(
        solver=solver_session, field="velocity-magnitude", surfaces=["symmetry"]
    )

    xy_plot_object = XYPlot(solver=solver_session)
    xy_plot_object.surfaces = ['symmetry']
    xy_plot_object.y_axis_function = "temperature"

    monitor_object = Monitor(solver=solver_session)
    monitor_object.monitor_set_name = "residual"

    contour_window = GraphicsWindow()
    contour_window.add_graphics(contour_object)
    contour_window.show()

    xy_plot_window = GraphicsWindow()
    xy_plot_window.add_graphics(xy_plot_object)
    xy_plot_window.show()

    monitor_window = GraphicsWindow()
    monitor_window.add_graphics(monitor1)
    monitor_window.show()

    def auto_refresh_graphics(session, event_info):
        contour_window.refresh(session.id)
        xy_plot_window.refresh(session.id)
        monitor_window.refresh(session.id)

    #Register this callback with server events.
    solver_session.events.register_callback('InitializedEvent', auto_refresh_graphics)
    solver_session.events.register_callback('DataReadEvent', auto_refresh_graphics)
    solver_session.events.register_callback('TimestepEndedEvent', auto_refresh_graphics)

    #Create animation for contour.
    contour_window.animate(solver_session.id)

    solver_session.settings.solution.initialization.hybrid_initialize()
    solver_session.settings.solution.run_calculation.iterate(iter_count=50)
