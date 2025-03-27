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

from ansys.fluent.visualization.graphics import Graphics
from ansys.fluent.visualization.plotter import Plots


class _GraphicsContainer:
    """Base class for graphics containers."""

    def __getattr__(self, attr):
        return getattr(self.obj, attr)

    def __setattr__(self, attr, value):
        setattr(self.obj, attr, value)


class Mesh(_GraphicsContainer):
    """Mesh.

    Examples
    --------
    >>> from ansys.fluent.visualization import Mesh

    >>> # `solver_session` is a live Fluent session with a case
    >>> # and data which contains the following surfaces

    >>> mesh_object = Mesh(
    >>>     solver=solver_session, show_edges=True, surfaces=["in1", "in2", "in3"]
    >>> )
    """

    def __init__(self, solver, **kwargs):
        """__init__ method of Mesh class."""
        self.__dict__["obj"] = Graphics(session=solver).Meshes.create(**kwargs)


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

    def __init__(self, solver, **kwargs):
        """__init__ method of Surface class."""
        self.__dict__.update(
            dict(
                type=kwargs.pop("type", None),
                creation_method=kwargs.pop("creation_method", None),
                x=kwargs.pop("x", None),
                y=kwargs.pop("y", None),
                z=kwargs.pop("z", None),
                field=kwargs.pop("field", None),
                iso_value=kwargs.pop("iso_value", None),
                rendering=kwargs.pop("rendering", None),
                obj=Graphics(session=solver).Surfaces.create(**kwargs),
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
        ]:
            val = getattr(self, attr)
            if val is not None:
                setattr(self, attr, val)

    def __setattr__(self, attr, value):
        if attr == "type":
            self.obj.definition.type = value
        elif attr == "creation_method":
            self.obj.definition.plane_surface.creation_method = value
        elif attr == "z":
            assert self.obj.definition.plane_surface.creation_method() == "xy-plane"
            self.obj.definition.plane_surface.xy_plane.z = value
        elif attr == "y":
            assert self.obj.definition.plane_surface.creation_method() == "zx-plane"
            self.obj.definition.plane_surface.zx_plane.y = value
        elif attr == "x":
            assert self.obj.definition.plane_surface.creation_method() == "yz-plane"
            self.obj.definition.plane_surface.yz_plane.x = value
        elif attr == "field":
            self.obj.definition.iso_surface.field = value
        elif attr == "iso_value":
            self.obj.definition.iso_surface.iso_value = value
        elif attr == "rendering":
            self.obj.definition.iso_surface.rendering = value
        else:
            setattr(self.obj, attr, value)


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

    def __init__(self, solver, **kwargs):
        """__init__ method of Contour class."""
        self.__dict__["obj"] = Graphics(session=solver).Contours.create(**kwargs)


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

    def __init__(self, solver, **kwargs):
        """__init__ method of Vector class."""
        self.__dict__["obj"] = Graphics(session=solver).Vectors.create(**kwargs)


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

    def __init__(self, solver, **kwargs):
        """__init__ method of Pathline class."""
        self.__dict__["obj"] = Graphics(session=solver).Pathlines.create(**kwargs)


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

    def __init__(self, solver, local_surfaces_provider=None, **kwargs):
        """__init__ method of XYPlot class."""
        self.__dict__["obj"] = Plots(
            session=solver, local_surfaces_provider=Graphics(solver).Surfaces
        ).XYPlots.create(**kwargs)


class Monitor(_GraphicsContainer):
    """Monitor.

    Examples
    --------
    >>> from ansys.fluent.visualization import Monitor

    >>> residual = Monitor(solver=solver_session)
    >>> residual.monitor_set_name = "residual"
    """

    def __init__(self, solver, local_surfaces_provider=None, **kwargs):
        """__init__ method of Monitor class."""
        self.__dict__["obj"] = Plots(
            session=solver, local_surfaces_provider=Graphics(solver).Surfaces
        ).Monitors.create(**kwargs)
