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

from ansys.fluent.visualization.plotter import plotter_windows_manager


class _PlotterWindow:
    def __init__(self, window_id, grid: tuple = (1, 1), renderer=None, plot_objs=None):
        self._grid = grid
        self._plot_objs = plot_objs
        self._subplot_titles = []
        self.window_id = plotter_windows_manager.open_window(
            window_id=window_id, grid=self._grid, renderer=renderer
        )
        self._populate_subplot_titles()
        plotter_windows_manager.plot_graphics(self._plot_objs, self.window_id)
        self.plotter_window = plotter_windows_manager._post_windows.get(self.window_id)
        self.plotter = self.plotter_window.plotter

    def add_plots(self, object, position: tuple = (0, 0), title: str = "") -> None:
        """Add data to a plot.

        Parameters
        ----------
        object: GraphicsDefn
            Object to plot as a sub-plot.
        position: tuple, optional
            Position of the sub-plot.
        title: str, optional
            Title of the sub-plot.
        """
        self._plot_objs.append({**locals()})

    def _populate_subplot_titles(self):
        for obj_dict in self._plot_objs:
            if obj_dict.get("title"):
                self._subplot_titles.append(obj_dict.get("title"))
            elif hasattr(obj_dict.get("object")._obj, "monitor_set_name"):
                self._subplot_titles.append(
                    obj_dict.get("object")._obj.monitor_set_name()
                )
            else:
                self._subplot_titles.append("XYPlot")

    def save_graphic(
        self,
        filename: str,
    ) -> None:
        """Save a graphics.

        Parameters
        ----------
        filename : str
            Path to save the graphic file to.
            Supported formats are SVG, EPS, PS, PDF, and TEX.

        Raises
        ------
        ValueError
            If the window does not support the specified format.
        """
        if self.window_id:
            self.plotter_window.plotter.save_graphic(filename)

    def refresh(
        self,
        session_id: str | None = "",
        overlay: bool | None = None,
    ) -> None:
        """Refresh windows.

        Parameters
        ----------
        session_id : str, optional
           Session ID for refreshing the windows that belong only to this
           session. The default is ``""``, in which case the windows in all
           sessions are refreshed.
        """
        if self.window_id:
            plotter_windows_manager.refresh_windows(
                windows_id=[self.window_id], session_id=session_id
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
            plotter_windows_manager.animate_windows(
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
            plotter_windows_manager.close_windows(
                windows_id=[self.window_id], session_id=session_id
            )
