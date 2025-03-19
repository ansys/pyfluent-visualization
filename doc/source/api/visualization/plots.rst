.. _ref_plots:

Plots
=====
.. autoclass:: ansys.fluent.visualization.plotter.plotter_objects.Plots


In the following example, a ``Plots`` object is instantiated with a Fluent session
as its context. The ``Plots`` object is used to generate and plot two XY plots and
a monitor plot. 

.. code-block:: python

        from ansys.fluent.visualization import GraphicsWindow, XYPlot, Monitor
    
        plot1 = XYPlot(solver=session)
        plot1.surfaces = ['symmetry', 'wall']
        plot1.y_axis_function = "temperature"
        plot1.plot("window-0")

        plotter = GraphicsWindow()
        plotter.add_graphics(plot1)
        plotter.show()
        
        #To plot monitors
        
        monitor1 = Monitor(solver=session)
        monitor1.monitor_set_name = "residual"

        plotter = GraphicsWindow()
        plotter.add_graphics(monitor1)
        plotter.show()

.. toctree::
   :maxdepth: 2
   :hidden:
      
   xyplot 
   monitorplot    
 

