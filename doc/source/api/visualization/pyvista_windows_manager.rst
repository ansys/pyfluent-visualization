.. _ref_pyvista_windows_manager:

PyVista Windows Manager
=======================   

This class manages `PyVista` windows and provides methods to directly interact with them.
By registering these methods to EventsManager, graphics can be updated during run 
time and animations can be created.

The following example will update `window-1` during solution initialization and whenever data 
is read. Also during calculation it will update `window-1` at end of every time step and
will create animation.

`Important`:Animation will be saved whenever window is closed.

.. code-block:: python

    from ansys.fluent.visualization.pyvista import Graphics
    from ansys.fluent.visualization.pyvista import pyvista_windows_manager
    
    graphics_session = Graphics(session)
    
    #Create contour.
    contour1 = graphics_session.Contours["contour-1"]
    contour1.field = "velocity-magnitude"
    contour1.surfaces_list = ['symmetry']
    
    #Display contour on window-1.
    contour1.display("window-1")
    
    #Create callback which refreshes window-1.    
    def auto_refersh_contour(session_id, event_info):    
        pyvista_windows_manager.refresh_windows(session_id, ["window-1"])        
           
    #Register this callback with server events.    
    cb_init_id = session.events_manager.register_callback('InitializedEvent', auto_refersh_contour)
    cb_data_read_id = session.events_manager.register_callback('DataReadEvent', auto_refersh_contour)
    cb_time_step_ended_id = session.events_manager.register_callback('TimestepEndedEvent', auto_refersh_contour)         

    #Create animation for window-1 
    pyvista_windows_manager.animate_windows(session.id, ["window-1"])
    
    
.. autoclass:: ansys.fluent.visualization.pyvista.pyvista_windows_manager.PyVistaWindowsManager
   :members: