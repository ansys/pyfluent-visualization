.. _ref_plots:

Plots
=====
.. autoclass:: ansys.fluent.visualization.matplotlib.matplot_objects.Plots


In the following example, a ``Plots`` object is instantiated with a Fluent session
as its context. The ``Plots`` object is used to generate and plot two XY plots and
a monitor plot. 

.. code-block:: python

        from ansys.fluent.visualization.matplotlib import Plots
    
        plots_session = Plots(session)
        plot1 = plots_session.XYPlots["plot-1"]        
        plot1.surfaces_list = ['symmetry', 'wall']
        plot1.y_axis_function = "temperature"
        plot1.plot("window-0")        
        
        
        #To plot data on local surface created in PyVista
        
        from ansys.fluent.visualization.pyvista import  Graphics        
        pyvista_surface_provider = Graphics(session).Surfaces       
        plots_session = Plots(session, pyvista_surface_provider)
        plot2 = plots_session.XYPlots["plot-2"]         
        plot2.surfaces_list = ['iso-surface-1']
        plot2.y_axis_function = "temperature"
        plot2.plot("window-0")        
        
        
        #To plot monitors
        
        monitor1=plots_session.Monitors["monitor-1"]                       
        monitor1.monitor_set_name = "residual"
        monitor1.plot("window-0")        
        
.. toctree::
   :maxdepth: 2
   :hidden:
      
   xyplot 
   monitorplot    
 

