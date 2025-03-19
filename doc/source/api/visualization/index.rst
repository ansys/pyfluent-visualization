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

Visualization example (graphics)
--------------------------------

Here field data is extracted from the Fluent session into the Python
environment. Visualization is then used to visualize the extracted data.

.. code:: python

  # import module
  from ansys.fluent.visualization import GraphicsWindow, Mesh, Contour, Surface

  # get the graphics objects for the session
  mesh1 = Mesh(solver=solver_session)
  contour1 = Contour(solver=solver_session)
  contour2 = Contour(solver=solver_session)
  surface1 = Surface(solver=solver_session)

  # set graphics objects properties

  # mesh
  mesh1.show_edges = True
  mesh1.surfaces = ['symmetry']

  # contour
  contour1.field = "velocity-magnitude"
  contour1.surfaces = ['symmetry']

  contour2.field = "temperature"
  contour2.surfaces = ['symmetry', 'wall']

  # iso surface
  surface1.definition.type = "iso-surface"
  surface1.definition.iso_surface.field= "velocity-magnitude"
  surface1.definition.iso_surface.rendering= "contour"

  # display
  plotter = GraphicsWindow(grid=(2, 2))
  plotter.add_graphics(mesh1, position=(0, 0))
  plotter.add_graphics(contour1, position=(0, 1))
  plotter.add_graphics(contour2, position=(1, 0))
  plotter.add_graphics(surface1, position=(1, 1))
  plotter.show()
  
Visualization example (XY plots)
--------------------------------

Here plot data is extracted from the Fluent session into the Python
environment. Visualization is then used to plot data.

.. code:: python

  # import module
  from ansys.fluent.visualization import XYPlot

  # get the plots object for the session
  plots_session1 = XYPlot(solver=solver_session)
  
  #set properties
  plots_session1.surfaces = ["symmetry"]
  plots_session1.y_axis_function = "temperature"
  
  #Draw plot
  plotter = GraphicsWindow()
  plotter.add_graphics(plots_session1)
  plotter.show()

  solver_session.exit()

.. currentmodule:: ansys.fluent.visualization

.. autosummary::
   :toctree: _autosummary

.. toctree::
   :maxdepth: 2
   :hidden:
   
   post_objects
