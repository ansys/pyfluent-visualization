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

"""A wrapper to improve the user interface of graphics."""
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

import ansys.fluent.visualization as pyviz
from ansys.fluent.visualization import get_config
from ansys.fluent.visualization.graphics import graphics_windows_manager
from ansys.fluent.visualization.plotter.plotter_windows import PlotterWindow

_qt_window = None


class GraphicsWindow:
    """Create a graphics window to perform operations like display,
    save, animate, etc. on graphics objects.

    Examples
    --------
    You can add graphics objects like mesh, surface or plots and then display it.

    >>> from ansys.fluent.visualization import GraphicsWindow

    >>> graphics_window = GraphicsWindow()
    >>> graphics_window.add_graphics(mesh_object)
    >>> graphics_window.show()

    You can add multiple graphics objects and display as a structured layout.

    >>> graphics_window = GraphicsWindow(grid=(2, 2))
    >>> graphics_window.add_graphics(mesh_object, position=(0, 0))
    >>> graphics_window.add_graphics(temperature_contour_object, position=(0, 1))
    >>> graphics_window.add_graphics(velocity_vector_object, position=(1, 0))
    >>> graphics_window.add_graphics(xy_plot, position=(1, 1))
    >>> graphics_window.show()
    """

    def __init__(self, grid: tuple = (1, 1)):
        """__init__ method of GraphicsWindow class."""
        self._grid = grid
        self._graphics_objs = []
        self.window_id = None

    def add_graphics(
        self,
        object,
        position: tuple = (0, 0),
        opacity: float = 1,
        title: str = "",
    ) -> None:
        """Add data to a plot.

        Parameters
        ----------
        object: GraphicsDefn
            Object to plot as a sub-plot.
        position: tuple, optional
            Position of the sub-plot.
        opacity: float, optional
            Transparency of the sub-plot.
        title: str, optional
            Title of the sub-plot (only for plots).
        """
        self._graphics_objs.append({**locals()})

    def _all_plt_objs(self):
        from ansys.fluent.core.post_objects.post_object_definitions import PlotDefn

        for obj in self._graphics_objs:
            if not isinstance(obj["object"].obj, PlotDefn):
                return False
        return True

    def show(self) -> None:
        """Render the objects in window and display the same."""
        self.window_id = graphics_windows_manager.open_window(grid=self._grid)
        if self._all_plt_objs() and get_config()["blocking"]:
            p = PlotterWindow(grid=self._grid)
            for obj in self._graphics_objs:
                p.add_plots(obj["object"], position=obj["position"], title=obj["title"])
            p.show(self.window_id)
        else:
            self.graphics_window = graphics_windows_manager._post_windows.get(
                self.window_id
            )
            self._renderer = self.graphics_window.renderer
            self.plotter = self.graphics_window.renderer.plotter
            for i in range(len(self._graphics_objs)):
                graphics_windows_manager.add_graphics(
                    object=self._graphics_objs[i]["object"].obj,
                    window_id=self.window_id,
                    fetch_data=True,
                    overlay=True,
                    position=self._graphics_objs[i]["position"],
                    opacity=self._graphics_objs[i]["opacity"],
                )
            if pyviz.SINGLE_WINDOW:
                global _qt_window
                if not _qt_window:
                    QApplication.instance() or QApplication()
                    _qt_window = MainWindow()
                    _qt_window.show()
                _qt_window._add_tab(
                    self.plotter,
                    title=self.window_id.replace(
                        self.window_id[-1], str(int(self.window_id[-1]) + 1)
                    ),
                )
            else:
                graphics_windows_manager.show_graphics(self.window_id)

    def save_graphic(
        self,
        filename: str,
    ) -> None:
        """Save a screenshot of the rendering window as a graphic file.

        Parameters
        ----------
        filename : str
            Path to save the graphic file to.
            Supported formats are SVG, EPS, PS, PDF, and TEX.

        Raises
        ------
        ValueError
            If the window does not support the specified format.

        Examples
        --------
        >>> import ansys.fluent.core as pyfluent
        >>> from ansys.fluent.core import examples
        >>> from ansys.fluent.visualization import GraphicsWindow, Vector
        >>>
        >>> import_case = examples.download_file(
        >>> file_name="exhaust_system.cas.h5", directory="pyfluent/exhaust_system"
        >>> )
        >>> import_data = examples.download_file(
        >>> file_name="exhaust_system.dat.h5", directory="pyfluent/exhaust_system"
        >>> )
        >>>
        >>> solver_session = pyfluent.launch_fluent()
        >>> solver_session.settings.file.read_case(file_name=import_case)
        >>> solver_session.settings.file.read_data(file_name=import_data)
        >>>
        >>> velocity_vector = Vector(
        >>> solver=solver_session, field="pressure", surfaces=["solid_up:1:830"]
        >>> )
        >>> graphics_window = GraphicsWindow()
        >>> graphics_window.add_graphics(velocity_vector)
        >>> graphics_window.save_graphic("saved_vector.svg")
        """
        if self.window_id:
            self._renderer.save_graphic(filename)

    def refresh(
        self,
        session_id: str | None = "",
        overlay: bool | None = False,
    ) -> None:
        """Refresh windows.

        Parameters
        ----------
        session_id : str, optional
           Session ID for refreshing the windows that belong only to this
           session. The default is ``""``, in which case the windows in all
           sessions are refreshed.
        overlay : bool, Optional
            Overlay graphics over existing graphics.
        """
        if self.window_id:
            graphics_windows_manager.refresh_windows(
                windows_id=[self.window_id], session_id=session_id, overlay=overlay
            )

    def animate(
        self,
        session_id: str | None = "",
    ) -> None:
        """Animate windows.

        Parameters
        ----------
        session_id : str, optional
           Session ID for animating the windows that belong only to this
           session. The default is ``""``, in which case the windows in all
           sessions are animated.

        Raises
        ------
        NotImplementedError
            If not implemented.
        """
        if self.window_id:
            graphics_windows_manager.animate_windows(
                windows_id=[self.window_id], session_id=session_id
            )

    def close(
        self,
        session_id: str | None = "",
    ) -> None:
        """Close windows.

        Parameters
        ----------
        session_id : str, optional
           Session ID for closing the windows that belong only to this session.
           The default is ``""``, in which case the windows in all sessions
           are closed.
        """
        if self.window_id:
            graphics_windows_manager.close_windows(
                windows_id=[self.window_id], session_id=session_id
            )


# Define the main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyFluent Visualization Plots")
        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width() * 0.75)
        height = int(screen.height() * 0.75)
        self.setGeometry(
            (screen.width() - width) // 2,  # Center X
            (screen.height() - height) // 2,  # Center Y
            width,
            height,
        )
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setMovable(True)
        self.plotters = []

    def _add_tab(self, plotter, title="-"):
        tab = QWidget()
        layout = QVBoxLayout()

        self.plotters.append(plotter)
        layout.addWidget(plotter.interactor)
        tab.setLayout(layout)

        # Add tabs with PyVista BackgroundPlotters
        self.tabs.addTab(tab, f"PyViz ({title})")

    def closeEvent(self, event):
        """Ensure proper cleanup of plotter instances on window close."""
        for plotter in self.plotters:
            plotter.close()  # Properly close each PyVista plotter
        event.accept()
        global _qt_window
        _qt_window = None
