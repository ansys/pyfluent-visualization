.. _ref_vector:

Vector
======  

.. autopostdoc:: ansys.fluent.visualization.containers.Vector

Creates a vector object.

.. code-block:: python

    from ansys.fluent.visualization import Vector

    velocity_vector = Vector(
        solver=solver_session,
        field="pressure",
        surfaces=["solid_up:1:830"],
        scale=2,
    )
