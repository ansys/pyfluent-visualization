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
import ansys.fluent.visualization as pyviz
from ansys.fluent.visualization.graphics import graphics_windows_manager

_qt_window = None


class _GraphicsWindow:
    """Create a graphics window to perform operations like display,
    save, animate, etc. on graphics objects.
    """

    def __init__(
        self, window_id, grid: tuple = (1, 1), renderer=None, graphics_objs=None
    ):
        """__init__ method of GraphicsWindow class."""
        self._grid = grid
        self._graphics_objs = graphics_objs
        self.window_id = graphics_windows_manager.open_window(
            window_id=window_id,
            grid=self._grid,
            renderer=renderer,
        )
        graphics_windows_manager.plot_graphics(self._graphics_objs, self.window_id)
        self.graphics_window = graphics_windows_manager._post_windows.get(
            self.window_id
        )
        self._renderer = self.graphics_window.renderer
        try:
            self.plotter = self.graphics_window.renderer.plotter
        except AttributeError:
            self.plotter = None
        if pyviz.config.single_window:
            try:
                from PySide6.QtWidgets import QApplication

                from ansys.fluent.visualization.graphics.single_qt_windows import (
                    MainWindow,
                )
            except ModuleNotFoundError as ex:
                raise ModuleNotFoundError(
                    "Missing dependencies, "
                    "use 'pip install ansys-fluent-visualization[single-window]' "
                    "to install them."
                ) from ex

            global _qt_window
            if not _qt_window:
                QApplication.instance() or QApplication()
                _qt_window = MainWindow()
                _qt_window.show()
            _qt_window._add_tab(
                self.plotter,
                title=self.window_id,
            )

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
