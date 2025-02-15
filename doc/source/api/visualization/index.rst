.. _ref_visualization:

Visualization
=============

Postprocessing of Fluent results can be done with either built-in Fluent
postprocessing capabilities, PyVista, or Matplotlib integration.

Fluent TUI command example
--------------------------

Here visualization objects are constructed within Fluent. You can use
standard Fluent commands to write graphics to a file.

.. code:: python

  solver_session.tui.display.objects.contour['contour-1'] = {'boundary_values': True, 'color_map': {'color': 'field-velocity', 'font_automatic': True, 'font_name': 'Helvetica', 'font_size': 0.032, 'format': '%0.2e', 'length': 0.54, 'log_scale': False, 'position': 1, 'show_all': True, 'size': 100, 'user_skip': 9, 'visible': True, 'width': 6.0}, 'coloring': {'smooth': False}, 'contour_lines': False, 'display_state_name': 'None', 'draw_mesh': False, 'field': 'pressure', 'filled': True, 'mesh_object': '', 'node_values': True, 'range_option': {'auto_range_on': {'global_range': True}}, 'surfaces': [2, 5]}
  solver_session.tui.display.objects.contour['contour-1']()
  solver_session.tui.display.objects.contour['contour-1'].field.set_state('velocity-magnitude')
  solver_session.tui.display.objects.contour['contour-1'].field()
  solver_session.tui.display.objects.contour['contour-1'].color_map.size.set_state(80.0)
  solver_session.tui.display.objects.contour['contour-1'].color_map.size()
  solver_session.tui.display.objects.contour['contour-1'].rename('my-contour')
  del solver_session.tui.display.objects.contour['my-contour']

PyVista example (graphics)
--------------------------

Here field data is extracted from the Fluent session into the Python
environment. PyVista is then used to visualize the extracted data.

.. code:: python

  # import module
  from ansys.fluent.visualization import Graphics

  # get the graphics objects for the session

  graphics_session1 = Graphics(solver_session)
  mesh1 = graphics_session1.Meshes["mesh-1"]
  contour1 = graphics_session1.Contours["contour-1"]
  contour2 = graphics_session1.Contours["contour-2"]
  surface1 = graphics_session1.Surfaces["surface-1"]

  # set graphics objects properties

  # mesh
  mesh1.show_edges = True
  mesh1.surfaces = ['symmetry']

  # contour
  contour1.field = "velocity-magnitude"
  contour1.surfaces = ['symmetry']

  contour2.field = "temperature"
  contour2.surfaces = ['symmetry', 'wall']

  # copy
  graphics_session1.Contours["contour-3"] = contour2()

  # update
  contour3 = graphics_session1.Contours["contour-3"]
  contour3.update(contour1())

  # delete
  del graphics_session1.Contours["contour-3"] 

  # loop
  for name, _ in graphics_session1.Contours.items():
      print(name)

  # iso surface
  surface1.surface.iso_surface.field= "velocity-magnitude"
  surface1.surface.iso_surface.rendering= "contour"

  # display 
  contour1.display()
  mesh1.display()
  surface1.display()
  
  # To display in specific window e.g. window-2
  contour1.display("window-2")
  
Matplotlib example (XY plots)
-----------------------------

Here plot data is extracted from the Fluent session into the Python
environment. Matplotlib is then used to plot data.

.. code:: python

  # import module
  from ansys.fluent.visualization import Plots

  # get the plots object for the session
  plots_session1 = Plots(solver_session)
  
  #get xyplot object
  plot1=plots_session1.XYPlots["plot-1"]
  
  #set properties
  plot1.surfaces = ["symmetry"]
  plot1.y_axis_function = "temperature"
  
  #Draw plot
  plot1.plot("window-1")

  solver_session.exit()

.. currentmodule:: ansys.fluent.visualization

.. autosummary::
   :toctree: _autosummary

.. toctree::
   :maxdepth: 2
   :hidden:
   
   post_objects
