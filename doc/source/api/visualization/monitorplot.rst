.. _ref_monitorplot:

MonitorPlot
===========

.. autopostdoc:: ansys.fluent.visualization.plotter.plotter_objects.Monitor

Creates a monitor object.

.. code-block:: python

    from ansys.fluent.visualization import Monitor

    residual = Monitor(solver=solver_session)
    residual.monitor_set_name = "residual"
