"""Module for pyVista windows management."""

from enum import Enum
import itertools
import threading
from typing import Dict, List, Optional, Union

from ansys.fluent.core.fluent_connection import FluentConnection
from ansys.fluent.core.post_objects.check_in_notebook import in_notebook
from ansys.fluent.core.post_objects.post_object_definitions import GraphicsDefn
from ansys.fluent.core.post_objects.singleton_meta import AbstractSingletonMeta
import numpy as np
import pyvista as pv
from pyvistaqt import BackgroundPlotter

from ansys.fluent.visualization import get_config
from ansys.fluent.visualization.post_data_extractor import FieldDataExtractor
from ansys.fluent.visualization.post_windows_manager import (
    PostWindow,
    PostWindowsManager,
)


class FieldDataType(Enum):
    """Provides surface data types."""

    Meshes = 1
    Vectors = 2
    Contours = 3
    Pathlines = 4


class PyVistaWindow(PostWindow):
    """Provides for managing PyVista windows."""

    def __init__(self, id: str, post_object: GraphicsDefn):
        """Instantiate a PyVista window.

        Parameters
        ----------
        id : str
            Window ID.
        post_object : GraphicsDefn
            Object to draw.
        """
        self.post_object: GraphicsDefn = post_object
        self.id: str = id
        self.plotter: Union[BackgroundPlotter, pv.Plotter] = (
            pv.Plotter(title=f"PyFluent ({self.id})")
            if in_notebook() or get_config()["blocking"]
            else BackgroundPlotter(title=f"PyFluent ({self.id})")
        )
        self.overlay: bool = False
        self.fetch_data: bool = False
        self.show_window: bool = True
        self.animate: bool = False
        self.close: bool = False
        self.refresh: bool = False
        self.update: bool = False
        self._visible: bool = False
        self._init_properties()
        self._data = {}
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

    def set_data(self, data_type: FieldDataType, data: Dict[int, Dict[str, np.array]]):
        """Set data for graphics."""
        self._data[data_type] = data

    def fetch(self):
        """Fetch data for graphics."""
        if not self.post_object:
            return
        obj = self.post_object
        if obj.__class__.__name__ == "Mesh":
            self._fetch_mesh(obj)
        elif obj.__class__.__name__ == "Surface":
            self._fetch_surface(obj)
        elif obj.__class__.__name__ == "Contour":
            self._fetch_contour(obj)
        elif obj.__class__.__name__ == "Vector":
            self._fetch_vector(obj)
        elif obj.__class__.__name__ == "Pathlines":
            self._fetch_pathlines(obj)

    def render(self):
        """Render graphics."""
        if not self.post_object:
            return
        obj = self.post_object
        plotter = self.plotter
        camera = plotter.camera.copy()
        if not self.overlay:
            if in_notebook() and self.plotter.theme._jupyter_backend == "pythreejs":
                plotter.remove_actor(plotter.renderer.actors.copy())
            else:
                plotter.clear()
        if obj.__class__.__name__ == "Mesh":
            self._display_mesh(obj, plotter)
        elif obj.__class__.__name__ == "Surface":
            self._display_surface(obj, plotter)
        elif obj.__class__.__name__ == "Contour":
            self._display_contour(obj, plotter)
        elif obj.__class__.__name__ == "Vector":
            self._display_vector(obj, plotter)
        elif obj.__class__.__name__ == "Pathlines":
            self._display_pathlines(obj, plotter)
        if self.animate:
            plotter.write_frame()
        view = get_config()["set_view_on_display"]
        view_fun = {
            "xy": plotter.view_xy,
            "xz": plotter.view_xz,
            "yx": plotter.view_yx,
            "yz": plotter.view_yz,
            "zx": plotter.view_zx,
            "zy": plotter.view_zy,
            "isometric": plotter.view_isometric,
        }.get(view)
        if view_fun:
            view_fun()
        else:
            plotter.camera = camera.copy()
        if not self._visible and self.show_window:
            plotter.show()
            self._visible = True

    def plot(self):
        """Display graphics."""
        self.fetch()
        self.render()

    # private methods

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

    def _fetch_vector(self, obj):
        if self._data.get(FieldDataType.Vectors) is None or self.fetch_data:
            self._data[FieldDataType.Vectors] = FieldDataExtractor(obj).fetch_data()

    def _display_vector(self, obj, plotter: Union[BackgroundPlotter, pv.Plotter]):
        field_info = obj._api_helper.field_info()
        vectors_of = obj.vectors_of()
        # scalar bar properties
        scalar_bar_args = self._scalar_bar_default_properties()

        field = obj.field()
        field_unit = obj._api_helper.get_field_unit(field)
        field = f"{field}\n[{field_unit}]" if field_unit else field

        for surface_id, mesh_data in self._data[FieldDataType.Vectors].items():
            if "vertices" not in mesh_data or "faces" not in mesh_data:
                continue
            mesh_data["vertices"].shape = mesh_data["vertices"].size // 3, 3
            mesh_data[vectors_of].shape = (
                mesh_data[vectors_of].size // 3,
                3,
            )
            vector_scale = mesh_data["vector-scale"][0]
            topology = "line" if mesh_data["faces"][0] == 2 else "face"
            if topology == "line":
                mesh = pv.PolyData(
                    mesh_data["vertices"],
                    lines=mesh_data["faces"],
                )
            else:
                mesh = pv.PolyData(
                    mesh_data["vertices"],
                    faces=mesh_data["faces"],
                )
            mesh.cell_data["vectors"] = mesh_data[vectors_of]
            scalar_field = mesh_data[obj.field()]
            velocity_magnitude = np.linalg.norm(mesh_data[vectors_of], axis=1)
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
            plotter.add_mesh(
                glyphs,
                scalars=field,
                scalar_bar_args=scalar_bar_args,
                clim=range_,
            )
            if obj.show_edges():
                plotter.add_mesh(mesh, show_edges=True, color="white")

    def _fetch_pathlines(self, obj):
        if self._data.get(FieldDataType.Pathlines) is None or self.fetch_data:
            self._data[FieldDataType.Pathlines] = FieldDataExtractor(obj).fetch_data()

    def _display_pathlines(self, obj, plotter: Union[BackgroundPlotter, pv.Plotter]):
        field = obj.field()
        field_unit = obj._api_helper.get_field_unit(field)
        field = f"{field}\n[{field_unit}]" if field_unit else field

        # scalar bar properties
        scalar_bar_args = self._scalar_bar_default_properties()

        # loop over all meshes
        for surface_id, surface_data in self._data[FieldDataType.Pathlines].items():
            if "vertices" not in surface_data or "lines" not in surface_data:
                continue
            surface_data["vertices"].shape = surface_data["vertices"].size // 3, 3

            mesh = pv.PolyData(
                surface_data["vertices"],
                lines=surface_data["lines"],
            )

            mesh.point_data[field] = surface_data[obj.field()]
            plotter.add_mesh(
                mesh,
                scalars=field,
                scalar_bar_args=scalar_bar_args,
            )

    def _fetch_contour(self, obj):
        if self._data.get(FieldDataType.Contours) is None or self.fetch_data:
            self._data[FieldDataType.Contours] = FieldDataExtractor(obj).fetch_data()

    def _display_contour(self, obj, plotter: Union[BackgroundPlotter, pv.Plotter]):
        # contour properties
        field = obj.field()
        field_unit = obj._api_helper.get_field_unit(field)
        field = f"{field}\n[{field_unit}]" if field_unit else field
        range_option = obj.range.option()
        filled = obj.filled()
        contour_lines = obj.contour_lines()
        node_values = obj.node_values()

        # scalar bar properties
        scalar_bar_args = self._scalar_bar_default_properties()

        # loop over all meshes
        for surface_id, surface_data in self._data[FieldDataType.Contours].items():
            if "vertices" not in surface_data or "faces" not in surface_data:
                continue
            surface_data["vertices"].shape = surface_data["vertices"].size // 3, 3
            topology = "line" if surface_data["faces"][0] == 2 else "face"
            if topology == "line":
                mesh = pv.PolyData(
                    surface_data["vertices"],
                    lines=surface_data["faces"],
                )
            else:
                mesh = pv.PolyData(
                    surface_data["vertices"],
                    faces=surface_data["faces"],
                )
            if node_values:
                mesh.point_data[field] = surface_data[obj.field()]
            else:
                mesh.cell_data[field] = surface_data[obj.field()]
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
                                plotter.add_mesh(
                                    minimum_above,
                                    scalars=field,
                                    show_edges=obj.show_edges(),
                                    scalar_bar_args=scalar_bar_args,
                                )

                            if (not filled or contour_lines) and (
                                np.min(minimum_above[field])
                                != np.max(minimum_above[field])
                            ):
                                plotter.add_mesh(minimum_above.contour(isosurfaces=20))
                else:
                    if filled:
                        plotter.add_mesh(
                            mesh,
                            clim=[
                                auto_range_off.minimum(),
                                auto_range_off.maximum(),
                            ],
                            scalars=field,
                            show_edges=obj.show_edges(),
                            scalar_bar_args=scalar_bar_args,
                        )
                    if (not filled or contour_lines) and (
                        np.min(mesh[field]) != np.max(mesh[field])
                    ):
                        plotter.add_mesh(mesh.contour(isosurfaces=20))
            else:
                auto_range_on = obj.range.auto_range_on
                if auto_range_on.global_range():
                    if filled:
                        field_info = obj._api_helper.field_info()
                        plotter.add_mesh(
                            mesh,
                            clim=field_info.get_scalar_field_range(obj.field(), False),
                            scalars=field,
                            show_edges=obj.show_edges(),
                            scalar_bar_args=scalar_bar_args,
                        )
                    if (not filled or contour_lines) and (
                        np.min(mesh[field]) != np.max(mesh[field])
                    ):
                        plotter.add_mesh(mesh.contour(isosurfaces=20))

                else:
                    if filled:
                        plotter.add_mesh(
                            mesh,
                            scalars=field,
                            show_edges=obj.show_edges(),
                            scalar_bar_args=scalar_bar_args,
                        )
                    if (not filled or contour_lines) and (
                        np.min(mesh[field]) != np.max(mesh[field])
                    ):
                        plotter.add_mesh(mesh.contour(isosurfaces=20))

    def _fetch_surface(self, obj):
        dummy_object = "dummy_object"
        post_session = obj.get_root()
        if (
            obj.definition.type() == "iso-surface"
            and obj.definition.iso_surface.rendering() == "contour"
        ):
            contour = post_session.Contours[dummy_object]
            contour.field = obj.definition.iso_surface.field()
            contour.surfaces_list = [obj._name]
            contour.show_edges = obj.show_edges()
            contour.range.auto_range_on.global_range = True
            contour.boundary_values = True
            self._fetch_contour(contour)
            del post_session.Contours[dummy_object]
        else:
            mesh = post_session.Meshes[dummy_object]
            mesh.surfaces_list = [obj._name]
            mesh.show_edges = obj.show_edges()
            self._fetch_mesh(mesh)
            del post_session.Meshes[dummy_object]

    def _display_surface(self, obj, plotter: Union[BackgroundPlotter, pv.Plotter]):
        dummy_object = "dummy_object"
        post_session = obj.get_root()
        if (
            obj.definition.type() == "iso-surface"
            and obj.definition.iso_surface.rendering() == "contour"
        ):
            contour = post_session.Contours[dummy_object]
            contour.field = obj.definition.iso_surface.field()
            contour.surfaces_list = [obj._name]
            contour.show_edges = obj.show_edges()
            contour.range.auto_range_on.global_range = True
            contour.boundary_values = True
            self._display_contour(contour, plotter)
            del post_session.Contours[dummy_object]
        else:
            mesh = post_session.Meshes[dummy_object]
            mesh.surfaces_list = [obj._name]
            mesh.show_edges = obj.show_edges()
            self._display_mesh(mesh, plotter)
            del post_session.Meshes[dummy_object]

    def _fetch_mesh(self, obj):
        if self._data.get(FieldDataType.Meshes) is None or self.fetch_data:
            self._data[FieldDataType.Meshes] = FieldDataExtractor(obj).fetch_data()

    def _display_mesh(self, obj, plotter: Union[BackgroundPlotter, pv.Plotter]):
        for surface_id, mesh_data in self._data[FieldDataType.Meshes].items():
            if "vertices" not in mesh_data or "faces" not in mesh_data:
                continue
            mesh_data["vertices"].shape = mesh_data["vertices"].size // 3, 3
            topology = "line" if mesh_data["faces"][0] == 2 else "face"
            if topology == "line":
                mesh = pv.PolyData(
                    mesh_data["vertices"],
                    lines=mesh_data["faces"],
                )
            else:
                mesh = pv.PolyData(
                    mesh_data["vertices"],
                    faces=mesh_data["faces"],
                )
            color_size = len(self._colors.values())
            color = list(self._colors.values())[surface_id % color_size]
            plotter.add_mesh(mesh, show_edges=obj.show_edges(), color=color)

    def _get_refresh_for_plotter(self, window: "PyVistaWindow"):
        def refresh():
            with PyVistaWindowsManager._condition:
                plotter = window.plotter
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
                    PyVistaWindowsManager._condition.notify()

        return refresh


class PyVistaWindowsManager(PostWindowsManager, metaclass=AbstractSingletonMeta):
    """Provides for managing PyVista windows."""

    _condition = threading.Condition()

    def __init__(self):
        """Instantiate ``PyVistaWindow`` for PyVista."""
        self._post_windows: Dict[str:PyVistaWindow] = {}
        self._plotter_thread: threading.Thread = None
        self._post_object: GraphicsDefn = None
        self._window_id: Optional[str] = None
        self._exit_thread: bool = False
        self._app = None

    def get_window(self, window_id: str) -> PyVistaWindow:
        """Get the PyVista window.

        Parameters
        ----------
        window_id : str
            Window ID.

        Returns
        -------
        PyVistaWindow
            PyVista window.
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
            return self._post_windows[window_id].plotter

    def open_window(self, window_id: Optional[str] = None) -> str:
        """Open a new window.

        Parameters
        ----------
        window_id : str, optional
            ID for the new window. The default is ``None``, in which
            case a unique ID is automatically assigned.

        Returns
        -------
        str
            ID for the new window.
        """
        with self._condition:
            if not window_id:
                window_id = self._get_unique_window_id()
            if in_notebook() or get_config()["blocking"]:
                self._open_window_notebook(window_id)
            else:
                self._open_and_plot_console(None, window_id)
            return window_id

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

    def plot(
        self,
        object: GraphicsDefn,
        window_id: Optional[str] = None,
        fetch_data: Optional[bool] = False,
        overlay: Optional[bool] = False,
    ) -> None:
        """Draw a plot.

        Parameters
        ----------
        object: GraphicsDefn
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
        if not isinstance(object, GraphicsDefn):
            raise RuntimeError("Object type currently not supported.")
        with self._condition:
            if not window_id:
                window_id = self._get_unique_window_id()
            if in_notebook() or get_config()["blocking"]:
                self._plot_notebook(object, window_id, fetch_data, overlay)
            else:
                self._open_and_plot_console(object, window_id, fetch_data, overlay)

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
            Graphic file format. Supported formats are SVG, EPS, PS, PDF, and TEX.

        Raises
        ------
        ValueError
            If the window does not support the specified format.
        """
        with self._condition:
            window = self._post_windows.get(window_id)
            if window:
                window.plotter.save_graphic(f"{window_id}.{format}")

    def refresh_windows(
        self,
        session_id: Optional[str] = "",
        windows_id: Optional[List[str]] = [],
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
        windows_id: Optional[List[str]] = [],
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
        with self._condition:
            windows_id = self._get_windows_id(session_id, windows_id)
            for window_id in windows_id:
                window = self._post_windows.get(window_id)
                if window:
                    window.animate = True
                    window.plotter.open_gif(f"{window.id}.gif")

    def close_windows(
        self,
        session_id: Optional[str] = "",
        windows_id: Optional[List[str]] = [],
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
        with self._condition:
            windows_id = self._get_windows_id(session_id, windows_id)
            for window_id in windows_id:
                window = self._post_windows.get(window_id)
                if window:
                    if in_notebook() or get_config()["blocking"]:
                        window.plotter.close()
                    window.close = True

    # private methods

    def _display(self) -> None:
        while True:
            with self._condition:
                if self._exit_thread:
                    break
                if self._window_id:
                    window = self._post_windows.get(self._window_id)
                    plotter = window.plotter if window else None
                    animate = window.animate if window else False
                    if not plotter or plotter._closed:
                        window = PyVistaWindow(self._window_id, self._post_object)
                        plotter = window.plotter
                        self._app = plotter.app
                        plotter.add_callback(
                            window._get_refresh_for_plotter(window),
                            100,
                        )
                    window.post_object = self._post_object
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
                plotter = window.plotter
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
    ) -> None:
        if self._exit_thread:
            return
        with self._condition:
            self._window_id = window_id
            self._post_object = obj
            self._fetch_data = fetch_data
            self._overlay = overlay

        if not self._plotter_thread:
            if FluentConnection._monitor_thread:
                FluentConnection._monitor_thread.cbs.append(self._exit)
            self._plotter_thread = threading.Thread(target=self._display, args=())
            self._plotter_thread.start()

        with self._condition:
            self._condition.wait()

    def _open_window_notebook(self, window_id: str) -> pv.Plotter:
        window = self._post_windows.get(window_id)
        if window and not window.close and window.refresh:
            window.refresh = False
        else:
            window = PyVistaWindow(window_id, None)
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

    def _get_windows_id(
        self,
        session_id: Optional[str] = "",
        windows_id: Optional[List[str]] = [],
    ) -> List[str]:
        with self._condition:
            return [
                window_id
                for window_id in [
                    window_id
                    for window_id, window in self._post_windows.items()
                    if not window.plotter._closed
                    and (
                        not session_id
                        or session_id == window.post_object._api_helper.id()
                    )
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
                window_id = f"window-{next(itr_count)}"
                if window_id not in self._post_windows:
                    return window_id


pyvista_windows_manager = PyVistaWindowsManager()
