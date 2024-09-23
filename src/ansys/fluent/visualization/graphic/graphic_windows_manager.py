"""Module for graphic windows management."""

from ansys.fluent.visualization.graphic.pyvista.graphic_defns import (
    PyVistaWindowsManager,
)


class GraphicWindowsManager(PyVistaWindowsManager):
    pass


graphic_windows_manager = GraphicWindowsManager()
