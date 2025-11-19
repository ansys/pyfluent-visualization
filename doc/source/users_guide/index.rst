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
    from ansys.fluent.visualization import config

    config.interactive = False
    config.view = "isometric"

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
    from ansys.fluent.core.solver import WallBoundaries

    mesh = Mesh(solver=solver_session, show_edges=True, surfaces=WallBoundaries(settings_source=solver_session))
    window = GraphicsWindow()
    window.add_graphics(mesh, position=(0, 0))

    mesh = Mesh(solver=solver_session, surfaces=WallBoundaries(settings_source=solver_session))
    window.add_graphics(mesh, position=(0, 1))
    window.show()

Display plane-surface
~~~~~~~~~~~~~~~~~~~~~
Create and visualize a plane surface at a specified z-coordinate:

.. code-block:: python

    from ansys.fluent.visualization import PlaneSurface

    surf_xy_plane = PlaneSurface.create_xy_plane(solver=solver_session, z=-0.0441921)
    window = GraphicsWindow()
    window.add_graphics(surf_xy_plane)
    window.show()

The same plane can also be created using point and normal:

.. code-block:: python

    from ansys.fluent.visualization import PlaneSurface

    surf_xy_plane = PlaneSurface.create_from_point_and_normal(
        solver=solver_session, point=[0.0, 0.0, -0.0441921], normal=[0.0, 0.0, 1.0]
    )

Display iso-surface
~~~~~~~~~~~~~~~~~~~
Generate an iso-surface based on the y-coordinate:

.. code-block:: python

    from ansys.fluent.visualization import IsoSurface

    surf_outlet_plane = IsoSurface.create(
        solver=solver_session,
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
    from ansys.fluent.core.solver import WallBoundaries
    from ansys.units import VariableCatalog

    temperature_contour_manifold = Contour(
        solver=solver_session,
        field=VariableCatalog.TEMPERATURE,
        surfaces=WallBoundaries(settings_source=solver_session),
    )
    window = GraphicsWindow()
    window.add_graphics(temperature_contour_manifold)
    window.show()

Display vector
~~~~~~~~~~~~~~
Visualize velocity vectors over a selected surface:

.. code-block:: python

    from ansys.fluent.visualization import Vector
    from ansys.fluent.core.solver import WallBoundary
    from ansys.units import VariableCatalog

    velocity_vector = Vector(
        solver=solver_session,
        field=VariableCatalog.VELOCITY_X,
        surfaces=[WallBoundary(settings_source=solver_session, name="solid_up:1:830")],
        scale=20,
    )
    window = GraphicsWindow()
    window.add_graphics(velocity_vector)
    window.show()

Display pathlines
~~~~~~~~~~~~~~~~~
Visualize pathlines to analyze flow patterns:

.. code-block:: python

    from ansys.fluent.visualization import Pathline
    from ansys.fluent.core.solver import VelocityInlets
    from ansys.units import VariableCatalog

    pathlines = Pathline(solver=solver_session)
    pathlines.field = VariableCatalog.VELOCITY_MAGNITUDE
    pathlines.surfaces = VelocityInlets(settings_source=solver_session)

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
    from ansys.fluent.core.solver import PressureOutlets
    from ansys.units import VariableCatalog

    xy_plot = XYPlot(
        solver=solver_session,
        surfaces=PressureOutlets(settings_source=solver_session),
        y_axis_function=VariableCatalog.TEMPERATURE,
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

- At the end of every time step during the calculation

.. code-block:: python

    from ansys.fluent.visualization import Contour, XYPlot, Monitor, GraphicsWindow
    from ansys.fluent.core import SolverEvent

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

    contour_window.real_time_update(
        events=[SolverEvent.SOLUTION_INITIALIZED, SolverEvent.ITERATION_ENDED]
    )

    xy_plot_window.real_time_update(
        events=[SolverEvent.SOLUTION_INITIALIZED, SolverEvent.ITERATION_ENDED]
    )

    monitor_window.real_time_update(
        events=[SolverEvent.SOLUTION_INITIALIZED, SolverEvent.ITERATION_ENDED]
    )

    solver_session.settings.solution.initialization.hybrid_initialize()
    solver_session.settings.solution.run_calculation.iterate(iter_count=50)

These updates are implemented using explicit callback registrations.
Additionally, animations can be created from a graphics window.

Context-managed graphics workflow
---------------------------------
PyFluent-Visualization also supports a context-managed workflow with the
``using()`` interface. A context manager automatically handles setup and
cleanup of solver sessions and graphics containers, ensuring that resources are
released cleanly when the block completes.

This approach improves readability, avoids manual window management, and
prevents graphics objects from remaining open longer than intended. It is
especially helpful when generating multiple plots or exporting images in a
scripted workflow.

The following example demonstrates context-managed creation and display of a
mesh visualization:

.. code-block:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples
    from ansys.fluent.core.solver import WallBoundaries, using
    from ansys.fluent.visualization import Mesh, GraphicsWindow

    # Download input files
    case = examples.download_file(
        "exhaust_system.cas.h5", "pyfluent/exhaust_system"
    )
    data = examples.download_file(
        "exhaust_system.dat.h5", "pyfluent/exhaust_system"
    )

    # Launch Fluent
    solver = pyfluent.launch_fluent(mode=pyfluent.FluentMode.SOLVER)
    solver.settings.file.read_case(case)
    solver.settings.file.read_data(data)

    # Context-managed workflow
    with using(solver):

        # Create a graphics window
        window = GraphicsWindow()

        # Add mesh displays
        window.add_graphics(Mesh(show_edges=True, surfaces=WallBoundaries()), position=(0, 0))
        window.add_graphics(Mesh(surfaces=WallBoundaries()), position=(0, 1))

        # Export and display
        window.save_graphics("mesh_view.pdf")
        window.show()

Using this pattern ensures that both the Fluent session and graphics containers
are closed safely and consistently when the code block finishes. It also
helps maintain clean, predictable behavior in larger automated
post-processing workflows.

This guide provides a structured approach to using PyFluent-Visualization.
For detailed usage of individual modules,
refer to the respective module documentation, see :ref:`ref_visualization`.

.. toctree::
   :hidden:
   :maxdepth: 2
