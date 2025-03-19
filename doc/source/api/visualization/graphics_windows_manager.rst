.. _ref_graphics_windows_manager:

Graphics windows manager
========================
The ``GraphicsWindowsManager`` class provides for managing and directly interacting
with PyVista windows. By registering these methods with ``EventsManager``, you
can update graphics during run time and create animations.

The following example updates ``p_cont`` during solution initialization and
whenever data is read. During the calculation, it also updates ``p_cont`` at
the end of every time step and creates an animation.

.. note::
  The animation is saved when the window is closed.

.. code-block:: python

    from ansys.fluent.visualization import Contour, GraphicsWindow
    
    #Create contour.
    contour1 = Contour(
        solver=session, field="velocity-magnitude", surfaces=["symmetry"]
    )
    
    #Display contour.
    p_cont = GraphicsWindow()
    p_cont.add_graphics(contour1)
    p_cont.show()
    
    #Create callback that refreshes 'p_cont'.
    def auto_refresh_contour(session, event_info):
        # 'p_cont' uses 'graphics_windows_manager' in its implementation
        p_cont.refresh_windows(session.id)

    #Register this callback with server events.    
    cb_init_id = session.events.register_callback('InitializedEvent', auto_refresh_contour)
    cb_data_read_id = session.events.register_callback('DataReadEvent', auto_refresh_contour)
    cb_time_step_ended_id = session.events.register_callback('TimestepEndedEvent', auto_refresh_contour)

    #Create animation.
    p_cont.animate_windows(session.id)
    
.. autoclass:: ansys.fluent.visualization.graphics.graphics_windows_manager.GraphicsWindowsManager
   :members: