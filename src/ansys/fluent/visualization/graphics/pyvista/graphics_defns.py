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

"""Module for pyVista windows management."""
import numpy as np
import pyvista as pv

import ansys.fluent.visualization as pyviz

try:
    from pyvistaqt import BackgroundPlotter
except ModuleNotFoundError:
    BackgroundPlotter = None

from ansys.fluent.visualization.graphics.abstract_graphics_defns import AbstractRenderer


class Renderer(AbstractRenderer):
    def __init__(
        self,
        win_id: str,
        in_notebook: bool,
        non_interactive: bool,
        grid: tuple | None = (1, 1),
    ):
        self.plotter: BackgroundPlotter | pv.Plotter = (
            pv.Plotter(title=f"PyFluent ({win_id})", shape=grid)
            if in_notebook or non_interactive
            else BackgroundPlotter(
                title=f"PyFluent ({win_id})",
                shape=grid,
                show=False if pyviz.SINGLE_WINDOW else True,
            )
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

    def _init_properties(self):
        self.plotter.theme.cmap = "jet"
        self.plotter.background_color = "white"
        self.plotter.theme.font.color = "black"

    def _scalar_bar_default_properties(self) -> dict:
        return dict(
            title_font_size=20,
            label_font_size=16,
            shadow=True,
            fmt="%.6e",
            font_family="arial",
            vertical=True,
            position_x=0.06,
            position_y=0.3,
        )

    def _clear_plotter(self, in_notebook):
        if in_notebook and self.plotter.theme._jupyter_backend == "pythreejs":
            self.plotter.remove_actor(self.plotter.renderer.actors.copy())
        else:
            self.plotter.clear()

    def _set_camera(self, view: str):
        camera = self.plotter.camera.copy()
        view_fun = getattr(self.plotter, f"view_{view}", None)
        if view_fun:
            view_fun()
        else:
            self.plotter.camera = camera.copy()

    def write_frame(self):
        self.plotter.write_frame()

    def show(self):
        """Show graphics."""
        self.plotter.show()

    def render(self, mesh, **kwargs):
        """Render graphics in window.

        Parameters
        ----------
        mesh : pyvista.DataSet | dict
            Any PyVista or VTK mesh is supported.
        """
        if "position" in kwargs:
            self.plotter.subplot(kwargs["position"][0], kwargs["position"][1])
            del kwargs["position"]
        if isinstance(mesh, pv.DataSet):
            self.plotter.add_mesh(mesh, **kwargs)
        else:
            y_range = None
            chart = pv.Chart2D()
            chart.title = mesh["properties"].get("title") or ""
            chart.x_label = mesh["properties"].get("xlabel") or ""
            chart.y_label = mesh["properties"].get("ylabel") or ""
            if mesh["properties"].get("yscale") == "log":
                chart.y_axis.log_scale = True
                y_range = 0
            del mesh["properties"]

            color_list = ["b", "r", "g", "c", "m", "y", "k"]
            style_list = ["-", "--", "-.", "-.."]

            min_y_value = max_y_value = min_x_value = max_x_value = None
            for count, curve in enumerate(mesh):
                chart.line(
                    mesh[curve]["xvalues"].tolist(),
                    mesh[curve]["yvalues"].tolist(),
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
            self.plotter.add_chart(chart, **kwargs)

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

    def close(self):
        """Close graphics window."""
        self.plotter.close()
