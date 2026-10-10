.. _ref_graphics:

Graphics
======== 
 
.. autopostdoc:: ansys.fluent.visualization.pyvista.pyvista_objects.Graphics   

In the following example, a ``Graphics`` object is instantiated with a Fluent
session as its context. The ``Graphics`` object is used to create a mesh,
contour, vector, and surface. The contour is then deleted.

.. code-block:: python

        from ansys.fluent.visualization.pyvista import  Graphics
        graphics_session = Graphics(session)
        
        #Create object
        mesh1 = graphics_session.Meshes["mesh-1"]
        contour1 = graphics_session.Contours["contour-1"]
        vector1 = graphics_session.Vectors["vector-1"]
        surface1 = graphics_session.Surfaces["surface-1"]
        
        #Delete object
        del graphics_session.Contours["contour-1"] 
           
.. toctree::
   :maxdepth: 2
   :hidden:
      
   mesh
   surface
   contour  
   vector   