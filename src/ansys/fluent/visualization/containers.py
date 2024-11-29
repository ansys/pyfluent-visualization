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
