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
from ansys.fluent.core.field_data_interfaces import _to_field_name_str
from ansys.fluent.core.utils.context_managers import _get_active_session
from ansys.units import VariableDescriptor

from ansys.fluent.visualization.graphics import Graphics
from ansys.fluent.visualization.plotter import Plots


class _GraphicsContainer:
    """Base class for graphics containers."""

    def __init__(self, solver, **kwargs):
        self.__dict__["solver"] = solver or _get_active_session()
        self.__dict__["kwargs"] = kwargs
        if self.solver is None:
            raise RuntimeError("No solver session provided and none found in context.")
        if "field" in self.kwargs:
            self.kwargs["field"] = _to_field_name_str(self.kwargs["field"])

    def __getattr__(self, attr):
        return getattr(self._obj, attr)

    def __setattr__(self, attr, value):
        if attr == "surfaces":
            value = list(value)
        setattr(self._obj, attr, value)

    def __dir__(self):
        return sorted(set(super().__dir__()) | set(dir(self._obj)))


class Mesh(_GraphicsContainer):
    """Mesh.

    Examples
    --------
    >>> from ansys.fluent.visualization import Mesh

    >>> # `solver_session` is a live Fluent session with a case
    >>> # and data which contains the following surfaces

    >>> mesh = Mesh(
    >>>     solver=solver_session, show_edges=True, surfaces=["in1", "in2", "in3"]
    >>> )
    """

    def __init__(self, solver=None, **kwargs):
        """__init__ method of Mesh class."""
        super().__init__(solver, **kwargs)
        self.__dict__["_obj"] = Graphics(session=self.solver).Meshes.create(
            **self.kwargs
        )


class Surface(_GraphicsContainer):
    """Surface.

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
    >>> surf_outlet_plane = Surface(solver=solver_session)
    >>> surf_outlet_plane.type = "iso-surface"
    >>> surf_outlet_plane.field = "y-coordinate"
    >>> surf_outlet_plane.iso_value = -0.125017
    """

    def __init__(self, solver=None, **kwargs):
        """__init__ method of Surface class."""
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
            assert self._obj.definition.plane_surface.creation_method() == "xy-plane"
            self._obj.definition.plane_surface.xy_plane.z = value
        elif attr == "y":
            assert self._obj.definition.plane_surface.creation_method() == "zx-plane"
            self._obj.definition.plane_surface.zx_plane.y = value
        elif attr == "x":
            assert self._obj.definition.plane_surface.creation_method() == "yz-plane"
            self._obj.definition.plane_surface.yz_plane.x = value
        elif attr == "field":
            self._obj.definition.iso_surface.field = _to_field_name_str(value)
        elif attr == "iso_value":
            self._obj.definition.iso_surface.iso_value = value
        elif attr == "rendering":
            self._obj.definition.iso_surface.rendering = value
        elif attr == "point":
            assert (
                self._obj.definition.plane_surface.creation_method()
                == "point-and-normal"
            )
            self._obj.definition.plane_surface.point.x = value[0]
            self._obj.definition.plane_surface.point.y = value[1]
            self._obj.definition.plane_surface.point.z = value[2]
        elif attr == "normal":
            assert (
                self._obj.definition.plane_surface.creation_method()
                == "point-and-normal"
            )
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
    """IsoSurface derived from Surface.
    Provides factory method for creating iso-surfaces.

    Examples
    --------
    >>> from ansys.fluent.visualization import IsoSurface

    >>> # `solver_session` is a live Fluent session with a case file loaded

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


class Contour(_GraphicsContainer):
    """Contour.

    Examples
    --------
    >>> from ansys.fluent.visualization import Contour

    >>> # `solver_session` is a live Fluent session with a case
    >>> # and data which contains the following surfaces

    >>> temperature_contour_object = Contour(
    >>>     solver=solver_session, field="temperature", surfaces=["in1", "in2", "in3",]
    >>> )
    """

    def __init__(self, solver=None, **kwargs):
        """__init__ method of Contour class."""
        super().__init__(solver, **kwargs)
        self.__dict__["_obj"] = Graphics(session=self.solver).Contours.create(
            **self.kwargs
        )


class Vector(_GraphicsContainer):
    """Vector.

    Examples
    --------
    >>> from ansys.fluent.visualization import Vector

    >>> # `solver_session` is a live Fluent session with a case
    >>> # and data which contains the following surfaces

    >>> velocity_vector_object = Vector(
    >>>     solver=solver_session,
    >>>     field="x-velocity",
    >>>     surfaces=["solid_up:1:830"],
    >>>     scale=2,
    >>> )
    """

    def __init__(self, solver=None, **kwargs):
        """__init__ method of Vector class."""
        super().__init__(solver, **kwargs)
        self.__dict__["_obj"] = Graphics(session=self.solver).Vectors.create(
            **self.kwargs
        )


class Pathline(_GraphicsContainer):
    """Pathline.

    Examples
    --------
    >>> from ansys.fluent.visualization import Pathline

    >>> # `solver_session` is a live Fluent session with a case
    >>> # and data which contains the following surfaces

    >>> pathlines = Pathline(solver=solver_session)
    >>> pathlines.field = "velocity-magnitude"
    >>> pathlines.surfaces = ["inlet", "inlet1", "inlet2"]
    """

    def __init__(self, solver=None, **kwargs):
        """__init__ method of Pathline class."""
        super().__init__(solver, **kwargs)
        self.__dict__["_obj"] = Graphics(session=self.solver).Pathlines.create(
            **self.kwargs
        )


class XYPlot(_GraphicsContainer):
    """XYPlot.

    Examples
    --------
    >>> from ansys.fluent.visualization import XYPlot

    >>> xy_plot = XYPlot(
    >>>     solver=solver_session,
    >>>     surfaces=["outlet"],
    >>>     y_axis_function="temperature",
    >>> )
    """

    def __init__(self, solver=None, local_surfaces_provider=None, **kwargs):
        """__init__ method of XYPlot class."""
        super().__init__(solver, **kwargs)
        if "y_axis_function" in self.kwargs:
            self.kwargs["y_axis_function"] = _to_field_name_str(
                self.kwargs["y_axis_function"]
            )
        self.__dict__["_obj"] = Plots(
            session=self.solver, local_surfaces_provider=Graphics(solver).Surfaces
        ).XYPlots.create(**self.kwargs)


class Monitor(_GraphicsContainer):
    """Monitor.

    Examples
    --------
    >>> from ansys.fluent.visualization import Monitor

    >>> residual = Monitor(solver=solver_session)
    >>> residual.monitor_set_name = "residual"
    """

    def __init__(self, solver=None, local_surfaces_provider=None, **kwargs):
        """__init__ method of Monitor class."""
        super().__init__(solver, **kwargs)
        self.__dict__["_obj"] = Plots(
            session=self.solver, local_surfaces_provider=Graphics(solver).Surfaces
        ).Monitors.create(**self.kwargs)
