.. _ref_mesh:

Mesh
==== 

.. autopostdoc:: ansys.fluent.visualization.containers.Mesh

Creates a mesh object.

.. code-block:: python

    from ansys.fluent.visualization import Mesh

    mesh_object = Mesh(
        solver=solver_session, show_edges=True, surfaces=["in1", "in2", "in3"]
        )
