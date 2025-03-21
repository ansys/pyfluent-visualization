.. _ref_configure:

=========
Configure
=========
PyFluent-Visualization uses PyVista as the default graphics rendering tool
and Matplotlib for plotting 2D data. It also allows users to configure
other Python-supported tools for rendering data.

Configuration Steps
~~~~~~~~~~~~~~~~~~~
Follow these steps to integrate additional Python libraries into PyFluent-Visualization:

1. Navigate to either:
   - `src/ansys/fluent/visualization/graphics` or
   - `src/ansys/fluent/visualization/plotter`

2. Locate the files:
   - `abstract_graphics_defns.py` (for graphics rendering)
   - `abstract_plotter_defns.py` (for 2D plotting)

3. Use these abstract definitions as a base to create your own implementations:
   - `graphics_defns.py` (for graphics rendering)
   - `plotter_defns.py` (for 2D plotting)

4. Place your custom implementation in a directory to make it accessible.

5. Refer to existing implementations as examples:
   - `pyvista.graphics_defns.py` in `src/ansys/fluent/visualization/graphics`
   - `matplotlib.plotter_defns.py` or `pyvista.plotter_defns.py` in `src/ansys/fluent/visualization/plotter`

Using this approach, you can integrate other Python-based graphics renderers or
2D plotting tools into PyFluent-Visualization.
