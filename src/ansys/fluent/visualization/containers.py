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

    Example
    -------
    >>> from ansys.fluent.visualization import Mesh

    >>> mesh_object = Mesh(
    >>>     solver=solver_session, show_edges=True, surfaces=["in1", "in2", "in3"]
    >>> )
    """

    def __init__(self, solver, **kwargs):
        self.__dict__["obj"] = Graphics(session=solver).Meshes.create(**kwargs)


class Surface(_GraphicsContainer):
    """Surface.

    Example
    -------
    >>> from ansys.fluent.visualization import Surface

    >>> # For plane-surface
    >>> surf_xy_plane = Surface(solver=solver_session)
    >>> surf_xy_plane.definition.type = "plane-surface"
    >>> surf_xy_plane.definition.plane_surface.creation_method = "xy-plane"
    >>> plane_surface_xy = surf_xy_plane.definition.plane_surface.xy_plane
    >>> plane_surface_xy.z = -0.0441921

    >>> # For iso-surface
    >>> surf_outlet_plane = Surface(solver=solver_session)
    >>> surf_outlet_plane.definition.type = "iso-surface"
    >>> iso_surf = surf_outlet_plane.definition.iso_surface
    >>> iso_surf.field = "y-coordinate"
    >>> iso_surf.iso_value = -0.125017
    """

    def __init__(self, solver, **kwargs):
        self.__dict__["obj"] = Graphics(session=solver).Surfaces.create(**kwargs)


class Contour(_GraphicsContainer):
    """Contour.

    Example
    -------
    >>> from ansys.fluent.visualization import Contour

    >>> temperature_contour_object = Contour(
    >>>     solver=solver_session, field="temperature", surfaces=["in1", "in2", "in3",]
    >>> )
    """

    def __init__(self, solver, **kwargs):
        self.__dict__["obj"] = Graphics(session=solver).Contours.create(**kwargs)


class Vector(_GraphicsContainer):
    """Vector.

    Example
    -------
    >>> from ansys.fluent.visualization import Vector

    >>> velocity_vector_object = Vector(
    >>>     solver=solver_session,
    >>>     field="pressure",
    >>>     surfaces=["solid_up:1:830"],
    >>>     scale=2,
    >>> )
    """

    def __init__(self, solver, **kwargs):
        self.__dict__["obj"] = Graphics(session=solver).Vectors.create(**kwargs)


class Pathline(_GraphicsContainer):
    """Pathline.

    Example
    -------
    >>> from ansys.fluent.visualization import Pathline

    >>> pathlines = Pathline(solver=solver_session)
    >>> pathlines.field = "velocity-magnitude"
    >>> pathlines.surfaces = ["inlet", "inlet1", "inlet2"]
    """

    def __init__(self, solver, **kwargs):
        self.__dict__["obj"] = Graphics(session=solver).Pathlines.create(**kwargs)


class XYPlot(_GraphicsContainer):
    """XYPlot.

    Example
    -------
    >>> from ansys.fluent.visualization import XYPlot

    >>> xy_plot = XYPlot(
    >>>     solver=solver_session,
    >>>     surfaces=["outlet"],
    >>>     y_axis_function="temperature",
    >>> )
    """

    def __init__(self, solver, local_surfaces_provider=None, **kwargs):
        self.__dict__["obj"] = Plots(
            session=solver, local_surfaces_provider=Graphics(solver).Surfaces
        ).XYPlots.create(**kwargs)


class Monitor(_GraphicsContainer):
    """Monitor.

    Example
    -------
    >>> from ansys.fluent.visualization import Monitor

    >>> residual = Monitor(solver=solver_session)
    >>> residual.monitor_set_name = "residual"
    """

    def __init__(self, solver, local_surfaces_provider=None, **kwargs):
        self.__dict__["obj"] = Plots(
            session=solver, local_surfaces_provider=Graphics(solver).Surfaces
        ).Monitors.create(**kwargs)
