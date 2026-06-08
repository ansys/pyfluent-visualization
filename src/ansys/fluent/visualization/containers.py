# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

import warnings

from ansys.fluent.core.field_data_interfaces import _to_field_name_str
from ansys.fluent.core.utils.context_managers import _get_active_session
from ansys.units import VariableDescriptor

from ansys.fluent.visualization.graphics import Graphics
from ansys.fluent.visualization.plotter import Plots
from ansys.fluent.visualization.post_data_extractor import (
    FieldDataExtractor,
    XYPlotDataExtractor,
)


class GraphicsObject:
    """Base class for graphics containers."""

    def __init__(self, solver, **kwargs):
        self.__dict__["solver"] = solver or _get_active_session()
        self.__dict__["kwargs"] = kwargs
        if self.solver is None:
            raise RuntimeError("No solver session provided and none found in context.")
        if "field" in self.kwargs:
            self.kwargs["field"] = _to_field_name_str(self.kwargs["field"])
        if "vectors_of" in self.kwargs:
            self.kwargs["vectors_of"] = _to_field_name_str(self.kwargs["vectors_of"])

    def get_field_data(self):
        """Exposes field data."""
        return FieldDataExtractor(self._obj).fetch_data()

    def __getattr__(self, attr):
        return getattr(self._obj, attr)

    def __setattr__(self, attr, value):
        if attr == "surfaces":
            value = list(value)
        setattr(self._obj, attr, value)

    def __dir__(self):
        return sorted(set(super().__dir__()) | set(dir(self._obj)))


class Mesh(GraphicsObject):
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
        self, surfaces: list[str], show_edges: bool = False, solver=None, **kwargs
    ):
        """__init__ method of Mesh class."""
        kwargs.update(
            {
                "show_edges": show_edges,
                "surfaces": surfaces,
            }
        )
        super().__init__(solver, **kwargs)
        self.__dict__["_obj"] = Graphics(session=self.solver).Meshes.create(
            **self.kwargs
        )


class Surface(GraphicsObject):
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

    def __init__(self, type: str, solver=None, **kwargs):
        """__init__ method of Surface class."""
        kwargs.update(
            {
                "type": type,
            }
        )
        super().__init__(solver, **kwargs)
        self.__dict__.update(
            dict(
                type=self.kwargs.pop("type", None),
                creation_method=self.kwargs.pop("creation_method", None),
                x=self.kwargs.pop("x", None),
                y=self.kwargs.pop("y", None),
                z=self.kwargs.pop("z", None),
                field=self.kwargs.pop("field", None),
                iso_value=self.kwargs.pop("iso_value", None),
                rendering=self.kwargs.pop("rendering", None),
                point=self.kwargs.pop("point", None),
                normal=self.kwargs.pop("normal", None),
                _obj=Graphics(session=self.solver).Surfaces.create(**self.kwargs),
            )
        )
        for attr in [
            "type",
            "creation_method",
            "x",
            "y",
            "z",
            "field",
            "iso_value",
            "rendering",
            "point",
            "normal",
        ]:
            val = getattr(self, attr)
            if val is not None:
                setattr(self, attr, val)

    def __setattr__(self, attr, value):
        if attr == "type":
            self._obj.definition.type = value
        elif attr == "creation_method":
            self._obj.definition.plane_surface.creation_method = value
        elif attr == "z":
            if self._obj.definition.plane_surface.creation_method() != "xy-plane":
                raise ValueError("Expected plane creation method to be 'xy-plane'")
            self._obj.definition.plane_surface.xy_plane.z = value
        elif attr == "y":
            if self._obj.definition.plane_surface.creation_method() != "zx-plane":
                raise ValueError("Expected plane creation method to be 'zx-plane'")
            self._obj.definition.plane_surface.zx_plane.y = value
        elif attr == "x":
            if self._obj.definition.plane_surface.creation_method() != "yz-plane":
                raise ValueError("Expected plane creation method to be 'yz-plane'")
            self._obj.definition.plane_surface.yz_plane.x = value
        elif attr == "field":
            self._obj.definition.iso_surface.field = _to_field_name_str(value)
        elif attr == "iso_value":
            self._obj.definition.iso_surface.iso_value = value
        elif attr == "rendering":
            self._obj.definition.iso_surface.rendering = value
        elif attr in ["point", "normal"]:
            if (
                self._obj.definition.plane_surface.creation_method()
                != "point-and-normal"
            ):
                raise ValueError(
                    "Expected plane creation method to be 'point-and-normal'"
                )
            if attr == "point":
                self._obj.definition.plane_surface.point.x = value[0]
                self._obj.definition.plane_surface.point.y = value[1]
                self._obj.definition.plane_surface.point.z = value[2]
            elif attr == "normal":
                self._obj.definition.plane_surface.normal.x = value[0]
                self._obj.definition.plane_surface.normal.y = value[1]
                self._obj.definition.plane_surface.normal.z = value[2]
        else:
            setattr(self._obj, attr, value)


class PlaneSurface(Surface):
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
    >>>     )
    >>> # Create same plane using 'create_xy_plane' method
    >>> surf_xy_plane = PlaneSurface.create_xy_plane(
    >>>     solver=solver_session,
    >>>     z=-0.0441921,
    >>>     )
    """

    @classmethod
    def create_xy_plane(cls, solver=None, z: float = 0.0, **kwargs):
        """Create a plane surface in the XY plane at a given Z value."""
        return cls(
            solver=solver,
            type="plane-surface",
            creation_method="xy-plane",
            z=z,
            **kwargs,
        )

    @classmethod
    def create_yz_plane(cls, solver=None, x=0.0, **kwargs):
        """Create a plane surface in the YZ plane at a given X value."""
        return cls(
            solver=solver,
            type="plane-surface",
            creation_method="yz-plane",
            x=x,
            **kwargs,
        )

    @classmethod
    def create_zx_plane(cls, solver=None, y=0.0, **kwargs):
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
        cls, solver=None, point=None, normal=None, **kwargs
    ):
        """Create a plane surface from a point and a normal vector."""
        if normal is None:
            normal = [0.0, 0.0, 0.0]
        if point is None:
            point = [0.0, 0.0, 0.0]
        return cls(
            solver=solver,
            type="plane-surface",
            creation_method="point-and-normal",
            point=point,
            normal=normal,
            **kwargs,
        )


class IsoSurface(Surface):
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
        solver=None,
        field: str | VariableDescriptor | None = None,
        rendering: str | None = None,
        iso_value: float | None = None,
        **kwargs
    ):
        """Create an iso-surface."""
        super().__init__(
            solver=solver,
            type="iso-surface",
            field=field,
            rendering=rendering,
            iso_value=iso_value,
            **kwargs,
        )


class Contour(GraphicsObject):
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

    def __init__(
        self,
        field: str | VariableDescriptor,
        surfaces: list[str],
        solver=None,
        **kwargs
    ):
        """__init__ method of Contour class."""
        kwargs.update(
            {
                "field": field,
                "surfaces": surfaces,
            }
        )
        super().__init__(solver, **kwargs)
        self.__dict__["_obj"] = Graphics(session=self.solver).Contours.create(
            **self.kwargs
        )


class Vector(GraphicsObject):
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

    def __init__(
        self,
        field: str | VariableDescriptor,
        surfaces: list[str],
        color_by: str | VariableDescriptor | None = None,
        scale: float = 1.0,
        solver=None,
        **kwargs
    ):
        """__init__ method of Vector class."""
        if color_by is None:
            color_by = field
        kwargs.update(
            {
                "vectors_of": field,
                "field": color_by,
                "surfaces": surfaces,
                "scale": scale,
            }
        )
        super().__init__(solver, **kwargs)
        self.__dict__["_obj"] = Graphics(session=self.solver).Vectors.create(
            **self.kwargs
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

    @staticmethod
    def _get_mapped_attrs(attr):
        _attr_map = {
            "field": "vectors_of",
            "color_by": "field",
        }
        return _attr_map.get(attr)

    def __getattr__(self, attr):
        attr = self._get_mapped_attrs(attr) or attr
        return getattr(self._obj, attr)

    def __setattr__(self, attr, value):
        attr = self._get_mapped_attrs(attr) or attr
        if attr == "surfaces":
            value = list(value)
        setattr(self._obj, attr, value)


class Pathline(GraphicsObject):
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

    def __init__(
        self,
        field: str | VariableDescriptor,
        surfaces: list[str],
        solver=None,
        **kwargs
    ):
        """__init__ method of Pathline class."""
        kwargs.update(
            {
                "field": field,
                "surfaces": surfaces,
            }
        )
        super().__init__(solver, **kwargs)
        self.__dict__["_obj"] = Graphics(session=self.solver).Pathlines.create(
            **self.kwargs
        )


class XYPlot(GraphicsObject):
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

    def __init__(
        self,
        surfaces: list[str],
        y_axis_function: str | VariableDescriptor,
        solver=None,
        local_surfaces_provider=None,
        **kwargs
    ):
        """__init__ method of XYPlot class."""
        kwargs.update(
            {
                "y_axis_function": y_axis_function,
                "surfaces": surfaces,
            }
        )
        super().__init__(solver, **kwargs)
        if "y_axis_function" in self.kwargs:
            self.kwargs["y_axis_function"] = _to_field_name_str(
                self.kwargs["y_axis_function"]
            )
        self.__dict__["_obj"] = Plots(
            session=self.solver, local_surfaces_provider=Graphics(solver).Surfaces
        ).XYPlots.create(**self.kwargs)

    def get_field_data(self):
        """Exposes 2d plot data data."""
        return XYPlotDataExtractor(self._obj).fetch_data()


class Monitor(GraphicsObject):
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

    def __init__(
        self, monitor_set_name: str, solver=None, local_surfaces_provider=None, **kwargs
    ):
        """__init__ method of Monitor class."""
        kwargs.update(
            {
                "monitor_set_name": monitor_set_name,
            }
        )
        super().__init__(solver, **kwargs)
        self.__dict__["_obj"] = Plots(
            session=self.solver, local_surfaces_provider=Graphics(solver).Surfaces
        ).Monitors.create(**self.kwargs)

    def get_field_data(self):
        """Exposes monitor data."""
        return self._obj.session.monitors.get_monitor_set_data(
            self.kwargs["monitor_set_name"]
        )
