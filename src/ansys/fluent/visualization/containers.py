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


class GraphicsContainer:
    """Base class for graphics containers."""

    def __getattr__(self, attr):
        return getattr(self.obj, attr)

    def __setattr__(self, attr, value):
        setattr(self.obj, attr, value)


class Mesh(GraphicsContainer):
    """Mesh."""

    def __init__(self, solver, **kwargs):
        self.__dict__["obj"] = Graphics(session=solver).Meshes.create(**kwargs)


class Surface(GraphicsContainer):
    """Surface."""

    def __init__(self, solver, **kwargs):
        self.__dict__["obj"] = Graphics(session=solver).Surfaces.create(**kwargs)


class Contour(GraphicsContainer):
    """Contour."""

    def __init__(self, solver, **kwargs):
        self.__dict__["obj"] = Graphics(session=solver).Contours.create(**kwargs)


class Vector(GraphicsContainer):
    """Vector."""

    def __init__(self, solver, **kwargs):
        self.__dict__["obj"] = Graphics(session=solver).Vectors.create(**kwargs)


class Pathline(GraphicsContainer):
    """Pathline."""

    def __init__(self, solver, **kwargs):
        self.__dict__["obj"] = Graphics(session=solver).Pathlines.create(**kwargs)


class XYPlot(GraphicsContainer):
    """XYPlot."""

    def __init__(self, solver, local_surfaces_provider=None, **kwargs):
        self.__dict__["obj"] = Plots(
            session=solver, local_surfaces_provider=Graphics(solver).Surfaces
        ).XYPlots.create(**kwargs)


class Monitor(GraphicsContainer):
    """Monitor."""

    def __init__(self, solver, local_surfaces_provider=None, **kwargs):
        self.__dict__["obj"] = Plots(
            session=solver, local_surfaces_provider=Graphics(solver).Surfaces
        ).Monitors.create(**kwargs)
