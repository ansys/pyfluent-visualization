.. _ref_user_guide:

==========
User guide
==========
You can use PyFluent-Visualization for postprocessing of Fluent results
to display graphics objects and plot data.

Graphics operations
-------------------
Examples follow for graphics operations that PyFluent-Visualization
supports.

Display mesh
~~~~~~~~~~~~
This example shows how you can display a mesh:

.. code:: python

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples
    from ansys.fluent.visualization import set_config
    from ansys.fluent.visualization.matplotlib import Plots
    from ansys.fluent.visualization.pyvista import Graphics

    set_config(blocking=True, set_view_on_display="isometric")

    import_case = examples.download_file(
        filename="exhaust_system.cas.h5", directory="pyfluent/exhaust_system"
    )

    import_data = examples.download_file(
        filename="exhaust_system.dat.h5", directory="pyfluent/exhaust_system"
    )

    solver_session = pyfluent.launch_fluent(precision="double", processor_count=2, mode="solver")

    solver_session.tui.file.read_case(import_case)
    solver_session.tui.file.read_data(import_data)

    graphics = Graphics(session=solver_session)
    mesh1 = graphics.Meshes["mesh-1"]
    mesh1.show_edges = True
    mesh1.surfaces_list = [
        "in1",
        "in2",
        "in3",
        "out1",
        "solid_up:1",
        "solid_up:1:830",
        "solid_up:1:830-shadow",
    ]
    mesh1.display("window-1")

Display iso-surface
~~~~~~~~~~~~~~~~~~~
This example shows how you can display an iso-surface:

.. code:: python

    surf_outlet_plane = graphics.Surfaces["outlet-plane"]
    surf_outlet_plane.surface.type = "iso-surface"
    iso_surf1 = surf_outlet_plane.surface.iso_surface
    iso_surf1.field = "y-coordinate"
    iso_surf1.iso_value = -0.125017
    surf_outlet_plane.display("window-2")

Display contour
~~~~~~~~~~~~~~~
This example shows how you can display a contour:

.. code:: python

    temperature_contour_manifold = graphics.Contours["contour-temperature-manifold"]
    temperature_contour_manifold.field = "temperature"
    temperature_contour_manifold.surfaces_list = [
        "in1",
        "in2",
        "in3",
        "out1",
        "solid_up:1",
        "solid_up:1:830",
    ]
    temperature_contour_manifold.display("window-3")

Display vector
~~~~~~~~~~~~~~
This example shows how you can display a vector:

.. code:: python

    velocity_vector = graphics.Vectors["velocity-vector"]
    velocity_vector.surfaces_list = ["outlet-plane"]
    velocity_vector.scale = 1
    velocity_vector.display("window-4")

Plot operations
---------------
Examples follow for plot operations that PyFluent-Visualization
supports.

Display plot
~~~~~~~~~~~~
This example shows how you can display the XY plot:

.. code:: python

    plots_session_1 = Plots(solver_session)
    xy_plot = plots_session_1.XYPlots["xy-plot"]
    xy_plot.surfaces_list = ["outlet"]
    xy_plot.y_axis_function = "temperature"
    xy_plot.plot("window-5")

Display solution residual plot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This example shows how you can display the solution residual plot:

.. code:: python


    matplotlib_plots1 = Plots(solver_session)
    residual = matplotlib_plots1.Monitors["residual"]
    residual.monitor_set_name = "residual"
    residual.plot("window-6")

Display solution monitors plot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This example shows how you can display the solution monitors plot:

.. code:: python

    solver_session.tui.solve.initialize.hyb_initialization()
    solver_session.tui.solve.set.number_of_iterations(50)
    solver_session.tui.solve.iterate()
    solver_session.monitors_manager.get_monitor_set_names()
    matplotlib_plots1 = Plots(solver_session)
    mass_bal_rplot = matplotlib_plots1.Monitors["mass-bal-rplot"]
    mass_bal_rplot.monitor_set_name = "mass-bal-rplot"
    mass_bal_rplot.plot("window-7")
