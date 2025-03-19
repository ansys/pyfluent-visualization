.. _ref_xyplot:

XY plot
=======

.. autopostdoc:: ansys.fluent.visualization.containers.XYPlot

Creates a xy-plot object.

.. code-block:: python

    from ansys.fluent.visualization import XYPlot

    xy_plot = XYPlot(
        solver=solver_session,
        surfaces=["outlet"],
        y_axis_function="temperature",
    )
