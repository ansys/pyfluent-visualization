"""Module providing visualization objects for PyVista."""

from enum import Enum
import sys
from typing import Callable, List, Optional, Union

from ansys.fluent.core.post_objects.meta import Attribute, Command, PyLocalPropertyMeta
from ansys.fluent.core.post_objects.post_helper import PostAPIHelper
from ansys.fluent.core.post_objects.post_object_definitions import (
    ContourDefn,
    GraphicsDefn,
    MeshDefn,
    PathlinesDefn,
    SurfaceDefn,
    VectorDefn,
)
from ansys.fluent.core.post_objects.post_objects_container import (
    Graphics as GraphicsContainer,
)
import numpy as np
import pyvista as pv

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


class Format(Enum):
    """Format of the data label."""

    DATA_ONLY = 1
    INDEX_AND_DATA = 2


class SolutionVariablesGraphicsDefn(GraphicsDefn):
    """SolutionVariablesGraphics definition."""

    PLURAL = "SolutionVariablesGraphics"

    class zones(metaclass=PyLocalPropertyMeta):
        """List of zones for solution variables graphics."""

        value: List[str] = []

        @Attribute
        def allowed_values(self):
            """Zones allowed values."""
            return (
                self._api_helper.fields().solution_variable_info.get_zones_info().zones
            )

    class domain(metaclass=PyLocalPropertyMeta):
        """Domain for solution variables graphics."""

        value: str = "mixture"

        @Attribute
        def allowed_values(self):
            """Domain allowed values."""
            return (
                self._api_helper.fields()
                .solution_variable_info.get_zones_info()
                .domains
            )

    class variables(metaclass=PyLocalPropertyMeta):
        """List of variables for solution variables graphics."""

        value: List[str] = []

        @Attribute
        def allowed_values(self):
            """Variables allowed values."""
            info = self._api_helper.fields().solution_variable_info.get_variables_info(
                self._parent.zones(), self._parent.domain()
            )
            if info is None:
                return []
            return info.solution_variables

    class format(metaclass=PyLocalPropertyMeta):
        """Format for solution variables graphics."""

        value: Union[Format, Callable] = Format.INDEX_AND_DATA

    class precision(metaclass=PyLocalPropertyMeta):
        """Precision for solution variables graphics."""

        value: int = 2

        @Attribute
        def range(self):
            """Precision range."""
            return 0, sys.float_info.dig

    class font_size(metaclass=PyLocalPropertyMeta):
        """Font size for solution variables graphics."""

        value: int = 10

        @Attribute
        def range(self):
            """Font size range."""
            return 0, 100

    class bold(metaclass=PyLocalPropertyMeta):
        """Bold for solution variables graphics."""

        value: bool = False


class SolutionVariablesGraphics(SolutionVariablesGraphicsDefn):
    """Provides for displaying solution variables.

    Parameters
    ----------
    name :

    parent :

    api_helper :


    .. code-block:: python

        from ansys.fluent.visualization.pyvista.solution_variables import SolutionVariablesGraphics  # noqa: E501

        graphics_session = Graphics(session)
        svg1 = graphics_session.SolutionVariablesGraphics["svg-1"]
        svg1.variables=["SV_P", "SV_T"]
        svg1.zones=["inlet2"]
        svg1.display("window-0")
    """

    @Command
    def display(self, window_id: Optional[str] = None, overlay: Optional[bool] = False):
        """Display solution variables graphics.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If an ID is not specified, a unique ID is used.
            The default is ``None``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        """
        centroid_data = self._api_helper.fields().solution_variable_data.get_data(
            solution_variable_name="SV_CENTROID",
            zone_names=self.zones(),
            domain_name=self.domain(),
        )
        centroid_data = np.concatenate(list(centroid_data.data.values())).reshape(-1, 3)

        variables_data = []
        for variable in self.variables():
            variable_data = self._api_helper.fields().solution_variable_data.get_data(
                solution_variable_name=variable,
                zone_names=self.zones(),
                domain_name=self.domain(),
            )
            variable_data = np.concatenate(list(variable_data.data.values()))
            variables_data.append(variable_data.tolist())

        def format_fn(index, *data):
            format = self.format()
            if format == Format.DATA_ONLY:
                if len(data) == 1:
                    return f"{data[0]:.{self.precision()}f}"
                else:
                    data_fmt = ", ".join(f"{d:.{self.precision()}f}" for d in data)
                    return f"({data_fmt})"
            elif format == Format.INDEX_AND_DATA:
                data_fmt = ", ".join(f"{d:.{self.precision()}f}" for d in data)
                return f"({index}, {data_fmt})"
            elif callable(format):
                return format(index, *data)

        poly = pv.PolyData(centroid_data)
        poly["Data"] = [
            format_fn(index, *data) for index, data in enumerate(zip(*variables_data))
        ]
        graphics = Graphics(session=self._api_helper)
        mesh_name = graphics.Meshes.Create()
        mesh = graphics.Meshes[mesh_name]
        mesh.show_edges = True
        mesh.surfaces_list = self.zones()
        mesh.display(window_id, overlay)
        plotter = pyvista_windows_manager.get_plotter(window_id)
        plotter.add_point_labels(
            poly,
            "Data",
            point_color="black",
            font_size=self.font_size(),
            bold=self.bold(),
            shape=None,
        )
        return plotter
