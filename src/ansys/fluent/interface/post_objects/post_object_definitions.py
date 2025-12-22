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

"""Module providing visualization objects definition."""

import abc
import logging
from abc import abstractmethod
from typing import TYPE_CHECKING, Literal, NamedTuple

from ansys.fluent.interface.post_objects.meta import (
    Attribute,
    PyLocalNamedObjectAbstract,
    PyLocalObjectMeta,
    PyLocalProperty,
    PyLocalPropertyMeta,
)

if TYPE_CHECKING:
    from ansys.fluent.interface.post_objects.post_objects_container import Container

logger = logging.getLogger("pyfluent.post_objects")


class BasePostObjectDefn(abc.ABC):
    """Base class for visualization objects."""

    @abc.abstractmethod
    def get_root(self) -> Container:
        raise NotImplementedError

    @abc.abstractmethod
    def surfaces(self) -> list[str]:
        raise NotImplementedError

    def _pre_display(self):
        local_surfaces_provider = self.get_root()._local_surfaces_provider()
        for surf_name in self.surfaces():
            if surf_name in list(local_surfaces_provider):
                surf_obj = local_surfaces_provider[surf_name]
                surf_api = surf_obj._api_helper.surface_api
                surf_api.create_surface_on_server()

    def _post_display(self):
        local_surfaces_provider = self.get_root()._local_surfaces_provider()
        for surf_name in self.surfaces():
            if surf_name in list(local_surfaces_provider):
                surf_obj = local_surfaces_provider[surf_name]
                surf_api = surf_obj._api_helper.surface_api
                surf_api.delete_surface_on_server()


class GraphicsDefn(BasePostObjectDefn, PyLocalNamedObjectAbstract):
    """Abstract base class for graphics objects."""

    @abstractmethod
    def display(self, window_id: str | None = None):
        """Display graphics.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If not specified, unique ID is used.
        """
        pass


class PlotDefn(BasePostObjectDefn, metaclass=PyLocalNamedObjectAbstract):
    """Abstract base class for plot objects."""

    @abstractmethod
    def plot(self, window_id: str | None = None):
        """Draw plot.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If not specified, unique ID is used.
        """
        pass


class Vector(NamedTuple):
    """Class for vector definition."""

    x: float
    y: float
    z: float


class MonitorDefn(PlotDefn):
    """Monitor Definition."""

    PLURAL = "Monitors"

    class monitor_set_name(PyLocalProperty):
        """Monitor set name."""

        value: str = None

        @Attribute
        def allowed_values(self):
            """Monitor set allowed values."""
            return self.monitors.get_monitor_set_names()


class XYPlotDefn(PlotDefn):
    """XYPlot Definition."""

    PLURAL = "XYPlots"

    class node_values(PyLocalProperty):
        """Plot nodal values."""

        value: bool = True

    class boundary_values(PyLocalProperty):
        """Plot Boundary values."""

        value: bool = True

    class direction_vector(PyLocalProperty):
        """Direction Vector."""

        value: Vector = [1, 0, 0]

    class y_axis_function(PyLocalProperty):
        """Y Axis Function."""

        value: str = None

        @Attribute
        def allowed_values(self):
            """Y axis function allowed values."""
            return list(self.field_data.scalar_fields())

    class x_axis_function(PyLocalProperty):
        """X Axis Function."""

        value: str = "direction-vector"

        @Attribute
        def allowed_values(self) -> list[str]:
            """X axis function allowed values."""
            return ["direction-vector"]

    class surfaces(PyLocalProperty):
        """List of surfaces for plotting."""

        value: list[str] = []

        @Attribute
        def allowed_values(self):
            """Surface list allowed values."""
            return list(self.field_data.surfaces()) + list(
                self.get_root()._local_surfaces_provider()
            )


class MeshDefn(GraphicsDefn):
    """Mesh graphics definition."""

    PLURAL = "Meshes"

    class surfaces(PyLocalProperty):
        """List of surfaces for mesh graphics."""

        value: list[str] = []

        @Attribute
        def allowed_values(self):
            """Surface list allowed values."""
            return list(self.field_data.surfaces()) + list(
                self.get_root()._local_surfaces_provider()
            )

    class show_edges(PyLocalProperty):
        """Show edges for mesh."""

        value: bool = False

    class show_nodes(PyLocalProperty):
        """Show nodes for mesh."""

        value: bool = False

    class show_faces(PyLocalProperty):
        """Show faces for mesh."""

        value: bool = True


class PathlinesDefn(GraphicsDefn):
    """Pathlines definition."""

    PLURAL = "Pathlines"

    class field(PyLocalProperty):
        """Pathlines field."""

        value: str = None

        @Attribute
        def allowed_values(self):
            """Field allowed values."""
            return list(self.field_data.scalar_fields())

    class surfaces(PyLocalProperty):
        """List of surfaces for pathlines."""

        value: list[str] = []

        @Attribute
        def allowed_values(self):
            """Surface list allowed values."""
            return list(self.field_data.surfaces()) + list(
                self.get_root()._local_surfaces_provider()
            )


class SurfaceDefn(GraphicsDefn):
    """Surface graphics definition."""

    PLURAL = "Surfaces"

    @property
    def name(self) -> str:
        """Return name of the surface."""
        return self._name

    class show_edges(PyLocalProperty[bool]):
        """Show edges for surface."""

        value: bool = True

    class definition(metaclass=PyLocalObjectMeta):
        """Specify surface definition type."""

        class type(PyLocalProperty[Literal["plane-surface", "iso-surface"]]):
            """Surface type."""

            value = "iso-surface"

            @Attribute
            def allowed_values(self):
                """Surface type allowed values."""
                return ["plane-surface", "iso-surface"]

        class plane_surface(metaclass=PyLocalObjectMeta):
            """Plane surface definition."""

            @Attribute
            def is_active(self):
                """Check whether current object is active or not."""
                return self._parent.type() == "plane-surface"

            class creation_method(PyLocalProperty):
                """Creation Method."""

                value: str = "xy-plane"

                @Attribute
                def allowed_values(self):
                    """Surface type allowed values."""
                    return ["xy-plane", "yz-plane", "zx-plane", "point-and-normal"]

            class point(metaclass=PyLocalObjectMeta):
                """Point entry for point-and-normal surface."""

                @Attribute
                def is_active(self):
                    """Check whether current object is active or not."""
                    return self._parent.creation_method() == "point-and-normal"

                class x(PyLocalProperty):
                    """X value."""

                    value: float = 0

                    @Attribute
                    def range(self):
                        """X value range."""
                        return self.field_data.scalar_fields.range("x-coordinate", True)

                class y(PyLocalProperty):
                    """Y value."""

                    value: float = 0

                    @Attribute
                    def range(self):
                        """Y value range."""
                        return self.field_data.scalar_fields.range("y-coordinate", True)

                class z(PyLocalProperty):
                    """Z value."""

                    value: float = 0

                    @Attribute
                    def range(self):
                        """Z value range."""
                        return self.field_data.scalar_fields.range("z-coordinate", True)

            class normal(metaclass=PyLocalObjectMeta):
                """Normal entry for point-and-normal surface."""

                @Attribute
                def is_active(self):
                    """Check whether current object is active or not."""
                    return self._parent.creation_method() == "point-and-normal"

                class x(PyLocalProperty):
                    """X value."""

                    value: float = 0

                    @Attribute
                    def range(self):
                        """X value range."""
                        return [-1, 1]

                class y(PyLocalProperty):
                    """Y value."""

                    value: float = 0

                    @Attribute
                    def range(self):
                        """Y value range."""
                        return [-1, 1]

                class z(PyLocalProperty):
                    """Z value."""

                    value: float = 0

                    @Attribute
                    def range(self):
                        """Z value range."""
                        return [-1, 1]

            class xy_plane(metaclass=PyLocalObjectMeta):
                """XY Plane definition."""

                @Attribute
                def is_active(self):
                    """Check whether current object is active or not."""
                    return self._parent.creation_method() == "xy-plane"

                class z(PyLocalProperty):
                    """Z value."""

                    value: float = 0

                    @Attribute
                    def range(self):
                        """Z value range."""
                        return self.field_data.scalar_fields.range("z-coordinate", True)

            class yz_plane(metaclass=PyLocalObjectMeta):
                """YZ Plane definition."""

                @Attribute
                def is_active(self):
                    """Check whether current object is active or not."""
                    return self._parent.creation_method() == "yz-plane"

                class x(PyLocalProperty):
                    """X value."""

                    value: float = 0

                    @Attribute
                    def range(self):
                        """X value range."""
                        return self.field_data.scalar_fields.range("x-coordinate", True)

            class zx_plane(metaclass=PyLocalObjectMeta):
                """ZX Plane definition."""

                @Attribute
                def is_active(self):
                    """Check whether current object is active or not."""
                    return self._parent.creation_method() == "zx-plane"

                class y(PyLocalProperty):
                    """Y value."""

                    value: float = 0

                    @Attribute
                    def range(self):
                        """Y value range."""
                        return self.field_data.scalar_fields.range("y-coordinate", True)

        class iso_surface(metaclass=PyLocalObjectMeta):
            """Iso surface definition."""

            @Attribute
            def is_active(self):
                """Check whether current object is active or not."""
                return self._parent.type() == "iso-surface"

            class field(PyLocalProperty):
                """Iso surface field."""

                value: str = None

                @Attribute
                def allowed_values(self):
                    """Field allowed values."""
                    return list(self.field_data.scalar_fields())

            class rendering(PyLocalProperty):
                """Iso surface rendering."""

                value: str = "mesh"

                @Attribute
                def allowed_values(self):
                    """Surface rendering allowed values."""
                    return ["mesh", "contour"]

            class iso_value(PyLocalProperty):
                """Iso value for field."""

                _value: float = None

                def _reset_on_change(self):
                    return [self._parent.field]

                @property
                def value(self):
                    """Iso value property setter."""
                    if getattr(self, "_value", None) is None:
                        rnge = self.range
                        self._value = (rnge[0] + rnge[1]) / 2.0 if rnge else None
                    return self._value

                @value.setter
                def value(self, value):
                    self._value = value

                @Attribute
                def range(self):
                    """Iso value range."""
                    field = self._parent.field()
                    if field:
                        return self.field_data.scalar_fields.range(field, True)


class ContourDefn(GraphicsDefn):
    """Contour graphics definition."""

    PLURAL = "Contours"

    class field(PyLocalProperty):
        """Contour field."""

        value: str = None

        @Attribute
        def allowed_values(self):
            """Field allowed values."""
            return list(self.field_data.scalar_fields())

    class surfaces(PyLocalProperty):
        """Contour surfaces."""

        value: list[str] = []

        @Attribute
        def allowed_values(self):
            """Surfaces list allowed values."""
            return list(self.field_data.surfaces()) + list(
                self.get_root()._local_surfaces_provider()
            )

    class filled(PyLocalProperty):
        """Draw filled contour."""

        value: bool = True

    class node_values(PyLocalProperty):
        """Draw nodal data."""

        _value: bool = True

        @Attribute
        def is_active(self):
            """Check whether current object is active or not."""
            filled = self.get_ancestors_by_type(ContourDefn).filled()
            auto_range_off = self.get_ancestors_by_type(
                ContourDefn
            ).range.auto_range_off
            if (
                filled is False
                or (auto_range_off and auto_range_off.clip_to_range()) is True
            ):
                return False
            return True

        @property
        def value(self):
            """Node value property setter."""
            if self.is_active is False:
                return True
            return self._value

        @value.setter
        def value(self, value):
            if value is False and self.is_active is False:
                raise ValueError(
                    "For unfilled and clipped contours, node values must be displayed. "
                )
            self._value = value

    class boundary_values(PyLocalProperty):
        """Draw boundary values."""

        value: bool = False

    class contour_lines(PyLocalProperty):
        """Draw contour lines."""

        value: bool = False

    class show_edges(PyLocalProperty):
        """Show edges."""

        value: bool = False

    class range(metaclass=PyLocalObjectMeta):
        """Range definition."""

        class option(PyLocalProperty):
            """Range option."""

            value: str = "auto-range-on"

            @Attribute
            def allowed_values(self):
                """Range option allowed values."""
                return ["auto-range-on", "auto-range-off"]

        class auto_range_on(metaclass=PyLocalObjectMeta):
            """Auto range on definition."""

            @Attribute
            def is_active(self):
                """Check whether current object is active or not."""
                return self._parent.option() == "auto-range-on"

            class global_range(PyLocalProperty):
                """Show global range."""

                value: bool = False

        class auto_range_off(metaclass=PyLocalObjectMeta):
            """Auto range off definition."""

            @Attribute
            def is_active(self):
                """Check whether current object is active or not."""
                return self._parent.option() == "auto-range-off"

            class clip_to_range(PyLocalProperty):
                """Clip contour within range."""

                value: bool = False

            class minimum(PyLocalProperty):
                """Range minimum."""

                _value: float = None

                def _reset_on_change(self):
                    return [
                        self.get_ancestors_by_type(ContourDefn).field,
                        self.get_ancestors_by_type(ContourDefn).node_values,
                    ]

                @property
                def value(self):
                    """Range minimum property setter."""
                    if getattr(self, "_value", None) is None:
                        field = self.get_ancestors_by_type(ContourDefn).field()
                        if field:
                            field_data = self.field_data
                            field_range = field_data.scalar_fields.range(
                                field,
                                self.get_ancestors_by_type(ContourDefn).node_values(),
                            )
                            self._value = field_range[0]
                    return self._value

                @value.setter
                def value(self, value):
                    self._value = value

            class maximum(PyLocalProperty):
                """Range maximum."""

                _value: float = None

                def _reset_on_change(self):
                    return [
                        self.get_ancestors_by_type(ContourDefn).field,
                        self.get_ancestors_by_type(ContourDefn).node_values,
                    ]

                @property
                def value(self):
                    """Range maximum property setter."""
                    if getattr(self, "_value", None) is None:
                        field = self.get_ancestors_by_type(ContourDefn).field()
                        if field:
                            field_data = self.field_data
                            field_range = field_data.scalar_fields.range(
                                field,
                                self.get_ancestors_by_type(ContourDefn).node_values(),
                            )
                            self._value = field_range[1]

                    return self._value

                @value.setter
                def value(self, value):
                    self._value = value


class VectorDefn(GraphicsDefn):
    """Vector graphics definition."""

    PLURAL = "Vectors"

    class vectors_of(PyLocalProperty):
        """Vector type."""

        value: str = None

        @Attribute
        def allowed_values(self):
            """Vectors of allowed values."""
            return list(self.field_data.vector_fields())

    class field(PyLocalProperty):
        """Vector color field."""

        value: str = None

        @Attribute
        def allowed_values(self):
            """Field allowed values."""
            return list(self.field_data.scalar_fields())

    class surfaces(PyLocalProperty):
        """List of surfaces for vector graphics."""

        value: list[str] = []

        @Attribute
        def allowed_values(self):
            """Surface list allowed values."""
            return list(self.field_data.surfaces()) + list(
                self.get_root()._local_surfaces_provider()
            )

    class scale(PyLocalProperty):
        """Vector scale."""

        value: float = 1.0

    class skip(PyLocalProperty):
        """Vector skip."""

        value: int = 0

    class show_edges(PyLocalProperty):
        """Show edges."""

        value: bool = False

    class range(metaclass=PyLocalObjectMeta):
        """Range definition."""

        class option(PyLocalProperty):
            """Range option."""

            value: str = "auto-range-on"

            @Attribute
            def allowed_values(self):
                """Range option allowed values."""
                return ["auto-range-on", "auto-range-off"]

        class auto_range_on(metaclass=PyLocalObjectMeta):
            """Auto range on definition."""

            @Attribute
            def is_active(self):
                """Check whether current object is active or not."""
                return self._parent.option() == "auto-range-on"

            class global_range(PyLocalProperty):
                """Show global range."""

                value: bool = False

        class auto_range_off(metaclass=PyLocalObjectMeta):
            """Auto range off definition."""

            @Attribute
            def is_active(self):
                """Check whether current object is active or not."""
                return self._parent.option() == "auto-range-off"

            class clip_to_range(PyLocalProperty):
                """Clip vector within range."""

                value: bool = False

            class minimum(PyLocalProperty):
                """Range minimum."""

                _value: float = None

                @property
                def value(self):
                    """Range minimum property setter."""
                    if getattr(self, "_value", None) is None:
                        field_data = self.field_data
                        field_range = field_data.scalar_fields.range(
                            "velocity-magnitude",
                            False,
                        )
                        self._value = field_range[0]
                    return self._value

                @value.setter
                def value(self, value):
                    self._value = value

            class maximum(PyLocalProperty):
                """Range maximum."""

                _value: float = None

                @property
                def value(self):
                    """Range maximum property setter."""
                    if getattr(self, "_value", None) is None:
                        field_data = self.field_data
                        field_range = field_data.scalar_fields.range(
                            "velocity-magnitude",
                            False,
                        )
                        self._value = field_range[1]
                    return self._value

                @value.setter
                def value(self, value):
                    self._value = value
