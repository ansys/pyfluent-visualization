.. _ref_matplot_windows_manager:

Matplotlib windows manager
========================== 

The ``MatplotWindowsManager`` class provides for managing and directly interacting
with Matplotlib windows. By registering these methods with ``EventsManager``, you can
update plots during run time.

The following example updates ``window-1`` and ``window-2`` during solution initialization 
and whenever data is read. During the calculation, it also updates both windows at the end
of every time step.

.. code-block:: python

    from ansys.fluent.visualization.matplotlib import Plots
    from ansys.fluent.visualization.matplotlib import matplot_windows_manager
    
    plots_session = Plots(session)
    
    #Create xy plot.
    plot1 = plots_session.XYPlots["plot-1"]
    plot1.surfaces_list = ['symmetry']
    plot1.y_axis_function = "temperature"
    
    
    # Plot XY plot on window-1.
    plot1.plot("window-1")
    
    #Create monitor plot.
    monitor1 = plots_session.Monitors["monitor-1"]
    monitor1.monitor_set_name = "residual"
    
    
    #Plot monitor on window-2.
    monitor1.plot("window-2")   
    
    # Create callback that refreshes window-1 and window-2.    
    def auto_refresh_plot(session_id, event_info):    
        matplot_windows_manager.refresh_windows(session_id, ["window-1", "window-2"])        
           
    #Register this callback with server events.    
    cb_init_id = session.events_manager.register_callback('InitializedEvent', auto_refresh_plot)
    cb_data_read_id = session.events_manager.register_callback('DataReadEvent', auto_refresh_plot)
    cb_time_step_ended_id = session.events_manager.register_callback('TimestepEndedEvent', auto_refresh_plot)         


.. autoclass:: ansys.fluent.visualization.matplotlib.matplot_windows_manager.MatplotWindowsManager
   :members: