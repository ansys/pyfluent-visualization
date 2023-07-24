"""Module providing visualization objects for PyVista."""

import sys
from typing import Optional

from ansys.fluent.core.meta import Command
from ansys.fluent.core.post_objects.post_helper import PostAPIHelper
from ansys.fluent.core.post_objects.post_object_definitions import (
    ContourDefn,
    MeshDefn,
    PathlinesDefn,
    SurfaceDefn,
    VectorDefn,
)
from ansys.fluent.core.post_objects.post_objects_container import (
    Graphics as GraphicsContainer,
)

from ansys.fluent.visualization.pyvista.pyvista_windows_manager import (
    pyvista_windows_manager,
)


class Graphics(GraphicsContainer):
    """
    This class provides access to ``Graphics`` object containers for a given
    session so that graphics objects can be created.
    """

    def __init__(
        self, session, post_api_helper=PostAPIHelper, local_surfaces_provider=None
    ):
        super().__init__(
            session, sys.modules[__name__], post_api_helper, local_surfaces_provider
        )


class Contours:
    def error_check(self, solver):
        allowed_fields = (
            solver.field_data.get_scalar_field_data.field_name.allowed_values()
        )
        allowed_surfaces = (
            solver.field_data.get_scalar_field_data.surface_name.allowed_values()
        )
        if self.field not in allowed_fields:
            raise ValueError(
                f"{self.field} is not valid field. Valid fields are - {allowed_fields}"
            )
        for surface in self.surfaces:
            if surface not in allowed_surfaces:
                raise ValueError(
                    f"{surface} is not valid surface. Valid surfaces are - {allowed_surfaces}"  # noqa: E501
                )

    def __init__(self, *args):
        if len(args) == 2:
            self.field, self.surfaces = args[0], args[1]
        elif len(args) == 3:
            self.solver = args[2]
            self.error_check(self.solver)
            self.field, self.surfaces = args[0], args[1]

    def draw(self, solver, target):
        self.error_check(solver)
        existing_contours = solver.results.graphics.contour.get_object_names()
        import time

        contour_name = f"Contour_{time.time()}"
        graphics_mode = target
        if graphics_mode.__class__.__name__ == "Graphics":
            contour = graphics_mode.Contours[contour_name]
        elif (
            graphics_mode.__class__.__name__ == "Solver" and len(existing_contours) != 0
        ):
            contour = solver.results.graphics.contour[existing_contours[0]]
        else:
            contour = solver.results.graphics.contour[contour_name]
        contour.field = self.field
        contour.surfaces_list = self.surfaces
        contour.display()


class Mesh(MeshDefn):
    """Provides for displaying mesh graphics.

    Parameters
    ----------
    name :

    parent :

    api_helper :


    .. code-block:: python

        from ansys.fluent.visualization.pyvista import  Graphics

        graphics_session = Graphics(session)
        mesh1 = graphics_session.Meshes["mesh-1"]
        mesh1.show_edges = True
        mesh1.surfaces_list = ['wall']
        mesh1.display("window-0")
    """

    @Command
    def display(self, window_id: Optional[str] = None, overlay: Optional[bool] = False):
        """Display mesh graphics.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If an ID is not specified, a unique ID is used.
            The default is ``None``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        """
        pyvista_windows_manager.plot(
            self, window_id=window_id, overlay=overlay, fetch_data=True
        )


class Pathlines(PathlinesDefn):
    """Pathlines definition for PyVista.

    .. code-block:: python

        from ansys.fluent.visualization.pyvista import  Graphics

        graphics_session = Graphics(session)
        pathlines1 = graphics_session.Pathlines["pathlines-1"]
        pathlines1.field = "velocity-magnitude"
        pathlines1.surfaces_list = ['inlet']
        pathlines1.display("window-0")
    """

    @Command
    def display(self, window_id: Optional[str] = None, overlay: Optional[bool] = False):
        """Display mesh graphics.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If an ID is not specified, a unique ID is used.
            The default is ``None``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        """
        pyvista_windows_manager.plot(
            self, window_id=window_id, overlay=overlay, fetch_data=True
        )


class Surface(SurfaceDefn):
    """Provides for displaying surface graphics.

    Parameters
    ----------
    name :

    parent :

    api_helper :


    .. code-block:: python

        from ansys.fluent.visualization.pyvista import Graphics

        graphics_session = Graphics(session)
        surface1 = graphics_session.Surfaces["surface-1"]
        surface1.definition.type = "iso-surface"
        surface1.definition.iso_surface.field= "velocity-magnitude"
        surface1.definition.iso_surface.rendering= "contour"
        surface1.definition.iso_surface.iso_value = 0.0
        surface1.display("window-0")
    """

    @Command
    def display(self, window_id: Optional[str] = None, overlay: Optional[bool] = False):
        """Display surface graphics.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If an ID is not specified, a unique ID is used.
            The default is ``None``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        """
        pyvista_windows_manager.plot(
            self, window_id=window_id, overlay=overlay, fetch_data=True
        )


class Contour(ContourDefn):
    """Provides for displaying contour graphics.

    Parameters
    ----------
    name :

    parent :

    api_helper :


    .. code-block:: python

        from ansys.fluent.visualization.pyvista import  Graphics

        graphics_session = Graphics(session)
        contour1 = graphics_session.Contours["contour-1"]
        contour1.field = "velocity-magnitude"
        contour1.surfaces_list = ['wall']
        contour1.display("window-0")
    """

    @Command
    def display(self, window_id: Optional[str] = None, overlay: Optional[bool] = False):
        """Display contour graphics.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If an ID is not specified, a unique ID is used.
            The default is ``None``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        """
        pyvista_windows_manager.plot(
            self, window_id=window_id, overlay=overlay, fetch_data=True
        )


class Vector(VectorDefn):
    """Provides for displaying vector graphics.

    Parameters
    ----------
    name :

    parent :

    api_helper :


    .. code-block:: python

        from ansys.fluent.visualization.pyvista import  Graphics

        graphics_session = Graphics(session)
        vector1 = graphics_session.Vectors["vector-1"]
        vector1.surfaces_list  = ['symmetry']
        vector1.scale = 4.0
        vector1.skip = 4
        vector1.display("window-0")
    """

    @Command
    def display(self, window_id: Optional[str] = None, overlay: Optional[bool] = False):
        """Display vector graphics.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If an ID is not specified, a unique ID is used.
            The default is ``None``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        """
        pyvista_windows_manager.plot(
            self, window_id=window_id, overlay=overlay, fetch_data=True
        )
