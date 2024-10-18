"""Module for plotter windows management."""

from typing import Union

from ansys.fluent.core.post_objects.check_in_notebook import in_notebook
from ansys.fluent.core.post_objects.post_object_definitions import (
    MonitorDefn,
    XYPlotDefn,
)

from ansys.fluent.visualization import PLOTTER, get_config

if PLOTTER == "matplotlib":
    from ansys.fluent.visualization.plotter.matplotlib.plotter_defns import Plotter
else:
    from ansys.fluent.visualization.plotter.pyvista.plotter_defns import Plotter

from ansys.fluent.visualization.post_data_extractor import XYPlotDataExtractor
from ansys.fluent.visualization.post_windows_manager import PostWindow


class _ProcessPlotterHandle:
    """Provides the process plotter handle."""

    pass


class PlotterWindow(PostWindow):
    """Provides for managing Plotter windows."""

    def __init__(self, id: str | None = None):
        """Instantiate a plotter window.

        Parameters
        ----------
        id : str|None
            Window ID.
        """
        self.id: str = id if id else "-"
        self.plotter: Union[_ProcessPlotterHandle, Plotter] = self._get_plotter()

    def plot(self, post_object):
        """Create a plot.

        Parameters
        ----------
        post_object : PlotDefn
            Object to plot.
        """
        self.post_object = post_object
        plot = (
            _XYPlot(self.post_object, self.plotter)
            if self.post_object.__class__.__name__ == "XYPlot"
            else _MonitorPlot(self.post_object, self.plotter)
        )
        plot()

    # private methods
    def _get_plotter(self):
        return (
            Plotter(self.id)
            if in_notebook() or get_config()["blocking"]
            else _ProcessPlotterHandle(self.id)
        )


class _XYPlot:
    """Provides for drawing an XY plot."""

    def __init__(
        self, post_object: XYPlotDefn, plotter: Union[_ProcessPlotterHandle, Plotter]
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
        self.plotter: Union[_ProcessPlotterHandle, Plotter] = plotter

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
        if in_notebook() or get_config()["blocking"]:
            self.plotter.set_properties(properties)
        else:
            try:
                self.plotter.set_properties(properties)
            except BrokenPipeError:
                self.plotter: Union[_ProcessPlotterHandle, Plotter] = (
                    self._get_plotter()
                )
                self.plotter.set_properties(properties)
        self.plotter.plot(xy_data)


class _MonitorPlot:
    """Provides for drawing monitor plots."""

    def __init__(
        self, post_object: MonitorDefn, plotter: Union[_ProcessPlotterHandle, Plotter]
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
        self.plotter: Union[_ProcessPlotterHandle, Plotter] = plotter

    def __call__(self):
        """Draw a monitor plot."""
        if not self.post_object:
            return
        monitors = self.post_object._api_helper.monitors
        indices, columns_data = monitors.get_monitor_set_data(
            self.post_object.monitor_set_name()
        )
        xy_data = {}
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

        if in_notebook() or get_config()["blocking"]:
            self.plotter.set_properties(properties)
        else:
            try:
                self.plotter.set_properties(properties)
            except BrokenPipeError:
                self.plotter: Union[_ProcessPlotterHandle, Plotter] = (
                    self._get_plotter()
                )
                self.plotter.set_properties(properties)
        if xy_data:
            self.plotter.plot(xy_data)
