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

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ansys.fluent.visualization.plotter.abstract_plotter_defns import AbstractPlotter


class Plotter(AbstractPlotter):
    """Class for matplotlib plotter."""

    def __init__(
        self,
        window_id: str,
        curves: list[str] | None = None,
        title: str | None = "XY Plot",
        xlabel: str | None = "position",
        ylabel: str | None = "",
        remote_process: bool | None = False,
    ):
        """Instantiate a matplotlib plotter.

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
        self.fig = None

    def plot(
        self, data: dict, grid=(1, 1), position=(0, 0), show=True, subplot_titles=[]
    ) -> None:
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
            if curve not in self._data:
                self._data[curve] = {}
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
            if not self.fig:
                self.fig = make_subplots(
                    rows=grid[0], cols=grid[1], subplot_titles=subplot_titles
                )
        for curve in self._curves:
            self.fig.add_trace(
                go.Scatter(
                    x=self._data[curve]["xvalues"],
                    y=self._data[curve]["yvalues"],
                    mode="lines",
                    name=curve,
                ),
                row=position[0] + 1,
                col=position[1] + 1,
            )
        self.fig.update_yaxes(
            title_text=self._ylabel,
            type=self._yscale if self._yscale else "linear",
            row=position[0] + 1,
            col=position[1] + 1,
        )
        self.fig.update_xaxes(
            title_text=self._xlabel, row=position[0] + 1, col=position[1] + 1
        )

        if show:
            if not self._visible:
                self._visible = True
                self.fig.show()

    def show(self):
        if not self._visible:
            self._visible = True
            self.fig.show()

    def close(self):
        """Close window."""
        del self.fig
        self._closed = True

    def is_closed(self):
        """Check if window is closed."""
        return self._closed

    def save_graphic(self, file_name: str):
        """Save graphics (static image (e.g., PNG, JPEG, PDF, SVG)).

        Please note:
            This requires the kaleido package.

            >>> pip install kaleido

        Parameters
        ----------
        file_name : str
            File name to save graphic.
        """
        self.fig.write_image(file_name)

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
        if not self.fig:
            return
