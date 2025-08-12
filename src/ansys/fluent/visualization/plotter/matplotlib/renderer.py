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

"""Module providing matplotlib plotter functionality."""

from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np

from ansys.fluent.visualization.base.renderer import AbstractRenderer


class Plotter(AbstractRenderer):
    """Class for matplotlib plotter."""

    def __init__(
        self,
        window_id: str,
        curves: List[str] | None = None,
        title: str | None = "XY Plot",
        xlabel: str | None = "position",
        ylabel: str | None = "",
        remote_process: Optional[bool] = False,
        grid: tuple | None = (1, 1),
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
        self._grid = grid

    @staticmethod
    def _compute_position(position: tuple) -> int:
        x = position[0]
        y = position[1]
        if x == y == 0:
            ret = 0
        elif x < y:
            ret = x + y
        else:
            ret = x + y + 1
        return ret

    def render(self, meshes: list[list[dict]]) -> None:
        """Draw plot in window.

        Parameters
        ----------
        meshes : list[list[dict]]
            Data to plot. Data consists the list of x and y
            values for each curve.
        """
        for data_sub_item in meshes:
            for data_dict in data_sub_item:
                if not self._remote_process:
                    self.fig = plt.figure(num=self._window_id)
                if "properties" in data_dict:
                    self.set_properties(data_dict.pop("properties"))
                data = data_dict.pop("data")
                try:
                    for curve in data:
                        min_y_value = np.amin(data[curve]["yvalues"])
                        max_y_value = np.amax(data[curve]["yvalues"])
                        min_x_value = np.amin(data[curve]["xvalues"])
                        max_x_value = np.amax(data[curve]["xvalues"])
                        self._data[curve]["xvalues"] = data[curve]["xvalues"].tolist()
                        self._data[curve]["yvalues"] = data[curve]["yvalues"].tolist()
                        self._min_y = (
                            min(self._min_y, min_y_value)
                            if self._min_y
                            else min_y_value
                        )
                        self._max_y = (
                            max(self._max_y, max_y_value)
                            if self._max_y
                            else max_y_value
                        )
                        self._min_x = (
                            min(self._min_x, min_x_value)
                            if self._min_x
                            else min_x_value
                        )
                        self._max_x = (
                            max(self._max_x, max_x_value)
                            if self._max_x
                            else max_x_value
                        )

                    self.ax = self.fig.add_subplot(
                        self._grid[0],
                        self._grid[1],
                        self._compute_position(data_dict["position"]) + 1,
                    )
                    if self._yscale:
                        self.ax.set_yscale(self._yscale)
                    self.fig.canvas.manager.set_window_title(
                        "PyFluent [" + self._window_id + "]"
                    )
                    plt.title(self._title)
                    plt.xlabel(self._xlabel)
                    plt.ylabel(self._ylabel)
                    if self._curves:
                        for curve in self._curves:
                            self.ax.plot(
                                self._data[curve]["xvalues"],
                                self._data[curve]["yvalues"],
                            )
                        plt.legend(labels=self._curves, loc="upper right")

                    if self._max_x and self._min_x:
                        if self._max_x > self._min_x:
                            self.ax.set_xlim(self._min_x, self._max_x)
                    if self._max_y and self._min_y:
                        y_range = self._max_y - self._min_y
                        if self._yscale == "log":
                            y_range = 0
                        self.ax.set_ylim(
                            self._min_y - y_range * 0.2, self._max_y + y_range * 0.2
                        )
                except KeyError:
                    pass

    def show(self):
        if not self._visible:
            self._visible = True
            plt.show()

    def close(self):
        """Close window."""
        plt.close(self.fig)
        self._closed = True

    def is_closed(self):
        """Check if window is closed."""
        return self._closed

    def save_graphic(self, file_name: str):
        """Save graphics.

        Parameters
        ----------
        file_name : str
            File name to save graphic.
        """
        if self.fig:
            self.fig.savefig(file_name)
        else:
            plt.savefig(file_name)

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
        plt.figure(self.fig.number)
        for curve_name in self._curves:
            try:
                self.ax.plot([], [], label=curve_name)
            except AttributeError:
                pass


class ProcessPlotter(Plotter):
    """Class for matplotlib process plotter.

    Opens matplotlib window in a separate process.
    """

    def __init__(
        self,
        window_id,
        curves_name: List[str] | None = None,
        title: str | None = "XY Plot",
        xlabel: str | None = "position",
        ylabel: str | None = "",
        grid: tuple | None = (1, 1),
    ):
        """Instantiate a matplotlib process plotter.

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
        """
        super().__init__(window_id, curves_name, title, xlabel, ylabel, True, grid=grid)
        if curves_name is None:
            curves_name = []

    def _call_back(self):
        try:
            while self.pipe.poll():
                data = self.pipe.recv()
                if data is None:
                    self.close()
                    return False
                elif data and isinstance(data, dict):
                    if "properties" in data:
                        properties = data["properties"]
                        self.set_properties(properties)
                    elif "save_graphic" in data:
                        name = data["save_graphic"]
                        self.save_graphic(name)
                    else:
                        self.render(meshes=data["data"])
            self.fig.canvas.draw()
        except BrokenPipeError:
            self.close()
        return True

    def __call__(self, pipe):
        """Reset and show plot."""
        self.pipe = pipe
        self.fig = plt.figure(num=self._window_id)
        self.ax = self.fig.add_subplot(111)
        self._reset()
        timer = self.fig.canvas.new_timer(interval=10)
        timer.add_callback(self._call_back)
        timer.start()
        self._visible = True
        plt.show()
