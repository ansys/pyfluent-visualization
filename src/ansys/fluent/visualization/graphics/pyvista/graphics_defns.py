"""Module for pyVista windows management."""

import pyvista as pv
from pyvistaqt import BackgroundPlotter


class Renderer:
    def __init__(self, win_id: str, in_notebook: bool, non_interactive: bool):
        self.plotter: Union[BackgroundPlotter, pv.Plotter] = (
            pv.Plotter(title=f"PyFluent ({win_id})")
            if in_notebook or non_interactive
            else BackgroundPlotter(title=f"PyFluent ({win_id})")
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
            self.plotter.remove_actor(plotter.renderer.actors.copy())
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
        self.plotter.show()

    def render(self, mesh, **kwargs):
        self.plotter.add_mesh(mesh, **kwargs)

    def close(self):
        self.plotter.close()
