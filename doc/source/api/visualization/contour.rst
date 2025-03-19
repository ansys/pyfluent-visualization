.. _ref_contour:

Contour
=======   

.. autopostdoc:: ansys.fluent.visualization.containers.Contour

Creates a contour object.

.. code-block:: python

    from ansys.fluent.visualization import Contour

    temperature_contour = Contour(
        solver=solver_session, field="temperature", surfaces=["in1", "in2", "in3",]
    )
