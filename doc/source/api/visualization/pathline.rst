.. _ref_pathline:

Pathline
========

.. autopostdoc:: ansys.fluent.visualization.containers.Pathline

Creates a pathlines object.

.. code-block:: python

    from ansys.fluent.visualization import Pathline

    pathlines = Pathline(solver=solver_session)
    pathlines.field = "velocity-magnitude"
    pathlines.surfaces = ["inlet", "inlet1", "inlet2"]
