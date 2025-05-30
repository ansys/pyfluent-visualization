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

"""Module for graphics windows management."""

from enum import Enum
import itertools
import threading
from typing import Dict, List, Optional, Union

import numpy as np
import pyvista as pv

from ansys.fluent.interface.post_objects.check_in_notebook import in_jupyter
from ansys.fluent.interface.post_objects.post_object_definitions import (
    GraphicsDefn,
    PlotDefn,
)
from ansys.fluent.interface.post_objects.singleton_meta import AbstractSingletonMeta

try:
    from pyvistaqt import BackgroundPlotter
except ModuleNotFoundError:
    BackgroundPlotter = None

import ansys.fluent.visualization as pyviz
from ansys.fluent.visualization.post_data_extractor import (
    FieldDataExtractor,
    XYPlotDataExtractor,
)
from ansys.fluent.visualization.visualization_windows_manager import (
    VisualizationWindow,
    VisualizationWindowsManager,
)


class FieldDataType(Enum):
    """Provides surface data types."""

    Meshes = "Mesh"
    Vectors = "Vector"
    Contours = "Contour"
    Pathlines = "Pathlines"


class GraphicsWindow(VisualizationWindow):
    """Provides for managing Graphics windows."""

    def __init__(
        self,
        id: str,
        post_object: GraphicsDefn,
        grid: tuple | None = (1, 1),
        renderer: str = None,
    ):
        """Instantiate a Graphics window.

        Parameters
        ----------
        id : str
            Window ID.
        post_object : GraphicsDefn
            Object to draw.
        grid: tuple, optional
            Layout or arrangement of the graphics window. The default is ``(1, 1)``.
        """
        self.post_object: GraphicsDefn = post_object
        self.id: str = id
        self._grid = grid
        self.renderer = self._get_renderer(renderer_string=renderer)
        self.overlay: bool = False
        self.fetch_data: bool = False
        self.show_window: bool = True
        self.animate: bool = False
        self.close: bool = False
        self.refresh: bool = False
        self.update: bool = False
        self._visible: bool = False
        self._data = {}
        self._subplot = None
        self._opacity = None

    # private methods
    def _get_renderer(self, renderer_string=None):
        from ansys.fluent.visualization.registrar import _renderer, get_renderer

        if renderer_string is None:
            renderer_string = pyviz.config.three_dimensional_renderer
        try:
            if renderer_string == "pyvista":
                from ansys.fluent.visualization.graphics.pyvista.graphics_defns import (
                    Renderer,
                )

                renderer = Renderer
            else:
                renderer = get_renderer(renderer_string)
        except KeyError as ex:
            error_message = (
                f"Error: Renderer '{renderer_string}' not found or registered. "
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
        return renderer(self.id, in_jupyter(), not pyviz.config.interactive, self._grid)

    def set_data(self, data_type: FieldDataType, data: Dict[int, Dict[str, np.array]]):
        """Set data for graphics."""
        self._data[data_type] = data

    def fetch(self):
        """Fetch data for graphics."""
        if not self.post_object:
            return
        obj = self.post_object
        if obj.__class__.__name__ == "Surface":
            self._fetch_surface(obj)
        elif obj.__class__.__name__ == "XYPlot":
            self._fetch_xy_data(obj)
        elif obj.__class__.__name__ == "MonitorPlot":
            self._fetch_monitor_data(obj)
        else:
            self._fetch_data(obj, FieldDataType(obj.__class__.__name__))

    def render(self):
        """Render graphics."""
        self._render_graphics()
        if not self._visible and self.show_window:
            self.renderer.show()
            self._visible = True

    def _render_graphics(self, position=(0, 0), opacity=1):
        """Render graphics."""
        if not self.post_object:
            return
        obj = self.post_object
        if self._subplot:
            position = self._subplot
        if self._opacity:
            opacity = self._opacity

        if not self.overlay:
            self.renderer._clear_plotter(in_jupyter())
        if obj.__class__.__name__ == "Mesh":
            self._display_mesh(obj, position, opacity)
        elif obj.__class__.__name__ == "Surface":
            self._display_surface(obj, position, opacity)
        elif obj.__class__.__name__ == "Contour":
            self._display_contour(obj, position, opacity)
        elif obj.__class__.__name__ == "Vector":
            self._display_vector(obj, position, opacity)
        elif obj.__class__.__name__ == "Pathlines":
            self._display_pathlines(obj, position, opacity)
        elif obj.__class__.__name__ == "XYPlot":
            self._display_xy_plot(position, opacity)
        elif obj.__class__.__name__ == "MonitorPlot":
            self._display_monitor_plot(position, opacity)
        if self.animate:
            self.renderer.write_frame()
        self.renderer._set_camera(pyviz.config.view)

    def add_graphics(self, position, opacity=1):
        """Fetch and render graphics."""
        self.fetch()
        self._render_graphics(position, opacity)

    def show_graphics(self):
        """Display graphics."""
        if not self._visible and self.show_window:
            self.renderer.show()
            self._visible = True

    def plot(self):
        """Display graphics."""
        self.fetch()
        self.render()

    # private methods
    def _fetch_data(self, obj, data_type: FieldDataType):
        if self._data.get(data_type) is None or self.fetch_data:
            self._data[data_type] = FieldDataExtractor(obj).fetch_data()

    def _fetch_or_display_surface(self, obj, fetch: bool, position=[0, 0], opacity=1):
        dummy_object = "dummy_object"
        post_session = obj.get_root()
        if (
            obj.definition.type() == "iso-surface"
            and obj.definition.iso_surface.rendering() == "contour"
        ):
            contour = post_session.Contours[dummy_object]
            contour.field = obj.definition.iso_surface.field()
            contour.surfaces = [obj._name]
            contour.show_edges = obj.show_edges()
            contour.range.auto_range_on.global_range = True
            contour.boundary_values = True
            if fetch:
                self._fetch_data(contour, FieldDataType.Contours)
            else:
                self._display_contour(contour, position=position, opacity=opacity)
            del post_session.Contours[dummy_object]
        else:
            mesh = post_session.Meshes[dummy_object]
            mesh.surfaces = [obj._name]
            mesh.show_edges = obj.show_edges()
            if fetch:
                self._fetch_data(mesh, FieldDataType.Meshes)
            else:
                self._display_mesh(mesh, position=position, opacity=opacity)
            del post_session.Meshes[dummy_object]

    def _fetch_surface(self, obj):
        self._fetch_or_display_surface(obj, fetch=True)

    def _fetch_xy_data(self, obj):
        self._data["XYPlot"] = XYPlotDataExtractor(obj).fetch_data()
        self._data["XYPlot"]["properties"] = {
            "curves": list(self._data["XYPlot"]),
            "title": "XY Plot",
            "xlabel": "position",
            "ylabel": obj.y_axis_function(),
        }

    def _fetch_monitor_data(self, obj):
        monitors = obj.session.monitors
        indices, columns_data = monitors.get_monitor_set_data(obj.monitor_set_name())
        xy_data = {}
        for column_name, column_data in columns_data.items():
            xy_data[column_name] = {"xvalues": indices, "yvalues": column_data}
        monitor_set_name = obj.monitor_set_name()
        self._data["MonitorPlot"] = xy_data
        self._data["MonitorPlot"]["properties"] = {
            "curves": list(xy_data.keys()),
            "title": monitor_set_name,
            "xlabel": monitors.get_monitor_set_prop(monitor_set_name, "xlabel"),
            "ylabel": monitors.get_monitor_set_prop(monitor_set_name, "ylabel"),
            "yscale": "log" if monitor_set_name == "residual" else "linear",
        }

    @staticmethod
    def _pack_faces_connectivity_data(faces_data):
        flat = []
        for face in faces_data:
            flat.append(len(face))
            flat.extend(face)
        return np.array(flat)

    def _resolve_mesh_data(self, mesh_data):
        if mesh_data.connectivity[0].shape[0] == 2:  # Line
            return pv.PolyData(
                mesh_data.vertices,
                lines=self._pack_faces_connectivity_data(mesh_data.connectivity),
            )
        else:  # Face
            return pv.PolyData(
                mesh_data.vertices,
                faces=self._pack_faces_connectivity_data(mesh_data.connectivity),
            )

    def _display_vector(self, obj, position=(0, 0), opacity=1):
        field_info = obj.session.field_info
        vectors_of = obj.vectors_of()
        # scalar bar properties
        scalar_bar_args = self.renderer._scalar_bar_default_properties()

        field = obj.field()
        field_unit = obj._api_helper.get_field_unit(field)
        field = f"{field}\n[{field_unit}]" if field_unit else field

        for surface_id, mesh_data in self._data[FieldDataType.Vectors].items():
            if not all(
                hasattr(mesh_data, attr) for attr in ("vertices", "connectivity")
            ):
                continue
            mesh_data.vertices.shape = mesh_data.vertices.size // 3, 3
            getattr(mesh_data, vectors_of).shape = (
                getattr(mesh_data, vectors_of).size // 3,
                3,
            )
            vector_scale = mesh_data.vector_scale[0]
            mesh = self._resolve_mesh_data(mesh_data)
            mesh.cell_data["vectors"] = getattr(mesh_data, vectors_of)
            scalar_field = getattr(mesh_data, obj.field())
            velocity_magnitude = np.linalg.norm(getattr(mesh_data, vectors_of), axis=1)
            if obj.range.option() == "auto-range-off":
                auto_range_off = obj.range.auto_range_off
                range_ = [auto_range_off.minimum(), auto_range_off.maximum()]
                if auto_range_off.clip_to_range():
                    velocity_magnitude = np.ma.masked_outside(
                        velocity_magnitude,
                        auto_range_off.minimum(),
                        auto_range_off.maximum(),
                    ).filled(fill_value=0)
            else:
                auto_range_on = obj.range.auto_range_on
                if auto_range_on.global_range():
                    range_ = field_info.get_scalar_field_range(obj.field(), False)
                else:
                    range_ = [np.min(scalar_field), np.max(scalar_field)]

            if obj.skip():
                vmag = np.zeros(velocity_magnitude.size)
                vmag[:: obj.skip() + 1] = velocity_magnitude[:: obj.skip() + 1]
                velocity_magnitude = vmag
            mesh.cell_data["Velocity Magnitude"] = velocity_magnitude
            mesh.cell_data[field] = scalar_field
            glyphs = mesh.glyph(
                orient="vectors",
                scale="Velocity Magnitude",
                factor=vector_scale * obj.scale(),
                geom=pv.Arrow(),
            )
            self.renderer.render(
                glyphs,
                scalars=field,
                scalar_bar_args=scalar_bar_args,
                clim=range_,
                position=position,
                opacity=opacity,
            )
            if obj.show_edges():
                self.renderer.render(
                    mesh,
                    show_edges=True,
                    color="white",
                    position=position,
                    opacity=opacity,
                )

    def _display_pathlines(self, obj, position=(0, 0), opacity=1):
        field = obj.field()
        field_unit = obj._api_helper.get_field_unit(field)
        field = f"{field}\n[{field_unit}]" if field_unit else field

        # scalar bar properties
        scalar_bar_args = self.renderer._scalar_bar_default_properties()

        # loop over all meshes
        for surface_id, surface_data in self._data[FieldDataType.Pathlines].items():
            if not all(hasattr(surface_data, attr) for attr in ("vertices", "lines")):
                continue
            surface_data.vertices.shape = surface_data.vertices.size // 3, 3

            mesh = pv.PolyData(
                surface_data.vertices,
                lines=self._pack_faces_connectivity_data(surface_data.lines),
            )

            mesh.point_data[field] = surface_data.scalar_field
            self.renderer.render(
                mesh,
                scalars=field,
                scalar_bar_args=scalar_bar_args,
                position=position,
                opacity=opacity,
            )

    def _display_contour(self, obj, position=(0, 0), opacity=1):
        # contour properties
        field = obj.field()
        field_unit = obj._api_helper.get_field_unit(field)
        field = f"{field}\n[{field_unit}]" if field_unit else field
        range_option = obj.range.option()
        filled = obj.filled()
        contour_lines = obj.contour_lines()
        node_values = obj.node_values()

        # scalar bar properties
        scalar_bar_args = self.renderer._scalar_bar_default_properties()

        # loop over all meshes
        for surface_id, surface_data in self._data[FieldDataType.Contours].items():
            if not all(
                hasattr(surface_data, attr) for attr in ("vertices", "connectivity")
            ):
                continue
            surface_data.vertices.shape = surface_data.vertices.size // 3, 3
            mesh = self._resolve_mesh_data(surface_data)
            if node_values:
                mesh.point_data[field] = getattr(surface_data, obj.field())
            else:
                mesh.cell_data[field] = getattr(surface_data, obj.field())
            if range_option == "auto-range-off":
                auto_range_off = obj.range.auto_range_off
                if auto_range_off.clip_to_range():
                    if np.min(mesh[field]) < auto_range_off.maximum():
                        maximum_below = mesh.clip_scalar(
                            scalars=field,
                            value=auto_range_off.maximum(),
                        )
                        if np.max(maximum_below[field]) > auto_range_off.minimum():
                            minimum_above = maximum_below.clip_scalar(
                                scalars=field,
                                invert=False,
                                value=auto_range_off.minimum(),
                            )
                            if filled:
                                self.renderer.render(
                                    minimum_above,
                                    scalars=field,
                                    show_edges=obj.show_edges(),
                                    scalar_bar_args=scalar_bar_args,
                                    position=position,
                                    opacity=opacity,
                                )

                            if (not filled or contour_lines) and (
                                np.min(minimum_above[field])
                                != np.max(minimum_above[field])
                            ):
                                self.renderer.render(
                                    minimum_above.contour(isosurfaces=20),
                                    position=position,
                                    opacity=opacity,
                                )
                else:
                    if filled:
                        self.renderer.render(
                            mesh,
                            clim=[
                                auto_range_off.minimum(),
                                auto_range_off.maximum(),
                            ],
                            scalars=field,
                            show_edges=obj.show_edges(),
                            scalar_bar_args=scalar_bar_args,
                            position=position,
                            opacity=opacity,
                        )
                    if (not filled or contour_lines) and (
                        np.min(mesh[field]) != np.max(mesh[field])
                    ):
                        self.renderer.render(
                            mesh.contour(isosurfaces=20),
                            position=position,
                            opacity=opacity,
                        )
            else:
                auto_range_on = obj.range.auto_range_on
                if auto_range_on.global_range():
                    if filled:
                        field_info = obj.session.field_info
                        self.renderer.render(
                            mesh,
                            clim=field_info.get_scalar_field_range(obj.field(), False),
                            scalars=field,
                            show_edges=obj.show_edges(),
                            scalar_bar_args=scalar_bar_args,
                            position=position,
                            opacity=opacity,
                        )
                    if (not filled or contour_lines) and (
                        np.min(mesh[field]) != np.max(mesh[field])
                    ):
                        self.renderer.render(
                            mesh.contour(isosurfaces=20),
                            position=position,
                            opacity=opacity,
                        )

                else:
                    if filled:
                        self.renderer.render(
                            mesh,
                            scalars=field,
                            show_edges=obj.show_edges(),
                            scalar_bar_args=scalar_bar_args,
                            position=position,
                            opacity=opacity,
                        )
                    if (not filled or contour_lines) and (
                        np.min(mesh[field]) != np.max(mesh[field])
                    ):
                        self.renderer.render(
                            mesh.contour(isosurfaces=20),
                            position=position,
                            opacity=opacity,
                        )

    def _display_surface(self, obj, position=(0, 0), opacity=1):
        self._fetch_or_display_surface(
            obj, fetch=False, position=position, opacity=opacity
        )

    def _display_mesh(self, obj, position=(0, 0), opacity=1):
        for surface_id, mesh_data in self._data[FieldDataType.Meshes].items():
            if not all(
                hasattr(mesh_data, attr) for attr in ("vertices", "connectivity")
            ):
                continue
            mesh_data.vertices.shape = mesh_data.vertices.size // 3, 3
            mesh = self._resolve_mesh_data(mesh_data)
            color_size = len(self.renderer._colors)
            color = list(self.renderer._colors.values())[surface_id % color_size]
            self.renderer.render(
                mesh,
                show_edges=obj.show_edges(),
                color=color,
                position=position,
                opacity=opacity,
            )

    def _display_xy_plot(self, position=(0, 0), opacity=1):
        self.renderer.render(
            self._data["XYPlot"],
            position=position,
        )

    def _display_monitor_plot(self, position=(0, 0), opacity=1):
        self.renderer.render(
            self._data["MonitorPlot"],
            position=position,
        )

    def _get_refresh_for_plotter(self, window: "GraphicsWindow"):
        def refresh():
            with GraphicsWindowsManager._condition:
                plotter = window.renderer
                if window.close:
                    window.animate = False
                    plotter.close()
                    return
                if not window.update:
                    return
                window.update = False
                try:
                    window.plot()
                finally:
                    GraphicsWindowsManager._condition.notify()

        return refresh


class GraphicsWindowsManager(metaclass=AbstractSingletonMeta):
    """Provides for managing Graphics windows."""

    _condition = threading.Condition()

    def __init__(self):
        """Instantiate ``GraphicsWindow`` for Graphics."""
        self._post_windows: Dict[str:GraphicsWindow] = {}
        self._plotter_thread: threading.Thread = None
        self._post_object: GraphicsDefn = None
        self._window_id: Optional[str] = None
        self._exit_thread: bool = False
        self._app = None

    def get_window(self, window_id: str) -> GraphicsWindow:
        """Get the Graphics window.

        Parameters
        ----------
        window_id : str
            Window ID.

        Returns
        -------
        GraphicsWindow
            Graphics window.
        """
        with self._condition:
            return self._post_windows.get(window_id, None)

    def get_plotter(self, window_id: str) -> Union[BackgroundPlotter, pv.Plotter]:
        """Get the PyVista plotter.

        Parameters
        ----------
        window_id : str
            Window ID for the plotter.

        Returns
        -------
        Union[BackgroundPlotter, pv.Plotter]
            PyVista plotter.
        """
        with self._condition:
            return self._post_windows[window_id].renderer.plotter

    def set_object_for_window(self, object: GraphicsDefn, window_id: str) -> None:
        """Associate a visualization object with a running window instance.

        Parameters
        ----------
        object : GraphicsDefn
            Post object to associate with a running window instance.
        window_id : str
            Window ID for the association.

        Raises
        ------
        RuntimeError
            If the window does not support the object.
        """
        if not isinstance(object, GraphicsDefn):
            raise RuntimeError("Object type currently not supported.")
        with self._condition:
            window = self._post_windows.get(window_id)
            if window:
                window.post_object = object

    @staticmethod
    def _safety_check_for_plot(graphics_object):
        if not isinstance(graphics_object, (GraphicsDefn, PlotDefn)):
            raise RuntimeError("Object type currently not supported.")

    def save_graphic(
        self,
        window_id: str,
        format: str,
    ) -> None:
        """Save a graphics.

        Parameters
        ----------
        window_id : str
            Window ID for the graphics to save.
        format : str
            Graphic file format. Supported formats are SVG, EPS, PS, PDF, and TEX.

        Raises
        ------
        ValueError
            If the window does not support the specified format.
        """
        with self._condition:
            window = self._post_windows.get(window_id)
            if window:
                window.renderer.save_graphic(f"{window_id}.{format}")

    def refresh_windows(
        self,
        session_id: Optional[str] = "",
        windows_id=None,
        overlay: Optional[bool] = False,
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
        overlay : bool, Optional
            Overlay graphics over existing graphics.
        """
        if windows_id is None:
            windows_id = []
        with self._condition:
            windows_id = self._get_windows_id(session_id, windows_id)
            for window_id in windows_id:
                window = self._post_windows.get(window_id)
                if window:
                    window.refresh = True
                    self.plot(window.post_object, window.id, overlay=overlay)

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
        with self._condition:
            windows_id = self._get_windows_id(session_id, windows_id)
            for window_id in windows_id:
                window = self._post_windows.get(window_id)
                if window:
                    window.animate = True
                    window.renderer.get_animation(window.id)

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
        with self._condition:
            windows_id = self._get_windows_id(session_id, windows_id)
            for window_id in windows_id:
                window = self._post_windows.get(window_id)
                if window:
                    if in_jupyter() or not pyviz.config.interactive:
                        window.renderer.plotter.close()
                    window.close = True

    # private methods

    def _get_windows_id(
        self,
        session_id: Optional[str] = "",
        windows_id=None,
    ) -> List[str]:
        if windows_id is None:
            windows_id = []
        with self._condition:
            return [
                window_id
                for window_id in [
                    window_id
                    for window_id, window in self._post_windows.items()
                    if window
                    and not window.renderer.plotter._closed
                    and (not session_id or session_id == window.post_object.session.id)
                ]
                if not windows_id or window_id in windows_id
            ]

    def _exit(self) -> None:
        if self._plotter_thread:
            with self._condition:
                self._exit_thread = True
                self._condition.wait()
            self._plotter_thread.join()
            self._plotter_thread = None

    def _get_unique_window_id(self) -> str:
        itr_count = itertools.count()
        with self._condition:
            while True:
                window_id = f"window-{next(itr_count) + 1}"
                if window_id not in self._post_windows:
                    return window_id


class NonInteractiveGraphicsManager(
    GraphicsWindowsManager, VisualizationWindowsManager
):

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
        with self._condition:
            window_id = self._get_unique_window_id() if window_id is None else window_id
            self._open_window_notebook(window_id, grid, renderer=renderer)
            return window_id

    def plot(
        self,
        graphics_object: GraphicsDefn,
        window_id: Optional[str] = None,
        fetch_data: Optional[bool] = False,
        overlay: Optional[bool] = False,
    ) -> None:
        """Draw a plot.

        Parameters
        ----------
        graphics_object: GraphicsDefn
            Object to plot.
        window_id : str, optional
            Window ID for the plot. The default is ``None``, in which
            case a unique ID is assigned.
        fetch_data : bool, optional
            Whether to fetch data. The default is ``False``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        Raises
        ------
        RuntimeError
            If the window does not support the object.
        """
        self._safety_check_for_plot(graphics_object)
        with self._condition:
            window_id = self._get_unique_window_id() if window_id is None else window_id
            self._plot_notebook(graphics_object, window_id, fetch_data, overlay)

    def add_graphics(
        self,
        graphics_object: GraphicsDefn,
        window_id: str = None,
        fetch_data: bool | None = False,
        overlay: bool | None = False,
        position: tuple | None = (0, 0),
        opacity: float | None = 1,
    ) -> None:
        """Add graphics object to a window.

        Parameters
        ----------
        graphics_object: GraphicsDefn
            Object to plot.
        window_id : str
            Window ID for the plot.
        fetch_data : bool, optional
            Whether to fetch data. The default is ``False``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        position: tuple, optional
            Position of the sub-plot.
        opacity: float, optional
            Transparency of the sub-plot.
        Raises
        ------
        RuntimeError
            If the window does not support the object.
        """
        self._safety_check_for_plot(graphics_object)
        with self._condition:
            self._add_graphics_in_notebook(
                graphics_object, window_id, fetch_data, overlay, position, opacity
            )

    def show_graphics(self, window_id: str):
        """Display the graphics window."""
        with self._condition:
            self._show_graphics_in_notebook(window_id)

    def _open_window_notebook(
        self,
        window_id: str,
        grid: tuple | None = (1, 1),
        renderer=None,
    ) -> pv.Plotter:
        window = self._post_windows.get(window_id)
        if window and not window.close and window.refresh:
            window.refresh = False
        else:
            window = GraphicsWindow(window_id, None, grid, renderer=renderer)
            self._post_windows[window_id] = window
        return window

    def _plot_notebook(
        self, obj: object, window_id: str, fetch_data: bool, overlay: bool
    ) -> None:
        window = self._open_window_notebook(window_id)
        window.post_object = obj
        window.fetch_data = fetch_data
        window.overlay = overlay
        window.plot()

    def _add_graphics_in_notebook(
        self,
        obj: object,
        window_id: str,
        fetch_data: bool,
        overlay: bool,
        position=(0, 0),
        opacity=1.0,
    ) -> None:
        window = self._post_windows.get(window_id)
        window.post_object = obj
        window.fetch_data = fetch_data
        window.overlay = overlay
        window.add_graphics(position, opacity)

    def _show_graphics_in_notebook(self, window_id: str):
        self._post_windows[window_id].show_graphics()


class InteractiveGraphicsManager(GraphicsWindowsManager, VisualizationWindowsManager):

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
        with self._condition:
            window_id = self._get_unique_window_id() if window_id is None else window_id
            self._open_and_plot_console(None, window_id, grid=grid)
            return window_id

    def plot(
        self,
        graphics_object: GraphicsDefn,
        window_id: Optional[str] = None,
        fetch_data: Optional[bool] = False,
        overlay: Optional[bool] = False,
    ) -> None:
        """Draw a plot.

        Parameters
        ----------
        graphics_object: GraphicsDefn
            Object to plot.
        window_id : str, optional
            Window ID for the plot. The default is ``None``, in which
            case a unique ID is assigned.
        fetch_data : bool, optional
            Whether to fetch data. The default is ``False``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        Raises
        ------
        RuntimeError
            If the window does not support the object.
        """
        self._safety_check_for_plot(graphics_object)
        with self._condition:
            window_id = self._get_unique_window_id() if window_id is None else window_id
            self._open_and_plot_console(graphics_object, window_id, fetch_data, overlay)

    def add_graphics(
        self,
        graphics_object: GraphicsDefn,
        window_id: str = None,
        fetch_data: bool | None = False,
        overlay: bool | None = False,
        position: tuple | None = (0, 0),
        opacity: float | None = 1,
    ) -> None:
        """Add graphics object to a window.

        Parameters
        ----------
        graphics_object: GraphicsDefn
            Object to plot.
        window_id : str
            Window ID for the plot.
        fetch_data : bool, optional
            Whether to fetch data. The default is ``False``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        position: tuple, optional
            Position of the sub-plot.
        opacity: float, optional
            Transparency of the sub-plot.
        Raises
        ------
        RuntimeError
            If the window does not support the object.
        """
        self._safety_check_for_plot(graphics_object)
        with self._condition:
            self._open_and_plot_console(
                graphics_object, window_id, fetch_data, overlay, position, opacity
            )

    def show_graphics(self, window_id: str):
        """Display the graphics window."""
        pass

    def _display(self, grid=(1, 1)) -> None:
        while True:
            with self._condition:
                if self._exit_thread:
                    break
                if self._window_id:
                    window = self._post_windows.get(self._window_id)
                    plotter = window.renderer.plotter if window else None
                    animate = window.animate if window else False
                    if not plotter or plotter._closed:
                        window = GraphicsWindow(
                            self._window_id, self._post_object, grid=self._grid
                        )
                        plotter = window.renderer.plotter
                        self._app = plotter.app
                        plotter.add_callback(
                            window._get_refresh_for_plotter(window),
                            100,
                        )
                    window.post_object = self._post_object
                    window._subplot = self._subplot
                    window._opacity = self._opacity
                    window.fetch_data = self._fetch_data
                    window.overlay = self._overlay
                    window.animate = animate
                    window.update = True
                    self._post_windows[self._window_id] = window
                    self._post_object = None
                    self._window_id = None
            self._app.processEvents()
        with self._condition:
            for window in self._post_windows.values():
                if window:
                    plotter = window.renderer.plotter
                    plotter.close()
                    plotter.app.quit()
            self._post_windows.clear()
            self._condition.notify()

    def _open_and_plot_console(
        self,
        obj: object,
        window_id: str,
        fetch_data: bool = False,
        overlay: bool = False,
        position=(0, 0),
        opacity=1.0,
        grid=(1, 1),
    ) -> None:
        if self._exit_thread:
            return
        with self._condition:
            self._window_id = window_id
            self._post_object = obj
            self._fetch_data = fetch_data
            self._overlay = overlay
            self._subplot = position
            self._opacity = opacity
            self._grid = grid

        if not self._plotter_thread:
            if obj is not None:
                obj.session._fluent_connection.register_finalizer_cb(self._exit)
            self._plotter_thread = threading.Thread(target=self._display, args=())
            self._plotter_thread.start()

        with self._condition:
            self._condition.wait()


class _GraphicsManagerProxy:
    def __init__(self):
        self._real_instance = None

    def _initialize(self):
        if in_jupyter() or not pyviz.config.interactive or pyviz.config.single_window:
            self._real_instance = NonInteractiveGraphicsManager()
        else:
            self._real_instance = InteractiveGraphicsManager()

    def __getattr__(self, name):
        if self._real_instance is None:
            self._initialize()
        return getattr(self._real_instance, name)

    def __setattr__(self, name, value):
        if name == "_real_instance":
            super().__setattr__(name, value)
        else:
            if self._real_instance is None:
                self._initialize()
            setattr(self._real_instance, name, value)


graphics_windows_manager = _GraphicsManagerProxy()
