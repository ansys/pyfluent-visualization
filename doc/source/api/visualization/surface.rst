.. _ref_surface:


Surface
=======

.. autopostdoc:: ansys.fluent.visualization.containers.Surface

Creates a mesh object. Currently, only plane and iso surface are supported.

.. code-block:: python

    from ansys.fluent.visualization import Surface

    # For plane-surface
    surf_xy_plane = Surface(solver=solver_session)
    surf_xy_plane.definition.type = "plane-surface"
    surf_xy_plane.definition.plane_surface.creation_method = "xy-plane"
    plane_surface_xy = surf_xy_plane.definition.plane_surface.xy_plane
    plane_surface_xy.z = -0.0441921

    # For iso-surface
    surf_outlet_plane = Surface(solver=solver_session)
    surf_outlet_plane.definition.type = "iso-surface"
    iso_surf = surf_outlet_plane.definition.iso_surface
    iso_surf.field = "y-coordinate"
    iso_surf.iso_value = -0.125017
