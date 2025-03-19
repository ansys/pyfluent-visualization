.. _ref_graphics_window:

GraphicsWindow
==============
 
.. autopostdoc:: ansys.fluent.visualization.graphics.graphics_window.GraphicsWindow

Creates a window to display graphics. You can add graphics objects like a
mesh, surface or plots to this window and then display it.

.. code-block:: python

    from ansys.fluent.visualization import GraphicsWindow

    graphics_window = GraphicsWindow()
    graphics_window.add_graphics(mesh_object)
    graphics_window.display()


You can even add multiple graphics objects and display them in the same window
as a structured layout.

.. code-block:: python

    from ansys.fluent.visualization import GraphicsWindow

    graphics_window = GraphicsWindow(grid=(2, 2))
    graphics_window.add_graphics(mesh_object, position=(0, 0))
    graphics_window.add_graphics(temperature_contour, position=(0, 1))
    graphics_window.add_graphics(velocity_vector, position=(1, 0))
    graphics_window.add_graphics(xy_plot, position=(1, 1))
    graphics_window.display()
