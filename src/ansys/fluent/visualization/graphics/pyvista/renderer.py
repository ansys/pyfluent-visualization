# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Module for pyVista windows management."""

import importlib.util
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, TypedDict, cast

import numpy as np
import numpy.typing as npt
import pyvista as pv
from typing_extensions import override

import ansys.fluent.visualization as pyviz
from ansys.fluent.visualization.base.renderer import AbstractRenderer, SubPlot

if TYPE_CHECKING:
    from ansys.fluent.visualization.config import View


if importlib.util.find_spec("pyvistaqt") is None and pyviz.config.interactive:
    raise ModuleNotFoundError(
        "Missing dependencies, use 'pip install ansys-fluent-visualization[interactive]' to install them.",
        name="pyvistaqt",
    )


class CurveData(TypedDict):
    """TypedDict for individual curve data in a 2D chart."""

    xvalues: npt.NDArray[np.floating[Any]]
    yvalues: npt.NDArray[np.floating[Any]]


class MeshProperties(TypedDict, total=False):
    """TypedDict for mesh properties."""

    title: str
    xlabel: str
    ylabel: str
    yscale: str


class MeshDict(TypedDict, total=False):
    """TypedDict for mesh dictionary containing chart data."""

    properties: MeshProperties
    kwargs: dict[str, Any]


class Renderer(AbstractRenderer):
    def __init__(
        self,
        win_id: str,
        in_jupyter: bool,
        non_interactive: bool,
        grid: tuple[int, int] | str = (1, 1),
    ):
        if in_jupyter or non_interactive:
            self.plotter = pv.Plotter(title=f"PyFluent ({win_id})", shape=grid)
        else:
            from pyvistaqt import (  # pyright: ignore[reportMissingTypeStubs]
                BackgroundPlotter,
            )

            self.plotter = BackgroundPlotter(
                title=f"PyFluent ({win_id})",
                shape=grid,
                show=False if pyviz.config.single_window else True,
            )
        self._init_properties()
        self._colors = {
            "red": [255, 0, 0],
            "lime": [0, 255, 0],
            "blue": [0, 0, 255],
            "yellow": [255, 255, 0],
            "cyan": [0, 255, 255],
            "magenta": [255, 0, 255],
            "silver": [192, 192, 192],
            "gray": [128, 128, 128],
            "maroon": [128, 0, 0],
            "olive": [128, 128, 0],
            "green": [0, 128, 0],
            "purple": [128, 0, 128],
            "teal": [0, 128, 128],
            "navy": [0, 0, 128],
            "orange": [255, 165, 0],
            "brown": [210, 105, 30],
            "white": [255, 255, 255],
        }

    def _init_properties(self) -> None:
        self.plotter.theme.cmap = "jet"
        self.plotter.background_color = "white"  # pyright: ignore[reportAttributeAccessIssue]  # types are inferred wrong
        self.plotter.theme.font.color = "black"

    def _scalar_bar_default_properties(self) -> Mapping[str, object]:
        return {
            "title_font_size": 20,
            "label_font_size": 16,
            "shadow": True,
            "fmt": "%.6e",
            "font_family": "arial",
            "vertical": True,
            "position_x": 0.06,
            "position_y": 0.3,
        }

    def _clear_plotter(self, in_jupyter: bool) -> None:
        if in_jupyter and self.plotter.theme._jupyter_backend == "pythreejs":
            assert isinstance(
                self.plotter, pv.Plotter
            )  # not sure why this isn't narrowing
            plotter = cast(pv.Plotter, self.plotter)
            plotter.remove_actor(plotter.renderer.actors.copy())  # pyright: ignore[reportArgumentType]  # remove_actor uses functools.wraps internally which isn't typed for methods
        else:
            self.plotter.clear()

    def _set_camera(self, view: View) -> None:
        assert isinstance(self.plotter, pv.Plotter)  # not sure why this isn't narrowing
        plotter = cast(pv.Plotter, self.plotter)
        camera = plotter.camera.copy()
        view_fun = getattr(plotter, f"view_{view}", None)
        if view_fun:
            view_fun()
        else:
            plotter.camera = camera.copy()

    def write_frame(self):
        self.plotter.write_frame()

    @override
    def show(self):
        """Show graphics."""
        self.plotter.show()

    @override
    def render(self, meshes: Sequence[SubPlot[pv.DataSet | Mapping[str, CurveData]]]):
        """Render graphics in window.

        Parameters
        ----------
        meshes : list[list[dict]]
            Data to plot. Data consists the list of x and y
            values for each curve.
        """
        self.plotter.clear()
        for mesh_sub_item in meshes:
            for mesh_dict in mesh_sub_item:
                mesh = mesh_dict["data"]
                position = mesh_dict.get("position")
                kwargs = mesh_dict.get("kwargs", {})

                if position:
                    self.plotter.subplot(position[0], position[1])

                if isinstance(mesh, pv.DataSet):
                    if mesh.n_points > 0:
                        self.plotter.add_mesh(mesh, **kwargs)  # pyright: ignore[reportAny]
                else:
                    y_range = None
                    chart = pv.Chart2D()
                    chart.title = mesh["properties"].get("title") or ""
                    chart.x_label = mesh["properties"].get("xlabel") or ""
                    chart.y_label = mesh["properties"].get("ylabel") or ""
                    if mesh["properties"].get("yscale") == "log":
                        chart.y_axis.log_scale = True
                        y_range = 0

                    color_list = ["b", "r", "g", "c", "m", "y", "k"]
                    style_list = ["-", "--", "-.", "-.."]

                    min_y_value = max_y_value = min_x_value = max_x_value = None
                    for count, curve in enumerate(mesh):
                        chart.line(
                            mesh[curve]["xvalues"],
                            mesh[curve]["yvalues"],
                            width=2.5,
                            color=color_list[count % len(color_list)],
                            style=style_list[count % len(style_list)],
                            label=curve,
                        )
                        min_y_value = (
                            min(np.amin(mesh[curve]["yvalues"]), min_y_value)
                            if min_y_value
                            else np.amin(mesh[curve]["yvalues"])
                        )
                        max_y_value = (
                            max(np.amax(mesh[curve]["yvalues"]), max_y_value)
                            if max_y_value
                            else np.amax(mesh[curve]["yvalues"])
                        )
                        min_x_value = (
                            min(np.amin(mesh[curve]["xvalues"]), min_x_value)
                            if min_x_value
                            else np.amin(mesh[curve]["xvalues"])
                        )
                        max_x_value = (
                            max(np.amax(mesh[curve]["xvalues"]), max_x_value)
                            if max_x_value
                            else np.amax(mesh[curve]["xvalues"])
                        )
                    if min_x_value and max_x_value:
                        chart.x_range = [min_x_value, max_x_value]
                    if min_y_value and max_y_value:
                        if y_range is None:
                            y_range = max_y_value - min_y_value
                        chart.y_range = [
                            min_y_value - y_range * 0.2,
                            max_y_value + y_range * 0.2,
                        ]

                    chart.title = mesh_dict["title"]
                    self.plotter.add_chart(  # add_chart uses functools.wraps internally which isn't typed for methods
                        chart,
                        **kwargs,  # pyright: ignore[reportArgumentType]
                    )

    @override
    def save_graphic(self, file_name: str):
        """Save graphics to the specified file.

        Parameters
        ----------
        file_name : str
            File name to save graphic.
        """
        self.plotter.save_graphic(file_name)

    def get_animation(self, win_id: str):
        """Animate windows.

        Parameters
        ----------
        win_id : str
            ID for the window to animate.
        """
        self.plotter.open_gif(f"{win_id}.gif")

    @override
    def close(self):
        """Close graphics window."""
        self.plotter.close()
