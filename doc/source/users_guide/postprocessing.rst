Analyzing your results
======================
PyFluent postprocessing supports graphics and plotting.

Rendering graphics objects
--------------------------
The visualization package library is used for rendering graphics objects.
The following graphics operations are supported.

Displaying mesh objects
~~~~~~~~~~~~~~~~~~~~~~~
The following example demonstrates how you can display the mesh object:

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

    session = pyfluent.launch_fluent(precision="double", processor_count=2)

    session.solver.tui.file.read_case(case_file_name=import_case)
    session.solver.tui.file.read_data(case_file_name=import_data)

    graphics = Graphics(session=session)
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

Displaying iso-surfaces
~~~~~~~~~~~~~~~~~~~~~~~
The following example demonstrates how you can display the iso-surface:

.. code:: python

    surf_outlet_plane = graphics.Surfaces["outlet-plane"]
    surf_outlet_plane.surface.type = "iso-surface"
    iso_surf1 = surf_outlet_plane.surface.iso_surface
    iso_surf1.field = "y-coordinate"
    iso_surf1.iso_value = -0.125017
    surf_outlet_plane.display("window-2")

Displaying contours
~~~~~~~~~~~~~~~~~~~
The following example demonstrates how you can display the contour object:

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

Displaying vectors
~~~~~~~~~~~~~~~~~~
The following example demonstrates how you can display the vector object:

.. code:: python

    velocity_vector = graphics.Vectors["velocity-vector"]
    velocity_vector.surfaces_list = ["outlet-plane"]
    velocity_vector.scale = 1
    velocity_vector.display("window-4")

Plotting your data
------------------
The following plotting operations are supported.

Displaying XY plots
~~~~~~~~~~~~~~~~~~~
The following example demonstrates how you can display the XY plot:

.. code:: python

    plots_session_1 = Plots(session)
    xy_plot = plots_session_1.XYPlots["xy-plot"]
    xy_plot.surfaces_list = ["outlet"]
    xy_plot.y_axis_function = "temperature"
    xy_plot.plot("window-5")

Plotting residual plots
~~~~~~~~~~~~~~~~~~~~~~~~
The following example demonstrates how you can plot solution residual
plots:

.. code:: python


    matplotlib_plots1 = Plots(session)
    residual = matplotlib_plots1.Monitors["residual"]
    residual.monitor_set_name = "residual"
    residual.plot("window-6")

Plotting solution monitors
~~~~~~~~~~~~~~~~~~~~~~~~~~
The following example demonstrates how you can plot solution monitors:

.. code:: python

    session.solver.tui.solve.initialize.hyb_initialization()
    session.solver.tui.solve.set.number_of_iterations(50)
    session.solver.tui.solve.iterate()
    session.monitors_manager.get_monitor_set_names()
    matplotlib_plots1 = Plots(session)
    mass_bal_rplot = matplotlib_plots1.Monitors["mass-bal-rplot"]
    mass_bal_rplot.monitor_set_name = "mass-bal-rplot"
    mass_bal_rplot.plot("window-7")