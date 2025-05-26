.. _ref_user_guide:

==========
User guide
==========
PyFluent-Visualization enables post-processing of Fluent results,
allowing you to display graphical objects and plot data efficiently.

Launch Fluent and read data
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use the following script to launch Fluent and load your case and data files:

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

    solver_session = pyfluent.launch_fluent(
        precision=pyfluent.Precision.DOUBLE,
        processor_count=2,
        mode=pyfluent.FluentMode.SOLVER,
    )

    solver_session.settings.file.read_case(file_name=import_case)
    solver_session.settings.file.read_data(file_name=import_data)

Graphics operations
-------------------
PyFluent-Visualization supports various graphical operations.

Display mesh
~~~~~~~~~~~~
The following example demonstrates how to display a mesh with and without edges:

.. code-block:: python

    from ansys.fluent.visualization import GraphicsWindow, Mesh

    mesh = Mesh(solver=solver_session, show_edges=True, surfaces=["in1", "in2", "in3"])
    window = GraphicsWindow()
    window.add_graphics(mesh, position=(0, 0))

    mesh = Mesh(solver=solver_session, surfaces=["in1", "in2", "in3"])
    window.add_graphics(mesh, position=(0, 1))
    window.show()

Display plane-surface
~~~~~~~~~~~~~~~~~~~~~
Create and visualize a plane surface at a specified z-coordinate:

.. code-block:: python

    from ansys.fluent.visualization import Surface

    surf_xy_plane = Surface(solver=solver_session)
    surf_xy_plane.type = "plane-surface"
    surf_xy_plane.creation_method = "xy-plane"
    surf_xy_plane.z = -0.0441921
    window = GraphicsWindow()
    window.add_graphics(surf_xy_plane)
    window.show()

Display iso-surface
~~~~~~~~~~~~~~~~~~~
Generate an iso-surface based on the y-coordinate:

.. code-block:: python

    surf_outlet_plane = Surface(
        solver=solver_session,
        type="iso-surface",
        field="y-coordinate",
        iso_value=-0.125017
        )
    window = GraphicsWindow()
    window.add_graphics(surf_outlet_plane)
    window.show()

Display contour
~~~~~~~~~~~~~~~
Plot a temperature contour over selected surfaces:

.. code-block:: python

    from ansys.fluent.visualization import Contour

    temperature_contour_manifold = Contour(
        solver=solver_session,
        field="temperature",
        surfaces=["in1", "in2", "in3"],
    )
    window = GraphicsWindow()
    window.add_graphics(temperature_contour_manifold)
    window.show()

Display vector
~~~~~~~~~~~~~~
Visualize velocity vectors over a selected surface:

.. code-block:: python

    from ansys.fluent.visualization import Vector

    velocity_vector = Vector(
        solver=solver_session,
        field="pressure",
        surfaces=["solid_up:1:830"],
        scale=2,
    )
    window = GraphicsWindow()
    window.add_graphics(velocity_vector)
    window.show()

Display pathlines
~~~~~~~~~~~~~~~~~
Visualize pathlines to analyze flow patterns:

.. code-block:: python

    from ansys.fluent.visualization import Pathline

    pathlines = Pathline(solver=solver_session)
    pathlines.field = "velocity-magnitude"
    pathlines.surfaces = ["inlet", "inlet1", "inlet2"]

    window = GraphicsWindow()
    window.add_graphics(pathlines)
    window.show()

Plot operations
---------------
PyFluent-Visualization supports various plot operations.

Display plot
~~~~~~~~~~~~
Generate an XY plot of temperature variations at an outlet:

.. code-block:: python

    from ansys.fluent.visualization import XYPlot

    xy_plot = XYPlot(
        solver=solver_session,
        surfaces=["outlet"],
        y_axis_function="temperature",
    )
    window = GraphicsWindow()
    window.add_plot(xy_plot)
    window.show()

Display solution residual plot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Plot solution residuals:

.. code-block:: python

    from ansys.fluent.visualization import Monitor

    residual = Monitor(solver=solver_session)
    residual.monitor_set_name = "residual"
    window = GraphicsWindow()
    window.add_plot(residual)
    window.show()

Display solution monitors plot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Monitor solution convergence using mass balance and velocity plots:

.. code-block:: python

    solver_session.settings.solution.initialization.hybrid_initialize()
    solver_session.settings.solution.run_calculation.iterate(iter_count=50)

    mass_bal_rplot = Monitor(solver=solver_session)
    mass_bal_rplot.monitor_set_name = "mass-bal-rplot"
    window = GraphicsWindow()
    window.add_plot(mass_bal_rplot, position=(0, 0))

    point_vel_rplot = Monitor(solver=solver_session, monitor_set_name="point-vel-rplot")
    window.add_plot(point_vel_rplot, position=(0, 1))
    window.show()

Interactive Graphics
--------------------
The ``GraphicsWindow`` class provides functionality for managing and directly
interacting with the graphics window. By registering the window with ``EventsManager``,
you can dynamically update graphics during runtime and create animations.

The following example demonstrates how to update multiple graphics windows
(contour_window, xy_plot_window, and monitor_window) during different solution
stages. Graphics updates occur:

- During solution initialization

- Whenever data is read

- At the end of every time step during the calculation

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
    xy_plot_window.add_plot(xy_plot_object)
    xy_plot_window.show()

    monitor_window = GraphicsWindow()
    monitor_window.add_plot(monitor1)
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

These updates are implemented using explicit callback registrations.
Additionally, animations can be created from a graphics window.

This guide provides a structured approach to using PyFluent-Visualization.
For detailed usage of individual modules,
refer to the respective module documentation, see :ref:`ref_visualization`.
