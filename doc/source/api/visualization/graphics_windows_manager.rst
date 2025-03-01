.. _ref_graphics_windows_manager:

Graphics windows manager
========================
The ``GraphicsWindowsManager`` class provides for managing and directly interacting
with PyVista windows. By registering these methods with ``EventsManager``, you
can update graphics during run time and create animations.

The following example updates ``window-1`` during solution initialization and
whenever data is read. During the calculation, it also updates ``window-1`` at
the end of every time step and creates an animation.

.. note::
  The animation is saved when the window is closed.

.. code-block:: python

    from ansys.fluent.visualization import Graphics
    from ansys.fluent.visualization.graphics import graphics_windows_manager
    
    graphics_session = Graphics(session)
    
    #Create contour.
    contour1 = graphics_session.Contours["contour-1"]
    contour1.field = "velocity-magnitude"
    contour1.surfaces = ['symmetry']
    
    #Display contour on window-1.
    contour1.display("window-1")
    
    #Create callback that refreshes window-1.    
    def auto_refresh_contour(session_id, event_info):    
        graphics_windows_manager.refresh_windows(session_id, ["window-1"])
           
    #Register this callback with server events.    
    cb_init_id = session.events_manager.register_callback('InitializedEvent', auto_refresh_contour)
    cb_data_read_id = session.events_manager.register_callback('DataReadEvent', auto_refresh_contour)
    cb_time_step_ended_id = session.events_manager.register_callback('TimestepEndedEvent', auto_refresh_contour)         

    #Create animation for window-1. 
    graphics_windows_manager.animate_windows(session.id, ["window-1"])
    
    
.. autoclass:: ansys.fluent.visualization.graphics.graphics_windows_manager.GraphicsWindowsManager
   :members: