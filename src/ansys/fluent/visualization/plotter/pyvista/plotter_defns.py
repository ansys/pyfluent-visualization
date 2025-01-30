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

from typing import List, Optional

import numpy as np
import pyvista as pv

from ansys.fluent.visualization.plotter.abstract_plotter_defns import AbstractPlotter


class Plotter(AbstractPlotter):
    """Class for pyvista chart 2D plotter."""

    def __init__(
        self,
        window_id: str,
        curves: Optional[List[str]] = None,
        title: Optional[str] = "XY Plot",
        xlabel: Optional[str] = "position",
        ylabel: Optional[str] = "",
        remote_process: Optional[bool] = False,
    ):
        """Instantiate a pyvista chart 2D plotter.

        Parameters
        ----------
        window_id : str
            Window id.
        curves : List[str], optional
            List of curves name.
        title : str, optional
            Plot title.
        xlabel : str, optional
            X axis label.
        ylabel : str, optional
            Y axis label.
        figure : str, optional
            Matplot lib figure.
        axis : str, optional
            Subplot indices.
        remote_process: bool, optional
            Is remote process.
        """
        self._curves = [] if curves is None else curves
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._window_id = window_id
        self._min_y = None
        self._max_y = None
        self._min_x = None
        self._max_x = None
        self._yscale = None
        self._data = {}
        self._closed = False
        self._visible = False
        self._remote_process = remote_process
        self.chart = None
        self.plotter = None

    def plot(self, data: dict) -> None:
        """Draw plot in window.

        Parameters
        ----------
        data : dict
            Data to plot. Data consists the list of x and y
            values for each curve.
        """
        if not data:
            return
        for curve in data:
            min_y_value = np.amin(data[curve]["yvalues"])
            max_y_value = np.amax(data[curve]["yvalues"])
            min_x_value = np.amin(data[curve]["xvalues"])
            max_x_value = np.amax(data[curve]["xvalues"])
            self._data[curve]["xvalues"] = data[curve]["xvalues"].tolist()
            self._data[curve]["yvalues"] = data[curve]["yvalues"].tolist()
            self._min_y = min(self._min_y, min_y_value) if self._min_y else min_y_value
            self._max_y = max(self._max_y, max_y_value) if self._max_y else max_y_value
            self._min_x = min(self._min_x, min_x_value) if self._min_x else min_x_value
            self._max_x = max(self._max_x, max_x_value) if self._max_x else max_x_value

        if not self._remote_process:
            self.plotter = pv.Plotter(title=f"PyFluent [{self._window_id}]")
            self.chart = pv.Chart2D()
            self.plotter.add_chart(self.chart)
        self.chart.title = self._title
        self.chart.x_label = self._xlabel or ""
        self.chart.y_label = self._ylabel or ""
        color_list = ["b", "r", "g", "c", "m", "y", "k"]
        style_list = ["-", "--", "-.", "-.."]
        for count, curve in enumerate(self._curves):
            plot = self.chart.line(
                self._data[curve]["xvalues"],
                self._data[curve]["yvalues"],
                width=2.5,
                color=color_list[count % len(color_list)],
                style=style_list[count % len(style_list)],
                label=curve,
            )

        if self._max_x > self._min_x:
            self.chart.x_range = [self._min_x, self._max_x]
        y_range = self._max_y - self._min_y
        if self._yscale == "log":
            self.chart.y_axis.log_scale = True
            y_range = 0
        self.chart.y_range = [self._min_y - y_range * 0.2, self._max_y + y_range * 0.2]

        if not self._visible:
            self._visible = True
            self.plotter.show()

    def close(self):
        """Close window."""
        self.plotter.close()
        self._closed = True

    def is_closed(self):
        """Check if window is closed."""
        return self._closed

    def save_graphic(self, file_name: str):
        """Save graphics.

        Parameters
        ----------
        file_name : str
            File name to save graphics.
        """
        self.plotter.save_graphic(file_name)

    def set_properties(self, properties: dict):
        """Set plot properties.

        Parameters
        ----------
        properties : dict
            Plot properties i.e. curves, title, xlabel and ylabel.
        """
        self._curves = properties.get("curves", self._curves)
        self._title = properties.get("title", self._title)
        self._xlabel = properties.get("xlabel", self._xlabel)
        self._ylabel = properties.get("ylabel", self._ylabel)
        self._yscale = properties.get("yscale", self._yscale)
        self._data = {}
        self._min_y = None
        self._max_y = None
        self._min_x = None
        self._max_x = None
        self._reset()

    def __call__(self):
        """Reset and show plot."""
        self._reset()
        self._visible = False

    # private methods
    def _reset(self):
        for curve_name in self._curves:
            self._data[curve_name] = {}
            self._data[curve_name]["xvalues"] = []
            self._data[curve_name]["yvalues"] = []
        if not self.plotter:
            return
        for curve_name in self._curves:
            plot = self.chart.line([], [])
            plot.label = curve_name
