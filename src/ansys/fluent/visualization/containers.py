# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Containers for graphics."""

import abc
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Literal,
    Required,
    Self,
    TypedDict,
    Unpack,
)
import warnings

from ansys.fluent.core.field_data_interfaces import _to_field_name_str
from ansys.fluent.core.utils.context_managers import _get_active_session
from ansys.units import VariableDescriptor
from typing_extensions import TypeVar, override

from ansys.fluent.visualization.graphics import Graphics
from ansys.fluent.visualization.plotter import Plots
from ansys.fluent.visualization.post_data_extractor import (
    FieldDataExtractor,
    XYPlotDataExtractor,
)

if TYPE_CHECKING:
    from ansys.fluent.core.session_solver import Solver

    from ansys.fluent.interface.post_objects.meta import _DeleteKwargs
    from ansys.fluent.interface.post_objects.post_object_definitions import (
        ContourDefn,
        Defns,
        MeshDefn,
        MonitorDefn,
        PathlinesDefn,
        SurfaceDefn,
        VectorDefn,
        XYPlotDefn,
    )
    from ansys.fluent.interface.post_objects.post_objects_container import Container

DefnT = TypeVar("DefnT", bound="Defns", default="Defns")


class GraphicsObject(Generic[DefnT]):
    """Base class for graphics containers."""

    solver: "Solver"  # pyright: ignore[reportUninitializedInstanceVariable]
    _obj: "Defns"  # pyright: ignore[reportUninitializedInstanceVariable]
    kwargs: dict[str, Any]  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self, solver: "Solver | None", **kwargs: Any):
        super().__init__()
        self.__dict__["solver"] = solver or _get_active_session()
        self.__dict__["kwargs"] = kwargs
        if self.solver is None:  # pyright: ignore[reportUnnecessaryComparison]
            raise RuntimeError("No solver session provided and none found in context.")
        if "field" in self.kwargs:
            self.kwargs["field"] = kwargs["field"] = _to_field_name_str(
                self.kwargs["field"]
            )
        if "vectors_of" in self.kwargs:
            self.kwargs["vectors_of"] = kwargs["vectors_of"] = _to_field_name_str(
                self.kwargs["vectors_of"]
            )

    def get_field_data(self):
        """Exposes field data."""
        return FieldDataExtractor(self._obj).fetch_data()

    if TYPE_CHECKING:
        # we have these due to inheriting from the ABCs at type time but the attributes coming from ._obj
        # the type checker thinks they aren't valid to instantiate otherwise
        def get_root(
            self, instance: object = None
        ) -> Container: ...  # pyright: ignore[reportUnusedParameter]
        def display(
            self, window_id: str | None = None
        ) -> None: ...  # pyright: ignore[reportUnusedParameter]

        surfaces: Any  # pyright: ignore[reportUninitializedInstanceVariable]  # something is definitely bugged here in the type checker as () -> list[str doesn't work]
    else:

        def __getattr__(self, attr):
            return getattr(self._obj, attr)

        @override
        def __setattr__(self, attr, value):
            if attr == "surfaces":  # TODO typing?
                value = list(value)
            setattr(self._obj, attr, value)

    @override
    def __dir__(self) -> list[str]:
        return sorted(set(super().__dir__()) | set(dir(self._obj)))


class Mesh(  # pyright: ignore[reportUnsafeMultipleInheritance]
    GraphicsObject["MeshDefn"], MeshDefn if TYPE_CHECKING else abc.ABC
):
    """Mesh visualization object.

    Creates a Fluent mesh graphic object on the specified surfaces.
    It is typically used to display the computational mesh with optional
    edge highlighting.

    Parameters
    ----------
    surfaces : list[str]
        List of Fluent surfaces on which the mesh should be displayed.
    show_edges : ``bool``, optional
        If ``True``, mesh edges are drawn. If ``False`` (default), the mesh
        is shown without explicit edge highlighting.
    solver : FluentSession, optional
        Active Fluent session. If ``None``, the parent container determines
        the session.
    **kwargs : dict
        Additional keyword arguments forwarded to
        ``Graphics(session).Mesh.create()`` or handled by the base class.

    Examples
    --------
    >>> from ansys.fluent.visualization import Mesh
    >>> # `solver_session` is a live Fluent session with a case
    >>> # and data which contains the following surfaces
    >>> mesh = Mesh(
    >>>     solver=solver_session, show_edges=True, surfaces=["in1", "in2", "in3"]
    >>> )
    """

    def __init__(
        self,
        *,
        surfaces: list[str],
        show_edges: bool = False,
        solver: "Solver | None" = None,
        **kwargs: Unpack["_DeleteKwargs"],
    ):
        """__init__ method of Mesh class."""

        super().__init__(
            solver,
            **kwargs
            | {
                "surfaces": surfaces,
                "show_edges": show_edges,
            },
        )
        super().__setattr__(
            "_obj", Graphics(session=self.solver).Meshes.create(**self.kwargs)
        )


SurfaceType = Literal["plane-surface", "iso-surface"]
SurfaceCreationMethod = Literal["xy-plane", "yz-plane", "zx-plane", "point-and-normal"]
SurfaceRendering = Literal["mesh", "contour"]


class SurfaceKwargsNoType(TypedDict, total=False):
    creation_method: SurfaceCreationMethod
    x: float
    y: float
    z: float
    field: str | VariableDescriptor
    iso_value: float
    rendering: SurfaceRendering
    point: tuple[float, float, float]
    normal: tuple[float, float, float]


class SurfaceKwargs(SurfaceKwargsNoType):
    type: SurfaceType


class Surface(  # pyright: ignore[reportUnsafeMultipleInheritance]
    GraphicsObject["SurfaceDefn"], SurfaceDefn if TYPE_CHECKING else abc.ABC
):
    """Surface definition for Fluent post-processing.

    The ``Surface`` class represents any Fluent surface generated for
    post-processing, including plane surfaces and iso-surfaces. After creation,
    additional attributes (such as ``field``, ``iso_value``, ``creation_method``,
    etc.) may be set on the object to fully define the surface.

    Parameters
    ----------
    type : str
        The type of surface to create. Examples include
        ``"plane-surface"`` and ``"iso-surface"``.
    solver : FluentSession, optional
        Active Fluent session. If ``None``, the parent container or base
        class determines the session.
    **kwargs : dict
        Additional keyword arguments used to define the surface and passed to
        ``Graphics(session).Surfaces.create()``. These vary depending on
        the chosen surface type.

    Notes
    -----
    A Surface object may be defined either:

    * Directly at construction time using keyword arguments
      (e.g., specifying ``creation_method``, ``origin``/``normal``,
      ``z`` for plane surfaces, etc.)

    * Or incrementally after creation by setting attributes on the
      surface object before it is first evaluated or drawn.

    Examples
    --------
    >>> from ansys.fluent.visualization import Surface
    >>> # `solver_session` is a live Fluent session with a case file loaded
    >>> # For plane-surface
    >>> surf_xy_plane = Surface(
    >>>     solver=solver_session,
    >>>     type="plane-surface",
    >>>     creation_method="xy-plane",
    >>>     z=-0.0441921
    >>>     )
    >>> # For iso-surface
    >>> surf_outlet_plane = Surface(solver=solver_session, type="iso-surface")
    >>> surf_outlet_plane.field = "y-coordinate"
    >>> surf_outlet_plane.iso_value = -0.125017
    """

    _obj: "SurfaceDefn"  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self, *, solver: "Solver | None" = None, **kwargs: Unpack[SurfaceKwargs]
    ):
        """__init__ method of Surface class."""
        super().__init__(solver, **kwargs)
        super().__setattr__(
            "_obj", Graphics(session=self.solver).Surfaces.create(**self.kwargs)
        )
        self.type = kwargs["type"]
        if "creation_method" in kwargs:
            self.creation_method = kwargs["creation_method"]
        if "x" in kwargs:
            self.x = kwargs["x"]
        if "y" in kwargs:
            self.y = kwargs["y"]
        if "z" in kwargs:
            self.z = kwargs["z"]
        if "field" in kwargs:
            self.field = kwargs["field"]
        if "iso_value" in kwargs:
            self.iso_value = kwargs["iso_value"]
        if "rendering" in kwargs:
            self.rendering = kwargs["rendering"]
        if "point" in kwargs:
            self.point = kwargs["point"]
        if "normal" in kwargs:
            self.normal = kwargs["normal"]

    @property
    @override
    def type(self) -> SurfaceType:
        """Surface definition type."""
        return self._obj.definition.type()

    @type.setter
    def type(self, value: SurfaceType) -> None:
        self._obj.definition.type = value

    @property
    def creation_method(
        self,
    ) -> SurfaceCreationMethod:
        """Plane surface creation method."""
        return self._obj.definition.plane_surface.creation_method()

    @creation_method.setter
    def creation_method(self, value: SurfaceCreationMethod) -> None:
        self._obj.definition.plane_surface.creation_method = value

    @property
    def x(self) -> float:
        """X coordinate for yz-plane."""
        return self._obj.definition.plane_surface.yz_plane.x()

    @x.setter
    def x(self, value: float) -> None:
        if self._obj.definition.plane_surface.creation_method() != "yz-plane":
            raise ValueError("Expected plane creation method to be 'yz-plane'")
        self._obj.definition.plane_surface.yz_plane.x = value

    @property
    def y(self) -> float:
        """Y coordinate for zx-plane."""
        return self._obj.definition.plane_surface.zx_plane.y()

    @y.setter
    def y(self, value: float) -> None:
        if self._obj.definition.plane_surface.creation_method() != "zx-plane":
            raise ValueError("Expected plane creation method to be 'zx-plane'")
        self._obj.definition.plane_surface.zx_plane.y = value

    @property
    def z(self) -> float:
        """Z coordinate for xy-plane."""
        return self._obj.definition.plane_surface.xy_plane.z()

    @z.setter
    def z(self, value: float) -> None:
        if self._obj.definition.plane_surface.creation_method() != "xy-plane":
            raise ValueError("Expected plane creation method to be 'xy-plane'")
        self._obj.definition.plane_surface.xy_plane.z = value

    @property
    def field(self) -> str | None:
        """Iso-surface field."""
        return self._obj.definition.iso_surface.field()

    @field.setter
    def field(self, value: str | VariableDescriptor | None) -> None:
        self._obj.definition.iso_surface.field = _to_field_name_str(value)

    @property
    def iso_value(self) -> float | None:
        """Iso-surface value."""
        return self._obj.definition.iso_surface.iso_value()

    @iso_value.setter
    def iso_value(self, value: float | None) -> None:
        self._obj.definition.iso_surface.iso_value = value

    @property
    def rendering(self) -> SurfaceRendering:
        """Iso-surface rendering method."""
        return self._obj.definition.iso_surface.rendering()

    @rendering.setter
    def rendering(self, value: SurfaceRendering) -> None:
        self._obj.definition.iso_surface.rendering = value

    @property
    def point(self) -> tuple[float, float, float]:
        """Point for point-and-normal surface."""
        pt = self._obj.definition.plane_surface.point
        return (pt.x(), pt.y(), pt.z())

    @point.setter
    def point(self, value: tuple[float, float, float]) -> None:
        if self._obj.definition.plane_surface.creation_method() != "point-and-normal":
            raise ValueError("Expected plane creation method to be 'point-and-normal'")
        pt = self._obj.definition.plane_surface.point
        pt.x, pt.y, pt.z = value

    @property
    def normal(self) -> tuple[float, float, float]:
        """Normal vector for point-and-normal surface."""
        norm = self._obj.definition.plane_surface.normal
        return (norm.x(), norm.y(), norm.z())

    @normal.setter
    def normal(self, value: tuple[float, float, float]) -> None:
        if self._obj.definition.plane_surface.creation_method() != "point-and-normal":
            raise ValueError("Expected plane creation method to be 'point-and-normal'")
        norm = self._obj.definition.plane_surface.normal
        norm.x, norm.y, norm.z = value


class PlaneSurface(Surface, abc.ABC):
    """PlaneSurface derived from Surface.
    Provides factory methods for creating plane surfaces like XY, YZ, and XZ planes.

    Examples
    --------
    >>> from ansys.fluent.visualization import PlaneSurface
    >>> # `solver_session` is a live Fluent session with a case file loaded
    >>>
    >>> # Creating using point and normal
    >>> surf_xy_plane = PlaneSurface.create_from_point_and_normal(
    >>>     solver=solver_session,
    >>>     point=[0.0, 0.0, -0.0441921],
    >>>     normal=[0.0, 0.0, 1.0],
    >>> )
    >>>
    >>> # Create same plane using 'create_xy_plane' method
    >>> surf_xy_plane = PlaneSurface.create_xy_plane(
    >>>     solver=solver_session,
    >>>     z=-0.0441921,
    >>> )
    """

    @classmethod
    def create_xy_plane(
        cls, *, solver: "Solver | None" = None, z: float = 0.0, **kwargs: Any
    ) -> Self:
        """Create a plane surface in the XY plane at a given Z value."""
        return cls(
            solver=solver,
            type="plane-surface",
            creation_method="xy-plane",
            z=z,
            **kwargs,
        )

    @classmethod
    def create_yz_plane(
        cls, solver: "Solver | None" = None, x: float = 0.0, **kwargs: Any
    ) -> Self:
        """Create a plane surface in the YZ plane at a given X value."""
        return cls(
            solver=solver,
            type="plane-surface",
            creation_method="yz-plane",
            x=x,
            **kwargs,
        )

    @classmethod
    def create_zx_plane(
        cls, solver: "Solver | None" = None, y: float = 0.0, **kwargs: Any
    ):
        """Create a plane surface in the ZX plane at a given Y value."""
        return cls(
            solver=solver,
            type="plane-surface",
            creation_method="zx-plane",
            y=y,
            **kwargs,
        )

    @classmethod
    def create_from_point_and_normal(
        cls,
        solver: "Solver | None" = None,
        point: tuple[float, float, float] = (0, 0, 0),
        normal: tuple[float, float, float] = (0, 0, 0),
        **kwargs: Any,
    ):
        """Create a plane surface from a point and a normal vector."""
        return cls(
            solver=solver,
            type="plane-surface",
            creation_method="point-and-normal",
            point=point,
            normal=normal,
            **kwargs,
        )


class IsoSurface(Surface, abc.ABC):
    """Iso-surface derived from :class:`Surface`.

    The ``IsoSurface`` class simplifies creation of iso-surfaces by providing
    a higher-level interface on top of the generic :class:`Surface` class.
    It supports specifying the scalar field and iso-value directly, and
    internally configures the corresponding Fluent surface object.

    Parameters
    ----------
    solver : FluentSession, optional
        Active Fluent session. If ``None``, the parent container or base class
        determines the session.
    field : str or VariableDescriptor, optional
        The scalar field over which the iso-surface is computed.
    rendering : str, optional
        Rendering method for the iso-surface depending on Fluent capabilities.
    iso_value : float, optional
        The value of the scalar field at which the iso-surface is extracted.
    **kwargs : dict
        Additional keyword arguments forwarded to
        ``Graphics(session).Surfaces.create()`` or handled by the base class.

    Examples
    --------
    >>> from ansys.fluent.visualization import IsoSurface
    >>> # `solver_session` is a live Fluent session with a case file loaded
    >>>
    >>> # Creating iso-surface
    >>> surf_outlet_plane = IsoSurface.create(
    >>>     solver=solver_session,
    >>>     field="y-coordinate",
    >>>     iso_value=-0.125017,
    >>>     )
    """

    def __init__(
        self,
        solver: "Solver | None" = None,
        **kwargs: Unpack[SurfaceKwargsNoType],
    ):
        """Create an iso-surface."""
        super().__init__(
            solver=solver,
            type="iso-surface",
            **kwargs,
        )


class GenericCreateArgs(TypedDict, total=False):
    name: str


class ContourKwargs(TypedDict, total=False):
    field: str | VariableDescriptor
    surfaces: list[str]
    filled: bool
    node_values: bool
    boundary_values: bool
    contour_lines: bool
    show_edges: bool


class Contour(  # pyright: ignore[reportUnsafeMultipleInheritance]
    GraphicsObject["ContourDefn"],
    ContourDefn if TYPE_CHECKING else abc.ABC,
    abc.ABC,
):
    """
    Contour visualization object.

    The ``Contour`` class represents a Fluent contour plot of a scalar field
    drawn over one or more surfaces. Contours are commonly used to visualize
    variations in temperature, pressure, velocity magnitude, turbulence
    quantities, or any other field available in the solver.

    Parameters
    ----------
    field : str or VariableDescriptor
        Name of the scalar field to be contoured. This defines the quantity
        used for color interpolation across the specified surfaces.
    surfaces : list of str
        List of Fluent surfaces on which the contour is displayed.
        Surfaces may be boundary zones, interior surfaces, or custom
        surfaces such as iso-surfaces or plane surfaces.
    solver : FluentSession, optional
        Active Fluent session. If ``None``, the parent class or container
        determines the session.
    **kwargs : dict
        Additional keyword arguments forwarded to
        ``Graphics(session).Contours.create()`` or handled by the base class.

    Examples
    --------
    >>> from ansys.fluent.visualization import Contour
    >>> # `solver_session` is a live Fluent session with a case
    >>> # and data which contains the following surfaces
    >>> temperature_contour_object = Contour(
    >>>     solver=solver_session, field="temperature", surfaces=["in1", "in2", "in3",]
    >>> )
    """

    _obj: "ContourDefn"  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self, *, solver: "Solver | None" = None, **kwargs: Unpack[ContourKwargs]
    ):
        """__init__ method of Contour class."""
        super().__init__(solver, **kwargs)
        super().__setattr__(
            "_obj", Graphics(session=self.solver).Contours.create(**self.kwargs)
        )


# class VectorKwargs(TypedDict, total=False):
#     field: Required[str | VariableDescriptor]
#     surfaces: Required[list[str]]
#     vectors_of: str | VariableDescriptor | None
#     scale: float
#     skip: int
#     show_edges: bool


class Vector(  # pyright: ignore[reportUnsafeMultipleInheritance]
    GraphicsObject["VectorDefn"], VectorDefn if TYPE_CHECKING else abc.ABC, abc.ABC
):
    """Vector visualization object.

    Parameters
    ----------
    field : str|VariableDescriptor
        Name of the variable used for the **vector direction/magnitude**.
    color_by : str|VariableDescriptor
        Name of the variable used to **color** the vectors.
    surfaces : list[str]
        List of Fluent surfaces on which the vector plot is created.
    scale : float, optional
        Scaling factor applied to the vector lengths. Defaults to 1.0.
    solver : FluentSession, optional
        Active Fluent session. If ``None``, the parent container determines
        the session.
    **kwargs : dict
        Additional keyword arguments forwarded to
        ``Graphics(session).Vectors.create()``.

    Examples
    --------
    >>> from ansys.fluent.visualization import Vector
    >>> # `solver_session` is a live Fluent session with a case
    >>> # and data which contains the following surfaces
    >>> velocity_vector_object = Vector(
    >>>     solver=solver_session,
    >>>     field="velocity",
    >>>     color_by="pressure",
    >>>     surfaces=["solid_up:1:830"],
    >>>     scale=2,
    >>> )
    """

    _obj: "VectorDefn"  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        *,
        field: str | VariableDescriptor,
        surfaces: list[str],
        color_by: str | VariableDescriptor | None = None,
        scale: float = 1.0,
        skip: int = 0,
        show_edges: bool = False,
        solver: "Solver | None" = None,
        # **kwargs: Unpack[VectorKwargs],
    ):
        """__init__ method of Vector class."""
        if color_by is None:
            color_by = field

        super().__init__(
            solver,
            vectors_of=field,
            field=color_by,
            scale=scale,
            skip=skip,
            show_edges=show_edges,
        )
        super().__setattr__(
            "_obj", Graphics(session=self.solver).Vectors.create(**self.kwargs)
        )

        if field not in self._obj.vectors_of.allowed_values:
            warnings.warn(
                "API update: `field` now represents the vector variable, and `color_by`"
                " controls the scalar coloring field.\n"
                "Your input seems to use `field` as a scalar (old behavior). "
                "It is being interpreted as `color_by`, and the vector field has been "
                "defaulted to 'velocity' for compatibility.\n"
                "Please update your code to: field=<vector>, color_by=<scalar>."
            )

    if not TYPE_CHECKING:

        @staticmethod
        def _get_mapped_attrs(attr: str) -> str | None:
            _attr_map = {
                "field": "vectors_of",
                "color_by": "field",
            }
            return _attr_map.get(attr)

        def __getattr__(self, attr: str) -> Any:
            attr = self._get_mapped_attrs(attr) or attr
            return getattr(self._obj, attr)

        @override
        def __setattr__(self, attr: str, value: Any) -> None:
            attr = self._get_mapped_attrs(attr) or attr
            if attr == "surfaces":
                value = list(value)
            setattr(self._obj, attr, value)


class PathlineKwargs(TypedDict, total=False):
    field: Required[str | VariableDescriptor]
    surfaces: Required[list[str]]


class Pathline(  # pyright: ignore[reportUnsafeMultipleInheritance]
    GraphicsObject["PathlinesDefn"],
    PathlinesDefn if TYPE_CHECKING else abc.ABC,
    abc.ABC,
):
    """Pathline visualization object.

    The ``Pathline`` class generates pathlines, which represent the trajectories
    of massless particles as they travel through the flow field based on the
    underlying velocity data. Pathlines are commonly used to visualize flow
    patterns, mixing, recirculation, and streamline-like behavior in transient
    or steady-state solutions.

    Parameters
    ----------
    field : str or VariableDescriptor
        The field used to determine particle motion, typically a velocity-based
        variable (e.g., ``"velocity-magnitude"``, ``"x-velocity"``, etc.).
    surfaces : list of str
        List of seed surfaces where pathlines originate. These may include
        boundary zones, inlets, interior surfaces, or user-defined surfaces.
    solver : FluentSession, optional
        Active Fluent session. If ``None``, the parent class or container
        determines the session.
    **kwargs : dict
        Additional keyword arguments forwarded to
        ``Graphics(session).Pathlines.create()`` or handled by the base class.

    Examples
    --------
    >>> from ansys.fluent.visualization import Pathline
    >>> # `solver_session` is a live Fluent session with a case
    >>> # and data which contains the following surfaces
    >>> pathlines = Pathline(
    >>>     solver=solver_session,
    >>>     field="velocity-magnitude",
    >>>     surfaces = ["inlet", "inlet1", "inlet2"],
    >>> )
    """

    _obj: "PathlinesDefn"  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        *,
        solver: "Solver | None" = None,
        **kwargs: Unpack[PathlineKwargs],
    ):
        """__init__ method of Pathline class."""
        super().__init__(solver, **kwargs)
        super().__setattr__(
            "_obj", Graphics(session=self.solver).Pathlines.create(**self.kwargs)
        )


class XYPlotKwargs(TypedDict, total=False):
    direction_vector: tuple[int, int, int]
    node_values: bool
    boundary_values: bool
    x_axis_function: Literal["direction-vector"]
    y_axis_function: Required[str | VariableDescriptor]
    surfaces: Required[list[str]]


class XYPlot(  # pyright: ignore[reportUnsafeMultipleInheritance]
    GraphicsObject["XYPlotDefn"], XYPlotDefn if TYPE_CHECKING else abc.ABC, abc.ABC
):
    """XY plot visualization object.

    The ``XYPlot`` class creates a Fluent XY plot of a scalar field evaluated
    along one or more surfaces. XY plots are typically used to visualize
    variations of a quantity along a line, surface intersection, or custom
    geometric curve.

    Parameters
    ----------
    surfaces : list of str
        List of Fluent surfaces on which the XY plot is evaluated. These may be
        boundary zones, interior surfaces, or user-defined surfaces such as line
        surfaces, intersections, or extracted curves.
    y_axis_function : str or VariableDescriptor
        The scalar field whose values are plotted on the Y-axis of the plot.
        Examples include ``"temperature"``, ``"pressure"``,
        ``"velocity-magnitude"``, or any available field in the solver.
    solver : FluentSession, optional
        Active Fluent session. If ``None``, the parent container or base class
        determines the session.
    **kwargs : dict
        Additional keyword arguments forwarded to
        ``Graphics(session).XYPlots.create()`` or handled by the base class.

    Examples
    --------
    >>> from ansys.fluent.visualization import XYPlot
    >>> xy_plot = XYPlot(
    >>>     solver=solver_session,
    >>>     surfaces=["outlet"],
    >>>     y_axis_function="temperature",
    >>> )
    """

    _obj: "XYPlotDefn"  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        *,
        solver: "Solver | None" = None,
        **kwargs: Unpack[XYPlotKwargs],
    ):
        """__init__ method of XYPlot class."""
        super().__init__(solver, **kwargs)
        if "y_axis_function" in self.kwargs:
            self.kwargs["y_axis_function"] = _to_field_name_str(
                self.kwargs["y_axis_function"]
            )
        super().__setattr__(
            "_obj",
            Plots(
                session=self.solver, local_surfaces_provider=Graphics(solver).Surfaces
            ).XYPlots.create(**self.kwargs),
        )


class MonitorKwargs(TypedDict, total=False):
    monitor_set_name: Required[str]

    def get_field_data(self):
        """Exposes 2d plot data data."""
        return XYPlotDataExtractor(self._obj).fetch_data()


class Monitor(  # pyright: ignore[reportUnsafeMultipleInheritance]
    GraphicsObject["MonitorDefn"],
    MonitorDefn if TYPE_CHECKING else abc.ABC,
    abc.ABC,
):
    """Monitor visualization object.

    The ``Monitor`` class provides access to Fluent monitor data for plotting,
    visualization, or post-processing. Monitors typically track quantities
    such as residuals, mass flow rates, forces, moments, lift/drag coefficients,
    or any user-defined monitored variables over iterative or time-dependent
    calculations.

    Parameters
    ----------
    monitor_set_name : str
        Name of the Fluent monitor set to load. Examples include
        ``"residual"``, ``"mass-flow"`` or any user-created monitor defined
        in the Fluent session.
    solver : FluentSession, optional
        Active Fluent session. If ``None``, the parent class or container
        determines the session.
    **kwargs : dict
        Additional arguments forwarded to
        ``Graphics(session).Monitors.create()`` or handled by the base class.

    Examples
    --------
    >>> from ansys.fluent.visualization import Monitor
    >>> residual = Monitor(solver=solver_session, monitor_set_name="residual")
    """

    _obj: "MonitorDefn"  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        *,
        monitor_set_name: str,
        solver: "Solver | None" = None,
        **kwargs: Unpack[MonitorKwargs],
    ):
        """__init__ method of Monitor class."""
        kwargs.update(
            {
                "monitor_set_name": monitor_set_name,
            }
        )
        super().__init__(solver, **kwargs)
        super().__setattr__(
            "_obj",
            Plots(
                session=self.solver, local_surfaces_provider=Graphics(solver).Surfaces
            ).MonitorPlots.create(**self.kwargs),
        )

    def get_field_data(self):
        """Exposes monitor data."""
        return self._obj.session.monitors.get_monitor_set_data(
            self.kwargs["monitor_set_name"]
        )
