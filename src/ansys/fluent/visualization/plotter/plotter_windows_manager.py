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

"""Module for plotter windows management."""

import itertools
import multiprocessing as mp
from typing import Dict, List, Optional, Union

from ansys.fluent.core.fluent_connection import FluentConnection

from ansys.fluent.interface.post_objects.check_in_notebook import in_jupyter
from ansys.fluent.interface.post_objects.post_object_definitions import (
    MonitorDefn,
    PlotDefn,
    XYPlotDefn,
)
from ansys.fluent.interface.post_objects.singleton_meta import AbstractSingletonMeta
import ansys.fluent.visualization as pyviz
from ansys.fluent.visualization.plotter.matplotlib.renderer import ProcessPlotter
from ansys.fluent.visualization.post_data_extractor import XYPlotDataExtractor
from ansys.fluent.visualization.visualization_windows_manager import (
    VisualizationWindow,
    VisualizationWindowsManager,
)


class _ProcessPlotterHandle:
    """Provides the process plotter handle."""

    def __init__(
        self,
        window_id,
        curves=[],
        title="XY Plot",
        xlabel="position",
        ylabel="",
        grid=(1, 1),
    ):
        self._closed = False
        self.plot_pipe, plotter_pipe = mp.Pipe()
        self.plotter = ProcessPlotter(
            window_id, curves, title, xlabel, ylabel, grid=grid
        )
        self.plot_process = mp.Process(
            target=self.plotter, args=(plotter_pipe,), daemon=True
        )
        self.plot_process.start()
        FluentConnection._monitor_thread.cbs.append(self.close)

    def render(self, data):
        self.plot_pipe.send({"data": data})

    def show(self):
        self.plotter.show()

    # def set_properties(self, properties):
    #     self.plot_pipe.send({"properties": properties})

    def save_graphic(self, name: str):
        self.plot_pipe.send({"save_graphic": name})

    def is_closed(self):
        if self._closed:
            return True
        try:
            self.plot_pipe.send({})
        except (BrokenPipeError, AttributeError):
            self._closed = True
        return self._closed

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            self.plot_pipe.send(None)
        except (BrokenPipeError, AttributeError):
            pass


class PlotterWindow(VisualizationWindow):
    """Provides for managing Plotter windows."""

    def __init__(
        self,
        id: str,
        grid: tuple | None = (1, 1),
        renderer: str = None,
    ):
        """Instantiate a plotter window.

        Parameters
        ----------
        id : str
            Window ID.
        grid: tuple, optional
            Layout or arrangement of the graphics window. The default is ``(1, 1)``.
        renderer: str, optional
            Renderer for the graphics window. The default is ``None``.
        """
        self.id: str = id
        self.post_object = None
        self._grid = grid
        self.plotter: Union[_ProcessPlotterHandle, "Plotter"] = self._get_plotter(
            plotter_string=renderer
        )
        self.close: bool = False
        self.refresh: bool = False
        self._object_list_to_render: list = []
        self._obj_list: list = []

    def plot(self, grid=(1, 1), position=(0, 0), show=True, subplot_titles=None):
        """Draw a plot."""
        if self.post_object is not None:
            plot = (
                _XYPlot(self.post_object, self.plotter)
                if self.post_object.__class__.__name__ == "XYPlot"
                else _MonitorPlot(self.post_object, self.plotter)
            )
            plot_data = plot()
            self._object_list_to_render.append(
                [
                    {
                        "data": plot_data[0],
                        "properties": plot_data[1],
                        "position": (0, 0),
                        "kwargs": {},
                    }
                ]
            )
            self.plotter.render(self._object_list_to_render)
            self.plotter.show()

    def plot_graphics(self, object_list):
        self._obj_list = object_list
        if self.refresh:
            self._object_list_to_render = []
        for obj_dict in object_list:
            self.post_object = obj_dict["object"]._obj
            plot = (
                _XYPlot(self.post_object, self.plotter)
                if self.post_object.__class__.__name__ == "XYPlot"
                else _MonitorPlot(self.post_object, self.plotter)
            )

            plot_data = plot()
            self._object_list_to_render.append(
                [
                    {
                        "data": plot_data[0],
                        "properties": plot_data[1],
                        "position": obj_dict["position"],
                        "kwargs": obj_dict["kwargs"],
                    }
                ]
            )
        self.plotter.render(self._object_list_to_render)

    def _show_plot(self):
        self.plotter.show()

    # private methods
    def _get_plotter(self, plotter_string=None):
        from ansys.fluent.visualization.registrar import _renderer, get_renderer

        if plotter_string is None:
            plotter_string = pyviz.config.two_dimensional_renderer
        try:
            plotter = get_renderer(plotter_string)
        except KeyError as ex:
            error_message = (
                f"Error: Renderer '{plotter_string}' not found or registered. "
                "We tried to load the renderer but encountered an issue.\n"
                "Possible reasons could include:\n"
                "  - The renderer name might be misspelled.\n"
                "  - The renderer might not be installed or available.\n"
                "  - There might be an issue with the system configuration.\n\n"
                "Currently available renderers are: "
                f"{', '.join(_renderer.keys())}.\n"
                "Please ensure that the renderer name is correct or register the"
                " renderer if it is custom. If the issue persists, check your"
                " system configuration."
            )

            raise KeyError(error_message) from ex
        return (
            plotter(self.id, grid=self._grid)
            if in_jupyter() or not pyviz.config.interactive
            else _ProcessPlotterHandle(self.id, grid=self._grid)
        )


class _XYPlot:
    """Provides for drawing an XY plot."""

    def __init__(
        self, post_object: XYPlotDefn, plotter: Union[_ProcessPlotterHandle, "Plotter"]
    ):
        """Instantiate an XY plot.

        Parameters
        ----------
        post_object : XYPlotDefn
            Object to plot.
        plotter: Union[_ProcessPlotterHandle, Plotter]
            Plotter to plot the data.
        """
        self.post_object: XYPlotDefn = post_object
        self.plotter: Union[_ProcessPlotterHandle, "Plotter"] = plotter

    def __call__(self):
        """Draw an XY plot."""
        if not self.post_object:
            return
        xy_data = XYPlotDataExtractor(self.post_object).fetch_data()
        properties = {
            "curves": list(xy_data),
            "title": "XY Plot",
            "xlabel": "position",
            "ylabel": self.post_object.y_axis_function(),
        }
        return xy_data, properties


class _MonitorPlot:
    """Provides for drawing monitor plots."""

    def __init__(
        self, post_object: MonitorDefn, plotter: Union[_ProcessPlotterHandle, "Plotter"]
    ):
        """Instantiate a monitor plot.

        Parameters
        ----------
        post_object : MonitorDefn
            Object to plot.
        plotter: Union[_ProcessPlotterHandle, Plotter]
            Plotter to plot the data.
        """
        self.post_object: MonitorDefn = post_object
        self.plotter: Union[_ProcessPlotterHandle, "Plotter"] = plotter

    def __call__(self):
        """Draw a monitor plot."""
        if not self.post_object:
            return
        self.post_object.session.monitors.refresh(None, None)
        monitors = self.post_object.session.monitors
        xy_data = {}
        timeout = 5
        count = 0.0
        import time

        while True:
            indices, columns_data = monitors.get_monitor_set_data(
                self.post_object.monitor_set_name()
            )
            if columns_data != {} or count > timeout:
                break
            time.sleep(0.1)
            count += 0.1

        for column_name, column_data in columns_data.items():
            xy_data[column_name] = {"xvalues": indices, "yvalues": column_data}
        monitor_set_name = self.post_object.monitor_set_name()
        properties = {
            "curves": list(xy_data.keys()),
            "title": monitor_set_name,
            "xlabel": monitors.get_monitor_set_prop(monitor_set_name, "xlabel"),
            "ylabel": monitors.get_monitor_set_prop(monitor_set_name, "ylabel"),
            "yscale": "log" if monitor_set_name == "residual" else "linear",
        }
        return xy_data, properties


class PlotterWindowsManager(
    VisualizationWindowsManager, metaclass=AbstractSingletonMeta
):
    """Provides for managing Plotter windows."""

    def __init__(self):
        """Instantiate a windows manager for the plotter."""
        self._post_windows: Dict[str, PlotterWindow] = {}

    def open_window(
        self,
        window_id: str | None = None,
        grid: tuple | None = (1, 1),
        renderer: str | None = None,
    ) -> str:
        """Open a new window.

        Parameters
        ----------
        window_id : str, optional
            ID for the new window. The default is ``None``, in which
            case a unique ID is automatically assigned.
        grid: tuple, optional
            Layout or arrangement of the graphics window. The default is ``(1, 1)``.
        renderer: str, optional
            Renderer for the graphics window. The default is ``None``.

        Returns
        -------
        str
            ID for the new window.
        """
        if not window_id:
            window_id = self._get_unique_window_id()
        self._open_window(window_id, grid, renderer=renderer)
        return window_id

    def set_object_for_window(self, object: PlotDefn, window_id: str) -> None:
        """Associate a visualization object with a running window instance.

        Parameters
        ----------
        object : PlotDefn
            Post object to associate with a running window instance.
        window_id : str
            Window ID for the association.

        Raises
        ------
        RuntimeError
            If the window does not support the object.
        """
        if not isinstance(object, PlotDefn):
            raise RuntimeError("object not implemented.")
        window = self._post_windows.get(window_id)
        if window:
            window.post_object = object

    def plot(
        self,
        object: PlotDefn,
        window_id: Optional[str] = None,
        grid=(1, 1),
        position=(0, 0),
        subplot_titles=None,
        show=True,
    ) -> None:
        """Draw a plot.

        Parameters
        ----------
        object: PlotDefn
            Object to plot.
        window_id : str, optional
            Window ID for the plot. The default is ``None``, in which
            case a unique ID is assigned.

        Raises
        ------
        RuntimeError
            If the window does not support the object.
        """
        if subplot_titles is None:
            subplot_titles = []
        if not isinstance(object, PlotDefn):
            raise RuntimeError("Object is not implemented.")
        if not window_id:
            window_id = self._get_unique_window_id()
        window = self._open_window(window_id)
        window.post_object = object
        window.plot(
            grid=grid, position=position, show=show, subplot_titles=subplot_titles
        )

    def plot_graphics(self, graphics_objects, window_id):
        for graphics_object_dict in graphics_objects:
            if not isinstance(graphics_object_dict["object"]._obj, PlotDefn):
                raise RuntimeError("Object type currently not supported.")
        window = self._post_windows.get(window_id) or self._open_window(window_id)
        window.plot_graphics(graphics_objects)

    def show_plots(self, window_id: str):
        window = self._open_window(window_id)
        window._show_plot()

    def save_graphic(
        self,
        window_id: str,
        format: str,
    ) -> None:
        """Save a graphic.

        Parameters
        ----------
        window_id : str
            Window ID for the graphic to save.
        format : str
            Graphic file format. Supported formats are EPS, JPEG, JPG,
            PDF, PGF, PNG, PS, RAW, RGBA, SVG, SVGZ, TIF, and TIFF.

        Raises
        ------
        ValueError
            If window does not support specified format.
        """
        window = self._post_windows.get(window_id)
        if window:
            window.plotter.save_graphic(f"{window_id}.{format}")

    def refresh_windows(
        self,
        session_id: Optional[str] = "",
        windows_id=None,
        overlay: Optional[bool] = None,
    ) -> None:
        """Refresh windows.

        Parameters
        ----------
        session_id : str, optional
           Session ID for refreshing the windows that belong only to this
           session. The default is ``""``, in which case the windows in all
           sessions are refreshed.
        windows_id : List[str], optional
            IDs of the windows to refresh. The default is ``[]``, in which case
            all windows are refreshed.
        """
        if windows_id is None:
            windows_id = []
        windows_id = self._get_windows_id(session_id, windows_id)
        for window_id in windows_id:
            window = self._post_windows.get(window_id)
            if window:
                window.refresh = True
                window.plot_graphics(window._obj_list)

    def animate_windows(
        self,
        session_id: Optional[str] = "",
        windows_id=None,
    ) -> None:
        """Animate windows.

         Parameters
        ----------
        session_id : str, optional
           Session ID for animating the windows that belong only to this
           session. The default is ``""``, in which case the windows in all
           sessions are animated.
        windows_id : List[str], optional
            List of IDs for the windows to animate. The default is ``[]``, in which
            case all windows are animated.
        Raises
        ------
        NotImplementedError
            If not implemented.
        """
        if windows_id is None:
            windows_id = []
        raise NotImplementedError("animate_windows not implemented.")

    def close_windows(
        self,
        session_id: Optional[str] = "",
        windows_id=None,
    ) -> None:
        """Close windows.

        Parameters
        ----------
        session_id : str, optional
           Session ID for closing the windows that belong only to this session.
           The default is ``""``, in which case the windows in all sessions
           are closed.
        windows_id : List[str], optional
            List of IDs for the windows to close. The default is ``[]``, in which
            all windows are closed.
        """
        if windows_id is None:
            windows_id = []
        windows_id = self._get_windows_id(session_id, windows_id)
        for window_id in windows_id:
            window = self._post_windows.get(window_id)
            if window:
                window.plotter.close()
                window.close = True

    # private methods

    def _open_window(
        self,
        window_id: str,
        grid: tuple | None = (1, 1),
        renderer=None,
    ) -> Union["Plotter", _ProcessPlotterHandle]:
        window = self._post_windows.get(window_id)
        if window and not window.plotter.is_closed():
            if not (in_jupyter() or not pyviz.config.interactive) or window.refresh:
                window.refresh = False
        else:
            window = PlotterWindow(window_id, grid, renderer=renderer)
            self._post_windows[window_id] = window
            if in_jupyter():
                window.plotter()
        return window

    def _get_windows_id(
        self,
        session_id: Optional[str] = "",
        windows_id=None,
    ) -> List[str]:
        if windows_id is None:
            windows_id = []
        return [
            window_id
            for window_id in [
                window_id
                for window_id, window in self._post_windows.items()
                if not window.plotter.is_closed()
                and (not session_id or session_id == window.post_object.session.id)
            ]
            if not windows_id or window_id in windows_id
        ]

    def _get_unique_window_id(self) -> str:
        itr_count = itertools.count()
        while True:
            window_id = f"window-{next(itr_count)}"
            if window_id not in self._post_windows:
                return window_id


plotter_windows_manager = PlotterWindowsManager()
