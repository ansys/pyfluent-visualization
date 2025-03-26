.. _ref_integration:

==================================================================
Integrating Custom Rendering Libraries with PyFluent-Visualization
==================================================================
PyFluent-Visualization uses PyVista as the default graphics rendering tool
and Matplotlib for plotting 2D data. It also allows users to configure
other Python-supported tools for rendering data. This is achieved by extending
the ``AbstractRenderer`` class and implementing the required methods.

Steps to Integrate a Custom Rendering Library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Follow the steps below to integrate a custom graphics rendering library
into PyFluent-Visualization:

1. Navigate to the Source Directory:
    - Locate the directory: (for example, src/ansys/fluent/visualization/graphics)

2. Use the Abstract Class as a Base:
    - Open the abstract_graphics_defns.py file.
    - The ``AbstractRenderer`` class defines the required interface for a custom renderer.

3. Create Your Own Renderer Implementation:
    - Create a new Python file (for example, custom_graphics_defns.py) inside a python package in the same directory.
    - Extend the ``AbstractRenderer`` class and implement its methods:

.. code:: python

    >>> class CustomRenderer(AbstractRenderer):
    >>>     def show(self):
    >>>         """Display the rendered graphics."""
    >>>         pass
    >>>
    >>>     def render(self, mesh, **kwargs):
    >>>         """Render the provided mesh using the custom graphics library."""
    >>>         pass
    >>>
    >>>     def save_graphic(self, file_name: str):
    >>>         """Save the rendered graphic to a file."""
    >>>         pass
    >>>
    >>>     def get_animation(self, win_id: str):
    >>>         """Animate the specified window."""
    >>>         pass
    >>>
    >>>     def close(self):
    >>>         """Close the graphics window."""
    >>>     pass


4. Register and Use Your Renderer
    - Ensure your custom renderer is placed in a directory accessible
    by PyFluent-Visualization.

    - Use the custom renderer in your visualization workflow:

.. code:: python

    >>> from custom_graphics_defns import CustomRenderer

    >>> renderer = CustomRenderer()
    >>> # `mesh_data` is the data to be rendered
    >>> renderer.render(mesh_data)
    >>> renderer.show()


5. Refer to Existing Implementations

To better understand how to implement your renderer, refer to existing implementations:
   - `pyvista.graphics_defns.py` (PyVista-based rendering)
   - `matplotlib.plotter_defns.py` (Matplotlib-based rendering)

By following these steps, you can seamlessly integrate any Python-based graphics
rendering library into PyFluent-Visualization. This approach provides flexibility
to leverage different rendering engines while maintaining a consistent interface.
