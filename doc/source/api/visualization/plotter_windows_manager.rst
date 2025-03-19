.. _ref_plotter_windows_manager:

Plotter windows manager
=======================

The ``PlotterWindowsManager`` class provides for managing and directly interacting
with Matplotlib windows. By registering these methods with ``EventsManager``, you can
update plots during run time.

The following example updates ``p_xy`` and ``p_res`` during solution initialization
and whenever data is read. During the calculation, it also updates both windows at the end
of every time step.

.. code-block:: python

    from ansys.fluent.visualization import XYPlot, Monitor, GraphicsWindow
    
    plots_session = Plots(session)
    
    #Create xy plot.
    plot1 = XYPlot(solver=session)
    plot1.surfaces = ['symmetry']
    plot1.y_axis_function = "temperature"
    
    
    # Plot XY plot.
    p_xy = GraphicsWindow()
    p_xy.add_graphics(plot1)
    p_xy.show()
    
    #Create monitor plot.
    monitor1 = Monitor(solver=session)
    monitor1.monitor_set_name = "residual"
    
    
    #Plot monitor.
    p_res = GraphicsWindow()
    p_res.add_graphics(monitor1)
    p_res.show()
    
    # Create callback that refreshes 'p_xy' and 'p_res'.
    def auto_refresh_plot(session_id, event_info):
        # 'p_xy' and 'p_res' uses 'plotter_windows_manager' in its implementation
        p_xy.refresh_windows(session.id)
        p_res.refresh_windows(session.id)
           
    #Register this callback with server events.    
    cb_init_id = session.events.register_callback('InitializedEvent', auto_refresh_plot)
    cb_data_read_id = session.events.register_callback('DataReadEvent', auto_refresh_plot)
    cb_time_step_ended_id = session.events.register_callback('TimestepEndedEvent', auto_refresh_plot)

.. autoclass:: ansys.fluent.visualization.plotter.plotter_windows_manager.PlotterWindowsManager
   :members: