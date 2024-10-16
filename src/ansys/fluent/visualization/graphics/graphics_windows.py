"""Module for graphics windows management."""

from enum import Enum
from typing import Dict

from ansys.fluent.core.post_objects.check_in_notebook import in_notebook
import numpy as np
import pyvista as pv

from ansys.fluent.visualization import get_config
from ansys.fluent.visualization.post_data_extractor import FieldDataExtractor
from ansys.fluent.visualization.post_windows_manager import PostWindow


class FieldDataType(Enum):
    """Provides surface data types."""

    Meshes = "Mesh"
    Vectors = "Vector"
    Contours = "Contour"
    Pathlines = "Pathlines"


from ansys.fluent.visualization.graphics.pyvista.graphics_defns import Renderer


class GraphicsWindow(PostWindow):
    """Provides for managing Graphics windows."""

    def __init__(self, id: str | None = None):
        """Instantiate a Graphics window.

        Parameters
        ----------
        id : str|None
            Window ID.
        """
        self.renderer = Renderer(None, in_notebook(), get_config()["blocking"])
        self._data = {}

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
        else:
            self._fetch_data(obj, FieldDataType(obj.__class__.__name__))

    def render(self):
        """Render graphics."""
        if not self.post_object:
            return
        obj = self.post_object

        if not self.overlay:
            self.renderer._clear_plotter(in_notebook())
        if obj.__class__.__name__ == "Mesh":
            self._display_mesh(obj)
        elif obj.__class__.__name__ == "Surface":
            self._display_surface(obj)
        elif obj.__class__.__name__ == "Contour":
            self._display_contour(obj)
        elif obj.__class__.__name__ == "Vector":
            self._display_vector(obj)
        elif obj.__class__.__name__ == "Pathlines":
            self._display_pathlines(obj)
        if self.animate:
            self.renderer.write_frame()
        self.renderer._set_camera(get_config()["set_view_on_display"])

    def plot(self, post_object=None):
        """Render graphics.

        Parameters
        ----------
        post_object : GraphicsDefn
            Object to draw.
        """
        self.post_object = post_object
        self.fetch()
        self.render()

    def show(self):
        """Display Graphics window."""
        self.renderer.show()

    # private methods
    def _fetch_data(self, obj, data_type: FieldDataType):
        if self._data.get(data_type) is None or self.fetch_data:
            self._data[data_type] = FieldDataExtractor(obj).fetch_data()

    def _fetch_or_display_surface(self, obj, fetch: bool):
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
            if fetch:
                self._fetch_data(contour, FieldDataType.Contours)
            else:
                self._display_contour(contour)
            del post_session.Contours[dummy_object]
        else:
            mesh = post_session.Meshes[dummy_object]
            mesh.surfaces_list = [obj._name]
            mesh.show_edges = obj.show_edges()
            if fetch:
                self._fetch_data(mesh, FieldDataType.Meshes)
            else:
                self._display_mesh(mesh)
            del post_session.Meshes[dummy_object]

    def _fetch_surface(self, obj):
        self._fetch_or_display_surface(obj, fetch=True)

    def _resolve_mesh_data(self, mesh_data):
        topology = "line" if mesh_data["faces"][0] == 2 else "face"
        if topology == "line":
            return pv.PolyData(
                mesh_data["vertices"],
                lines=mesh_data["faces"],
            )
        else:
            return pv.PolyData(
                mesh_data["vertices"],
                faces=mesh_data["faces"],
            )

    def _display_vector(self, obj):
        field_info = obj._api_helper.field_info()
        vectors_of = obj.vectors_of()
        # scalar bar properties
        scalar_bar_args = self.renderer._scalar_bar_default_properties()

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
            mesh = self._resolve_mesh_data(mesh_data)
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
            self.renderer.render(
                glyphs,
                scalars=field,
                scalar_bar_args=scalar_bar_args,
                clim=range_,
            )
            if obj.show_edges():
                self.renderer.render(mesh, show_edges=True, color="white")

    def _display_pathlines(self, obj):
        field = obj.field()
        field_unit = obj._api_helper.get_field_unit(field)
        field = f"{field}\n[{field_unit}]" if field_unit else field

        # scalar bar properties
        scalar_bar_args = self.renderer._scalar_bar_default_properties()

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
            self.renderer.render(
                mesh,
                scalars=field,
                scalar_bar_args=scalar_bar_args,
            )

    def _display_contour(self, obj):
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
            if "vertices" not in surface_data or "faces" not in surface_data:
                continue
            surface_data["vertices"].shape = surface_data["vertices"].size // 3, 3
            mesh = self._resolve_mesh_data(surface_data)
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
                                self.renderer.render(
                                    minimum_above,
                                    scalars=field,
                                    show_edges=obj.show_edges(),
                                    scalar_bar_args=scalar_bar_args,
                                )

                            if (not filled or contour_lines) and (
                                np.min(minimum_above[field])
                                != np.max(minimum_above[field])
                            ):
                                self.renderer.render(
                                    minimum_above.contour(isosurfaces=20)
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
                        )
                    if (not filled or contour_lines) and (
                        np.min(mesh[field]) != np.max(mesh[field])
                    ):
                        self.renderer.render(mesh.contour(isosurfaces=20))
            else:
                auto_range_on = obj.range.auto_range_on
                if auto_range_on.global_range():
                    if filled:
                        field_info = obj._api_helper.field_info()
                        self.renderer.render(
                            mesh,
                            clim=field_info.get_scalar_field_range(obj.field(), False),
                            scalars=field,
                            show_edges=obj.show_edges(),
                            scalar_bar_args=scalar_bar_args,
                        )
                    if (not filled or contour_lines) and (
                        np.min(mesh[field]) != np.max(mesh[field])
                    ):
                        self.renderer.render(mesh.contour(isosurfaces=20))

                else:
                    if filled:
                        self.renderer.render(
                            mesh,
                            scalars=field,
                            show_edges=obj.show_edges(),
                            scalar_bar_args=scalar_bar_args,
                        )
                    if (not filled or contour_lines) and (
                        np.min(mesh[field]) != np.max(mesh[field])
                    ):
                        self.renderer.render(mesh.contour(isosurfaces=20))

    def _display_surface(self, obj):
        self._fetch_or_display_surface(obj, fetch=False)

    def _display_mesh(self, obj):
        for surface_id, mesh_data in self._data[FieldDataType.Meshes].items():
            if "vertices" not in mesh_data or "faces" not in mesh_data:
                continue
            mesh_data["vertices"].shape = mesh_data["vertices"].size // 3, 3
            mesh = self._resolve_mesh_data(mesh_data)
            color_size = len(self.renderer._colors)
            color = list(self.renderer._colors.values())[surface_id % color_size]
            self.renderer.render(mesh, show_edges=obj.show_edges(), color=color)
