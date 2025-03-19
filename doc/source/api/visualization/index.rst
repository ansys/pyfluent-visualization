.. _ref_visualization:

Visualization
=============

Postprocessing of Fluent results can be done with either built-in Fluent
postprocessing capabilities, PyVista, or Matplotlib integration.

Fluent command example
----------------------

Here visualization objects are constructed within Fluent. You can use
standard Fluent commands to write graphics to a file.

.. code:: python

  solver_session.settings.results.graphics.contour['contour-1'] = {'boundary_values': True, 'color_map': {'color': 'field-velocity', 'font_automatic': True, 'font_name': 'Helvetica', 'font_size': 0.032, 'format': '%0.2e', 'length': 0.54, 'log_scale': False, 'position': 1, 'show_all': True, 'size': 100, 'user_skip': 9, 'visible': True, 'width': 6.0}, 'coloring': {'smooth': False}, 'contour_lines': False, 'display_state_name': 'None', 'draw_mesh': False, 'field': 'pressure', 'filled': True, 'mesh_object': '', 'node_values': True, 'range_option': {'auto_range_on': {'global_range': True}}, 'surfaces': [2, 5]}
  solver_session.settings.results.graphics.contour['contour-1']()
  solver_session.settings.results.graphics.contour['contour-1'].field = 'velocity-magnitude'
  solver_session.settings.results.graphics.contour['contour-1'].field()
  solver_session.settings.results.graphics.contour['contour-1'].color_map.size.set_state(80.0)
  solver_session.settings.results.graphics.contour['contour-1'].color_map.size()
  solver_session.settings.results.graphics.contour['contour-1'].rename('my-contour')
  del solver_session.settings.results.graphics.contour['contour-1']['my-contour']

Visualization example
---------------------

Here field data is extracted from the Fluent session into the Python
environment. Visualization is then used to visualize the extracted data.

.. code-block:: python

      from ansys.fluent.visualization import GraphicsWindow, Mesh, Contour, Surface, XYPlot

      # get the graphics objects for the session
      mesh_object = Mesh(solver=solver_session)
      contour_object_1 = Contour(solver=solver_session)
      contour_object_2 = Contour(solver=solver_session)
      surface_object = Surface(solver=solver_session)
      plots_object = XYPlot(solver=solver_session)

      # set graphics objects properties
      mesh_object.show_edges = True
      mesh_object.surfaces = ['symmetry']

      contour_object_1.field = "velocity-magnitude"
      contour_object_1.surfaces = ['symmetry']

      contour_object_2.field = "temperature"
      contour_object_2.surfaces = ['symmetry', 'wall']

      surface_object.definition.type = "iso-surface"
      surface_object.definition.iso_surface.field= "velocity-magnitude"
      surface_object.definition.iso_surface.rendering= "contour"

      plots_object.surfaces = ["symmetry"]
      plots_object.y_axis_function = "temperature"

      graphics_window = GraphicsWindow(grid=(2, 2))
      graphics_window.add_graphics(mesh_object, position=(0, 0))
      graphics_window.add_graphics(contour_object_2, position=(0, 1))
      graphics_window.add_graphics(surface_object, position=(1, 0))
      graphics_window.add_graphics(plots_object, position=(1, 1))
      graphics_window.show()

      solver_session.exit()

.. currentmodule:: ansys.fluent.visualization

.. autosummary::
   :toctree: _autosummary

.. toctree::
   :maxdepth: 2
   :hidden:

   mesh
   surface
   contour
   vector
   pathline
   xyplot
   monitorplot
   graphics_window